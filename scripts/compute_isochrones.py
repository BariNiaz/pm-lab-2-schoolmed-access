# -*- coding: utf-8 -*-
"""Расчёт пешеходных изохрон 10/15/20 минут для школ и поликлиник Уфы.

Шаги:
1. Если нет кэша графа — собрать пешеходный граф из выгрузки Geofabrik (PBF) по bbox Уфы.
2. Для каждого объекта посчитать изохроны 10/15/20 минут.
3. Посчитать расстояние по пешеходной сети от школ до ближайшей поликлиники.

Запуск из корня репозитория:
    python scripts/compute_isochrones.py

Нужны данные: data/raw/volga-fed-district-latest.osm.pbf
(скачивается отдельно с https://download.geofabrik.de/russia/volga-fed-district-latest.osm.pbf).
Кэш графа и промежуточные файлы — в .cache/ (не коммитится).
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Geod, Transformer
from shapely.geometry import MultiPoint

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "volga-fed-district-latest.osm.pbf"
CACHE = ROOT / ".cache"
GRAPH_PKL = CACHE / "walk_graph.pkl"
BBOX = (55.6, 54.5, 56.3, 55.0)          # lon_min, lat_min, lon_max, lat_max
WALK = {"footway", "path", "pedestrian", "living_street", "residential", "unclassified",
        "service", "tertiary", "secondary", "primary", "trunk", "track", "steps",
        "cycleway", "bridleway", "road", "crossing"}
SPEED_KMH = 4.5
M_PER_MIN = SPEED_KMH * 1000 / 60
ZONES_MIN = (10, 15, 20)
GEOD = Geod(ellps="WGS84")
TR = Transformer.from_crs(4326, 32640, always_xy=True)


def build_graph() -> dict:
    """Читает выгрузку OSM и строит пешеходный граф (узлы в WGS84, длины в метрах)."""
    import pyogrio

    CACHE.mkdir(exist_ok=True)
    gdf = pyogrio.read_dataframe(RAW, layer="lines", bbox=BBOX,
                                 columns=["osm_id", "highway", "access", "foot", "service"])
    gdf = gdf[gdf["highway"].isin(WALK)]
    for col, bad in (("access", "private"), ("foot", "no"), ("service", "private")):
        if col in gdf.columns:
            gdf = gdf[gdf[col] != bad]

    nodes, node_xy, edges = {}, [], {}
    def nid(pt):
        key = (round(pt[0], 7), round(pt[1], 7))
        if key not in nodes:
            nodes[key] = len(node_xy)
            node_xy.append((pt[0], pt[1]))
        return nodes[key]

    for geom in gdf.geometry:
        if geom is None:
            continue
        for part in getattr(geom, "geoms", [geom]):
            coords = list(part.coords)
            for a, b in zip(coords, coords[1:], strict=False):
                u, v = nid(a), nid(b)
                if u == v:
                    continue
                _, _, dist = GEOD.inv(a[0], a[1], b[0], b[1])
                if dist <= 0:
                    continue
                key = (min(u, v), max(u, v))
                if key not in edges or dist < edges[key]:
                    edges[key] = float(dist)

    edge_arr = np.array([[k[0], k[1], v] for k, v in edges.items()], dtype=float)
    data = {"nodes": np.array(node_xy, dtype=float), "edges": edge_arr}
    with open(GRAPH_PKL, "wb") as f:
        pickle.dump(data, f)
    return data


def load_graph() -> tuple[nx.Graph, np.ndarray, np.ndarray]:
    if not GRAPH_PKL.exists():
        build_graph()
    with open(GRAPH_PKL, "rb") as f:
        data = pickle.load(f)
    xs, ys = TR.transform(data["nodes"][:, 0], data["nodes"][:, 1])
    G = nx.Graph()
    for u, v, length in data["edges"]:
        G.add_edge(int(u), int(v), length=float(length))
    return G, xs, ys


def nearest_node(px: float, py: float, xs: np.ndarray, ys: np.ndarray) -> tuple[int, float]:
    d2 = (xs - px) ** 2 + (ys - py) ** 2
    return int(np.argmin(d2)), float(d2[np.argmin(d2)] ** 0.5)


def main() -> int:
    G, xs, ys = load_graph()
    stats = {"graph_nodes": G.number_of_nodes(), "graph_edges": G.number_of_edges(),
             "speed_kmh": SPEED_KMH, "zones_min": list(ZONES_MIN)}
    print(f"graph: {stats['graph_nodes']} nodes, {stats['graph_edges']} edges")

    for layer, cols in (("schools", ["osm_id", "name"]), ("clinics", ["osm_id", "name"])):
        gdf = gpd.read_file(ROOT / "data" / "processed" / f"{layer}.gpkg").to_crs(32640)
        keep = [c for c in cols if c in gdf.columns]
        rows, skipped = [], 0
        for _, row in gdf.iterrows():
            node, dist = nearest_node(row.geometry.x, row.geometry.y, xs, ys)
            if dist > 300:
                skipped += 1
                continue
            for minutes in ZONES_MIN:
                reach = nx.single_source_dijkstra_path_length(
                    G, node, cutoff=minutes * M_PER_MIN, weight="length")
                if len(reach) < 3:
                    continue
                pts = [(xs[n], ys[n]) for n in reach]
                rec = {"minutes": minutes, "geometry": MultiPoint(pts).convex_hull.buffer(60)}
                for c in keep:
                    rec[c] = row.get(c)
                rows.append(rec)
        out = gpd.GeoDataFrame(rows, geometry="geometry", crs=32640)
        dst = ROOT / "data" / "isochrones" / f"{layer}.geojson"
        dst.parent.mkdir(parents=True, exist_ok=True)
        out.to_file(dst, driver="GeoJSON")
        stats[layer] = {"objects": int(len(gdf)), "isochrones": int(len(out)), "skipped": skipped}
        print(layer, stats[layer])

    clinics = gpd.read_file(ROOT / "data" / "processed" / "clinics.gpkg").to_crs(32640)
    clinic_nodes = set()
    for _, row in clinics.iterrows():
        node, dist = nearest_node(row.geometry.x, row.geometry.y, xs, ys)
        if dist <= 300:
            clinic_nodes.add(node)
    dist = nx.multi_source_dijkstra_path_length(G, clinic_nodes, cutoff=15000, weight="length")
    schools = gpd.read_file(ROOT / "data" / "processed" / "schools.gpkg").to_crs(32640)
    rows = []
    for _, row in schools.iterrows():
        node, _ = nearest_node(row.geometry.x, row.geometry.y, xs, ys)
        rows.append({"osm_id": row.get("osm_id"), "name": row.get("name"),
                     "network_distance_m": round(float(dist.get(node, np.nan)), 1)})
    res = pd.DataFrame(rows)
    dst = ROOT / "data" / "analysis" / "schools_network_clinic.csv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(dst, index=False)
    stats["schools_network"] = {
        "within_1000m": int((res["network_distance_m"] <= 1000).sum()),
        "share_within_1000m_pct": round(100 * (res["network_distance_m"] <= 1000).mean(), 1),
        "median_m": round(float(res["network_distance_m"].median()), 1),
    }
    print(stats["schools_network"])
    (CACHE / "iso_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
