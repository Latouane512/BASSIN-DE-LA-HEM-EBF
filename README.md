# BASSIN-DE-LA-HEM-EBF
**Détermination de l'Espace de Bon Fonctionnement (EBF) de la vallée de la HEM**

# Plateforme Web : Diagnostic Morphodynamique, Modélisation EBF & Urbanisme

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-589632?style=for-the-badge&logo=QGIS&logoColor=white)

Application de cartographie web (WebSIG) interactive développée dans le cadre de la définition de l'**Espace de Bon Fonctionnement (EBF)** sur le bassin versant de la Hem. 

Cet outil permet de visualiser et de vulgariser les résultats de modélisations spatiales (QGIS/Python) croisant géomorphologie, puissance spécifique, hydrologie et contraintes réglementaires (documents d'urbanisme).

---

##  Fonctionnalités Principales

L'application est structurée en deux vues distinctes, accessibles via un menu de navigation fluide :

### 1️ Vue Diagnostic (Puissance Spécifique)
* **Cartographie interactive** : Visualisation des tronçons homogènes selon la typologie de Malavoi (Énergie E1 à E4).
* **Sélecteur de crues** : Bascule dynamique entre les périodes de retour (Q2, Q5, Q10, Q20, Q50, Q100).
* **Panel de données au survol** : Affichage en temps réel des caractéristiques du tronçon survolé (Largeur, Pente, Puissance Spécifique exacte).
* **Couches d'habillage** : Intégration du réseau hydrographique détaillé (avec toponymie), des stations hydrométriques et des ouvrages faisant obstacle à l'écoulement.

### 2️ Vue Modélisation EBF & Urbanisme (Aide à la décision)
* **Sidebar interactive** : Décomposition thématique des couches de modélisation (Potentiel EFO, Arbitrage EFN, Contexte géographique).
* **Lexique GEMA intégré** : Chaque couche dispose d'un pop-up didactique expliquant son rôle scientifique (ex: *MRVBF, Lits perchés, Tampons biogéochimiques*).
* **Analyse réglementaire (PLUi)** : 
    * Intégration des couches de zonage du Plan Local d'Urbanisme intercommunal, intersectées sur les emprises de l'EFO et de l'EFN.
    * Pop-ups enrichis affichant le type de zone (A, N, U, AU) et le libellé complet du règlement.
* **Dashboard interactif (Chart.js)** : Un graphique en anneau (Doughnut) interactif généré dynamiquement pour visualiser en temps réel les pourcentages d'occupation des sols (conflits fonciers) entre l'EFO et l'EFN.

---

##  Technologies Utilisées

* **Front-end** : HTML5, CSS3, JavaScript (Vanilla).
* **Bibliothèques Web** : 
    * [Leaflet.js](https://leafletjs.com/) (v1.9.4) pour le rendu cartographique.
    * [Chart.js](https://www.chartjs.org/) pour la datavisualisation interactive.
* **Fonds de plan** : OpenStreetMap & Esri World Imagery (Satellite).
* **Données** : Fichiers `.geojson` générés via des scripts d'automatisation PyQGIS.

---

##  Architecture des Données (Prérequis)

Pour fonctionner correctement sur un serveur web (ou GitHub Pages), l'application s'attend à trouver les fichiers `GeoJSON` suivants à sa racine.  
**Règle d'or :** Tous les fichiers géographiques doivent obligatoirement être projetés en **EPSG:4326 (WGS84)** pour être lus par Leaflet.

| Catégorie | Nom de fichier attendu dans le code |
| :--- | :--- |
| **Bases & Diagnostic** | `hem_troncons_homogenes_finaux_1.geojson` |
| **Contexte & Habillage** | `Reseau_Hydrographique.geojson`, `Station.geojson`, `Ouvrage_WGS.geojson` |
| **Briques EBF (Géomorpho)** | `Geologie.geojson`, `MRVBF_LISSER.geojson`, `ZDH_Global.geojson`, `ZH_Enjeux.geojson`, `LIT_perche_WGS.geojson` |
| **Buffers Dynamiques** | `EBF_Geochimique_25m.geojson`, `EBF_Geochimique_5m.geojson`, `Buffer_Erosion_EFO.geojson`, `Buffer_Erosion_EFN.geojson` |
| **Enveloppes Finales** | `EFO_FINAL_WGS.geojson`, `EFN_FINAL_WGS.geojson`, `Bati_route.geojson` |
| **Données d'Urbanisme** | `EFO_PLUI.geojson`, `EFN_PLUI.geojson` |

---

## Installation & Déploiement

Aucune installation complexe (type Node.js ou base de données) n'est requise. Il s'agit d'une application "Static Web" (Côté client).

1. Clonez ce dépôt ou téléchargez les fichiers.
2. Assurez-vous que l'ensemble des fichiers `.geojson` mentionnés ci-dessus se trouvent dans le même dossier que votre fichier `index.html`.
3. Lancez le fichier `index.html` via un serveur local (ex: extension *Live Server* sur VS Code, ou `python -m http.server`) pour contourner les restrictions CORS des navigateurs.
4. **Déploiement en ligne** : Poussez vos fichiers sur la branche principale de GitHub et activez **GitHub Pages** dans les paramètres du dépôt. L'application sera immédiatement accessible en ligne.
