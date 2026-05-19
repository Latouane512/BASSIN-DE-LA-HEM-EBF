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

Pensé comme un véritable **Outil d'Aide à la Décision (OAD)**, cet outil permet de visualiser, d'explorer et de vulgariser les résultats de modélisations spatiales (QGIS/Python) croisant géomorphologie, puissance spécifique, hydrologie et contraintes réglementaires (documents d'urbanisme). En vue d'un futur transfert vers les outils institutionnels (ex: Webmapping du Parc), ce prototype fait l'objet d'améliorations ergonomiques continues.

---

## Fonctionnalités Principales

L'application est structurée en deux vues distinctes, accessibles via un menu de navigation fluide :

### 1️ Vue Diagnostic (Puissance Spécifique & Energie cinétique)
* **Cartographie interactive** : Visualisation des tronçons homogènes selon la typologie de Malavoi. La sémiologie graphique a été spécifiquement optimisée pour distinguer clairement les dynamiques d'équilibre (E3 - Orange adouci) et d'érosion active (E4 - Rouge intense) lors de la superposition des crues.
* **Sélecteur de crues** : Bascule dynamique entre les périodes de retour (Q2, Q5, Q10, Q20, Q50, Q100).
* **Fonds de plan enrichis & UI** : Choix entre *CartoDB Voyager* (clair, contrasté et routier), *OSM Topo* (naturaliste/relief) et *Esri Satellite*. Intégration d'une échelle cartographique dynamique.

### 2️ Vue Modélisation EBF & Urbanisme (Aide à la décision)
* **Moteur de recherche par commune** : Menu déroulant permettant un vol dynamique (`flyToBounds`) sur l'emprise géographique exacte de la commune sélectionnée.
* **Générateur d'exports réglementaires** : Téléchargement dynamique des cartographies communales pré-générées en haute résolution (PNG). 
* **Modale de Contexte GEMA** : Fiche didactique intégrée détaillant le cadre conceptuel (les 5 dimensions de l'EBF, distinction EFO/EFN) et réglementaire (DCE, SDAGE Artois-Picardie).
* **Analyse réglementaire (PLUi)** : Intégration des couches de zonage intersectées. Pop-ups enrichis affichant le code (ex: *1AU*) et le libellé long du règlement.
* **Dashboard interactif (Chart.js)** : Graphique en anneau dynamique visualisant en temps réel les pourcentages de conflits fonciers (U/AU vs A/N) entre l'EFO et l'EFN.

---

##  Index des Données et Millésimes

Afin d'assurer la reproductibilité et la transparence de l'analyse, voici l'ensemble des sources de données mobilisées pour la modélisation spatiale et l'habillage de l'application :

| Thématique | Source de la donnée | Millésime | Remarques & Justifications |
| :--- | :--- | :--- | :--- |
| **Topographie & Morphologie** | IGN (LiDAR HD ) | 2022 | Donnée socle pour l'extraction des pentes, la modélisation du MRVBF et la détection des lits perchés (potentiel d'avulsion). |
| **Réseau Hydrographique** | IGN (BD Topo) | 2022 | Tracé précis des cours d'eau du bassin versant de la Hem. |
| **Débits & Hydrométrie** | Hydro portail (Vigicrue) / DREAL | 2023 | Localisation des stations et extraction des débits de crues (Q2 à Q100) indispensables au calcul de la Puissance Spécifique (Ps). |
| **Ouvrages & Obstacles** | OFB / Sandre (Base ROE) | 2023 | Référentiel des Obstacles à l'Écoulement (moulins, seuils) justifiant géographiquement les secteurs de sédimentation forcée (E1). |
| **Géologie** | BRGM (Cartes 1/50 000) | - | Vecteurs de l'emprise des alluvions quaternaires (Fz) marquant l'historique des migrations du lit. |
| **Milieux (ZDH)** | DREAL / Agence de l'Eau | 2021 | Modélisation globale des Zones à Dominance Humide (ZDH). |
| **Zones Humides à Enjeux** | Inventaires locaux (SAGE / SmageAa) | - | Cartographie fine des zones humides avérées à forte valeur biologique, intégrées prioritairement dans l'EFN. |
| **Enjeux Anthropiques** | IGN (OCS GE) | 2021 | *Bien que la base régionale OCS2D des Hauts-de-France soit une référence d'occupation du sol, l'OCS GE a été privilégiée ici pour l'extraction stricte des "enveloppes dures" (bâti et infrastructures routières) nécessaires au rabotage de l'EFO. L'OCS GE répond spécifiquement à ce besoin géométrique.* |
| **Urbanisme** | PLUi / Géoportail de l'Urbanisme (GPU) | 2023 | Zonages réglementaires de l'intercommunalité pour l'analyse des conflits fonciers. |
| **Limites Administratives** | IGN (Admin Express) | 2023 | Polygones des communes utilisés pour le moteur de recherche dynamique et l'export des cartes réglementaires. |

---

##  Architecture des Fichiers (Prérequis technique)

Pour fonctionner correctement (en local ou sur GitHub Pages), l'application nécessite une arborescence précise.
**Règle d'or :** Tous les fichiers géographiques (`.geojson`) doivent être projetés en **EPSG:4326 (WGS84)** pour être lus par Leaflet.

### 1. Données Cartographiques (Racine)
| Catégorie | Nom de fichier attendu dans le code |
| :--- | :--- |
| **Diagnostic** | `hem_troncons_homogenes_finaux_1.geojson` |
| **Contexte** | `Reseau_Hydrographique.geojson`, `Station.geojson`, `Ouvrage_WGS.geojson`, `communes.geojson` |
| **Bases EBF** | `Geologie.geojson`, `MRVBF_LISSER.geojson`, `ZDH_Global.geojson`, `ZH_Enjeux.geojson`, `LIT_perche_WGS.geojson` |
| **Buffers EBF** | `EBF_Geochimique_25m.geojson`, `EBF_Geochimique_5m.geojson`, `Buffer_Erosion_EFO.geojson`, `Buffer_Erosion_EFN.geojson` |
| **Synthèses** | `EFO_FINAL_WGS.geojson`, `EFN_FINAL_WGS.geojson`, `Bati_route.geojson` |
| **Urbanisme** | `EFO_PLUI.geojson`, `EFN_PLUI.geojson` |

### 2. Dossiers d'Exports (Pour les téléchargements PNG)
À la racine du projet, 3 dossiers doivent être créés et contenir les images des cartes communales selon la syntaxe suivante :
* 📁 `EFO/` (ex: *NomDeLaCommune_EFO.png*)
* 📁 `EFN/` (ex: *NomDeLaCommune_EFN.png*)
* 📁 `Complet/` (ex: *NomDeLaCommune_EBF_Global.png*)

---

##  Déploiement

Aucune installation complexe (type Node.js ou base de données) n'est requise. C'est une application front-end "Static Web".

1. Clonez ce dépôt.
2. Assurez-vous de l'intégrité de l'arborescence (fichiers `.geojson` à la racine, dossiers d'images créés).
3. Lancez le fichier `index.html` via un serveur web local (ex: *Live Server* sur VS Code ou `python -m http.server`) pour éviter les restrictions CORS des navigateurs.
4. **Mise en ligne** : Poussez le tout sur la branche principale et activez **GitHub Pages** dans les paramètres du dépôt.
