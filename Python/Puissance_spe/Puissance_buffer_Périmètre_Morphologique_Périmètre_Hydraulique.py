import processing
from qgis.core import (QgsProject, QgsFeature, QgsVectorLayer, QgsField)
from PyQt5.QtCore import QVariant

# --- CONFIGURATION ---
NOM_COUCHE = "hem_troncons_hydrologique" 
CHAMP_W = "Largeur_moy"
CHAMP_STRAHLER = "STRAHLER"
CHAMP_ENERGIE = "Cl_Q100"
CHAMP_DEBIT = "Q_Q100_m3s" # Crue de référence Q100

layer = QgsProject.instance().mapLayersByName(NOM_COUCHE)[0]
crs = layer.crs().authid()

# Création des couches mémoires
vl_efo = QgsVectorLayer(f"Polygon?crs={crs}", "EFO_Final", "memory")
vl_efn = QgsVectorLayer(f"Polygon?crs={crs}", "EFN_Final", "memory")
for vl in [vl_efo, vl_efn]:
    vl.dataProvider().addAttributes([QgsField("Diag_Hydra", QVariant.String)])
    vl.updateFields()

features_efo, features_efn = [], []

for feat in layer.getFeatures():
    w = feat[CHAMP_W]
    st = feat[CHAMP_STRAHLER]
    en = feat[CHAMP_ENERGIE]
    q = feat[CHAMP_DEBIT]
    geom = feat.geometry()
    
    if not geom or not w or w <= 0: continue

    # =========================================================
    # 1. CALCUL DU SEUIL HYDRAULIQUE (h x V)
    # On utilise la formule : Débit / Largeur = h x V
    # =========================================================
    h_v = q / w
    is_grand_ecoulement = h_v > 0.5
    diag = "Normal" if not is_grand_ecoulement else "GRAND ÉCOULEMENT (h*V > 0.5)"

    # =========================================================
    # 2. APPLICATION DES RÈGLES DE DIMENSIONNEMENT
    # =========================================================
    
    # --- CAS A : Petits cours d'eau (Strahler 1 & 2) ---
    if st <= 2:
        r_efo = (w / 2) + 10
        r_efn = (w / 2) + 5
        
    # --- CAS B : Secteurs MOBILES (E3 / E4) ---
    elif en in ['E3', 'E4']:
        # EFO : 15x la largeur (Majorant) | EFN : 10x la largeur (Moyenne)
        r_efo = (w * 15) / 2
        r_efn = (w * 10) / 2
        
    # --- CAS C : Secteurs PEU MOBILES (E1 / E2) ---
    else:
        # EFO : 6x la largeur | EFN : 3x la largeur
        r_efo = (w * 6) / 2
        r_efn = (w * 3) / 2
        
        # AJUSTEMENT HYDRAULIQUE : Si Grand Écoulement, on passe au 
        # majorant de la règle (5x au lieu de 3x) pour l'EFN
        if is_grand_ecoulement:
            r_efn = (w * 5) / 2

    # Création des buffers
    f_efo, f_efn = QgsFeature(vl_efo.fields()), QgsFeature(vl_efn.fields())
    f_efo.setGeometry(geom.buffer(r_efo, 8))
    f_efn.setGeometry(geom.buffer(r_efn, 8))
    f_efo.setAttribute("Diag_Hydra", diag)
    f_efn.setAttribute("Diag_Hydra", diag)
    
    features_efo.append(f_efo)
    features_efn.append(f_efn)

# Ajout et Dissolve
vl_efo.dataProvider().addFeatures(features_efo)
vl_efn.dataProvider().addFeatures(features_efn)

res_efo = processing.run("native:dissolve", {'INPUT': vl_efo, 'OUTPUT': 'memory:EFO_Final'})['OUTPUT']
res_efn = processing.run("native:dissolve", {'INPUT': vl_efn, 'OUTPUT': 'memory:EFN_Final'})['OUTPUT']

QgsProject.instance().addMapLayers([res_efo, res_efn])
print(" Modélisation Morpho-Hydraulique terminée.")