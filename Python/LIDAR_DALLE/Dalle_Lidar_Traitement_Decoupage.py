# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:47:10 2026

@author: ASUS
"""

# -*- coding: utf-8 -*-
"""
Script de traitement LiDAR-HD : Téléchargement, Fusion (VRT) et Découpage (Warp)
Optimisé pour les gros volumes de données (Basse consommation RAM)
"""

import os
import requests
import rasterio
import geopandas as gpd
from urllib.parse import urlparse, parse_qs
import glob
import sys
from osgeo import gdal

# =================================================================
# --- 1. CONFIGURATION DES CHEMINS (À VÉRIFIER) ---
# =================================================================
FILE_TXT = r"D:/Master_OTG_2/1_STAGE/dalles.txt"
GPKG_PATH = r"D:/Master_OTG_2/1_STAGE/DONNE/BV_HEM.gpkg"
DOWNLOAD_DIR = r"D:/Master_OTG_2/1_STAGE/DONNE/Dalles_Brutes"
OUTPUT_DIR = r"D:/Master_OTG_2/1_STAGE/DONNE/Resultats_dalles"

MNT_FINAL = os.path.join(OUTPUT_DIR, "MNT_HEM_Decoupe.tif")


if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Activer les exceptions GDAL pour voir les erreurs précises
gdal.UseExceptions()

# =================================================================
# --- 2. ÉTAPE 1 : TÉLÉCHARGEMENT ET VÉRIFICATION ---
# =================================================================
if not os.path.exists(FILE_TXT):
    print(f"ERREUR : Le fichier {FILE_TXT} est introuvable.")
    sys.exit()

with open(FILE_TXT, 'r') as f:
    urls = [line.strip() for line in f if "http" in line]

print(f"--- ÉTAPE 1 : TÉLÉCHARGEMENT SÉCURISÉ ({len(urls)} fichiers) ---")

for i, url in enumerate(urls):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    filename = params.get('FILENAME', [f"dalle_{i}.tif"])[0]
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    # Vérification d'intégrité si le fichier existe déjà
    if os.path.exists(filepath):
        try:
            with rasterio.open(filepath) as check_src:
                # Lecture d'un micro-bloc pour tester si le fichier est corrompu
                _ = check_src.read(1, window=rasterio.windows.Window(0, 0, 5, 5))
            continue # Fichier OK, on passe au suivant
        except Exception:
            print(f"(!) Fichier corrompu détecté : {filename}. Suppression...")
            os.remove(filepath)

    # Téléchargement
    print(f"[{i+1}/{len(urls)}] Téléchargement de : {filename}...")
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    except Exception as e:
        print(f"ERREUR sur {filename} : {e}")

# Récupération de la liste finale des dalles valides
dalles_list = glob.glob(os.path.join(DOWNLOAD_DIR, "*.tif"))
if not dalles_list:
    print("ERREUR : Aucune dalle disponible pour la fusion.")
    sys.exit()

# =================================================================
# --- 3. ÉTAPE 2 : FUSION ET DÉCOUPAGE (GDAL HIGH PERFORMANCE) ---
# =================================================================
print("\n--- ÉTAPE 2 : FUSION ET DÉCOUPAGE ---")

vrt_path = os.path.join(OUTPUT_DIR, "mosaique_virtuelle.vrt")
temp_geojson = os.path.join(OUTPUT_DIR, "temp_mask.json")

try:
    # A. Création du Raster Virtuel (VRT)
    print("-> Création du catalogue virtuel (VRT)...")
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
    gdal.BuildVRT(vrt_path, dalles_list, options=vrt_options)

    # B. Préparation du masque de découpe
    print("-> Préparation du découpage via GeoPackage...")
    gdf = gpd.read_file(GPKG_PATH)
    # Export temporaire en GeoJSON (format préféré de GDAL Warp)
    gdf.to_file(temp_geojson, driver='GeoJSON')

    # C. Fusion + Découpage (Warp)
    print("-> Fusion et découpage en cours (écriture directe sur disque)...")
    # Cette méthode traite par blocs et ne sature pas la RAM
    gdal.Warp(
        MNT_FINAL,
        vrt_path,
        format='GTiff',
        cutlineDSName=temp_geojson,
        cropToCutline=True,
        dstNodata=-9999,
        creationOptions=[
            'COMPRESS=DEFLATE', 
            'TILED=YES', 
            'BIGTIFF=YES',
            'PREDICTOR=2' # Améliore la compression pour les données d'altitude
        ]
    )
    print(f"\nFÉLICITATIONS ! MNT créé avec succès : \n{MNT_FINAL}")

except Exception as e:
    print(f"\nERREUR CRITIQUE lors du traitement : {e}")

# =================================================================
# --- 4. NETTOYAGE DES FICHIERS TEMPORAIRES ---
# =================================================================
finally:
    if os.path.exists(vrt_path): os.remove(vrt_path)
    if os.path.exists(temp_geojson): os.remove(temp_geojson)

print("\n--- TRAITEMENT TERMINÉ ---")