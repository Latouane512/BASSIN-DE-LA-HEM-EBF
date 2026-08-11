import os
import processing
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer


nom_couche_somme = "ExZEco_100_SOMME"
print("Recherche de la couche de somme brute dans QGIS...")
layers = QgsProject.instance().mapLayersByName(nom_couche_somme)

if not layers:
    raise Exception(f"La couche '{nom_couche_somme}' est introuvable. Assurez-vous qu'elle est cochée dans QGIS.")

# On récupère le chemin exact du fichier sur votre PC
raster_somme_brute = layers[0].source().replace('\\', '/')
print(f"Couche trouvée : {raster_somme_brute}")

dossier_travail = os.path.dirname(raster_somme_brute)

raster_seuille = f"{dossier_travail}/ExZEco_100_Robustes_80pc.tif"
vector_output = f"{dossier_travail}/Axes_Ruissellement_Robustes_80pc.gpkg"

print("Application du seuil de robustesse à 80% via GDAL...")
params_calc = {
    'INPUT_A': raster_somme_brute,
    'BAND_A': 1,
    'FORMULA': 'A >= 40',
    'OUTPUT': raster_seuille
}
processing.run("gdal:rastercalculator", params_calc)

# Vérification absolue de l'existence du fichier
if not os.path.exists(raster_seuille):
    raise Exception(f" GDAL n'a pas pu créer le fichier. Vérifiez l'espace disque ou les droits d'écriture sur : {dossier_travail}")

calc_layer = QgsRasterLayer(raster_seuille, "temp_binaire")
if not calc_layer.isValid():
    raise Exception(" Le fichier binaire a été créé mais QGIS refuse de le lire.")

print(" Vectorisation des axes hydro-topographiques robustes...")
params_poly = {
    'INPUT': calc_layer,
    'BAND': 1,
    'FIELD': 'DN',
    'EIGHT_CONNECTEDNESS': False,
    'OUTPUT': vector_output
}
processing.run("gdal:polygonize", params_poly)

print(" Chargement et application du filtre SQL...")
layer_vector = QgsVectorLayer(vector_output, "Axes_Ruissellement_Robustes_80%", "ogr")

if layer_vector.isValid():
    # Masquage des polygones inutiles (les zones qui n'étaient pas des axes)
    layer_vector.setSubsetString('"DN" = 0') 
    QgsProject.instance().addMapLayer(layer_vector)
    print(" SUCCÈS ! Les polygones de vos autoroutes de ruissellement à 80% sont affichés.")
else:
    print("Erreur lors du chargement du fichier vectoriel final.")