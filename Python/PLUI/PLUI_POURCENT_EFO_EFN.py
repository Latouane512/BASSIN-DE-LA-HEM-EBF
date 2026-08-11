from qgis.core import QgsProject
import processing

# =====================================================================
# 1. CONFIGURATION DES COUCHES ET CHAMPS
# =====================================================================
lyr_efo_name = "EFO_FINAL"  # Nom exact de ta couche EFO
lyr_efn_name = "EFN_FINAL_V3"  # Nom exact de ta couche EFN
lyr_plui_name = "PLUi_HEM"          # Nom exact de ta couche d'urbanisme


# =====================================================================
# 2. FONCTION DE SÉCURITÉ
# =====================================================================
def get_layer(nom):
    couches = QgsProject.instance().mapLayersByName(nom.strip())
    if not couches:
        raise ValueError(f" ERREUR : La couche '{nom.strip()}' est introuvable. Vérifie l'orthographe.")
    return couches[0]

# =====================================================================
# 3. FONCTION D'ANALYSE ET DE REGROUPEMENT
# =====================================================================
def analyser_plui():
    print("\n" + "="*50)
    print(" DÉBUT DE L'ANALYSE D'URBANISME (EBF x PLUi)")
    print("="*50)

    try:
        efo = get_layer(lyr_efo_name)
        efn = get_layer(lyr_efn_name)
        plui = get_layer(lyr_plui_name)

        # Vérification de l'existence de la colonne dans le PLUi
        if plui.fields().indexFromName(champ_zone) == -1:
            raise ValueError(f" ERREUR : La colonne '{champ_zone}' n'existe pas dans la table du PLUi.")

        def calculer_stats(couche_ebf, nom_ebf):
            print(f"\n Croisement géométrique {nom_ebf} avec le PLUi en cours...")
            
            # 1. Intersection géométrique
            intersect = processing.run("native:intersection", {
                'INPUT': couche_ebf,
                'OVERLAY': plui,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })['OUTPUT']

            # Ajouter la couche d'intersection à la carte pour que tu puisses la voir
            QgsProject.instance().addMapLayer(intersect).setName(f"Intersection_{nom_ebf}_PLUi")

            stats = {'U (Urbain)': 0, 'AU (A urbaniser)': 0, 'A (Agricole)': 0, 'N (Naturel)': 0, 'Autre': 0}
            surface_totale_ha = 0

            # 2. Parcours des entités intersectées et calcul des surfaces
            for feat in intersect.getFeatures():
                zone_brute = str(feat[champ_zone]).upper().strip()
                
                # Regroupement intelligent des sous-zones (1AU, Ua, Np...)
                if zone_brute.startswith('1AU') or zone_brute.startswith('2AU') or zone_brute.startswith('AU'):
                    cat = 'AU (A urbaniser)'
                elif zone_brute.startswith('U'):
                    cat = 'U (Urbain)'
                elif zone_brute.startswith('A'):
                    cat = 'A (Agricole)'
                elif zone_brute.startswith('N'):
                    cat = 'N (Naturel)'
                else:
                    cat = 'Autre'

                # Calcul de la surface en Hectares (division par 10 000)
                # Attention : le projet QGIS doit être en Lambert 93 (EPSG:2154) pour des m² corrects
                area_ha = feat.geometry().area() / 10000.0 
                
                stats[cat] += area_ha
                surface_totale_ha += area_ha

            # 3. Affichage des résultats
            print(f"\n--- RÉSULTATS POUR L'{nom_ebf} ---")
            print(f"Surface totale intersectée : {surface_totale_ha:.2f} ha")
            
            for cat in ['U (Urbain)', 'AU (A urbaniser)', 'A (Agricole)', 'N (Naturel)', 'Autre']:
                area = stats[cat]
                if surface_totale_ha > 0:
                    pct = (area / surface_totale_ha) * 100
                    print(f"  {cat.ljust(18)} : {area:>8.2f} ha  ({pct:>5.1f} %)")
                else:
                    print(f"  {cat.ljust(18)} : {area:>8.2f} ha  (0.0 %)")

        # Lancer le calcul pour l'EFO puis l'EFN
        calculer_stats(efo, "EFO")
        calculer_stats(efn, "EFN")
        
        print("\n Terminé ! Les couches d'intersections ont été ajoutées à la carte.")

    except Exception as e:
        print("\n ERREUR :")
        print(e)

# =====================================================================
# Lancer le script
# =====================================================================
analyser_plui()