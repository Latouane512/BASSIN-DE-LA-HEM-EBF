from qgis.core import *
import processing

# --- CONFIGURATION ---
nom_riviere = '2025_HYDRO_HEM'  # Ta couche avec "largeur_moy"
nom_ocs = 'OCSGE_HEM'                 # Ta couche OCSGE
nom_rpg = 'RPG_HEM'                   # Remplace par le nom exact de ta couche RPG dans QGIS
# ---------------------

project = QgsProject.instance()

# Vérification de la présence des 3 couches nécessaires
try:
    riv_layer = project.mapLayersByName(nom_riviere)[0]
    ocs_layer = project.mapLayersByName(nom_ocs)[0]
    rpg_layer = project.mapLayersByName(nom_rpg)[0]
except IndexError:
    print("ERREUR : Vérifiez le nom de vos trois couches dans QGIS (Orthographe/Majuscules).")

def generer_ebf_geochimique(distance_cible):
    print(f"\n--- Traitement Hypothèse : {distance_cible}m (Croisement OCSGE x RPG avec Zone Urbaine) ---")
    
    # 1. Buffer Dynamique : (Largeur / 2) + distance
    expr_buffer = f'("largeur_moy" / 2) + {distance_cible}'
    
    params_buf = {
        'INPUT': riv_layer,
        'DISTANCE': QgsProperty.fromExpression(expr_buffer),
        'DISSOLVE': True,
        'OUTPUT': 'memory:buf_brut'
    }
    buf_brut = processing.run("native:buffer", params_buf)['OUTPUT']

    # 2. Intersection spatiale avec l'OCSGE
    params_int = {
        'INPUT': buf_brut,
        'OVERLAY': ocs_layer,
        'OUTPUT': 'memory:ebf_inter'
    }
    ebf_inter = processing.run("native:intersection", params_int)['OUTPUT']

    # 3. Préparation de l'index spatial RPG pour un croisement ultra-rapide
    index_rpg = QgsSpatialIndex(rpg_layer.getFeatures())
    
    # Détection automatique des colonnes clés
    colonnes_ocs = [f.name() for f in ebf_inter.fields()]
    col_code_cs = next((c for c in colonnes_ocs if 'CODE_CS' in c.upper()), None)
    
    colonnes_rpg = [f.name() for f in rpg_layer.fields()]
    col_group_rpg = next((c for c in colonnes_rpg if 'GROUP' in c.upper()), None)

    # Création de la couche finale de sortie (contient toutes les classes, y compris l'urbain)
    final_layer = QgsVectorLayer("MultiPolygon?crs=" + riv_layer.crs().authid(), f"EBF_Complet_RPG_{distance_cible}m", "memory")
    final_layer.dataProvider().addAttributes(ebf_inter.fields())
    final_layer.updateFields()
    
    # Initialisation des compteurs de surfaces
    total_area = 0
    naturel_area = 0
    agricole_area = 0
    urbain_area = 0
    features_finales = []

    # 4. Boucle d'analyse spatiale et d'arbitrage OCSGE x RPG x Urbain
    for f in ebf_inter.getFeatures():
        code_cs = str(f[col_code_cs]) if col_code_cs else ""
        geom = f.geometry()
        area = geom.area()
        
        total_area += area
        features_finales.append(f)
        
        # CAS 1 : Zone Urbaine / Imperméabilisée (Bâti dur, infrastructures, routes)
        if code_cs.startswith('CS1.1'):
            urbain_area += area
            continue # Passe directement à l'entité suivante
            
        # Requête spatiale pour les espaces herbacés/agricoles : intersecte-t-on le RPG ?
        ids_rpg_potentiels = index_rpg.intersects(geom.boundingBox())
        est_dans_rpg = False
        group_rpg = None
        
        for rpg_id in ids_rpg_potentiels:
            f_rpg = rpg_layer.getFeature(rpg_id)
            if geom.intersects(f_rpg.geometry()):
                est_dans_rpg = True
                if col_group_rpg and f_rpg[col_group_rpg] is not None:
                    try:
                        group_rpg = int(f_rpg[col_group_rpg])
                    except (ValueError, TypeError):
                        group_rpg = 0
                break # On retient le premier groupe dominant trouvé
        
        # CAS 2 : Application de la typologie sur les surfaces non-urbaines
        if est_dans_rpg:
            if group_rpg == 18:
                # Groupe 18 = Prairies Permanentes (PPH) -> Déjà fonctionnel
                naturel_area += area
            else:
                # Groupes 19 (PTR), 16 (Légumineuses) et autres cultures -> Potentiel de restauration
                agricole_area += area
        else:
            # Hors RPG (Forêts CS2.2, friches naturelles, surfaces en eau) -> Déjà fonctionnel
            naturel_area += area

    final_layer.dataProvider().addFeatures(features_finales)
    project.addMapLayer(final_layer)

    # 5. Calcul des ratios et affichage des indicateurs pour le mémoire
    pct_naturel = (naturel_area / total_area * 100) if total_area > 0 else 0
    pct_agricole = (agricole_area / total_area * 100) if total_area > 0 else 0
    pct_urbain = (urbain_area / total_area * 100) if total_area > 0 else 0
    
    print(f"RÉSULTATS POUR {distance_cible}m :")
    print(f"  > Surface totale de l'EBF (Emprise globale) : {round(total_area / 10000, 2)} ha")
    print(f"  > Dont DÉJÀ FONCTIONNEL (Forêts, Friches, PPH) : {round(naturel_area / 10000, 2)} ha ({round(pct_naturel, 1)} %)")
    print(f"  > Dont POTENTIEL DE RESTAURATION (Cultures, PTR) : {round(agricole_area / 10000, 2)} ha ({round(pct_agricole, 1)} %)")
    print(f"  > Dont URBAIN / IMPERMÉABILISÉ (Dette écologique) : {round(urbain_area / 10000, 2)} ha ({round(pct_urbain, 1)} %)")
    print("-" * 60)

# --- EXECUTION ---
generer_ebf_geochimique(5)
generer_ebf_geochimique(25)

print("\nTraitement terminé. Les couches complètes (incluant l'urbain) ont été chargées dans le projet QGIS.")