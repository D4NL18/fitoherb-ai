import pytest
from app.domains.routing.traffic_model import TrafficPredictor, CityTier

def test_traffic_multiplier_city_tiers():
    # Salvador é metrópole (Tier 1)
    tier_ssa = TrafficPredictor.get_city_tier("Salvador")
    assert tier_ssa == CityTier.METROPOLIS

    # Feira de Santana é polo regional (Tier 2)
    tier_fsa = TrafficPredictor.get_city_tier("Feira de Santana")
    assert tier_fsa == CityTier.REGIONAL_HUB

    # Mata de São João é cidade pequena / litoral
    tier_msj = TrafficPredictor.get_city_tier("Mata de São João")
    assert tier_msj == CityTier.SMALL_TOWN

def test_traffic_rush_hour_vs_offpeak():
    # Pico da Manhã às 08:15 (495 min) em Salvador
    k_morning, cond_morning = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=495.0,
        distance_km=10.0,
        origin_city="Salvador",
        dest_city="Salvador"
    )
    assert k_morning >= 1.60
    assert "PICO" in cond_morning

    # Entrepico às 11:00 (660 min) em Salvador
    k_offpeak, cond_offpeak = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=660.0,
        distance_km=10.0,
        origin_city="Salvador",
        dest_city="Salvador"
    )
    assert k_offpeak <= 1.10
    assert cond_offpeak == "LIVRE"

def test_corridor_highway_attenuation():
    # Trecho rodoviário longo (> 20 km) na Linha Verde (Lauro de Freitas -> Guarajuba)
    k_hwy, cond_hwy = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=495.0, # 08:15
        distance_km=35.0,
        origin_city="Lauro de Freitas",
        dest_city="Guarajuba",
        base_city="Lauro de Freitas"
    )
    # Rodovia atenua o pico
    assert k_hwy < 1.45

def test_time_parsing_and_formatting():
    mins = TrafficPredictor.parse_time_str("08:30")
    assert mins == 510.0

    clock = TrafficPredictor.format_clock(510.0)
    assert clock == "08:30"
