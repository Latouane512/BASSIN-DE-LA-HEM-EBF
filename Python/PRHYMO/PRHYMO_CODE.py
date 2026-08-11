import processing
from qgis.core import QgsProject, QgsField, edit
from PyQt5.QtCore import QVariant


NOM_COUCHE_PRHYMO = "USRA_HEM" 

project = QgsProject.instance()
layers = project.mapLayersByName(NOM_COUCHE_PRHYMO)

if not layers:
    print(f" Erreur : La couche '{NOM_COUCHE_PRHYMO}' est introuvable.")
else:
    layer = layers[0]
    
    # Vérification et création de la colonne Morpho Ripisylve (mor_rip)
    champ_rip = QgsField("mor_rip", QVariant.Int)
    if layer.fields().indexFromName(champ_rip.name()) == -1:
        layer.dataProvider().addAttributes([champ_rip])
        layer.updateFields()
        print(" Colonne 'mor_rip' (Note 1 à 5) ajoutée à la table d'attributs.")

    # Vérification et création du champ de score final
    champ_score = QgsField("Score_100", QVariant.Double)
    if layer.fields().indexFromName(champ_score.name()) == -1:
        layer.dataProvider().addAttributes([champ_score])
        layer.updateFields()
        print(" Champ 'Score_100' créé avec succès.")

    count = 0
    

    with edit(layer):
        for f in layer.getFeatures():
            
            # Fonctions de sécurité pour la lecture des données
            def get_val_int(champ, default=1):
                try: return int(f[champ]) if f[champ] not in [None, 'NULL', ''] else default
                except: return default
            
            def get_val_float(champ, default=0.0):
                try: return float(f[champ]) if f[champ] not in [None, 'NULL', ''] else default
                except: return default

            # --- DÉTERMINATION DE LA NOTE DE RIPISYLVE (Basée sur veget10 textuel) ---
            # Inversion : Fort = 1 (très bon), Très faible = 5 (très dégradé)
            status_veget = str(f["veget10"]).strip().lower()
            
            if status_veget == "fort":
                note_ripisylve = 1
            elif status_veget == "moyen":
                note_ripisylve = 3
            elif status_veget == "faible":
                note_ripisylve = 4
            elif status_veget == "tres_faible" or status_veget == "très faible":
                note_ripisylve = 5
            else:
                # Sécurité au cas où une valeur textuelle manque : on repasse sur le %
                tx_veget = get_val_float("veget10_v", 100.0)
                if tx_veget >= 80.0: note_ripisylve = 1
                elif tx_veget >= 40.0: note_ripisylve = 3
                elif tx_veget >= 20.0: note_ripisylve = 4
                else: note_ripisylve = 5

            # Écriture physique de la note de ripisylve dans la nouvelle colonne
            f["mor_rip"] = note_ripisylve

            # --- PARTIE 1 : Somme des 9 critères physiques ---
            sum_classes = (
                get_val_int("mor_pll") + get_val_int("mor_ssl") + get_val_int("mor_riv") + 
                get_val_int("con_pro") + get_val_int("con_sed") + get_val_int("con_amp") +
                get_val_int("hyd_dyn") + get_val_int("hyd_qte") + note_ripisylve
            )
            
            # --- PARTIE 2 : Pressions Continues ---
            malus_agri = get_val_float("agri3w_v", 0.0) * 0.2
            malus_amenag = get_val_float("txamg_v", 0.0) * 0.2
            
            # --- CALCUL DU SCORE BRUT ---
            score_brut = sum_classes + malus_agri + malus_amenag
            
            # --- NORMALISATION ÉQUITABLE (0 à 100 %) ---
            min_theorique = 9.0
            max_theorique = 85.0
            score_normalise = ((score_brut - min_theorique) / (max_theorique - min_theorique)) * 100.0
            score_normalise = max(0.0, min(100.0, score_normalise))
            
            # Enregistrement final des deux attributs
            f["Score_100"] = round(score_normalise, 1)
            layer.updateFeature(f)
            count += 1
            
    print("\n" + "="*60)
    print(f" MISE À JOUR RÉUSSIE : {count} tronçons calculés.")
    print(" La colonne 'mor_rip' contient désormais vos notes de 1 à 5.")
    print(" Le 'Score_100' est recalibré de manière robuste sur cette base.")
    print("="*60)