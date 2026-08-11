import os
import processing
from qgis.core import QgsProject, QgsRasterLayer

# --- 1. CONFIGURATION ---
# Mets ici le chemin exact du dossier où sont tes 50 fichiers .tif
dossier_sources = "D:/Master_OTG_2/1_STAGE/DONNE/Resultats_Exzeco_100_Somme"
# Le nom que tu veux pour ton fichier final
nom_final = "ExZEco_100_SOMME_BRUTE_ASSEMBLÉE.tif"

# --- 2. RÉCUPÉRATION DES FICHIERS ---
print(" Recherche des fichiers accumulation...")
liste_fichiers = []
for f in os.listdir(dossier_sources):
    # On ne prend que les fichiers d'accumulation (ceux qui commencent par 'accum')
    if f.startswith("accum") and f.endswith(".tif"):
        chemin_complet = os.path.join(dossier_sources, f)
        # On crée un objet couche pour que QGIS puisse le lire
        couche = QgsRasterLayer(chemin_complet, f)
        if couche.isValid():
            liste_fichiers.append(couche)

print(f" {len(liste_fichiers)} fichiers trouvés et valides.")

# --- 3. ASSEMBLAGE (CELL STATISTICS) ---
if len(liste_fichiers) == 50:
    print(" Assemblage en cours (Calcul de la Somme)...")
    output_path = os.path.join(dossier_sources, nom_final)
    
    processing.run("native:cellstatistics", {
        'INPUT': liste_fichiers,
        'STATISTIC': 0,  # 0 = SOMME
        'IGNORE_NODATA': True,
        'REFERENCE_LAYER': liste_fichiers[0],
        'OUTPUT': output_path
    })

    # Ajout à la carte QGIS
    lyr = QgsRasterLayer(output_path, "ExZEco_100_SOMME_FINALE")
    QgsProject.instance().addMapLayer(lyr)
    print(f" Terminé ! Ton fichier assemblé est ici : {output_path}")
else:
    print(f" Attention : Tu as {len(liste_fichiers)} fichiers au lieu de 50. Vérifie ton dossier !")