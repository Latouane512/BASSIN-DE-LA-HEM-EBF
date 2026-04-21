# BASSIN-DE-LA-HEM-EBF
Détermination de l'espace de bon fonctionnement de la vallée de la HEM 

#  Plateforme Web : Diagnostic Morphodynamique & Modélisation EBF (La Hem)

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-589632?style=for-the-badge&logo=QGIS&logoColor=white)

Application de cartographie web (WebSIG) interactive développée dans le cadre de la définition de l'**Espace de Bon Fonctionnement (EBF)** sur le bassin versant de la Hem (SAGE Audomarois). 

Cet outil permet de visualiser et de vulgariser les résultats de modélisations spatiales (QGIS/Python) croisant puissance spécifique, géomorphologie et contraintes anthropiques.


## Fonctionnalités Principales

L'application est structurée en deux vues distinctes, accessibles via un menu de navigation fluide :

### 1️ Vue Diagnostic (Puissance Spécifique)
* **Cartographie interactive** : Visualisation des tronçons homogènes selon la typologie de Malavoi (Énergie E1 à E4).
* **Sélecteur de crues** : Bascule dynamique entre les périodes de retour (Q2 à Q100).
* **Panel de données au survol** : Affichage en temps réel des caractéristiques du tronçon survolé (Largeur, Pente, Puissance Spécifique exacte).
* **Couches d'habillage** : Intégration des stations hydrométriques et des ouvrages faisant obstacle à l'écoulement.

### 2️ Vue Modélisation EBF (Aide à la décision)
* **Sidebar interactive professionnelle** : Décomposition des couches de modélisation en 3 étapes (Potentiel EFO, Arbitrage EFN, Rabotage).
* **Lexique GEMA intégré** : Chaque couche dispose d'un pop-up didactique expliquant son rôle scientifique (ex: *Enveloppe MRVBF, Lits perchés, Tampons biogéochimiques*).
* **Charte graphique normalisée** : Couleurs et styles alignés sur les préconisations des Agences de l'Eau.



## Technologies Utilisées

* **Front-end** : HTML5, CSS3, JavaScript (Vanilla).
* **Bibliothèque Cartographique** : [Leaflet.js](https://leafletjs.com/) (v1.9.4).
* **Fonds de plan** : OpenStreetMap & Esri World Imagery.
* **Données** : Fichiers `.geojson` générés via des scripts d'automatisation PyQGIS.


## Architecture des Données (Prérequis)

Pour fonctionner en local, l'application s'attend à trouver les fichiers GeoJSON suivants à sa racine (exportés en **EPSG:4326 - WGS84**) :

| Catégorie | Nom de fichier attendu |
| :--- | :--- |
| **Diagnostic** | `hem_troncons_homogenes_finaux_1.geojson` |
| **Habillage** | `Station.geojson`, `Ouvrage_WGS.geojson` |
| **Bases EBF** | `Geologie.geojson`, `MRVBF_LISSER.geojson`, `ZDH_Global.geojson`, `ZH_Enjeux.geojson`, `LIT_perche_WGS.geojson` |
| **Buffers EBF** | `EBF_Geochimique_25m.geojson`, `EBF_Geochimique_5m.geojson`, `Buffer_Erosion_EFO.geojson`, `Buffer_Erosion_EFN.geojson` |
| **Synthèses** | `EFO_FINAL_WGS.geojson`, `EFN_FINAL_WGS.geojson`, `Bati_route.geojson` |
