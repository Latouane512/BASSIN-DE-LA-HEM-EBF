# BASSIN-DE-LA-HEM-EBF
**Outil de gestion intégrée et détermination de l'Espace de Bon Fonctionnement (EBF) de la vallée de la HEM**

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-589632?style=for-the-badge&logo=QGIS&logoColor=white)

Application de cartographie web (WebSIG) interactive développée pour centraliser la connaissance environnementale et définir l'**Espace de Bon Fonctionnement (EBF)** sur le bassin versant de la Hem. 

Pensé comme un véritable **Outil d'Aide à la Décision (OAD)** multi-acteurs, cet outil vulgarise et croise des données complexes : géomorphologie, hydrologie, biodiversité, risque inondation et contraintes réglementaires (PLUi). En vue d'un transfert vers les outils institutionnels (ex: Webmapping du Parc Naturel Régional), ce prototype intègre une gestion différenciée des accès (Public/Élus vs. Agents Techniques) pour sécuriser les données sensibles.

---

## Fonctionnalités & Ergonomie

*  **Système de profils (Public / Agent Technique)** : Accès restreint par mot de passe pour les modules avancés (Diagnostic morphodynamique, exports de données brutes).
*  **Filtres de données dynamiques** : Tri croisé par année et par type d'aménagement pour les couches historiques (données piscicoles, travaux hydrauliques doux).
*  **Export de données (GeoJSON)** : Panneau de sélection pour télécharger les couches modélisées directement depuis l'interface web (réservé aux agents).
*  **Légende contextuelle statique** : Légende synchronisée automatiquement avec l'onglet actif pour une lecture immédiate de la carte.

---

##  Les 3 Vues de l'Application

L'application est structurée en trois grands modules thématiques, accessibles via un menu de navigation fluide :

### 1 Présentation de la Vallée (Vision transversale)
* **Territoire & PNR** : Visualisation des limites communales, du périmètre actuel (2013-2028) et futur (2028-2044) du Parc Naturel Régional.
* **Risque Inondation & Ruissellement** : Croisement du PPRI, de l'Atlas des Zones Inondables (AZI), des repères de crues historiques et des modélisations d'axes de ruissellement.
* **Biodiversité (Trame Verte et Bleue)** : Cartographie exhaustive des enjeux écologiques (Zones Humides, Natura 2000, ZNIEFF, Réservoirs de biodiversité, Mares).
* **Suivi Piscicole & Aménagements** : Historique des pêches électriques, suivi des frayères (SNDP), réseau spécifique Anguille (RSA) et recensement des travaux hydrauliques doux (fascines, noues) avec filtre chronologique.

### 2 Modélisation EBF & Urbanisme (Aide à la décision)
* **Emprises EFO / EFN** : Visualisation de l'EBF Optimal (liberté totale) et de l'EBF Nécessaire (corridor de compromis réglementaire).
* **Moteur de recherche par commune** : Zoom dynamique sur une commune spécifique pour cibler l'analyse foncière.
* **Générateur d'exports réglementaires** : Téléchargement direct des cartes communales en haute résolution (PNG).
* **Analyse réglementaire (PLUi)** : Intégration des zonages. Pop-ups enrichis avec le règlement associé.
* **Dashboard interactif (Chart.js)** : Graphique en anneau visualisant en temps réel les conflits d'usage (Agricole/Naturel vs. Urbain/À Urbaniser) au sein des enveloppes EBF.

### 3️ Diagnostic Morphodynamique (Réservé aux experts)
* **Cartographie de la Puissance Spécifique (Ps)** : Affichage des tronçons selon la typologie de Malavoi (Crues Q2 à Q100) identifiant les zones d'érosion active (E4) et de dépôt (E1).
* **Indice de Dégradation PRHYMO** : Notation de l'altération physique du cours d'eau basée sur 9 indicateurs qualitatifs et des variables quantitatives (occupation des berges).
* **Vulnérabilité Agricole et Bâti** : Identification des parcelles agricoles et du bâti impactés par les flux de ruissellement, classés par niveaux d'urgence (Sécurité urgence, Consolidation MAEC, Veille).

---

##  Index des Données et Millésimes

L'outil agrège une quantité massive de données institutionnelles et de modélisations sur-mesure.

| Thématique | Source de la donnée | Millésime | Remarques |
| :--- | :--- | :--- | :--- |
| **Topographie & Morphologie** | IGN (LiDAR HD) | 2022 | Extraction des pentes, MRVBF, détection des lits perchés. |
| **Débits & Hydrométrie** | Hydro portail / DREAL | 2023 | Extraction des débits de crues (Q2 à Q100) pour le calcul de Ps. |
| **Géologie** | BRGM | - | Vecteurs de l'emprise des alluvions quaternaires (Fz). |
| **Inondation & Risques** | DDTM / DREAL | 2023 | PPRI, AZI, repères de crues historiques. |
| **Biodiversité** | DREAL / INPN / SRADDET | 2023 | Natura 2000, ZNIEFF 1 & 2, Trames Verte/Bleue, Sites Classés. |
| **Suivi Piscicole** | OFB / Féd. Pêche (FDAAPPMA 62)| 2011-2023| RSA Anguille, SAT Saumon, Inventaires PE, Suivi des Frayères (SNDP). |
| **Travaux & Aménagements** | SYMVAHEM / ROE (Sandre)| 2023 | Historique des aménagements doux (plantations, fascines) et obstacles. |
| **Occupation du Sol (Enjeux)** | IGN (OCS GE) | 2021 | Détection des "enveloppes dures" pour le rabotage de l'EFO. |
| **Urbanisme (PLUi)** | Géoportail de l'Urbanisme | 2023 | Analyse des conflits d'usage (Zonages A, N, U, AU). |

---

##  Architecture des Fichiers

Pour fonctionner correctement (en local ou sur GitHub Pages), l'application s'attend à trouver les données géographiques à sa racine.  
⚠️ **Tous les fichiers géographiques (`.geojson`) doivent être projetés en EPSG:4326 (WGS84).**

### 📁 Scripts Python de traitement (`/Python`)
Le projet contient un dossier dédié `Python/` regroupant les scripts automatisés (PyQGIS / GeoPandas) ayant servi à :
* Le prétraitement et le nettoyage des couches SIG brutes.
* Le calcul automatisé des emprises EBF, des indices PRHYMO et de la Puissance Spécifique (Ps).

**Données de base & EBF :**
* `communes.geojson`, `Hydro_HEM_WGS.geojson`
* `EFO_FINAL_WGS.geojson`, `EFN_FINAL_WGS.geojson`, `EFO_PLUI.geojson`, `EFN_PLUI.geojson`
* `Geologie.geojson`, `MRVBF_LISSER.geojson`, `ZDH_Global.geojson`, `ZH_Enjeux.geojson`, `LIT_perche_WGS.geojson`
* `EBF_Geochimique_25m.geojson`, `EBF_Geochimique_5m.geojson`, `Buffer_Erosion_EFO.geojson`, `Buffer_Erosion_EFN.geojson`, `Bati_route.geojson`

**Données de Présentation (Biodiversité, Risques, PNR) :**
* `PNR_CMO_2013-2028.geojson`, `PNR_CMO_2028-2044.geojson`, `Communes_2013-2028.geojson`, `Communes_2028-2044.geojson`, `Exutoire_HEM.geojson`
* `PPRI_ancien.geojson`, `Crues_AZI.geojson`, `lieux_inondes.geojson`, `bassin_hem.geojson`, `Axe_ruissellement_hors_lit_pente.geojson`
* `ZCS_HEM.geojson`, `ZNIEFF1.geojson`, `ZNIEFF2.geojson`, `reservoir_biodiversite.geojson`, `Sites_classe_hem.geojson`, `reserve_biosphere.geojson`, `trame_vert.geojson`, `trame_bleu.geojson`, `mares.geojson`
* `Plantations_hydraulique_douce.geojson`, `Travaux_lineaire_complet.geojson`, `Travaux_ponctuels_complet.geojson`
* `RSA_62.geojson`, `SIG_SAT62.geojson`, `SNDP_TRF_FD62.geojson`, `SNDP_LPF_FD62.geojson`, `SIG_PE_FD62.geojson`

**Données de Diagnostic :**
* `hem_troncons_homogenes_finaux_1.geojson`, `Station.geojson`, `Ouvrage_WGS.geojson`
* `USRA_HEM.geojson` (PRHYMO), `HEM_TON_SOL.geojson` (Parcelles Agri), `Zone_Bati.geojson` (Bâti impacté)

### Dossiers d'Exports (Téléchargements PDF/PNG)
À la racine du projet, 3 dossiers doivent être créés et contenir les images des cartes communales selon la syntaxe suivante :
* 📁 `EFO/` (ex: *NomDeLaCommune_EFO.png*)
* 📁 `EFN/` (ex: *NomDeLaCommune_EFN.png*)
* 📁 `Complet/` (ex: *NomDeLaCommune_EBF_Global.png*)

---

##  Déploiement

Aucune installation complexe (type Node.js ou base de données) n'est requise. Il s'agit d'une application front-end "Static Web".

1. Clonez ce dépôt.
2. Assurez-vous de l'intégrité de l'arborescence (fichiers `.geojson` à la racine, dossiers d'images créés).
3. Lancez le fichier `index.html` via un serveur web local (ex: extension *Live Server* sur VS Code, ou commande `python -m http.server`) pour éviter les restrictions CORS des navigateurs.
4. **Mise en ligne** : Poussez le tout sur la branche principale et activez **GitHub Pages** dans les paramètres du dépôt. L'application sera accessible immédiatement.
