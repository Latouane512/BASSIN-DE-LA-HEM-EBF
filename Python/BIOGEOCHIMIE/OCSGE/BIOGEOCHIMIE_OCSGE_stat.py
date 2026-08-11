from qgis.core import *
import processing

# --- CONFIGURATION ---
nom_riviere = '2025_HYDRO_HEM copie'  # Ta couche avec "largeur_moy"
nom_ocs = 'OCSGE_HEM'                 # Ta couche OCSGE
# ---------------------

project = QgsProject.instance()

# Vérification des couches
try:
    riv_layer = project.mapLayersByName(nom_riviere)[0]
    ocs_layer = project.mapLayersByName(nom_ocs)[0]
except IndexError:
    print("ERREUR : Vérifiez les noms des couches (orthographe et majuscules).")

def generer_ebf_geochimique(distance_cible):
    print(f"\n--- Traitement Hypothèse : {distance_cible}m ---")
    
    # 1. Buffer Dynamique : (Largeur / 2) + distance
    expr_buffer = f'("largeur_moy" / 2) + {distance_cible}'
    
    params_buf = {
        'INPUT': riv_layer,
        'DISTANCE': QgsProperty.fromExpression(expr_buffer),
        'DISSOLVE': True,
        'OUTPUT': 'memory:buf_brut'
    }
    buf_brut = processing.run("native:buffer", params_buf)['OUTPUT']

    # 2. Intersection avec l'OCSGE
    params_int = {
        'INPUT': buf_brut,
        'OVERLAY': ocs_layer,
        'OUTPUT': 'memory:ebf_inter'
    }
    ebf_inter = processing.run("native:intersection", params_int)['OUTPUT']

    # 3. Création de la couche finale et Calcul des statistiques
    final_layer = QgsVectorLayer("MultiPolygon?crs=" + riv_layer.crs().authid(), f"EBF_Geochimique_{distance_cible}m", "memory")
    final_layer.dataProvider().addAttributes(ebf_inter.fields())
    final_layer.updateFields()
    
    # Initialisation des compteurs pour le point 7.4
    total_area = 0
    naturel_area = 0
    agricole_area = 0
    features_finales = []

    # Détection automatique des colonnes (évite les KeyError)
    colonnes = [f.name() for f in ebf_inter.fields()]
    col_code = next((c for c in colonnes if 'CODE_CS' in c.upper()), None)
    col_lib = next((c for c in colonnes if 'LIB' in c.upper()), None)

    for f in ebf_inter.getFeatures():
        area = f.geometry().area()
        code_cs = str(f[col_code]) if col_code else ""
        libelle = str(f[col_lib]).lower() if col_lib else ""
        
        # FILTRE : On exclut l'urbain (CS1.1)
        if not code_cs.startswith('CS1.1'):
            features_finales.append(f)
            total_area += area
            
            # Classification pour indicateurs
            # Naturel : Forêts (CS2.2) ou mots-clés dans le libellé
            is_naturel = code_cs.startswith('CS2.2') or any(word in libelle for word in ['prairie', 'forêt', 'naturel', 'bois', 'haie'])
            # Agricole : Cultures (CS2.1)
            is_agricole = code_cs.startswith('CS2.1') or 'culture' in libelle

            if is_naturel:
                naturel_area += area
            elif is_agricole:
                agricole_area += area

    final_layer.dataProvider().addFeatures(features_finales)
    project.addMapLayer(final_layer)

    # 4. Affichage des indicateurs (Phase 7.4)
    ratio = (naturel_area / total_area * 100) if total_area > 0 else 0
    print(f"RÉSULTATS POUR {distance_cible}m :")
    print(f"  > Surface filtrante totale (hors bâti) : {round(total_area / 10000, 2)} ha")
    print(f"  > Dont déjà fonctionnel (Naturel) : {round(naturel_area / 10000, 2)} ha")
    print(f"  > Besoin de compensation (Agricole à planter) : {round(agricole_area / 10000, 2)} ha")
    print(f"  > Ratio de fonctionnalité : {round(ratio, 1)} %")

# --- EXECUTION ---
generer_ebf_geochimique(5)
generer_ebf_geochimique(25)

print("\nTraitement terminé. Les couches ont été ajoutées au projet.")