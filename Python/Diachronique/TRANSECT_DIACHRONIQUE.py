from qgis.core import (QgsProject, QgsFeature, QgsGeometry, 
                       QgsVectorLayer, QgsField)
from PyQt5.QtCore import QVariant

# ==========================================
# CONFIGURATION
# ==========================================
NOM_2025 = "2025_HYDRO_HEM"
NOM_SCAN50 = "SCAN50_HYDRO_HEM"
NOM_EM = "ETATMAJOR_HYDRO_HEM"
NOM_CASSINI = "CASSINI_HYDRO_HEM"

NOM_COLONNE_FILTRE = "BRAS" 
VALEURS_GARDEES = ["Principal", "Affluent", "Sou_Afflu"] 

PAS_ECHANTILLON = 10        # Précision diachronique
LONGUEUR_TRANSECT = 800     
TOLERANCE_TERRITORIALE = 20.0 

print("SCRIPT : Génération du Tableau de Bord (Brut) sans colonnes Vrai...")

project = QgsProject.instance()

try:
    l25 = project.mapLayersByName(NOM_2025)[0]
    ls50 = project.mapLayersByName(NOM_SCAN50)[0]
    lem = project.mapLayersByName(NOM_EM)[0]
    lcas = project.mapLayersByName(NOM_CASSINI)[0]
except IndexError:
    print(" ERREUR : Une couche est manquante.")
    raise

def preparer_geom(layer):
    geom_globale = QgsGeometry()
    idx = layer.fields().indexOf(NOM_COLONNE_FILTRE)
    for feat in layer.getFeatures():
        if idx != -1 and str(feat[NOM_COLONNE_FILTRE]) not in VALEURS_GARDEES:
            continue
        g = feat.geometry()
        if g.isEmpty(): continue
        g_2d = QgsGeometry(g.constGet().clone())
        g_2d.get().dropMValue(); g_2d.get().dropZValue()
        geom_globale = geom_globale.combine(g_2d) if not geom_globale.isEmpty() else g_2d
    return geom_globale

geom_25_ref = preparer_geom(l25)
geom_s50 = preparer_geom(ls50)
geom_em = preparer_geom(lem)
geom_cas = preparer_geom(lcas)

# --- CRÉATION DE LA COUCHE DE SORTIE ---
vl_out = QgsVectorLayer(f"LineString?crs={l25.crs().authid()}", "Tableau_Diachronique_Brut", "memory")
pr = vl_out.dataProvider()

# On ne garde que PK, Min et Max
champs = [
    QgsField("PK_km", QVariant.Double),
    QgsField("S50_Min", QVariant.Double), QgsField("S50_Max", QVariant.Double),
    QgsField("EM_Min", QVariant.Double), QgsField("EM_Max", QVariant.Double),
    QgsField("CAS_Min", QVariant.Double), QgsField("CAS_Max", QVariant.Double)
]
pr.addAttributes(champs)
vl_out.updateFields()

# --- FONCTION DE CALCUL (Min/Max uniquement) ---
def get_brut_stats(transect, pt_orig, geom_hist, geom_ref):
    inter = transect.intersection(geom_hist)
    if inter.isEmpty(): return None, None
    pts = [QgsGeometry(v) for v in inter.vertices()]
    valides = [p for p in pts if pt_orig.distance(p) <= p.distance(geom_ref) + TOLERANCE_TERRITORIALE]
    if not valides: return None, None
    dists = [pt_orig.distance(p) for p in valides]
    return round(min(dists), 2), round(max(dists), 2)

# --- CALCUL ---
print(" Scan de la Hem en cours...")
features = []
for feat in l25.getFeatures():
    idx_25 = l25.fields().indexOf(NOM_COLONNE_FILTRE)
    if idx_25 != -1 and str(feat[NOM_COLONNE_FILTRE]) not in VALEURS_GARDEES: continue

    geom = feat.geometry()
    d = 0
    while d <= geom.length():
        pt = geom.interpolate(d)
        p_av, p_ap = geom.interpolate(max(0, d-1)).asPoint(), geom.interpolate(min(geom.length(), d+1)).asPoint()
        angle = p_av.azimuth(p_ap)
        line = QgsGeometry.fromPolylineXY([pt.asPoint().project(LONGUEUR_TRANSECT/2, angle+90), pt.asPoint().project(LONGUEUR_TRANSECT/2, angle-90)])
        
        pk = round(d/1000, 3)
        s5_mi, s5_ma = get_brut_stats(line, pt, geom_s50, geom_25_ref)
        em_mi, em_ma = get_brut_stats(line, pt, geom_em, geom_25_ref)
        ca_mi, ca_ma = get_brut_stats(line, pt, geom_cas, geom_25_ref)

        f = QgsFeature(); f.setGeometry(line)
        f.setAttributes([pk, s5_mi, s5_ma, em_mi, em_ma, ca_mi, ca_ma])
        features.append(f)
        d += PAS_ECHANTILLON

pr.addFeatures(features)
project.addMapLayer(vl_out)
print(" Terminé ! Ta table ne contient plus que les distances Min et Max.")