import math
from typing import Dict, Any, Optional, Tuple

class CityTier:
    METROPOLIS = "METROPOLIS"          # > 1M hab ou Capitais (ex: Salvador, SP, RJ, BH)
    REGIONAL_HUB = "REGIONAL_HUB"      # 300k - 1M hab (ex: Feira de Santana, Lauro de Freitas, Camaçari)
    MEDIUM_CITY = "MEDIUM_CITY"        # 100k - 300k hab (ex: Alagoinhas, Simões Filho, Itabuna)
    SMALL_TOWN = "SMALL_TOWN"          # < 100k hab ou Litoral/Interior (ex: Mata de São João, Pojuca)

# Dicionário de classificação de cidades conhecidas (Bahia + Principais Capitais Brasileiras)
KNOWN_CITIES_TIERS: Dict[str, str] = {
    # Metrópoles / Capitais
    "salvador": CityTier.METROPOLIS,
    "sao paulo": CityTier.METROPOLIS,
    "rio de janeiro": CityTier.METROPOLIS,
    "belo horizonte": CityTier.METROPOLIS,
    "brasilia": CityTier.METROPOLIS,
    "curitiba": CityTier.METROPOLIS,
    "fortaleza": CityTier.METROPOLIS,
    "recife": CityTier.METROPOLIS,
    "porto alegre": CityTier.METROPOLIS,
    "goiania": CityTier.METROPOLIS,
    "manaus": CityTier.METROPOLIS,
    "belem": CityTier.METROPOLIS,
    
    # Polos Regionais e Cidades Grandes da Bahia / Brasil
    "feira de santana": CityTier.REGIONAL_HUB,
    "lauro de freitas": CityTier.REGIONAL_HUB,
    "camacari": CityTier.REGIONAL_HUB,
    "vitoria da conquista": CityTier.REGIONAL_HUB,
    "itabuana": CityTier.REGIONAL_HUB,
    "campinas": CityTier.REGIONAL_HUB,
    "santos": CityTier.REGIONAL_HUB,
    "ribeirao preto": CityTier.REGIONAL_HUB,
    "londrina": CityTier.REGIONAL_HUB,
    "joinville": CityTier.REGIONAL_HUB,
    "uberlandia": CityTier.REGIONAL_HUB,

    # Cidades Médias
    "alagoinhas": CityTier.MEDIUM_CITY,
    "simoes filho": CityTier.MEDIUM_CITY,
    "ilheus": CityTier.MEDIUM_CITY,
    "jequie": CityTier.MEDIUM_CITY,
    "porto seguro": CityTier.MEDIUM_CITY,
    "barreiras": CityTier.MEDIUM_CITY,
    "teixeira de freitas": CityTier.MEDIUM_CITY,
    "candeias": CityTier.MEDIUM_CITY,
    "dias d'avila": CityTier.MEDIUM_CITY,
    "dias davila": CityTier.MEDIUM_CITY,

    # Cidades Menores / Litoral Norte / Interior
    "mata de sao joao": CityTier.SMALL_TOWN,
    "praia do forte": CityTier.SMALL_TOWN,
    "guarajuba": CityTier.SMALL_TOWN,
    "itacimirim": CityTier.SMALL_TOWN,
    "sauipe": CityTier.SMALL_TOWN,
    "abrantes": CityTier.REGIONAL_HUB, # distrito integrado a Camaçari/Lauro
    "arembepe": CityTier.SMALL_TOWN,
    "madre de deus": CityTier.SMALL_TOWN,
    "sao francisco do conde": CityTier.SMALL_TOWN,
    "santo amaro": CityTier.SMALL_TOWN,
    "pojuca": CityTier.SMALL_TOWN
}

class TrafficPredictor:
    """
    Modelo de Previsão de Trânsito Dinâmico por Horário de Pico e Porte de Cidade.
    Implementa curvas contínuas com suavização e atenuação para rodovias interurbanas.
    """

    @classmethod
    def normalize_city_name(cls, city: Optional[str]) -> str:
        if not city:
            return ""
        c = city.lower().strip()
        import unicodedata
        c = unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode("utf-8")
        return c

    @classmethod
    def get_city_tier(cls, city_name: Optional[str], base_city: Optional[str] = None) -> str:
        norm_city = cls.normalize_city_name(city_name)
        if norm_city in KNOWN_CITIES_TIERS:
            return KNOWN_CITIES_TIERS[norm_city]

        # Se a cidade não estiver no dicionário explícito, herda o contexto da cidade base
        if base_city:
            norm_base = cls.normalize_city_name(base_city)
            if norm_base in KNOWN_CITIES_TIERS:
                return KNOWN_CITIES_TIERS[norm_base]

        # Padrão conservador: cidade média
        return CityTier.MEDIUM_CITY

    @classmethod
    def get_traffic_multiplier(
        cls,
        time_minutes_from_midnight: Optional[float],
        distance_km: float,
        origin_city: Optional[str] = None,
        dest_city: Optional[str] = None,
        base_city: Optional[str] = None
    ) -> Tuple[float, str]:
        """
        Calcula o multiplicador de trânsito k(tau) e o status descritivo.
        Se time_minutes_from_midnight for None, retorna fluxo neutro (1.0, 'LIVRE').
        """
        if time_minutes_from_midnight is None:
            return 1.0, "LIVRE"

        # Determina o porte predominante do trecho
        tier_orig = cls.get_city_tier(origin_city, base_city)
        tier_dest = cls.get_city_tier(dest_city, base_city)

        # Se qualquer uma das pontas for Metrópole, prevalece o impacto da Metrópole
        if tier_orig == CityTier.METROPOLIS or tier_dest == CityTier.METROPOLIS:
            effective_tier = CityTier.METROPOLIS
        elif tier_orig == CityTier.REGIONAL_HUB or tier_dest == CityTier.REGIONAL_HUB:
            effective_tier = CityTier.REGIONAL_HUB
        elif tier_orig == CityTier.MEDIUM_CITY or tier_dest == CityTier.MEDIUM_CITY:
            effective_tier = CityTier.MEDIUM_CITY
        else:
            effective_tier = CityTier.SMALL_TOWN

        # Curva Base por Faixa Horária
        # Horários de Pico:
        # Pico Manhã: 07:00 (420 min) a 09:30 (570 min), ápice às 08:15 (495 min)
        # Pico Almoço: 12:00 (720 min) a 13:30 (810 min), ápice às 12:45 (765 min)
        # Pico Tarde/Noite: 17:00 (1020 min) a 19:30 (1170 min), ápice às 18:15 (1095 min)
        t = time_minutes_from_midnight % 1440 # garante ciclo de 24h

        # Multiplicadores de pico máximos por Tier
        max_peaks = {
            CityTier.METROPOLIS: {"morning": 1.70, "lunch": 1.25, "evening": 1.75, "offpeak": 1.05},
            CityTier.REGIONAL_HUB: {"morning": 1.45, "lunch": 1.18, "evening": 1.48, "offpeak": 1.05},
            CityTier.MEDIUM_CITY: {"morning": 1.25, "lunch": 1.10, "evening": 1.28, "offpeak": 1.02},
            CityTier.SMALL_TOWN: {"morning": 1.10, "lunch": 1.05, "evening": 1.12, "offpeak": 1.00},
        }

        peaks = max_peaks[effective_tier]
        multiplier = peaks["offpeak"]
        condition = "LIVRE"

        # Pico Manhã (07:00 a 09:30)
        if 420 <= t <= 570:
            apex = 495.0 # 08:15
            dist_apex = abs(t - apex)
            intensity = max(0.0, 1.0 - (dist_apex / 75.0))
            multiplier = peaks["offpeak"] + (peaks["morning"] - peaks["offpeak"]) * intensity
            condition = "PICO_MANHA" if intensity > 0.4 else "MODERADO"

        # Pico Almoço (12:00 a 13:30)
        elif 720 <= t <= 810:
            apex = 765.0 # 12:45
            dist_apex = abs(t - apex)
            intensity = max(0.0, 1.0 - (dist_apex / 45.0))
            multiplier = peaks["offpeak"] + (peaks["lunch"] - peaks["offpeak"]) * intensity
            condition = "PICO_ALMOCO" if intensity > 0.4 else "MODERADO"

        # Pico Tarde/Noite (17:00 a 19:30)
        elif 1020 <= t <= 1170:
            apex = 1095.0 # 18:15
            dist_apex = abs(t - apex)
            intensity = max(0.0, 1.0 - (dist_apex / 75.0))
            multiplier = peaks["offpeak"] + (peaks["evening"] - peaks["offpeak"]) * intensity
            condition = "PICO_TARDE" if intensity > 0.4 else "MODERADO"

        # Madrugada (22:00 a 06:00): fluxo totalmente livre
        elif t >= 1320 or t < 360:
            multiplier = 1.00
            condition = "LIVRE"

        # Atenuação para Trechos Rodoviários Longos (> 20 km)
        # Rodovias retêm velocidades maiores mesmo em horário de pico
        if distance_km > 20.0 and multiplier > 1.15:
            # Reduz o excesso de congestionamento em 40% em trechos rodoviários
            excess = multiplier - 1.0
            multiplier = 1.0 + (excess * 0.60)
            if condition.startswith("PICO"):
                condition = "MODERADO_RODOVIA"

        return round(multiplier, 2), condition

    @classmethod
    def parse_time_str(cls, time_str: Optional[str]) -> Optional[float]:
        """Converte 'HH:MM' para minutos desde meia-noite, ou retorna None se não fornecido."""
        if not time_str or not str(time_str).strip():
            return None
        try:
            parts = str(time_str).strip().split(":")
            if len(parts) >= 2:
                return float(int(parts[0]) * 60 + int(parts[1]))
        except Exception:
            pass
        return None

    @classmethod
    def format_clock(cls, minutes_from_midnight: Optional[float]) -> Optional[str]:
        """Converte minutos desde meia-noite para formato 'HH:MM', ou None se não aplicável."""
        if minutes_from_midnight is None:
            return None
        total_mins = int(round(minutes_from_midnight)) % 1440
        h = total_mins // 60
        m = total_mins % 60
        return f"{h:02d}:{m:02d}"
