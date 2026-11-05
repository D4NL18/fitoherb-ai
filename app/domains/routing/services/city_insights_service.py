import json
import math
import unicodedata
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

from app.domains.routing.models.point import LocationPoint
from app.domains.routing.schemas.routing_dto import (
    CityInsightDto,
    OrderedStopDto,
    SuggestedStopDto,
)
from app.domains.routing.traffic_model import CityTier, TrafficPredictor
from app.domains.routing.infrastructure.osrm_provider import geo_cache


DISTRICT_TO_MUNICIPALITY_MAP: Dict[str, Tuple[str, str]] = {
    "abrantes": ("Camaçari", "BA"),
    "vila de abrantes": ("Camaçari", "BA"),
    "arembepe": ("Camaçari", "BA"),
    "guarajuba": ("Camaçari", "BA"),
    "itacimirim": ("Camaçari", "BA"),
    "monte gordo": ("Camaçari", "BA"),
    "barra do jacuipe": ("Camaçari", "BA"),
    "jacuipe": ("Camaçari", "BA"),
    "barra do pojuca": ("Camaçari", "BA"),
    "parafuso": ("Camaçari", "BA"),
    "itinga": ("Lauro de Freitas", "BA"),
    "vilas do atlantico": ("Lauro de Freitas", "BA"),
    "villas do atlantico": ("Lauro de Freitas", "BA"),
    "buraquinho": ("Lauro de Freitas", "BA"),
    "portao": ("Lauro de Freitas", "BA"),
    "pitangueiras": ("Lauro de Freitas", "BA"),
    "vida nova": ("Lauro de Freitas", "BA"),
    "caji": ("Lauro de Freitas", "BA"),
    "pituba": ("Salvador", "BA"),
    "itaigara": ("Salvador", "BA"),
    "caminho das arvores": ("Salvador", "BA"),
    "barra": ("Salvador", "BA"),
    "ondina": ("Salvador", "BA"),
    "rio vermelho": ("Salvador", "BA"),
    "itapua": ("Salvador", "BA"),
    "cajazeiras": ("Salvador", "BA"),
    "cabula": ("Salvador", "BA"),
    "imbui": ("Salvador", "BA"),
    "stiep": ("Salvador", "BA"),
    "brotas": ("Salvador", "BA"),
    "graca": ("Salvador", "BA"),
    "federacao": ("Salvador", "BA"),
    "calçada": ("Salvador", "BA"),
    "calcada": ("Salvador", "BA"),
    "paripe": ("Salvador", "BA"),
    "periperi": ("Salvador", "BA"),
    "praia do forte": ("Mata de São João", "BA"),
    "imbassai": ("Mata de São João", "BA"),
    "sauipe": ("Mata de São João", "BA"),
    "costa do sauipe": ("Mata de São João", "BA"),
    "diogo": ("Mata de São João", "BA"),
    "humildes": ("Feira de Santana", "BA"),
    "maria quiteria": ("Feira de Santana", "BA"),
    "arraial d'ajuda": ("Porto Seguro", "BA"),
    "arraial dajuda": ("Porto Seguro", "BA"),
    "trancoso": ("Porto Seguro", "BA"),
    "caraiva": ("Porto Seguro", "BA"),
}

CITY_TIER_LABELS: Dict[str, str] = {
    CityTier.METROPOLIS: "Metrópole (> 1M hab)",
    CityTier.REGIONAL_HUB: "Polo Regional (200k–1M hab)",
    CityTier.MEDIUM_CITY: "Cidade Média (70k–200k hab)",
    CityTier.SMALL_TOWN: "Pequeno Porte (< 70k hab)",
}

CURATED_MUNICIPALITIES_DB: Dict[str, Dict[str, Any]] = {
    "salvador": {
        "city": "Salvador",
        "state": "BA",
        "ibge_code": "2927408",
        "population": 2417678,
        "city_tier": CityTier.METROPOLIS,
        "demographic_density_hab_km2": 3486.5,
        "gdp_per_capita_brl": 27540.0,
        "regional_hub_name": "Capital / Região Metropolitana de Salvador (RMS)",
        "commercial_potential_summary": (
            "Altíssima densidade de redes farmacêuticas, drogarias independentes e empórios de vida saudável. "
            "Priorizar mix completo Fitoherb, linha de suplementos de alto giro e exposição em ponta de gôndola."
        ),
        "coords": (-12.9714, -38.5014),
    },
    "lauro de freitas": {
        "city": "Lauro de Freitas",
        "state": "BA",
        "ibge_code": "2919207",
        "population": 203331,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 3526.8,
        "gdp_per_capita_brl": 34120.0,
        "regional_hub_name": "Região Metropolitana de Salvador (Eixo Estrada do Coco)",
        "commercial_potential_summary": (
            "Sede operacional Fitoherb com elevado poder aquisitivo (Vilas do Atlântico, Buraquinho e Estrada do Coco). "
            "Forte demanda por fitoterápicos premium, suplementação esportiva, chás funcionais e farmácias de manipulação."
        ),
        "coords": (-12.8944, -38.3275),
    },
    "camacari": {
        "city": "Camaçari",
        "state": "BA",
        "ibge_code": "2905701",
        "population": 300372,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 382.4,
        "gdp_per_capita_brl": 89450.0,
        "regional_hub_name": "Polo Industrial e Orla Norte (Abrantes / Guarajuba)",
        "commercial_potential_summary": (
            "Mercado estratégico duplo: alto volume de trabalhadores no Centro/Polo Industrial e público de alta renda "
            "nos condomínios da Orla (Vila de Abrantes, Busca Vida e Guarajuba). Combinar linha popular e linha natural premium."
        ),
        "coords": (-12.6997, -38.3242),
    },
    "feira de santana": {
        "city": "Feira de Santana",
        "state": "BA",
        "ibge_code": "2910800",
        "population": 616272,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 460.6,
        "gdp_per_capita_brl": 28910.0,
        "regional_hub_name": "Portal do Sertão / Maior Entroncamento Rodoviário do Interior",
        "commercial_potential_summary": (
            "Principal polo atacadista e varejista do interior baiano. Excelente praça para pedidos de maior volume "
            "em redes regionais de farmácias, distribuidoras e lojas de produtos naturais do centro comercial."
        ),
        "coords": (-12.2664, -38.9663),
    },
    "simoes filho": {
        "city": "Simões Filho",
        "state": "BA",
        "ibge_code": "2930709",
        "population": 114559,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 568.9,
        "gdp_per_capita_brl": 52300.0,
        "regional_hub_name": "Região Metropolitana de Salvador (Eixo CIA-Aeroporto)",
        "commercial_potential_summary": (
            "Polo logístico e industrial com forte fluxo em drogarias de bairro e comércio central. "
            "Alta conversão em polivitamínicos, xaropes fitoterápicos, imunidade e energéticos naturais."
        ),
        "coords": (-12.7866, -38.4039),
    },
    "candeias": {
        "city": "Candeias",
        "state": "BA",
        "ibge_code": "2906501",
        "population": 72382,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 280.1,
        "gdp_per_capita_brl": 48100.0,
        "regional_hub_name": "Recôncavo Metropolitano / Polo Petroquímico",
        "commercial_potential_summary": (
            "Comércio central adensado com forte giro em farmácias independentes; priorizar linha de imunidade, "
            "extratos fluidos, chás medicinais e suplementos de venda recorrente."
        ),
        "coords": (-12.6675, -38.5506),
    },
    "dias davila": {
        "city": "Dias d'Ávila",
        "state": "BA",
        "ibge_code": "2910057",
        "population": 71485,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 388.2,
        "gdp_per_capita_brl": 41200.0,
        "regional_hub_name": "Região Metropolitana de Salvador (Polo das Águas)",
        "commercial_potential_summary": (
            "Eixo residencial e industrial em expansão; trabalhar reposição contínua em drogarias locais "
            "e lojas de suplementos e produtos naturais."
        ),
        "coords": (-12.6133, -38.2972),
    },
    "mata de sao joao": {
        "city": "Mata de São João",
        "state": "BA",
        "ibge_code": "2921005",
        "population": 42566,
        "city_tier": CityTier.SMALL_TOWN,
        "demographic_density_hab_km2": 67.2,
        "gdp_per_capita_brl": 31500.0,
        "regional_hub_name": "Litoral Norte / Costa dos Coqueiros",
        "commercial_potential_summary": (
            "Praça com forte vocação turística na orla (Praia do Forte / Imbassaí) e comércio tradicional na sede; "
            "destacar linha natural de bem-estar no litoral e fitoterápicos essenciais no centro."
        ),
        "coords": (-12.5303, -38.2992),
    },
    "alagoinhas": {
        "city": "Alagoinhas",
        "state": "BA",
        "ibge_code": "2900702",
        "population": 151055,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 203.8,
        "gdp_per_capita_brl": 26400.0,
        "regional_hub_name": "Litoral Norte e Agreste Baiano",
        "commercial_potential_summary": (
            "Polo comercial sub-regional com forte presença de farmácias independentes e ervanários; "
            "foco em ampliação de mix e fidelização quinzenal."
        ),
        "coords": (-12.1336, -38.4192),
    },
    "vitoria da conquista": {
        "city": "Vitória da Conquista",
        "state": "BA",
        "ibge_code": "2933307",
        "population": 370879,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 113.9,
        "gdp_per_capita_brl": 24800.0,
        "regional_hub_name": "Sudoeste Baiano",
        "commercial_potential_summary": (
            "Hub médico e universitário do Sudoeste; clima de altitude favorece alto giro em própolis, "
            "xaropes respiratórios, chás medicinais e suplementos imunológicos."
        ),
        "coords": (-14.8619, -40.8444),
    },
    "itabuna": {
        "city": "Itabuna",
        "state": "BA",
        "ibge_code": "2914802",
        "population": 186708,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 465.4,
        "gdp_per_capita_brl": 23900.0,
        "regional_hub_name": "Sul Baiano / Eixo Cacaueiro",
        "commercial_potential_summary": (
            "Centro de serviços e saúde do Sul da Bahia; forte atuação de redes regionais de drogarias "
            "e empórios de produtos naturais."
        ),
        "coords": (-14.7876, -39.2781),
    },
    "ilheus": {
        "city": "Ilhéus",
        "state": "BA",
        "ibge_code": "2913606",
        "population": 178649,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 112.5,
        "gdp_per_capita_brl": 27300.0,
        "regional_hub_name": "Litoral Sul / Costa do Cacau",
        "commercial_potential_summary": (
            "Demanda aquecida por produtos naturais, encapsulados e fitoterápicos em drogarias e empórios da zona central e sul."
        ),
        "coords": (-14.7936, -39.0464),
    },
    "porto seguro": {
        "city": "Porto Seguro",
        "state": "BA",
        "ibge_code": "2925303",
        "population": 168326,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 73.6,
        "gdp_per_capita_brl": 25100.0,
        "regional_hub_name": "Costa do Descobrimento / Extremo Sul",
        "commercial_potential_summary": (
            "Forte fluxo turístico e comércio de saúde ativo o ano inteiro; excelente giro para suplementos, "
            "hidratantes/protetores naturais e fitoterápicos."
        ),
        "coords": (-16.4497, -39.0647),
    },
    "jequie": {
        "city": "Jequié",
        "state": "BA",
        "ibge_code": "2918001",
        "population": 158813,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 52.3,
        "gdp_per_capita_brl": 21500.0,
        "regional_hub_name": "Médio Rio de Contas",
        "commercial_potential_summary": (
            "Comércio regional consolidado com forte aceitação da linha tradicional de fitoterápicos e produtos naturais Fitoherb."
        ),
        "coords": (-13.8586, -40.0836),
    },
    "barreiras": {
        "city": "Barreiras",
        "state": "BA",
        "ibge_code": "2903201",
        "population": 159734,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 20.3,
        "gdp_per_capita_brl": 46800.0,
        "regional_hub_name": "Oeste Baiano / Polo Agroindustrial",
        "commercial_potential_summary": (
            "Alto PIB per capita impulsionado pelo agronegócio; excelente ticket médio para suplementos e linha premium."
        ),
        "coords": (-12.1528, -44.9900),
    },
    "teixeira de freitas": {
        "city": "Teixeira de Freitas",
        "state": "BA",
        "ibge_code": "2931350",
        "population": 145216,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 124.8,
        "gdp_per_capita_brl": 22400.0,
        "regional_hub_name": "Extremo Sul Baiano",
        "commercial_potential_summary": (
            "Polo médico e varejista do Extremo Sul; alto potencial em redes de drogarias e casas de produtos naturais."
        ),
        "coords": (-17.5350, -39.7419),
    },
    "santo antonio de jesus": {
        "city": "Santo Antônio de Jesus",
        "state": "BA",
        "ibge_code": "2928703",
        "population": 103055,
        "city_tier": CityTier.MEDIUM_CITY,
        "demographic_density_hab_km2": 393.8,
        "gdp_per_capita_brl": 26900.0,
        "regional_hub_name": "Recôncavo Sul",
        "commercial_potential_summary": (
            "Comércio mais dinâmico do Recôncavo; forte presença de drogarias independentes e lojas de suplementos."
        ),
        "coords": (-12.9689, -39.2614),
    },
    "pojuca": {
        "city": "Pojuca",
        "state": "BA",
        "ibge_code": "2925204",
        "population": 32136,
        "city_tier": CityTier.SMALL_TOWN,
        "demographic_density_hab_km2": 110.8,
        "gdp_per_capita_brl": 34500.0,
        "regional_hub_name": "Região Metropolitana / Agreste",
        "commercial_potential_summary": (
            "Praça de relacionamento próximo com farmácias locais; priorizar itens campeões de venda Fitoherb."
        ),
        "coords": (-12.4306, -38.3278),
    },
    "madre de deus": {
        "city": "Madre de Deus",
        "state": "BA",
        "ibge_code": "2919926",
        "population": 18504,
        "city_tier": CityTier.SMALL_TOWN,
        "demographic_density_hab_km2": 574.6,
        "gdp_per_capita_brl": 29400.0,
        "regional_hub_name": "Baía de Todos-os-Santos / RMS",
        "commercial_potential_summary": (
            "Alta densidade urbana; foco em drogarias centrais e reposição rápida de fitoterápicos."
        ),
        "coords": (-12.7408, -38.6208),
    },
    "sao francisco do conde": {
        "city": "São Francisco do Conde",
        "state": "BA",
        "ibge_code": "2929206",
        "population": 37732,
        "city_tier": CityTier.SMALL_TOWN,
        "demographic_density_hab_km2": 142.3,
        "gdp_per_capita_brl": 195000.0,
        "regional_hub_name": "Recôncavo / RMS",
        "commercial_potential_summary": (
            "Município do Recôncavo com demanda concentrada em farmácias tradicionais e fitoterápicos."
        ),
        "coords": (-12.6275, -38.6800),
    },
    "santo amaro": {
        "city": "Santo Amaro",
        "state": "BA",
        "ibge_code": "2928604",
        "population": 56012,
        "city_tier": CityTier.SMALL_TOWN,
        "demographic_density_hab_km2": 113.6,
        "gdp_per_capita_brl": 19800.0,
        "regional_hub_name": "Recôncavo Baiano",
        "commercial_potential_summary": (
            "Forte tradição no consumo de fitoterápicos, chás e compostos naturais em farmácias e ervanários locais."
        ),
        "coords": (-12.5467, -38.7119),
    },
    "aracaju": {
        "city": "Aracaju",
        "state": "SE",
        "ibge_code": "2800308",
        "population": 602757,
        "city_tier": CityTier.REGIONAL_HUB,
        "demographic_density_hab_km2": 3315.1,
        "gdp_per_capita_brl": 30800.0,
        "regional_hub_name": "Capital / Grande Aracaju (SE)",
        "commercial_potential_summary": (
            "Mercado litorâneo de alto consumo per capita em saudabilidade, suplementos e redes de drogarias."
        ),
        "coords": (-10.9472, -37.0731),
    },
    "recife": {
        "city": "Recife",
        "state": "PE",
        "ibge_code": "2611606",
        "population": 1488920,
        "city_tier": CityTier.METROPOLIS,
        "demographic_density_hab_km2": 6803.6,
        "gdp_per_capita_brl": 35400.0,
        "regional_hub_name": "Capital / Região Metropolitana do Recife (PE)",
        "commercial_potential_summary": (
            "Grande polo médico e farmacêutico do Nordeste; priorizar grandes redes, distribuidoras e empórios naturais."
        ),
        "coords": (-8.0476, -34.8770),
    },
    "sao paulo": {
        "city": "São Paulo",
        "state": "SP",
        "ibge_code": "3550308",
        "population": 11451999,
        "city_tier": CityTier.METROPOLIS,
        "demographic_density_hab_km2": 7528.2,
        "gdp_per_capita_brl": 68700.0,
        "regional_hub_name": "Metrópole Nacional (SP)",
        "commercial_potential_summary": (
            "Maior mercado consumidor nacional de suplementos, fitoterápicos e redes farmacêuticas."
        ),
        "coords": (-23.5505, -46.6333),
    },
}


class CityInsightsService:
    """
    Serviço responsável pela Regra P-107: Relatório de Inteligência Demográfica,
    Econômica e Comercial das Cidades presentes na rota do vendedor Fitoherb.
    """

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        if not text:
            return ""
        s = unicodedata.normalize("NFD", text.strip())
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower().replace("'", "").replace("-", " ").strip()

    @classmethod
    def _infer_city_from_coords(
        cls, lat: Optional[float], lon: Optional[float], fallback_city: Optional[str] = None
    ) -> Tuple[str, str]:
        if lat is not None and lon is not None:
            best_city = None
            best_state = "BA"
            best_dist = 999999.0
            for data in CURATED_MUNICIPALITIES_DB.values():
                coords = data.get("coords")
                if not coords:
                    continue
                dlat = math.radians(coords[0] - lat)
                dlon = math.radians(coords[1] - lon)
                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(math.radians(lat))
                    * math.cos(math.radians(coords[0]))
                    * math.sin(dlon / 2) ** 2
                )
                dist_km = 6371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                if dist_km < best_dist:
                    best_dist = dist_km
                    best_city = data["city"]
                    best_state = data["state"]
            if best_city and best_dist <= 35.0:
                return best_city, best_state

        if fallback_city:
            return cls.resolve_municipality_name(fallback_city, "BA")
        return "Lauro de Freitas", "BA"

    @classmethod
    def resolve_municipality_name(
        cls,
        raw_city: Optional[str],
        raw_state: Optional[str] = "BA",
        neighborhood: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        fallback_city: Optional[str] = None,
    ) -> Tuple[str, str]:
        state_clean = (raw_state or "BA").strip().upper()
        if len(state_clean) > 2:
            state_clean = "BA"

        for candidate in (raw_city, neighborhood):
            norm = cls.normalize_text(candidate)
            if norm in DISTRICT_TO_MUNICIPALITY_MAP:
                return DISTRICT_TO_MUNICIPALITY_MAP[norm]

        norm_city = cls.normalize_text(raw_city)
        if norm_city in CURATED_MUNICIPALITIES_DB:
            entry = CURATED_MUNICIPALITIES_DB[norm_city]
            return entry["city"], entry["state"]

        if raw_city and raw_city.strip():
            return raw_city.strip(), state_clean

        return cls._infer_city_from_coords(lat, lon, fallback_city=fallback_city)

    def _fetch_ibge_municipality_metadata(
        self, city_name: str, state: str
    ) -> Optional[Dict[str, Any]]:
        norm_target = self.normalize_text(city_name)
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{state}/municipios"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Fitoherb-AI-Routing/1.0 (Commercial Intelligence; P-107)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    items = json.loads(resp.read().decode("utf-8"))
                    if isinstance(items, list):
                        for item in items:
                            nome = item.get("nome", "")
                            if self.normalize_text(nome) == norm_target:
                                micro = (
                                    item.get("microrregiao", {})
                                    or item.get("regiao-imediata", {})
                                    or {}
                                )
                                meso = micro.get("mesorregiao", {}) or {}
                                hub_name = (
                                    meso.get("nome")
                                    or micro.get("nome")
                                    or f"Região de {nome} ({state})"
                                )
                                return {
                                    "ibge_code": str(item.get("id", "2900000")),
                                    "official_name": nome,
                                    "regional_hub_name": hub_name,
                                }
        except Exception:
            pass
        return None

    def _get_or_build_city_profile(self, city_name: str, state: str) -> Dict[str, Any]:
        norm_city = self.normalize_text(city_name)
        if norm_city in DISTRICT_TO_MUNICIPALITY_MAP:
            city_name, state = DISTRICT_TO_MUNICIPALITY_MAP[norm_city]
            norm_city = self.normalize_text(city_name)

        if norm_city in CURATED_MUNICIPALITIES_DB:
            curated = CURATED_MUNICIPALITIES_DB[norm_city]
            tier = curated["city_tier"]
            return {
                "city": curated["city"],
                "state": curated["state"],
                "ibge_code": curated["ibge_code"],
                "population": curated["population"],
                "city_tier": tier,
                "city_tier_label": CITY_TIER_LABELS.get(tier, "Cidade Média"),
                "demographic_density_hab_km2": curated["demographic_density_hab_km2"],
                "gdp_per_capita_brl": curated["gdp_per_capita_brl"],
                "regional_hub_name": curated["regional_hub_name"],
                "commercial_potential_summary": curated["commercial_potential_summary"],
            }

        cache_key = f"{norm_city}:{state.lower()}"
        cached = geo_cache.get_city_insight(cache_key)
        if cached:
            return cached

        ibge_meta = self._fetch_ibge_municipality_metadata(city_name, state)
        tier = TrafficPredictor.get_city_tier(city_name)

        tier_defaults = {
            CityTier.METROPOLIS: {
                "population": 1250000,
                "density": 2850.0,
                "gdp": 34500.0,
                "summary": (
                    "Grande centro urbano com alta capilaridade de redes de drogarias e lojas especializadas "
                    "em suplementos e produtos naturais."
                ),
            },
            CityTier.REGIONAL_HUB: {
                "population": 265000,
                "density": 420.0,
                "gdp": 29800.0,
                "summary": (
                    "Polo regional de comércio e saúde; excelente praça para distribuição em drogarias líderes "
                    "e empórios naturais."
                ),
            },
            CityTier.MEDIUM_CITY: {
                "population": 98500,
                "density": 185.0,
                "gdp": 24200.0,
                "summary": (
                    "Município de porte médio com forte giro em farmácias independentes, linha de fitoterápicos "
                    "tradicionais e polivitamínicos Fitoherb."
                ),
            },
            CityTier.SMALL_TOWN: {
                "population": 34800,
                "density": 78.5,
                "gdp": 19600.0,
                "summary": (
                    "Praça de atendimento consultivo em drogarias locais e comércio central; foco nos produtos "
                    "campeões de giro e fidelização do lojista."
                ),
            },
        }
        defaults = tier_defaults.get(tier, tier_defaults[CityTier.MEDIUM_CITY])

        profile = {
            "city": ibge_meta["official_name"] if ibge_meta else city_name,
            "state": state,
            "ibge_code": ibge_meta["ibge_code"] if ibge_meta else "2999999",
            "population": defaults["population"],
            "city_tier": tier,
            "city_tier_label": CITY_TIER_LABELS.get(tier, "Cidade Média (70k–200k hab)"),
            "demographic_density_hab_km2": defaults["density"],
            "gdp_per_capita_brl": defaults["gdp"],
            "regional_hub_name": (
                ibge_meta["regional_hub_name"]
                if ibge_meta
                else f"Polo Regional de {city_name} ({state})"
            ),
            "commercial_potential_summary": defaults["summary"],
        }

        geo_cache.set_city_insight(cache_key, profile)
        return profile

    def build_city_insights(
        self,
        depot: LocationPoint,
        ordered_stops: List[OrderedStopDto],
        suggested_stops: Optional[List[SuggestedStopDto]] = None,
        default_service_minutes: int = 20,
    ) -> List[CityInsightDto]:
        """
        Gera a lista ordenada de CityInsightDto (Regra P-107) consolidando paradas confirmadas,
        oportunidades sugeridas e tempo estimado de atendimento em cada município da rota.
        """
        suggested_stops = suggested_stops or []
        base_fallback_city = (
            depot.address.city if (depot and depot.address and depot.address.city) else None
        )

        city_buckets: Dict[str, Dict[str, Any]] = {}
        city_order: List[str] = []
        counted_suggestion_ids = set()

        def _ensure_bucket(city_name: str, state: str) -> str:
            profile = self._get_or_build_city_profile(city_name, state)
            official_key = f"{profile['city']}|{profile['state']}"
            if official_key not in city_buckets:
                city_buckets[official_key] = {
                    "profile": profile,
                    "confirmed_stops_count": 0,
                    "suggested_leads_count": 0,
                    "estimated_dwell_minutes": 0,
                }
                city_order.append(official_key)
            return official_key

        for stop in ordered_stops:
            if stop.action != "VISIT":
                continue

            raw_city = stop.address.city if stop.address else None
            raw_state = stop.address.state if (stop.address and stop.address.state) else "BA"
            neighborhood = stop.address.neighborhood if stop.address else None

            resolved_city, resolved_state = self.resolve_municipality_name(
                raw_city=raw_city,
                raw_state=raw_state,
                neighborhood=neighborhood,
                lat=stop.lat,
                lon=stop.lon,
                fallback_city=base_fallback_city,
            )
            bucket_key = _ensure_bucket(resolved_city, resolved_state)

            dwell = (
                int(stop.service_duration_minutes)
                if (stop.service_duration_minutes is not None and stop.service_duration_minutes > 0)
                else int(default_service_minutes or 20)
            )

            if stop.is_suggestion:
                city_buckets[bucket_key]["suggested_leads_count"] += 1
                counted_suggestion_ids.add(stop.id)
            else:
                city_buckets[bucket_key]["confirmed_stops_count"] += 1

            city_buckets[bucket_key]["estimated_dwell_minutes"] += dwell

        for sug in suggested_stops:
            if sug.id in counted_suggestion_ids:
                continue
            raw_city = sug.address.city if sug.address else None
            raw_state = sug.address.state if (sug.address and sug.address.state) else "BA"
            neighborhood = sug.address.neighborhood if sug.address else None
            resolved_city, resolved_state = self.resolve_municipality_name(
                raw_city=raw_city,
                raw_state=raw_state,
                neighborhood=neighborhood,
                lat=sug.lat,
                lon=sug.lon,
                fallback_city=base_fallback_city,
            )
            bucket_key = _ensure_bucket(resolved_city, resolved_state)
            city_buckets[bucket_key]["suggested_leads_count"] += 1

        if not city_order and depot:
            raw_city = depot.address.city if depot.address else None
            raw_state = depot.address.state if (depot.address and depot.address.state) else "BA"
            neighborhood = depot.address.neighborhood if depot.address else None
            resolved_city, resolved_state = self.resolve_municipality_name(
                raw_city=raw_city,
                raw_state=raw_state,
                neighborhood=neighborhood,
                lat=depot.lat,
                lon=depot.lon,
            )
            _ensure_bucket(resolved_city, resolved_state)

        results: List[CityInsightDto] = []
        for key in city_order:
            bucket = city_buckets[key]
            prof = bucket["profile"]
            results.append(
                CityInsightDto(
                    city=prof["city"],
                    state=prof["state"],
                    ibge_code=prof["ibge_code"],
                    population=prof["population"],
                    city_tier=prof["city_tier"],
                    city_tier_label=prof["city_tier_label"],
                    demographic_density_hab_km2=prof["demographic_density_hab_km2"],
                    gdp_per_capita_brl=prof["gdp_per_capita_brl"],
                    regional_hub_name=prof["regional_hub_name"],
                    commercial_potential_summary=prof["commercial_potential_summary"],
                    confirmed_stops_count=bucket["confirmed_stops_count"],
                    suggested_leads_count=bucket["suggested_leads_count"],
                    estimated_dwell_minutes=bucket["estimated_dwell_minutes"],
                )
            )

        return results


city_insights_service = CityInsightsService()
