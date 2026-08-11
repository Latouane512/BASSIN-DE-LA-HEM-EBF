from qgis.core import QgsProject
import processing

# ==========================================
# --- CONFIGURATION DE LA COUCHE MRVBF ---
# ==========================================
nom_mrvbf = 'Vecteur_1_sans_bruit' 

project = QgsProject.instance()

# --- Chargement sécurisé de la couche ---
try:
    mrvbf_layer = project.mapLayersByName(nom_mrvbf)[0]
    print(f" La couche '{nom_mrvbf}' a été trouvée !")
except IndexError:
    print(f" ERREUR : QGIS ne trouve pas la couche '{nom_mrvbf}'.")
    raise SystemExit 

def nettoyer_mrvbf():
    print("\n Démarrage : Nettoyage topologique du fond de vallée...")
    
    # ---------------------------------------------------------
    # ETAPE 1 : Remplissage des trous
    # ---------------------------------------------------------
    print("1/3 - Bouchage des micro-trous internes (moins de 100 m²)...")
    # L'outil supprime tous les trous à l'intérieur des polygones en dessous de la surface indiquée
    mrvbf_bouche = processing.run("native:deleteholes", {
        'INPUT': mrvbf_layer, 
        'MIN_AREA': 500,  # Tu peux augmenter cette valeur (ex: 500) si de gros trous persistent
        'OUTPUT': 'memory:mrvbf_bouche'
    })['OUTPUT']

    # ---------------------------------------------------------
    # ETAPE 2 : Séparation des polygones
    # ---------------------------------------------------------
    print("2/3 - Séparation des entités...")
    mrvbf_separe = processing.run("native:multiparttosingleparts", {
        'INPUT': mrvbf_bouche, 
        'OUTPUT': 'memory:mrvbf_separe'
    })['OUTPUT']

    # ---------------------------------------------------------
    # ETAPE 3 : Suppression de la poussière
    # ---------------------------------------------------------
    print("3/3 - Suppression des artefacts Lidar (micro-polygones de moins de 5 m²)...")
    # On élimine les "confettis" géométriques générés par le calcul Lidar/Raster
    mrvbf_propre = processing.run("native:extractbyexpression", {
        'INPUT': mrvbf_separe, 
        'EXPRESSION': '$area > 5', 
        'OUTPUT': 'memory:mrvbf_propre'
    })['OUTPUT']

    # ---------------------------------------------------------
    # ETAPE 4 : AJOUT AU PROJET
    # ---------------------------------------------------------
    mrvbf_propre.setName("MRVBF_HEM (Nettoyé & Rebouché)")
    project.addMapLayer(mrvbf_propre)
    
    print("\n OPÉRATION TERMINÉE ! Votre MRVBF est prêt pour la découpe manuelle.")

# Lancement de la fonction
nettoyer_mrvbf()