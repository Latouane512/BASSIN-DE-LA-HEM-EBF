import processing
from qgis.core import QgsProject, QgsRasterLayer, QgsSettings
import random
import os
import tempfile

temp_dir = "D:/Master_OTG_2/1_STAGE/DONNE/Resultats_Exzeco_100_Somme"
os.makedirs(temp_dir, exist_ok=True)

QgsSettings().setValue("Processing/Configuration/TEMP_PATH", temp_dir)
os.environ['TEMP'] = temp_dir
os.environ['TMP'] = temp_dir
tempfile.tempdir = temp_dir


nom_mnt = 'MNT_REMPLI_2M'
iterations = 50 
bruit_val = 1.0 

layers = QgsProject.instance().mapLayersByName(nom_mnt)
if not layers:
    print(f" Erreur : La couche '{nom_mnt}' est introuvable dans QGIS !")
else:
    mnt_layer = layers[0]
    extent = mnt_layer.extent()
    print(f" Lancement ExZEco 100 BRUT ({iterations} itérations)...")

    results = []
    for i in range(iterations):
        rd = random.uniform(0, bruit_val)
        
        mnt_bruite_path = f"{temp_dir}/bruit_100_{i}.tif"
        accum_path = f"{temp_dir}/accum_100_{i}.tif"
        
        # Étape A : Ajout du bruit aléatoire (0 à 1m)
        processing.run("gdal:rastercalculator", {
            'INPUT_A': mnt_layer, 'BAND_A': 1,
            'FORMULA': f'A + {rd}',
            'OUTPUT': mnt_bruite_path
        })
        
        processing.run("grass7:r.watershed", {
            'elevation': mnt_bruite_path,
            'threshold': 100,
            'accumulation': accum_path,
            'convergence': 5,
            '-s': True, # Flux simple (Single Flow Direction)
            'GRASS_REGION_PARAMETER': extent,
            'GRASS_REGION_CELLSIZE_PARAMETER': 2 # Résolution de ton MNT
        })
        
        results.append(accum_path)
        print(f"    Itération {i+1}/{iterations} terminée")

    print(" Calcul de la Somme finale des 50 couches...")
    final_output_path = f"{temp_dir}/ExZEco_100_SOMME_BRUTE.tif"
    
    couches_valides = []
    for chemin in results:
        if os.path.exists(chemin):
            c = QgsRasterLayer(chemin, "temp")
            if c.isValid():
                couches_valides.append(c)

    if len(couches_valides) > 0:
        processing.run("native:cellstatistics", {
            'INPUT': couches_valides,
            'STATISTIC': 0, # 0 = SOMME
            'IGNORE_NODATA': True,
            'REFERENCE_LAYER': mnt_layer,
            'OUTPUT': final_output_path
        })

        lyr = QgsRasterLayer(final_output_path, "ExZEco_100_SOMME_BRUTE")
        QgsProject.instance().addMapLayer(lyr)
        
        print(" Nettoyage des fichiers temporaires (Gao de données)...")
        couches_valides.clear() 
        for i in range(iterations):
            try:
                os.remove(f"{temp_dir}/bruit_100_{i}.tif")
                os.remove(f"{temp_dir}/accum_100_{i}.tif")
            except: pass

        print("Terminé ! Ton fichier cumulé ExZEco 100 est prêt.")