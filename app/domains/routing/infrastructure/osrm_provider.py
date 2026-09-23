import json
import math
import sqlite3
import os
import urllib.request
import urllib.parse
from typing import List, Tuple, Dict, Any, Optional
from app.core.config import settings

class GeoCache:
    def __init__(self, db_path: str = "osrm_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS matrix_cache (
                        key TEXT PRIMARY KEY,
                        durations TEXT,
                        distances TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS polyline_cache (
                        key TEXT PRIMARY KEY,
                        geojson TEXT,
                        duration REAL,
                        distance REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        except Exception as e:
            print(f"[GeoCache] Erro ao inicializar SQLite: {e}")

    def _make_key(self, points: List[Tuple[float, float]]) -> str:
        return ";".join(f"{lat:.5f},{lon:.5f}" for lat, lon in points)

    def get_matrix(self, points: List[Tuple[float, float]]) -> Optional[Tuple[List[List[float]], List[List[float]]]]:
        try:
            key = self._make_key(points)
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT durations, distances FROM matrix_cache WHERE key = ?", (key,))
                row = cur.fetchone()
                if row:
                    durations = json.loads(row[0])
                    distances = json.loads(row[1])
                    return durations, distances
        except Exception:
            pass
        return None

    def set_matrix(self, points: List[Tuple[float, float]], durations: List[List[float]], distances: List[List[float]]):
        try:
            key = self._make_key(points)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO matrix_cache (key, durations, distances) VALUES (?, ?, ?)",
                    (key, json.dumps(durations), json.dumps(distances))
                )
        except Exception:
            pass

    def get_polyline(self, waypoints: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
        try:
            key = self._make_key(waypoints)
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT geojson, duration, distance FROM polyline_cache WHERE key = ?", (key,))
                row = cur.fetchone()
                if row:
                    return {
                        "geojson": json.loads(row[0]),
                        "duration": row[1],
                        "distance": row[2]
                    }
        except Exception:
            pass
        return None

    def set_polyline(self, waypoints: List[Tuple[float, float]], geojson: Dict[str, Any], duration: float, distance: float):
        try:
            key = self._make_key(waypoints)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO polyline_cache (key, geojson, duration, distance) VALUES (?, ?, ?, ?)",
                    (key, json.dumps(geojson), duration, distance)
                )
        except Exception:
            pass

geo_cache = GeoCache()

class OSRMProvider:
    BASE_URL = settings.OSRM_BASE_URL

    @staticmethod
    def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_matrix(self, points: List[Tuple[float, float]]) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Retorna (durations_segundos, distances_metros) para todos os N pontos.
        """
        cached = geo_cache.get_matrix(points)
        if cached:
            return cached

        coord_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
        url = f"{self.BASE_URL}/table/v1/driving/{coord_str}?annotations=duration,distance"

        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "Fitoherb-AI-Routing/1.0 (Logistics Optimization; Commercial)"}
            )
            with urllib.request.urlopen(req, timeout=settings.OSRM_TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("code") == "Ok":
                        durations = data["durations"]
                        distances = data["distances"]
                        geo_cache.set_matrix(points, durations, distances)
                        return durations, distances
        except Exception as e:
            print(f"[OSRMProvider] Falha de rede no OSRM ({e}). Acionando estimativa geodésica viária.")

        # Fallback offline resiliente: Haversine com sinuosidade urbana 1.35 e velocidade média 35 km/h
        n = len(points)
        durations = [[0.0] * n for _ in range(n)]
        distances = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = points[i]
                    lat2, lon2 = points[j]
                    dist_km = self._haversine_distance_km(lat1, lon1, lat2, lon2) * 1.35
                    dist_m = dist_km * 1000.0
                    duration_sec = (dist_km / 35.0) * 3600.0
                    distances[i][j] = round(dist_m, 1)
                    durations[i][j] = round(duration_sec, 1)

        geo_cache.set_matrix(points, durations, distances)
        return durations, distances

    ROUTE_LEG_COLORS = [
        "#2563eb",  # Trecho 1: Azul Real Vibrante
        "#d97706",  # Trecho 2: Âmbar / Laranja
        "#7c3aed",  # Trecho 3: Violeta / Roxo
        "#059669",  # Trecho 4: Verde Esmeralda
        "#dc2626",  # Trecho 5: Vermelho Carmim
        "#0891b2",  # Trecho 6: Azul Petróleo / Ciano
        "#ea580c",  # Trecho 7: Laranja Queimado
        "#4f46e5",  # Trecho 8: Índigo
        "#c026d3",  # Trecho 9: Magenta
        "#0d9488",  # Trecho 10: Teal
        "#65a30d",  # Trecho 11: Verde Lima
        "#475569"   # Trecho Retorno à Base: Ardósia
    ]

    def get_route_geometry(self, waypoints: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Retorna GeoJSON FeatureCollection com coordenadas curva a curva particionadas por trecho (leg),
        cada um com sua cor característica para identificação e destaque visual interativo.
        """
        if len(waypoints) < 2:
            return {"type": "FeatureCollection", "features": [], "coordinates": []}

        cached = geo_cache.get_polyline(waypoints)
        if cached:
            return cached["geojson"]

        coord_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in waypoints)
        url = f"{self.BASE_URL}/route/v1/driving/{coord_str}?overview=full&geometries=geojson&steps=true"

        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "Fitoherb-AI-Routing/1.0 (Logistics Optimization; Commercial)"}
            )
            with urllib.request.urlopen(req, timeout=settings.OSRM_TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("code") == "Ok" and len(data.get("routes", [])) > 0:
                        route = data["routes"][0]
                        duration = route.get("duration", 0)
                        distance = route.get("distance", 0)

                        legs = route.get("legs", [])
                        features = []
                        all_coords = []

                        for leg_idx, leg in enumerate(legs):
                            leg_coords = []
                            for step in leg.get("steps", []):
                                c = step.get("geometry", {}).get("coordinates", [])
                                if not leg_coords:
                                    leg_coords.extend(c)
                                else:
                                    if c and c[0] == leg_coords[-1]:
                                        leg_coords.extend(c[1:])
                                    else:
                                        leg_coords.extend(c)

                            # Fallback de segurança se os steps não contiverem geometria
                            if not leg_coords and leg_idx < len(waypoints) - 1:
                                p1 = waypoints[leg_idx]
                                p2 = waypoints[leg_idx + 1]
                                leg_coords = [[p1[1], p1[0]], [p2[1], p2[0]]]

                            all_coords.extend(leg_coords)
                            color = self.ROUTE_LEG_COLORS[leg_idx % len(self.ROUTE_LEG_COLORS)]

                            features.append({
                                "type": "Feature",
                                "properties": {
                                    "leg_index": leg_idx,
                                    "from_step": leg_idx,
                                    "to_step": leg_idx + 1,
                                    "color": color,
                                    "distance_m": leg.get("distance", 0),
                                    "duration_sec": leg.get("duration", 0)
                                },
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": leg_coords
                                }
                            })

                        geojson_result = {
                            "type": "FeatureCollection",
                            "features": features,
                            "coordinates": all_coords
                        }

                        geo_cache.set_polyline(waypoints, geojson_result, duration, distance)
                        return geojson_result
        except Exception as e:
            print(f"[OSRMProvider] Falha ao obter polilinha no OSRM ({e}). Gerando GeoJSON linear.")

        # Fallback offline resiliente: linha reta entre cada waypoint consecutivo com sua cor
        features = []
        all_coords = []
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            seg_coords = [[p1[1], p1[0]], [p2[1], p2[0]]]
            all_coords.extend(seg_coords)
            color = self.ROUTE_LEG_COLORS[i % len(self.ROUTE_LEG_COLORS)]
            features.append({
                "type": "Feature",
                "properties": {
                    "leg_index": i,
                    "from_step": i,
                    "to_step": i + 1,
                    "color": color,
                    "distance_m": self._haversine_distance_km(p1[0], p1[1], p2[0], p2[1]) * 1350.0,
                    "duration_sec": (self._haversine_distance_km(p1[0], p1[1], p2[0], p2[1]) * 1.35 / 35.0) * 3600.0
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": seg_coords
                }
            })

        fallback_geojson = {
            "type": "FeatureCollection",
            "features": features,
            "coordinates": all_coords
        }
        geo_cache.set_polyline(waypoints, fallback_geojson, 0, 0)
        return fallback_geojson

osrm_provider = OSRMProvider()
