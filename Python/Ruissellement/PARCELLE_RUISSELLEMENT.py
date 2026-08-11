import os
import processing
from qgis.core import QgsProject, QgsVectorLayer


nom_fiche = "Fiche_Contact_VH_V3"                # Couche Agricole (PACAGE)
nom_ocsge = "OCSGE_HEM"                          # Couche Territoire Total
nom_axes = "Axe_ruissellement_hors_lit_pente"    # L'Aléa (Ruissellement)

print(" Recherche des couches dans le projet...")
def get_layer(name):
    layers = QgsProject.instance().mapLayersByName(name)
    if not layers:
        raise Exception(f" La couche '{name}' est introuvable. Vérifiez l'orthographe.")
    return layers[0]

couche_fiche = get_layer(nom_fiche)
couche_ocsge = get_layer(nom_ocsge)
couche_axes = get_layer(nom_axes)

chemin_source = couche_fiche.source().split("|")[0]
dossier_travail = os.path.dirname(chemin_source).replace('\\', '/')

fichier_hem_ton_sol = f"{dossier_travail}/1_HEM_ton_sol_OAD.gpkg"
fichier_urbain = f"{dossier_travail}/2_Zones_Urbaines_Naturelles_OAD.gpkg"

print(" Nettoyage des anciens fichiers...")
noms_couches_finales = ["1_HEM_ton_sol_OAD", "2_Urbain_Naturel_OAD"]
fichiers_a_supprimer = [fichier_hem_ton_sol, fichier_urbain]

for nom in noms_couches_finales:
    couches_existantes = QgsProject.instance().mapLayersByName(nom)
    for c in couches_existantes:
        QgsProject.instance().removeMapLayer(c.id())

for f in fichiers_a_supprimer:
    if os.path.exists(f):
        try:
            os.remove(f)
        except OSError:
            print(f" Attention: Impossible de supprimer {f}.")


print(" Étape 0 : Nettoyage et réparation des géométries...")
fiche_reparee = processing.run("native:fixgeometries", {'INPUT': couche_fiche, 'OUTPUT': 'TEMPORARY_OUTPUT'})
ocsge_repare = processing.run("native:fixgeometries", {'INPUT': couche_ocsge, 'OUTPUT': 'TEMPORARY_OUTPUT'})


print(" Traitement 1/2 : Génération de la base Agricole (HEM_ton_sol)...")
join_hem = processing.run("qgis:joinbylocationsummary", {
    'INPUT': fiche_reparee['OUTPUT'],
    'JOIN': couche_axes,
    'PREDICATE': [0],
    'JOIN_FIELDS': ['_mean'],
    'SUMMARIES': [3], # 3 = MAX
    'DISCARD_NONMATCHING': False,
    'OUTPUT': fichier_hem_ton_sol
})

print(" Traitement 2/2 : Génération du reste du territoire (OCSGE sans parcelles agricoles)...")
ocsge_sans_fiche = processing.run("native:difference", {
    'INPUT': ocsge_repare['OUTPUT'],
    'OVERLAY': fiche_reparee['OUTPUT'], # On gomme les parcelles agricoles de l'OCS GE
    'OUTPUT': 'TEMPORARY_OUTPUT'
})

join_urbain = processing.run("qgis:joinbylocationsummary", {
    'INPUT': ocsge_sans_fiche['OUTPUT'],
    'JOIN': couche_axes,
    'PREDICATE': [0],
    'JOIN_FIELDS': ['_mean'],
    'SUMMARIES': [3], # 3 = MAX
    'DISCARD_NONMATCHING': False,
    'OUTPUT': fichier_urbain
})

print(" Chargement des couches dans QGIS...")
layer_hem = QgsVectorLayer(join_hem['OUTPUT'], "1_HEM_ton_sol_OAD", "ogr")
layer_urbain = QgsVectorLayer(join_urbain['OUTPUT'], "2_Urbain_Naturel_OAD", "ogr")

if layer_hem.isValid() and layer_urbain.isValid():
    QgsProject.instance().addMapLayer(layer_urbain)
    QgsProject.instance().addMapLayer(layer_hem)
    print(" SUCCÈS TOTAL ! Modèle simplifié en 2 couches terminé.")
else:
    print(" Erreur lors du chargement d'une des couches.")