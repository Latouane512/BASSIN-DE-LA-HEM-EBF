from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsFields, QgsField,
    QgsGeometry, QgsPointXY, QgsSpatialIndex, NULL
)
import processing


NOM_COUCHE_TRANSECTS = "transects"      # <--- Mets le nom de ta couche de lignes ici
NOM_COUCHE_MNT       = "MNT"            # <--- Mets le nom de ton MNT / LIDAR ici
NOM_COUCHE_SORTIE    = "Points_transects"

DISTANCE_POINTS      = 5.0              # Intervalle entre les points (mètres)
DECALAGE_DEBUT       = 0.0
DECALAGE_FIN         = 0.0
INCLURE_FIN          = True


def run_script():
    # Récupération des couches
    transects = None
    dem = None
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == NOM_COUCHE_TRANSECTS:
            transects = lyr
        if lyr.name() == NOM_COUCHE_MNT:
            dem = lyr

    if not transects or not dem:
        print("Erreur : Couche de transects ou MNT introuvable. Vérifie les noms.")
        return

    # 1. Points le long des transects
    pts = processing.run(
        "qgis:pointsalonglines",
        {
            "INPUT": transects,
            "DISTANCE": DISTANCE_POINTS,
            "START_OFFSET": DECALAGE_DEBUT,
            "END_OFFSET": DECALAGE_FIN,
            "INCLUDE_END": INCLURE_FIN,
            "OUTPUT": "memory:"
        }
    )["OUTPUT"]

    # 2. Sampling du MNT
    sampled = processing.run(
        "qgis:rastersampling",
        {
            "INPUT": pts,
            "RASTERCOPY": dem,
            "COLUMN_PREFIX": "elev_",
            "OUTPUT": "memory:"
        }
    )["OUTPUT"]

    elev_field = None
    for f in sampled.fields():
        if f.name().startswith("elev_"):
            elev_field = f.name()
            break

    # 3. Création de la couche finale
    crs = transects.crs()
    out = QgsVectorLayer(f"Point?crs={crs.authid()}", NOM_COUCHE_SORTIE, "memory")
    prov = out.dataProvider()

    fields = QgsFields()
    fields.append(QgsField("FID", QVariant.Int))
    fields.append(QgsField("CODE", QVariant.String))
    fields.append(QgsField("ID", QVariant.Int))
    fields.append(QgsField("DISTANCE", QVariant.Double))
    fields.append(QgsField("ELEVATION", QVariant.Double))

    prov.addAttributes(fields)
    out.updateFields()

    # 4. Attribution automatique des codes T1, T2, T3…
    transect_codes = {}
    for i, f in enumerate(transects.getFeatures(), start=1):
        transect_codes[f.id()] = f"T{i}"

    # 5. Rattachement via Index Spatial
    join_field = "_transect_id"
    sampled.dataProvider().addAttributes([QgsField(join_field, QVariant.Int)])
    sampled.updateFields()
    idx = sampled.fields().indexOf(join_field)

    index = QgsSpatialIndex(transects.getFeatures())

    for pt in sampled.getFeatures():
        g = pt.geometry()
        nearest_ids = index.nearestNeighbor(g.asPoint(), 5)

        best_dist = 999999999
        best_transect = None

        for tid in nearest_ids:
            tr = transects.getFeature(tid)
            dist_seg = tr.geometry().closestSegmentWithContext(g.asPoint())[0]
            if dist_seg < best_dist:
                best_dist = dist_seg
                best_transect = tid

        sampled.dataProvider().changeAttributeValues({pt.id(): {idx: best_transect}})

    # 6. Regroupement des points par transect
    groups = {}
    for f in sampled.getFeatures():
        lid = f[join_field]
        groups.setdefault(lid, []).append(f)

    # 7. Tri exact et calcul de distance natif
    new_feats = []
    fid_global = 1

    for lid, feats in groups.items():
        code_val = transect_codes.get(lid, "")
        tr = transects.getFeature(lid)
        line = tr.geometry()

        feats.sort(key=lambda f: line.lineLocatePoint(f.geometry()))

        local_id = 1
        for f in feats:
            cum_dist = line.lineLocatePoint(f.geometry())
            elev = f[elev_field]

            nf = QgsFeature(out.fields())
            nf.setGeometry(f.geometry())
            nf["FID"] = fid_global
            nf["CODE"] = code_val
            nf["ID"] = local_id
            nf["DISTANCE"] = round(cum_dist, 2)
            nf["ELEVATION"] = round(float(elev), 2) if (elev is not None and elev != NULL) else None

            new_feats.append(nf)
            local_id += 1
            fid_global += 1

    prov.addFeatures(new_feats)
    out.updateExtents()

    QgsProject.instance().addMapLayer(out)
    print(f"Succès : Couche '{NOM_COUCHE_SORTIE}' générée.")

run_script()
