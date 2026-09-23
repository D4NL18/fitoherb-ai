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

    def get_route_geometry(self, waypoints: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Retorna GeoJSON com coordenadas curva a curva para renderização no Leaflet.
        """
        if len(waypoints) < 2:
            return {"type": "LineString", "coordinates": []}

        cached = geo_cache.get_polyline(waypoints)
        if cached:
            return cached["geojson"]

        coord_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in waypoints)
        url = f"{self.BASE_URL}/route/v1/driving/{coord_str}?overview=full&geometries=geojson"

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
                        geojson = route["geometry"]
                        duration = route.get("duration", 0)
                        distance = route.get("distance", 0)
                        geo_cache.set_polyline(waypoints, geojson, duration, distance)
                        return geojson
        except Exception as e:
            print(f"[OSRMProvider] Falha ao obter polilinha no OSRM ({e}). Gerando GeoJSON linear.")

        fallback_geojson = {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in waypoints]
        }
        geo_cache.set_polyline(waypoints, fallback_geojson, 0, 0)
        return fallback_geojson

osrm_provider = OSRMProvider()
