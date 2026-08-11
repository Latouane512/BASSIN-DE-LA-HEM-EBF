from qgis.core import (QgsProject, QgsFeature, QgsGeometry, 
                       QgsVectorLayer, QgsField, QgsWkbTypes)
from PyQt5.QtCore import QVariant

# ==========================================
# CONFIGURATION
# ==========================================
NOM_RIVIERE_ACTUELLE = "2025_HYDRO_HEM"
COUCHES_HISTORIQUES = {
    "Cassini": "CASSINI_HYDRO_HEM",       
    "Etat-Major": "ETATMAJOR_HYDRO_HEM",         
    "Scan 50": "SCAN50_HYDRO_HEM"         
}

NOM_COLONNE_FILTRE = "BRAS" 
VALEURS_GARDEES = ["Principal", "Affluent", "Sou_Afflu"] 

PAS_CALCUL = 250
LONGUEUR_TRANSECT = 800
SEUIL_TOLERANCE = 10 
TOLERANCE_TERRITORIALE = 200.0 # Augmenté pour ne plus rater de points

print(" DÉMARRAGE : Génération avec colonnes MIN et MAX séparées...")

project = QgsProject.instance()
layer_2025 = project.mapLayersByName(NOM_RIVIERE_ACTUELLE)[0]
crs_authid = layer_2025.crs().authid()

def lire_couche_historique(layer, nom_couche):
    geom_globale = QgsGeometry()
    idx_champ = layer.fields().indexOf(NOM_COLONNE_FILTRE)
    for feat in layer.getFeatures():
        if idx_champ != -1 and str(feat[NOM_COLONNE_FILTRE]) not in VALEURS_GARDEES:
            continue 
        g = feat.geometry()
        if g.isEmpty(): continue
        g_2d = QgsGeometry(g.constGet().clone())
        g_2d.get().dropMValue(); g_2d.get().dropZValue()
        geom_globale = geom_globale.combine(g_2d) if not geom_globale.isEmpty() else g_2d
    return geom_globale

geom_riviere_complete = lire_couche_historique(layer_2025, "2025")
geometries_historiques = {ep: lire_couche_historique(project.mapLayersByName(nom)[0], ep) 
                          for ep, nom in COUCHES_HISTORIQUES.items() if project.mapLayersByName(nom)}

# --- CRÉATION DES COUCHES ---
vl_pk = QgsVectorLayer(f"Point?crs={crs_authid}", "Points_PK_2025", "memory")
vl_trans = QgsVectorLayer(f"LineString?crs={crs_authid}", "Transects_250m", "memory")
vl_inter = QgsVectorLayer(f"Point?crs={crs_authid}", "Points_Historiques_COMPLET", "memory")

pr_pk = vl_pk.dataProvider(); pr_trans = vl_trans.dataProvider(); pr_inter = vl_inter.dataProvider()

pr_pk.addAttributes([QgsField("PK_km", QVariant.Double)])
pr_trans.addAttributes([QgsField("PK_km", QVariant.Double)])
# Ici on définit bien les deux colonnes de distance
pr_inter.addAttributes([
    QgsField("PK_km", QVariant.Double),
    QgsField("Epoque", QVariant.String),
    QgsField("Dist_MIN", QVariant.Double),
    QgsField("Dist_MAX", QVariant.Double),
    QgsField("Valeur_Prop", QVariant.Double)
])

vl_pk.updateFields(); vl_trans.updateFields(); vl_inter.updateFields()

# --- CALCUL ---
dist_curv = 0
feats_pk, feats_trans, feats_inter = [], [], []

while dist_curv <= geom_riviere_complete.length():
    pt = geom_riviere_complete.interpolate(dist_curv)
    p_av = geom_riviere_complete.interpolate(max(0, dist_curv - 1)).asPoint()
    p_ap = geom_riviere_complete.interpolate(min(geom_riviere_complete.length(), dist_curv + 1)).asPoint()
    angle = p_av.azimuth(p_ap)
    
    p1 = pt.asPoint().project(LONGUEUR_TRANSECT / 2, angle + 90)
    p2 = pt.asPoint().project(LONGUEUR_TRANSECT / 2, angle - 90)
    line_geom = QgsGeometry.fromPolylineXY([p1, p2])
    pk_km = round(dist_curv / 1000.0, 3)

    feats_pk.append(QgsFeature()); feats_pk[-1].setGeometry(pt); feats_pk[-1].setAttributes([pk_km])
    feats_trans.append(QgsFeature()); feats_trans[-1].setGeometry(line_geom); feats_trans[-1].setAttributes([pk_km])

    for epoque, geom_hist in geometries_historiques.items():
        intersection = line_geom.intersection(geom_hist)
        if not intersection.isEmpty():
            points_v = [QgsGeometry(v) for v in intersection.vertices()]
            # Test territorial avec tolérance augmentée
            points_valides = [p for p in points_v if pt.distance(p) <= p.distance(geom_riviere_complete) + TOLERANCE_TERRITORIALE]
            
            if points_valides:
                dists = [pt.distance(p) for p in points_valides]
                d_min, d_max = min(dists), max(dists)
                
                val_prop = round((d_min + d_max) / 2, 2) if (d_max - d_min) <= SEUIL_TOLERANCE else QVariant(QVariant.Double)

                # On crée un point sur la position MAX (le plus représentatif du déplacement)
                # Mais la table contiendra les deux infos !
                f_inter = QgsFeature()
                f_inter.setGeometry(points_valides[dists.index(d_max)])
                f_inter.setAttributes([pk_km, epoque, round(d_min, 2), round(d_max, 2), val_prop])
                feats_inter.append(f_inter)

    dist_curv += PAS_CALCUL

pr_pk.addFeatures(feats_pk); pr_trans.addFeatures(feats_trans); pr_inter.addFeatures(feats_inter)
project.addMapLayers([vl_trans, vl_pk, vl_inter])

print(f" Terminé ! Vérifie la table de 'Points_Historiques_COMPLET'.")