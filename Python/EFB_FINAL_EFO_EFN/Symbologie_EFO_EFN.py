from qgis.core import *
from qgis.utils import iface

def appliquer_style(nom_couche, rouge, vert, bleu, style_ligne='solid', epaisseur='0.8'):
    # Cherche la couche dans le projet
    layers = QgsProject.instance().mapLayersByName(nom_couche)
    if not layers:
        print(f"Couche ignorée (non trouvée dans le panneau) : {nom_couche}")
        return
    
    layer = layers[0]
    
    # Propriétés du symbole : Remplissage transparent ('style': 'no') et bordure colorée
    proprietes = {
        'outline_color': f'{rouge},{vert},{bleu},255',
        'outline_width': epaisseur,
        'outline_style': style_ligne,
        'style': 'no' 
    }
    
    # Application du style si c'est bien une couche de polygones
    if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
        symbol = QgsFillSymbol.createSimple(proprietes)
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        print(f"Style appliqué avec succès à : {nom_couche}")

def appliquer_charte_agence_eau():
    print("--- Application automatique de la charte de l'Agence de l'Eau ---")
    
    # 1. Morphologie (Orange : 255-170-0)
    appliquer_style("EFO_FINAL", 255, 170, 0, 'solid', '1.0') # Épais et plein
    appliquer_style("EFN_FINAL", 255, 170, 0, 'dash', '1.0')  # Épais et pointillé
    
    # 2. Biogéochimie (Jaune : 255-255-0)
    appliquer_style("EBF_GEOCHIMIE_25m", 255, 255, 0, 'solid', '0.6')
    appliquer_style("EBF_GEOCHIMIE_5m", 255, 255, 0, 'dash', '0.6')
    
    # 3. Biologie (Vert : 56-168-0)
    appliquer_style("ZDH_Global", 56, 168, 0, 'solid', '0.6')
    appliquer_style("ZH_Enjeux", 56, 168, 0, 'dash', '0.6')
    
    # 4. Enjeux (Rouge : 255-0-0)
    appliquer_style("Bati_route", 255, 0, 0, 'solid', '0.4')
    
    print("Mise à jour de l'affichage...")
    iface.mapCanvas().refresh()
    print("Terminé ! Ta carte est aux normes.")

# Exécuter la fonction
appliquer_charte_agence_eau()