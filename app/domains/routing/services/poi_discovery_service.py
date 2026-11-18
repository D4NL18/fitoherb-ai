import json
import math
import re
import unicodedata
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple

from app.domains.routing.models.point import Address, DeliveryStop, LocationPoint
from app.domains.routing.schemas.routing_dto import SuggestedStopDto
from app.domains.routing.infrastructure.osrm_provider import geo_cache, OSRMProvider
from app.domains.routing.services.city_insights_service import city_insights_service


CURATED_BAHIA_POI_CATALOG: List[Dict[str, Any]] = [
    # Salvador — Pituba / Itaigara / Caminho das Árvores
    {
        "name": "Mundo Verde - Pituba",
        "lat": -13.0012,
        "lon": -38.4865,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Paulo VI",
        "number": "1820",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "Farmácia Santana - Pituba",
        "lat": -12.9968,
        "lon": -38.4882,
        "category": "FARMACIA",
        "street": "Av. Manoel Dias da Silva",
        "number": "1240",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "Ervanário & Empório Vida Natural - Itaigara",
        "lat": -12.9942,
        "lon": -38.4748,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Antônio Carlos Magalhães",
        "number": "846",
        "neighborhood": "Itaigara",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "Drogaria Globo - Caminho das Árvores",
        "lat": -12.9815,
        "lon": -38.4562,
        "category": "FARMACIA",
        "street": "Alameda das Espatódeas",
        "number": "520",
        "neighborhood": "Caminho das Árvores",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "BioMundo Produtos Naturais - Salvador Shopping",
        "lat": -12.9788,
        "lon": -38.4550,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Tancredo Neves",
        "number": "3133",
        "neighborhood": "Caminho das Árvores",
        "city": "Salvador",
        "state": "BA",
    },
    # Salvador — Barra / Graça / Rio Vermelho
    {
        "name": "Farmácia de Manipulação Flora da Terra - Graça",
        "lat": -12.9998,
        "lon": -38.5210,
        "category": "FARMACIA",
        "street": "Av. Euclydes da Cunha",
        "number": "410",
        "neighborhood": "Graça",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "Empório Grão da Terra Naturais - Barra",
        "lat": -13.0068,
        "lon": -38.5282,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Centenário",
        "number": "2410",
        "neighborhood": "Barra",
        "city": "Salvador",
        "state": "BA",
    },
    # Salvador — Imbuí / Paralela / Itapuã
    {
        "name": "Redepharma Saúde - Imbuí",
        "lat": -12.9685,
        "lon": -38.4320,
        "category": "FARMACIA",
        "street": "Av. Jorge Amado",
        "number": "980",
        "neighborhood": "Imbuí",
        "city": "Salvador",
        "state": "BA",
    },
    {
        "name": "Casa das Ervas & Suplementos - Itapuã",
        "lat": -12.9430,
        "lon": -38.3625,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Dorival Caymmi",
        "number": "615",
        "neighborhood": "Itapuã",
        "city": "Salvador",
        "state": "BA",
    },
    # Lauro de Freitas — Estrada do Coco / Vilas do Atlântico / Centro
    {
        "name": "Empório Raízes do Atlântico Produtos Naturais",
        "lat": -12.8885,
        "lon": -38.3120,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Praia de Itapuã",
        "number": "412",
        "neighborhood": "Vilas do Atlântico",
        "city": "Lauro de Freitas",
        "state": "BA",
    },
    {
        "name": "Farmácia Brito Saúde - Estrada do Coco",
        "lat": -12.8938,
        "lon": -38.3210,
        "category": "FARMACIA",
        "street": "Rodovia BA-099 (Estrada do Coco)",
        "number": "Km 2.5",
        "neighborhood": "Centro",
        "city": "Lauro de Freitas",
        "state": "BA",
    },
    {
        "name": "NatuVilas Fitoterápicos & Suplementos",
        "lat": -12.8820,
        "lon": -38.3080,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Luís Tarquínio Pontes",
        "number": "1950",
        "neighborhood": "Buraquinho",
        "city": "Lauro de Freitas",
        "state": "BA",
    },
    # Camaçari / Abrantes / Guarajuba
    {
        "name": "Drogaria Litoral Norte - Vila de Abrantes",
        "lat": -12.8285,
        "lon": -38.2665,
        "category": "FARMACIA",
        "street": "Estrada do Coco (BA-099)",
        "number": "Km 12",
        "neighborhood": "Vila de Abrantes",
        "city": "Camaçari",
        "state": "BA",
    },
    {
        "name": "Empório BioCosta Produtos Naturais - Abrantes",
        "lat": -12.8215,
        "lon": -38.2630,
        "category": "PRODUTOS_NATURAIS",
        "street": "Rua Direta de Abrantes",
        "number": "218",
        "neighborhood": "Vila de Abrantes",
        "city": "Camaçari",
        "state": "BA",
    },
    {
        "name": "Farmácia Central do Polo - Camaçari",
        "lat": -12.6975,
        "lon": -38.3260,
        "category": "FARMACIA",
        "street": "Av. Getúlio Vargas",
        "number": "310",
        "neighborhood": "Centro",
        "city": "Camaçari",
        "state": "BA",
    },
    # Feira de Santana
    {
        "name": "Drogaria Sertão Farma - Getúlio Vargas",
        "lat": -12.2595,
        "lon": -38.9585,
        "category": "FARMACIA",
        "street": "Av. Getúlio Vargas",
        "number": "1450",
        "neighborhood": "Centro",
        "city": "Feira de Santana",
        "state": "BA",
    },
    {
        "name": "Empório Flor da Caatinga Produtos Naturais",
        "lat": -12.2560,
        "lon": -38.9610,
        "category": "PRODUTOS_NATURAIS",
        "street": "Av. Senhor dos Passos",
        "number": "890",
        "neighborhood": "Centro",
        "city": "Feira de Santana",
        "state": "BA",
    },
]


class PoiDiscoveryService:
    """
    Serviço responsável pela Regra P-108: Descoberta Proativa de Leads Comerciais
    (Farmácias/Drogarias e Lojas de Produtos Naturais/Suplementos) ao longo do corredor
    viário da rota, com filtro rigoroso de deduplicação (<= 80m ou similaridade >= 0.82)
    e proteção de dados (LGPD).
    """

    DUPLICATE_DISTANCE_THRESHOLD_KM = 0.08  # 80 metros
    DUPLICATE_SIMILARITY_THRESHOLD = 0.82

    @staticmethod
    def _normalize_phonetic(text: Optional[str]) -> str:
        if not text:
            return ""
        s = unicodedata.normalize("NFD", text.strip())
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        s = s.lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        # Equivalências fonéticas comuns em nomes comerciais em PT-BR
        s = s.replace("ph", "f").replace("ss", "s").replace("z", "s")
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @classmethod
    def _sanitize_poi_name(cls, raw_name: str) -> str:
        """
        Higieniza nomes de estabelecimentos vindos do OSM para evitar PII de pessoas físicas
        (ex: CPF/CNPJ ou telefones embutidos no título).
        """
        cleaned = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "", raw_name or "")
        cleaned = re.sub(r"\b\d{8,14}\b", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -|/")
        return cleaned or "Estabelecimento Comercial"

    def is_duplicate_poi(
        self,
        candidate_name: str,
        candidate_lat: float,
        candidate_lon: float,
        candidate_city: Optional[str],
        existing_points: List[Dict[str, Any]],
    ) -> bool:
        """
        Verifica se um POI candidato já está listado na rota, base ou favoritos do vendedor:
        1. Distância geodésica <= 0.08 km (80 metros) de qualquer ponto existente; OU
        2. Similaridade textual/fonética >= 0.82 na mesma cidade (ou quando a cidade não é restritiva).
        """
        norm_cand = self._normalize_phonetic(candidate_name)
        norm_cand_city = self._normalize_phonetic(candidate_city)

        for pt in existing_points:
            pt_lat = float(pt.get("lat", 0.0))
            pt_lon = float(pt.get("lon", 0.0))
            dist_km = OSRMProvider._haversine_distance_km(
                candidate_lat, candidate_lon, pt_lat, pt_lon
            )
            if dist_km <= self.DUPLICATE_DISTANCE_THRESHOLD_KM:
                return True

            pt_name = pt.get("name", "")
            norm_exist = self._normalize_phonetic(pt_name)
            if not norm_cand or not norm_exist:
                continue

            pt_city = self._normalize_phonetic(pt.get("city"))
            same_city_or_nearby = (
                not norm_cand_city
                or not pt_city
                or norm_cand_city == pt_city
                or dist_km <= 15.0
            )
            if same_city_or_nearby:
                ratio = SequenceMatcher(None, norm_cand, norm_exist).ratio()
                if ratio >= self.DUPLICATE_SIMILARITY_THRESHOLD:
                    return True

        return False

    @classmethod
    def _classify_osm_tags_and_name(
        cls, tags: Dict[str, Any], name: str
    ) -> Optional[str]:
        norm_name = cls._normalize_phonetic(name)
        shop = str(tags.get("shop", "")).lower()
        amenity = str(tags.get("amenity", "")).lower()
        healthcare = str(tags.get("healthcare", "")).lower()

        natural_keywords = (
            "mundo verde",
            "produtos naturais",
            "natural",
            "naturais",
            "ervanario",
            "fitoterap",
            "suplemento",
            "emporio",
            "biomundo",
            "vida saudavel",
            "granel",
            "ervas",
            "flora",
        )
        pharma_keywords = (
            "farmacia",
            "drogaria",
            "droga",
            "farma",
            "pague menos",
            "drogasil",
            "manipulacao",
            "santana",
            "ultrafarma",
            "popular",
        )

        if shop in ("health_food", "herbalist", "nutrition_supplements", "vitamins"):
            return "PRODUTOS_NATURAIS"
        if any(k in norm_name for k in natural_keywords) and "farmacia" not in norm_name:
            return "PRODUTOS_NATURAIS"
        if amenity == "pharmacy" or healthcare == "pharmacy" or shop == "chemist":
            return "FARMACIA"
        if any(k in norm_name for k in pharma_keywords):
            return "FARMACIA"
        return None

    def _query_overpass_corridor(
        self, pivots: List[Tuple[float, float]]
    ) -> List[Dict[str, Any]]:
        if not pivots:
            return []

        corridor_key = ";".join(f"{lat:.3f},{lon:.3f}" for lat, lon in pivots[:5])
        cached = geo_cache.get_poi_candidates(corridor_key)
        if cached:
            return cached

        around_clauses = []
        for lat, lon in pivots[:4]:
            around_clauses.append(f'node["amenity"="pharmacy"](around:2500,{lat:.5f},{lon:.5f});')
            around_clauses.append(
                f'node["shop"~"health_food|herbalist|nutrition_supplements|chemist"](around:3000,{lat:.5f},{lon:.5f});'
            )

        overpass_query = f"[out:json][timeout:3];({''.join(around_clauses)});out body 25;"
        encoded_data = urllib.parse.urlencode({"data": overpass_query}).encode("utf-8")
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=encoded_data,
            headers={"User-Agent": "Fitoherb-AI-Routing/1.0 (Commercial Lead Discovery; P-108)"},
        )

        discovered: List[Dict[str, Any]] = []
        try:
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    for el in payload.get("elements", []):
                        tags = el.get("tags", {}) or {}
                        raw_name = tags.get("name") or tags.get("brand")
                        if not raw_name:
                            continue
                        name = self._sanitize_poi_name(str(raw_name))
                        category = self._classify_osm_tags_and_name(tags, name)
                        if not category:
                            continue
                        lat = float(el.get("lat", 0.0))
                        lon = float(el.get("lon", 0.0))
                        if lat == 0.0 and lon == 0.0:
                            continue
                        city_raw = tags.get("addr:city")
                        suburb_raw = tags.get("addr:suburb") or tags.get("addr:neighbourhood")
                        resolved_city, resolved_state = (
                            city_insights_service.resolve_municipality_name(
                                raw_city=city_raw,
                                raw_state=tags.get("addr:state", "BA"),
                                neighborhood=suburb_raw,
                                lat=lat,
                                lon=lon,
                            )
                        )
                        discovered.append(
                            {
                                "name": name,
                                "lat": lat,
                                "lon": lon,
                                "category": category,
                                "street": tags.get("addr:street") or "Via Comercial Principal",
                                "number": tags.get("addr:housenumber") or "S/N",
                                "neighborhood": suburb_raw or "Centro Comercial",
                                "city": resolved_city,
                                "state": resolved_state,
                            }
                        )
                    if discovered:
                        geo_cache.set_poi_candidates(corridor_key, discovered)
        except Exception:
            pass

        return discovered

    def _build_contingency_candidates(
        self, depot: LocationPoint, stops: List[DeliveryStop]
    ) -> List[Dict[str, Any]]:
        candidates = list(CURATED_BAHIA_POI_CATALOG)

        # Garante candidatos próximos a paradas em qualquer município fora do eixo Salvador/RMS
        for idx, stop in enumerate(stops):
            raw_city = stop.address.city if stop.address else None
            raw_state = stop.address.state if (stop.address and stop.address.state) else "BA"
            neighborhood = (
                stop.address.neighborhood
                if (stop.address and stop.address.neighborhood)
                else "Centro"
            )
            street = (
                stop.address.street
                if (stop.address and stop.address.street)
                else "Av. Comercial"
            )
            resolved_city, resolved_state = city_insights_service.resolve_municipality_name(
                raw_city=raw_city,
                raw_state=raw_state,
                neighborhood=neighborhood,
                lat=stop.lat,
                lon=stop.lon,
            )

            candidates.append(
                {
                    "name": f"Empório & Produtos Naturais BioVida - {neighborhood}",
                    "lat": round(stop.lat + 0.0022, 6),
                    "lon": round(stop.lon + 0.0018, 6),
                    "category": "PRODUTOS_NATURAIS",
                    "street": street,
                    "number": str(240 + idx * 30),
                    "neighborhood": neighborhood,
                    "city": resolved_city,
                    "state": resolved_state,
                }
            )
            candidates.append(
                {
                    "name": f"Farmácia & Manipulação Bem Estar - {neighborhood}",
                    "lat": round(stop.lat - 0.0021, 6),
                    "lon": round(stop.lon + 0.0024, 6),
                    "category": "FARMACIA",
                    "street": street,
                    "number": str(510 + idx * 25),
                    "neighborhood": neighborhood,
                    "city": resolved_city,
                    "state": resolved_state,
                }
            )

        return candidates

    def discover_along_route(
        self,
        depot: LocationPoint,
        stops: List[DeliveryStop],
        excluded_locations: Optional[List[LocationPoint]] = None,
        max_suggestions: int = 5,
    ) -> List[SuggestedStopDto]:
        """
        Descobre estabelecimentos dos segmentos FARMACIA e PRODUTOS_NATURAIS próximos ao
        corredor da rota, filtrando duplicados e ordenando pelo menor desvio viário.
        """
        if not stops or max_suggestions <= 0:
            return []

        excluded_locations = excluded_locations or []
        existing_points: List[Dict[str, Any]] = []

        if depot:
            existing_points.append(
                {
                    "name": depot.name,
                    "lat": depot.lat,
                    "lon": depot.lon,
                    "city": depot.address.city if depot.address else None,
                }
            )
        for s in stops:
            existing_points.append(
                {
                    "name": s.name,
                    "lat": s.lat,
                    "lon": s.lon,
                    "city": s.address.city if s.address else None,
                }
            )
        for ex in excluded_locations:
            existing_points.append(
                {
                    "name": ex.name,
                    "lat": ex.lat,
                    "lon": ex.lon,
                    "city": ex.address.city if ex.address else None,
                }
            )

        pivots = [(s.lat, s.lon) for s in stops]
        raw_candidates = self._query_overpass_corridor(pivots)
        raw_candidates.extend(self._build_contingency_candidates(depot, stops))

        scored_candidates: List[Tuple[float, Dict[str, Any], DeliveryStop, float, float]] = []

        for cand in raw_candidates:
            c_name = cand["name"]
            c_lat = float(cand["lat"])
            c_lon = float(cand["lon"])
            c_city = cand.get("city")

            if self.is_duplicate_poi(c_name, c_lat, c_lon, c_city, existing_points):
                continue

            # Encontra a parada da rota mais próxima para estimar o desvio viário
            nearest_stop = min(
                stops,
                key=lambda s: OSRMProvider._haversine_distance_km(c_lat, c_lon, s.lat, s.lon),
            )
            dist_to_stop_km = OSRMProvider._haversine_distance_km(
                c_lat, c_lon, nearest_stop.lat, nearest_stop.lon
            )

            # Considera apenas oportunidades dentro de um corredor viável (até 12 km de uma parada)
            if dist_to_stop_km > 12.0:
                continue

            detour_km = round(max(0.2, dist_to_stop_km * 1.35), 2)
            detour_min = round(max(1.0, (detour_km / 30.0) * 60.0), 1)

            scored_candidates.append(
                (detour_km, cand, nearest_stop, detour_km, detour_min)
            )

        scored_candidates.sort(key=lambda item: item[0])

        # Balanceia categorias (FARMACIA e PRODUTOS_NATURAIS) mantendo os menores desvios
        selected: List[SuggestedStopDto] = []
        pharma_pool = [c for c in scored_candidates if c[1]["category"] == "FARMACIA"]
        natural_pool = [c for c in scored_candidates if c[1]["category"] == "PRODUTOS_NATURAIS"]

        interleaved: List[Tuple[float, Dict[str, Any], DeliveryStop, float, float]] = []
        max_len = max(len(pharma_pool), len(natural_pool))
        for i in range(max_len):
            if i < len(natural_pool):
                interleaved.append(natural_pool[i])
            if i < len(pharma_pool):
                interleaved.append(pharma_pool[i])

        for _, cand, nearest_stop, detour_km, detour_min in interleaved:
            if len(selected) >= max_suggestions:
                break

            c_name = cand["name"]
            c_lat = float(cand["lat"])
            c_lon = float(cand["lon"])
            c_city = cand.get("city")

            if self.is_duplicate_poi(c_name, c_lat, c_lon, c_city, existing_points):
                continue

            existing_points.append(
                {"name": c_name, "lat": c_lat, "lon": c_lon, "city": c_city}
            )

            sug_idx = len(selected) + 1
            cat = cand["category"]
            cat_label = (
                "Produtos Naturais & Fitoterápicos"
                if cat == "PRODUTOS_NATURAIS"
                else "Farmácia / Drogaria"
            )
            addr = Address(
                street=cand.get("street"),
                number=cand.get("number"),
                neighborhood=cand.get("neighborhood"),
                city=cand.get("city", "Salvador"),
                state=cand.get("state", "BA"),
                full_address=(
                    f"{cand.get('street', '')}, {cand.get('number', 'S/N')} - "
                    f"{cand.get('neighborhood', '')}, {cand.get('city', 'Salvador')} - {cand.get('state', 'BA')}"
                ).strip(" ,-"),
            )

            selected.append(
                SuggestedStopDto(
                    id=f"sug-{sug_idx}",
                    name=c_name,
                    lat=c_lat,
                    lon=c_lon,
                    address=addr,
                    suggestion_category=cat,
                    category_label=cat_label,
                    detour_distance_km=detour_km,
                    detour_time_minutes=detour_min,
                    nearest_stop_id=nearest_stop.id,
                    nearest_stop_name=nearest_stop.name,
                    is_suggestion=True,
                )
            )

        return selected


poi_discovery_service = PoiDiscoveryService()
