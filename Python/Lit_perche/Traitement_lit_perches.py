from qgis.core import (QgsProject, QgsFeature, QgsGeometry, 
                       QgsVectorLayer, QgsField)
from PyQt5.QtCore import QVariant

NOM_PERCHE = "LITS_PERCHES"
NOM_NATUREL = "LITS_NATURELS"

print(" Création de l'enveloppe robuste (Correction force2D)...")

try:
    layer_perche = QgsProject.instance().mapLayersByName(NOM_PERCHE)[0]
    layer_naturel = QgsProject.instance().mapLayersByName(NOM_NATUREL)[0]
except IndexError:
    print(" ERREUR : Couches introuvables. Vérifie les noms dans QGIS.")
    raise

# 1. On fusionne tout le lit naturel et on force en 2D
geom_naturel_globale = QgsGeometry()
for feat in layer_naturel.getFeatures():
    g = feat.geometry()
    if g.isEmpty(): continue
    # Supprime les dimensions Z et M qui font planter les calculs
    g_2d = QgsGeometry(g.constGet().clone())
    g_2d.get().dropMValue()
    g_2d.get().dropZValue()
    
    if geom_naturel_globale.isEmpty(): 
        geom_naturel_globale = g_2d
    else: 
        geom_naturel_globale = geom_naturel_globale.combine(g_2d)

# 2. Création de la couche de sortie
vl_out = QgsVectorLayer(f"Polygon?crs={layer_perche.crs().authid()}", "Espace_Avulsion_OK", "memory")
pr = vl_out.dataProvider()
pr.addAttributes([QgsField("ID", QVariant.Int)])
vl_out.updateFields()

# 3. Traitement
for feat_p in layer_perche.getFeatures():
    g_p = feat_p.geometry()
    if g_p.isEmpty(): continue
    
    # Nettoyage de la ligne perchée
    g_p_2d = QgsGeometry(g_p.constGet().clone())
    g_p_2d.get().dropMValue()
    g_p_2d.get().dropZValue()
    
    # On trouve la partie du lit naturel proche
    zone_recherche = g_p_2d.buffer(300, 5) # Augmenté à 300 pour les grands méandres
    line_n = geom_naturel_globale.intersection(zone_recherche)
    
    if line_n.isEmpty(): continue

    # Fusion des deux lignes nettoyées
    fusion = g_p_2d.combine(line_n)
    
    # L'enveloppe concave (Concave Hull)
    # Le paramètre 0.99 permet de coller au plus près des lignes
    enveloppe = fusion.concaveHull(0.99, False)
    
    if not enveloppe.isEmpty():
        f = QgsFeature()
        f.setGeometry(enveloppe)
        f.setAttributes([feat_p.id()])
        pr.addFeature(f)

vl_out.updateExtents()
QgsProject.instance().addMapLayer(vl_out)
print(" Terminé ! Vérifie la couche 'Espace_Avulsion_OK'.")