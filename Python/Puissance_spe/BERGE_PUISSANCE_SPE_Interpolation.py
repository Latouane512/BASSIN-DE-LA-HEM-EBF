import processing
from qgis.core import (
    QgsProject, QgsField, edit, QgsFeatureRequest, QgsPointXY, QgsSpatialIndex
)
from PyQt5.QtCore import QVariant
import math


NOM_TRONCONS = 'hem_troncons_oieau'  
NOM_MNT = 'MNT_REMPLI_2M'           
NOM_POINTS_BV = 'Point_BNBV — point_bnbv' 

DIST_ENTRE_POINTS = 50.0    
CHAMP_LARG = 'Largeur_moy'
CHAMP_PERCHE = 'perche'
CHAMP_VALEUR_BV = 'Superficie' 

# --- SOUCHE HYDROLOGIQUE OFFICIELLE DE TOURNEHEM ---
BV_TOURNEHEM = 105.0 
Q_TOURNEHEM = {
    'Q2': 9.30, 
    'Q5': 14.08, 
    'Q10': 17.24, 
    'Q20': 20.28, 
    'Q50': 24.20, 
    'Q100': 27.15
}

# --- SOUCHE HYDROLOGIQUE DE RECQUES-SUR-HEM ---
BV_RECQUES = 125.0
Q_RECQUES = {
    'Q2': 12.81, 
    'Q5': 17.30, 
    'Q10': 20.27, 
    'Q20': 23.12,
    'Q50': 26.81,  
    'Q100': 29.58  
}

RHO_G = 9810
CRUES = ['Q2', 'Q5', 'Q10', 'Q20', 'Q50', 'Q100']

project = QgsProject.instance()
vlayer = project.mapLayersByName(NOM_TRONCONS)[0]
mnt_layer = project.mapLayersByName(NOM_MNT)[0]
couche_pts_bv = project.mapLayersByName(NOM_POINTS_BV)[0]

# --- FONCTIONS DE SEUILS D'ÉNERGIE (MALAVOI) ---
def get_code_energie(ps):
    if ps < 10: return "E1"
    elif ps <= 30: return "E2"
    elif ps <= 100: return "E3"
    else: return "E4"

def get_label_energie(ps):
    if ps < 10: return "Nulle (<10 W/m2)"
    elif ps <= 30: return "Faible (10-30 W/m2)"
    elif ps <= 100: return "Moyenne (30-100 W/m2)"
    else: return "Forte (>100 W/m2)"

def get_z(x, y):
    val, ok = mnt_layer.dataProvider().sample(QgsPointXY(x, y), 1)
    return val if ok and not math.isnan(val) else None


print("Étape 0 : Initialisation de l'index spatial pour BV_interp...")
idx_source_bv = couche_pts_bv.fields().lookupField(CHAMP_VALEUR_BV)
points_dict = {}
for f in couche_pts_bv.getFeatures():
    if f.geometry():
        val_bv = f.attributes()[idx_source_bv]
        if val_bv is not None:
            points_dict[f.id()] = (f.geometry().asPoint(), float(val_bv))

index_spatial_pts = QgsSpatialIndex(couche_pts_bv.getFeatures())


print(f"Étape 1 : Échantillonnage géométrique sur le MNT tous les {DIST_ENTRE_POINTS}m...")

res_pts = processing.run("native:pointsalonglines", {
    'INPUT': vlayer, 'DISTANCE': DIST_ENTRE_POINTS, 'OUTPUT': 'memory:'
})['OUTPUT']

champs_pts = [f.name() for f in res_pts.fields()]
nom_id_liaison = next((n for n in champs_pts if n in ['ID', 'parent_id', 'fid', 'orig_fid']), 'fid')

z_hb_data = {} 
features_pts = list(res_pts.getFeatures())

for i, f in enumerate(features_pts):
    geom = f.geometry().asPoint()
    angle_ligne = float(f['angle'])
    pid = f[nom_id_liaison]
    
    largeur = float(f[CHAMP_LARG]) if f[CHAMP_LARG] else 2.0
    demi_larg = largeur / 2.0
    
    # Rive Gauche
    rad_gauche = math.radians(angle_ligne + 90)
    x_gauche = geom.x() + (demi_larg * math.cos(rad_gauche))
    y_gauche = geom.y() + (demi_larg * math.sin(rad_gauche))
    z_gauche = get_z(x_gauche, y_gauche)
    
    # Rive Droite
    rad_droite = math.radians(angle_ligne - 90)
    x_droite = geom.x() + (demi_larg * math.cos(rad_droite))
    y_droite = geom.y() + (demi_larg * math.sin(rad_droite))
    z_droite = get_z(x_droite, y_droite)
    
    z_valides = [z for z in [z_gauche, z_droite] if z is not None]
    if z_valides:
        z_hb_data[i] = {'z': sum(z_valides)/len(z_valides), 'pid': pid}



print("Étape 2 : Calcul des pentes longitudinales...")

pentes_finales = {}
for i in z_hb_data:
    if i+1 in z_hb_data and z_hb_data[i]['pid'] == z_hb_data[i+1]['pid']:
        p_longi = abs(z_hb_data[i]['z'] - z_hb_data[i+1]['z']) / DIST_ENTRE_POINTS
        pid = z_hb_data[i]['pid']
        if pid not in pentes_finales: pentes_finales[pid] = []
        pentes_finales[pid].append(p_longi)

layer_finale = vlayer.materialize(QgsFeatureRequest())

# --- CRÉATION GLOBALE DES NOUVEAUX CHAMPS ---
print("Étape 3 : Structuration de la nouvelle table d'attributs...")
new_f = [
    QgsField("Pente_HB", QVariant.Double), 
    QgsField("BV_interp", QVariant.Double),
    QgsField("Cl_Energie", QVariant.String), 
    QgsField("Typologie", QVariant.String),
    QgsField("Typo_Dyn", QVariant.String)
]

for q in CRUES: 
    new_f.append(QgsField(f"Q_{q}_m3s", QVariant.Double))  
    new_f.append(QgsField(f"Ps_{q}", QVariant.Double))     
    new_f.append(QgsField(f"Cl_{q}", QVariant.String))

layer_finale.dataProvider().addAttributes(new_f)
layer_finale.updateFields()


print("Étape 4 : Calculs hydrologiques, puissances spécifiques et typologies...")

with edit(layer_finale):
    for f in layer_finale.getFeatures():
        id_val = f[nom_id_liaison] if nom_id_liaison in f.attributeMap() else f.id()
        p_list = pentes_finales.get(id_val, [0.0001])
        p_moy = sum(p_list) / len(p_list)
        
        # Filtre pont / sécurité lits perchés
        if f[CHAMP_PERCHE] == 0 or f[CHAMP_PERCHE] == '0' or f[CHAMP_PERCHE] is False:
            if p_moy > 0.015: p_moy = 0.003
        else:
            if p_moy > 0.1: p_moy = 0.1
            
        # CALCUL DE BV_INTERP (1 SEUL VOISIN LE PLUS PROCHE)
        geom = f.geometry()
        bv_interp_val = 0.1
        if geom:
            pt_milieu = geom.interpolate(geom.length() / 2.0).asPoint()
            # MODIFICATION ICI : On passe à 1 voisin pour éviter les erreurs liées aux méandres
            voisins_ids = index_spatial_pts.nearestNeighbor(pt_milieu, 1)
            somme_poids_valeurs, somme_poids = 0, 0
            exact_match = False
            
            for v_id in voisins_ids:
                if v_id in points_dict:
                    pt_voisin, val_voisin = points_dict[v_id]
                    dist = pt_milieu.distance(pt_voisin)
                    if dist == 0:
                        exact_match = True
                        bv_interp_val = val_voisin
                        break
                    poids = 1.0 / (dist ** 2)
                    somme_poids_valeurs += poids * val_voisin
                    somme_poids += poids
            
            if not exact_match and somme_poids > 0:
                bv_interp_val = somme_poids_valeurs / somme_poids

        largeur = float(f[CHAMP_LARG]) if f[CHAMP_LARG] and float(f[CHAMP_LARG]) > 0 else 2.0
        
        f["Pente_HB"] = p_moy
        f["BV_interp"] = bv_interp_val
        
        # COEUR DU CALCUL HYDROLOGIQUE MULTI-STATIONS ET SÉCURISATION DE L'AVAL
        classes_troncon = []
        ps_q100_val = 0
        
        for q in CRUES:
            q_tourn = Q_TOURNEHEM[q]
            q_recq = Q_RECQUES[q]
            
            # 1. Zone Amont : Transposition depuis Tournehem
            if bv_interp_val <= BV_TOURNEHEM:
                q_local = q_tourn * math.pow((bv_interp_val / BV_TOURNEHEM), 0.8)
            
            # 2. Zone de Transition : Interpolation linéaire parfaite entre les 2 stations
            elif BV_TOURNEHEM < bv_interp_val <= BV_RECQUES:
                facteur = (bv_interp_val - BV_TOURNEHEM) / (BV_RECQUES - BV_TOURNEHEM)
                q_local = q_tourn + (q_recq - q_tourn) * facteur
            
            # 3. Zone Aval : Transposition continue depuis Recques
            else:
                q_local = q_recq * math.pow((bv_interp_val / BV_RECQUES), 0.8)
            
            # Calcul de la puissance spécifique (Ps)
            ps_val = (RHO_G * q_local * p_moy) / largeur
            code_actuel = get_code_energie(ps_val)
            
            if q == 'Q100':
                ps_q100_val = ps_val
            classes_troncon.append(code_actuel)
            
            # Écriture des attributs
            f[f"Q_{q}_m3s"] = round(q_local, 2)
            f[f"Ps_{q}"] = round(ps_val, 1)
            f[f"Cl_{q}"] = code_actuel
            
        # SEUILS DE RÉFÉRENCE ET TYPOLOGIES (MALAVOI / DYNAMIQUE)
        cl_energie_q100 = get_label_energie(ps_q100_val)
        code_q100 = classes_troncon[-1]
        classe_q2 = classes_troncon[0]
        
        strahler = int(f['STRAHLER']) if 'STRAHLER' in layer_finale.fields().names() and f['STRAHLER'] else 0
        larg_arrondie = round(largeur)
        
        f["Cl_Energie"] = cl_energie_q100
        f["Typologie"] = f"S{strahler}-W{larg_arrondie}-{code_q100}"
        f["Typo_Dyn"] = f"S{strahler}-W{larg_arrondie} ({classe_q2} vers {code_q100})"
            
        layer_finale.updateFeature(f)


print("Étape 5 : Le Dissolve a été retiré. Calcul direct des longueurs spécifiques...")

layer_finale.startEditing()

champs_longueurs = [QgsField("Long_m", QVariant.Double)]
for q in CRUES:
    champs_longueurs.append(QgsField(f"Long_{q}", QVariant.Double))

layer_finale.dataProvider().addAttributes(champs_longueurs)
layer_finale.updateFields()

for f in layer_finale.getFeatures():
    # On calcule la longueur de chaque tronçon pour conserver son indépendance hydrologique
    longueur = round(f.geometry().length(), 1)
    layer_finale.changeAttributeValue(f.id(), layer_finale.fields().indexOf("Long_m"), longueur)
    for q in CRUES:
        layer_finale.changeAttributeValue(f.id(), layer_finale.fields().indexOf(f"Long_{q}"), longueur)

layer_finale.commitChanges()

layer_finale.setName("Hem_Troncons_Hydrologiques_Detailles")
QgsProject.instance().addMapLayer(layer_finale)

print(" Traitement terminé avec succès ! La couche 'Hem_Troncons_Hydrologiques_Detailles' a été ajoutée.")