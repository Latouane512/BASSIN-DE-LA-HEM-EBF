from qgis.core import *
import processing

# --- CONFIGURATION DES NOMS DE COUCHES ---
lyr_geologie = "Geologie_Alluvions"
lyr_mrvbf = "MRVBF_LISSER"
lyr_zdh = "ZDH_Global"
lyr_zhe = "ZH_Enjeux"
lyr_tampon_25 = "EBF_GEOCHIMIE_25m"
lyr_tampon_5 = "EBF_GEOCHIMIE_5m"
lyr_lits_perches = "AVULSION_LIT_PERCHE_"
lyr_bati = "Bati_route" 
lyr_crues_azi = "CRUES_AZI"


# 2. FONCTIONS OUTILS (Vérification et Calcul de surface)

def get_layer(nom):
    """Vérifie si la couche est chargée dans QGIS et retourne l'objet"""
    nom_propre = nom.strip()
    couches = QgsProject.instance().mapLayersByName(nom_propre)
    
    if not couches:
        raise ValueError(f" ERREUR : La couche '{nom_propre}' est introuvable. Vérifie le panneau des couches.")
    
    return couches[0]

def calculer_surface_couche(couche):
    """Calcule la surface totale d'une couche en hectares"""
    surface_totale_m2 = 0
    for feat in couche.getFeatures():
        if feat.geometry():
            surface_totale_m2 += feat.geometry().area()
    return round(surface_totale_m2 / 10000, 2)  # Conversion m² -> ha


# 3. FONCTION PRINCIPALE DE GÉNÉRATION ET COMPARAISON EBF

def generer_ebf_sur_mesure():
    print("\n" + "="*50)
    print(" DÉBUT DE LA MODÉLISATION EBF & ANALYSE DE L'IMPACT ANTHROPIQUE")
    print("="*50)

    try:
        # Récupération de la couche de bâti/contrainte
        couche_bati = get_layer(lyr_bati)

        # -------------------------------------------------------------
        # ÉTAPE A : CONSTRUCTION DE L'EFO (OPTIMAL - PAS DE RABOTAGE)
        # -------------------------------------------------------------
        print("\n[1/3] Assemblage de l'EFO (Scénario Optimal)...")
        noms_efo = [lyr_geologie, lyr_mrvbf, lyr_zdh, lyr_zhe, lyr_tampon_25, lyr_lits_perches, lyr_crues_azi]
        input_efo = [get_layer(nom) for nom in noms_efo] 
        
        efo_merge = processing.run("native:mergevectorlayers", {'LAYERS': input_efo, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        efo_final = processing.run("native:dissolve", {'INPUT': efo_merge, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        surf_efo_final = calculer_surface_couche(efo_final)
        
        # Ajout à la carte de l'EFO définitif (non raboté)
        QgsProject.instance().addMapLayer(efo_final).setName("EFO_DEFINITIF")
        print("    EFO_DEFINITIF généré avec succès.")

        # -------------------------------------------------------------
        # ÉTAPE B : CONSTRUCTION DE L'EFN BRUT (NÉCESSAIRE AVANT RABOTAGE)
        # -------------------------------------------------------------
        print("\n[2/3] Assemblage de l'EFN Brut...")
        noms_efn = [lyr_geologie, lyr_zhe, lyr_tampon_5, lyr_lits_perches, lyr_crues_azi]
        input_efn = [get_layer(nom) for nom in noms_efn]
        
        efn_merge = processing.run("native:mergevectorlayers", {'LAYERS': input_efn, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        efn_brut = processing.run("native:dissolve", {'INPUT': efn_merge, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        surf_efn_brut = calculer_surface_couche(efn_brut)

        # -------------------------------------------------------------
        # ÉTAPE C : RABOTAGE DE L'EFN PAR LE BÂTI
        # -------------------------------------------------------------
        print("\n[3/3] Rabotage de l'EFN par la couche Bâti/Route...")
        efn_final = processing.run("native:difference", {
            'INPUT': efn_brut,
            'OVERLAY': couche_bati,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        surf_efn_final = calculer_surface_couche(efn_final)

        # Ajout à la carte de l'EFN définitif (raboté)
        QgsProject.instance().addMapLayer(efn_final).setName("EFN_DEFINITIF")
        print("    EFN_DEFINITIF généré et raboté avec succès.")


        # ÉTAPE D : CALCUL DU BILAN DE PERTE SUR L'EFN
        
        perte_efn_ha = round(surf_efn_brut - surf_efn_final, 2)
        pct_perte_efn = round((perte_efn_ha / surf_efn_brut * 100), 1) if surf_efn_brut > 0 else 0

        print("\n" + "="*50)
        print(" MESURE DE LA CONTRAINTE ANTHROPIQUE SUR LE CORRIDOR")
        print("="*50)
        print(f" EFO DEFINITIF (Optimal - Préservé) : {surf_efo_final} ha")
        print("-" * 50)
        print(f" EFN BRUT (Nécessaire avant rabotage) : {surf_efn_brut} ha")
        print(f" EFN DEFINITIF (Nécessaire après rabotage) : {surf_efn_final} ha")
        print(f" Le bâti/route soustrait exactement : {perte_efn_ha} ha à l'EFN (soit une réduction de {pct_perte_efn} %)")
        print("="*50)
        print("\n Traitement terminé ! Les couches ont été ajoutées à ton projet QGIS.")

    except ValueError as err:
        print("\n" + "!"*40)
        print(err)
        print("!"*40 + "\n")
    except Exception as err:
        print("\n Une erreur inattendue est survenue durant le traitement :")
        print(err)

# 4. EXÉCUTION DU SCRIPT

generer_ebf_sur_mesure()