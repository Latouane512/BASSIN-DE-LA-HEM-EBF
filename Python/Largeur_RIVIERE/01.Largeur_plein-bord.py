from qgis.PyQt.QtCore import QVariant
from qgis.core import *
import numpy as np
from scipy.interpolate import CubicSpline

NOM_COUCHE_POINTS = "Points_transects" # <--- Couche de points générée par le script précédent
NOM_COUCHE_SORTIE = "Plein_bord_output"

CHAMP_CODE        = "CODE"
CHAMP_ID          = "ID"
CHAMP_DISTANCE    = "DISTANCE"
CHAMP_ELEVATION   = "ELEVATION"

ARRONDI_DECIMALES = 2


def run_script():
    # Recherche de la couche
    layer = None
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == NOM_COUCHE_POINTS:
            layer = lyr
            break

    if not layer or not isinstance(layer, QgsVectorLayer):
        print(f"Erreur : La couche '{NOM_COUCHE_POINTS}' est introuvable.")
        return

    # Couche résultat
    res = QgsVectorLayer("Point?crs=" + layer.crs().authid(), NOM_COUCHE_SORTIE, "memory")
    prov = res.dataProvider()
    prov.addAttributes([
        QgsField("CODE", QVariant.String),
        QgsField("TYPE", QVariant.String),
        QgsField("Y_bankfull", QVariant.Double),
        QgsField("L_bankfull", QVariant.Double)
    ])
    res.updateFields()

    # Groupement par CODE
    profils = {}
    for feat in layer.getFeatures():
        code = feat[CHAMP_CODE]
        profils.setdefault(code, []).append(feat)

    # Traitement par profil
    for code, feats in profils.items():
        if len(feats) < 3:
            continue

        xs = np.array([float(f[CHAMP_DISTANCE]) for f in feats], float)
        zs = np.array([float(f[CHAMP_ELEVATION]) for f in feats], float)

        coords = []
        for f in feats:
            pt = f.geometry().asPoint()
            coords.append((pt.x(), pt.y()))
        coords = np.array(coords)
        Xs_real = coords[:, 0]
        Ys_real = coords[:, 1]

        order = np.argsort(xs)
        xs = xs[order]
        zs = zs[order]
        Xs_real = Xs_real[order]
        Ys_real = Ys_real[order]

        idx_min = np.argmin(zs)
        ymin = zs[idx_min]
        x_th_real = Xs_real[idx_min]
        y_th_real = Ys_real[idx_min]

        ymax_g = np.max(zs[:idx_min+1])
        ymax_d = np.max(zs[idx_min:])
        ymax = min(ymax_g, ymax_d)

        spline = CubicSpline(xs, zs)

        bankfull_level = None
        xg = None
        xd = None
        last_valid = None

        for h in np.arange(ymin, ymax, 0.001):
            roots = (spline - h).roots()
            valid_roots = [r for r in roots if xs[0] <= r <= xs[-1]]
            valid_roots.sort()

            if len(valid_roots) == 2:
                last_valid = (h, valid_roots[0], valid_roots[1])
            elif len(valid_roots) < 2 and last_valid is not None:
                break

        feats_out = []

        if last_valid is not None:
            bankfull_level, xg, xd = last_valid
            bankfull_level = round(float(bankfull_level), ARRONDI_DECIMALES)
            xg = round(float(xg), ARRONDI_DECIMALES)
            xd = round(float(xd), ARRONDI_DECIMALES)

            xg_real = round(float(np.interp(xg, xs, Xs_real)), ARRONDI_DECIMALES)
            yg_real = round(float(np.interp(xg, xs, Ys_real)), ARRONDI_DECIMALES)

            xd_real = round(float(np.interp(xd, xs, Xs_real)), ARRONDI_DECIMALES)
            yd_real = round(float(np.interp(xd, xs, Ys_real)), ARRONDI_DECIMALES)

            largeur = round(abs(xd - xg), ARRONDI_DECIMALES)

            # BG
            f_bg = QgsFeature()
            f_bg.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(xg_real, yg_real)))
            f_bg.setAttributes([code, "BG", bankfull_level, None])
            feats_out.append(f_bg)

            # BD
            f_bd = QgsFeature()
            f_bd.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(xd_real, yd_real)))
            f_bd.setAttributes([code, "BD", bankfull_level, None])
            feats_out.append(f_bd)

            # Thalweg
            f_th = QgsFeature()
            f_th.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_th_real, y_th_real)))
            f_th.setAttributes([code, "Thalweg", bankfull_level, largeur])
            feats_out.append(f_th)

        else:
            f_th = QgsFeature()
            f_th.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_th_real, y_th_real)))
            f_th.setAttributes([code, "Thalweg", None, None])
            feats_out.append(f_th)

        prov.addFeatures(feats_out)

    QgsProject.instance().addMapLayer(res)
    print(f"Succès : Couche '{NOM_COUCHE_SORTIE}' générée.")

run_script()