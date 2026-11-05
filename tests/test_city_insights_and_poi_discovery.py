import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domains.routing.models.point import Address, LocationPoint, DeliveryStop
from app.domains.routing.schemas.routing_dto import (
    OptimizeRouteRequest,
    OrderedStopDto,
    CityInsightDto,
    SuggestedStopDto,
    ExportPdfRequest,
)
from app.domains.routing.services.city_insights_service import (
    CityInsightsService,
    city_insights_service,
)
from app.domains.routing.services.poi_discovery_service import (
    PoiDiscoveryService,
    poi_discovery_service,
)
from app.domains.routing.services.pdf_service import PdfReportService

client = TestClient(app)


class TestCityInsightsServiceP107:
    """Suíte TDD para a Regra P-107: Relatório de Inteligência Demográfica e Comercial por Cidade."""

    def test_build_city_insights_enriches_cities_and_normalizes_districts(self):
        # Arrange
        depot = LocationPoint(
            id="depot-1",
            name="Matriz Fitoherb",
            lat=-12.8992,
            lon=-38.3242,
            address=Address(
                street="Rua Itaeté",
                number="434",
                neighborhood="Pitangueiras",
                city="Lauro de Freitas",
                state="BA",
            ),
        )
        ordered_stops = [
            OrderedStopDto(
                step=0,
                id="depot-1",
                name="Matriz Fitoherb",
                action="DEPARTURE",
                is_fixed=True,
                priority="BASE",
                arrival_time_minutes=0.0,
                lat=-12.8992,
                lon=-38.3242,
                address=depot.address,
            ),
            OrderedStopDto(
                step=1,
                id="stop-ssa-1",
                name="Drogaria São Paulo - Pituba",
                action="VISIT",
                is_fixed=True,
                fixed_order=1,
                priority="HIGH",
                arrival_time_minutes=25.0,
                service_duration_minutes=30,
                lat=-12.9984,
                lon=-38.4908,
                is_suggestion=False,
                address=Address(
                    street="Av. Manoel Dias da Silva",
                    number="1500",
                    neighborhood="Pituba",
                    city="Salvador",
                    state="BA",
                ),
            ),
            OrderedStopDto(
                step=2,
                id="sug-ssa-1",
                name="Mundo Verde - Pituba",
                action="VISIT",
                is_fixed=False,
                priority="REGULAR",
                arrival_time_minutes=32.0,
                service_duration_minutes=15,
                lat=-13.0012,
                lon=-38.4865,
                is_suggestion=True,
                suggestion_category="PRODUTOS_NATURAIS",
                detour_distance_km=0.8,
                detour_time_minutes=2.5,
                address=Address(
                    street="Av. Paulo VI",
                    number="1820",
                    neighborhood="Pituba",
                    city="Salvador",
                    state="BA",
                ),
            ),
            OrderedStopDto(
                step=3,
                id="stop-abrantes-1",
                name="Farmácia Popular de Abrantes",
                action="VISIT",
                is_fixed=False,
                priority="REGULAR",
                arrival_time_minutes=58.0,
                service_duration_minutes=20,
                lat=-12.8250,
                lon=-38.2700,
                is_suggestion=False,
                address=Address(
                    street="Praça da Matriz",
                    number="10",
                    neighborhood="Vila de Abrantes",
                    city="Abrantes",
                    state="BA",
                ),
            ),
        ]

        # Act
        insights = city_insights_service.build_city_insights(
            depot=depot,
            ordered_stops=ordered_stops,
            suggested_stops=[],
            default_service_minutes=20,
        )

        # Assert
        assert len(insights) >= 2
        by_city = {item.city: item for item in insights}

        assert "Salvador" in by_city
        ssa = by_city["Salvador"]
        assert ssa.ibge_code == "2927408"
        assert ssa.population >= 2000000
        assert ssa.city_tier == "METROPOLIS"
        assert "Metrópole" in ssa.city_tier_label
        assert ssa.demographic_density_hab_km2 > 1000
        assert ssa.gdp_per_capita_brl > 10000
        assert len(ssa.regional_hub_name) > 3
        assert len(ssa.commercial_potential_summary) > 15
        assert ssa.confirmed_stops_count == 1
        assert ssa.suggested_leads_count == 1
        assert ssa.estimated_dwell_minutes == 45

        # Verifica se o distrito "Abrantes" foi normalizado para o município oficial "Camaçari"
        assert "Camaçari" in by_city
        camacari = by_city["Camaçari"]
        assert camacari.ibge_code == "2905701"
        assert camacari.confirmed_stops_count == 1
        assert camacari.estimated_dwell_minutes == 20

    def test_build_city_insights_resilience_when_ibge_api_times_out(self):
        # Arrange
        depot = LocationPoint(
            id="depot-1",
            name="Base",
            lat=-12.8992,
            lon=-38.3242,
            address=Address(city="Lauro de Freitas", state="BA"),
        )
        ordered_stops = [
            OrderedStopDto(
                step=1,
                id="stop-unknown",
                name="Farmácia Sertão Verde",
                action="VISIT",
                is_fixed=False,
                priority="REGULAR",
                arrival_time_minutes=40.0,
                service_duration_minutes=25,
                lat=-11.5000,
                lon=-39.5000,
                address=Address(city="Município Experimental Inexistente", state="BA"),
            )
        ]

        # Act - Simula falha/timeout total na rede externa (IBGE API)
        with patch("urllib.request.urlopen", side_effect=TimeoutError("IBGE API Timeout")):
            insights = city_insights_service.build_city_insights(
                depot=depot,
                ordered_stops=ordered_stops,
                suggested_stops=[],
                default_service_minutes=20,
            )

        # Assert
        assert len(insights) >= 1
        unknown_city = next(
            (i for i in insights if "Experimental" in i.city), None
        )
        assert unknown_city is not None
        assert unknown_city.population > 0
        assert unknown_city.demographic_density_hab_km2 > 0
        assert unknown_city.gdp_per_capita_brl > 0
        assert unknown_city.confirmed_stops_count == 1
        assert unknown_city.estimated_dwell_minutes == 25


class TestPoiDiscoveryServiceP108:
    """Suíte TDD para a Regra P-108: Descoberta Proativa de Farmácias e Lojas Naturais com Deduplicação Rigorosa."""

    def test_is_duplicate_poi_blocks_within_80m_and_phonetic_similarity_above_082(self):
        # Arrange
        existing_points = [
            {
                "name": "Drogaria São Paulo - Pituba",
                "lat": -12.9984,
                "lon": -38.4908,
                "city": "Salvador",
            },
            {
                "name": "Farmácia Pague Menos - Itaigara",
                "lat": -12.9920,
                "lon": -38.4720,
                "city": "Salvador",
            },
        ]

        # Act & Assert 1: Ponto a ~35 metros (< 80m / 0.08km) mesmo com nome diferente deve ser considerado duplicado
        is_dup_close = poi_discovery_service.is_duplicate_poi(
            candidate_name="Drogaria Nova Esquina",
            candidate_lat=-12.9985,
            candidate_lon=-38.4909,
            candidate_city="Salvador",
            existing_points=existing_points,
        )
        assert is_dup_close is True

        # Act & Assert 2: Ponto a > 500 metros mas com nome léxico/fonético >= 0.82 na mesma cidade deve ser bloqueado
        is_dup_name = poi_discovery_service.is_duplicate_poi(
            candidate_name="Drogaria Sao Paulo Pituba",
            candidate_lat=-13.0050,
            candidate_lon=-38.4850,
            candidate_city="Salvador",
            existing_points=existing_points,
        )
        assert is_dup_name is True

        # Act & Assert 3: Ponto legítimo inédito a > 80m e com nome distinto NÃO é duplicado
        is_dup_valid = poi_discovery_service.is_duplicate_poi(
            candidate_name="Mundo Verde - Pituba",
            candidate_lat=-13.0012,
            candidate_lon=-38.4865,
            candidate_city="Salvador",
            existing_points=existing_points,
        )
        assert is_dup_valid is False

    def test_discover_along_route_returns_non_duplicate_pharma_and_natural_leads_with_fallback(self):
        # Arrange
        depot = LocationPoint(
            id="depot-lf",
            name="Matriz Fitoherb",
            lat=-12.8992,
            lon=-38.3242,
            address=Address(city="Lauro de Freitas", state="BA"),
        )
        stops = [
            DeliveryStop(
                id="stop-1",
                name="Drogaria São Paulo - Pituba",
                lat=-12.9984,
                lon=-38.4908,
                priority="HIGH",
                address=Address(
                    street="Av. Manoel Dias da Silva",
                    number="1500",
                    neighborhood="Pituba",
                    city="Salvador",
                    state="BA",
                ),
            )
        ]
        excluded_locations = [
            LocationPoint(
                id="fav-excluded",
                name="Farmácia Pague Menos - Pituba",
                lat=-12.9991,
                lon=-38.4895,
                address=Address(city="Salvador", state="BA"),
            )
        ]

        # Act - Simula indisponibilidade da Overpass API para validar resiliência do catálogo/cache local
        with patch("urllib.request.urlopen", side_effect=TimeoutError("Overpass API Timeout")):
            suggestions = poi_discovery_service.discover_along_route(
                depot=depot,
                stops=stops,
                excluded_locations=excluded_locations,
                max_suggestions=5,
            )

        # Assert
        assert 1 <= len(suggestions) <= 5
        for sug in suggestions:
            assert isinstance(sug, SuggestedStopDto)
            assert sug.is_suggestion is True
            assert sug.suggestion_category in ("FARMACIA", "PRODUTOS_NATURAIS")
            assert sug.detour_distance_km is not None and sug.detour_distance_km >= 0.0
            assert sug.detour_time_minutes is not None and sug.detour_time_minutes >= 0.0
            # Garante que os pontos já listados ou excluídos não foram sugeridos
            assert "drogaria sao paulo" not in sug.name.lower()
            assert "drogaria são paulo" not in sug.name.lower()
            assert "pague menos - pituba" not in sug.name.lower()


class TestRoutingEndpointsAndPdfContract:
    """Suíte de contrato para /api/v1/routing/optimize, /recalculate e /export-pdf (P-105, P-107, P-108, P-109)."""

    def test_optimize_and_recalculate_endpoints_contract(self):
        # Arrange
        payload = {
            "depot": {
                "id": "base-1",
                "name": "Fitoherb Matriz",
                "lat": -12.8992,
                "lon": -38.3242,
                "address": {
                    "street": "Rua Itaeté",
                    "number": "434",
                    "neighborhood": "Pitangueiras",
                    "city": "Lauro de Freitas",
                    "state": "BA",
                },
            },
            "stops": [
                {
                    "id": "stop-1",
                    "name": "Drogaria São Paulo - Pituba",
                    "lat": -12.9984,
                    "lon": -38.4908,
                    "priority": "HIGH",
                    "service_duration_minutes": 25,
                    "address": {
                        "street": "Av. Manoel Dias da Silva",
                        "number": "1500",
                        "neighborhood": "Pituba",
                        "city": "Salvador",
                        "state": "BA",
                    },
                }
            ],
            "return_to_depot": True,
            "departure_time": "08:00",
            "discover_suggestions": True,
            "max_suggestions": 3,
            "excluded_locations": [
                {
                    "id": "fav-1",
                    "name": "Farmácia Pague Menos - Pituba",
                    "lat": -12.9991,
                    "lon": -38.4895,
                }
            ],
        }

        # Act 1: POST /api/v1/routing/optimize com discover_suggestions=True
        with patch("urllib.request.urlopen", side_effect=TimeoutError("Offline mode test")):
            resp_opt = client.post("/api/v1/routing/optimize", json=payload)

        # Assert 1
        assert resp_opt.status_code == 200
        data_opt = resp_opt.json()
        assert "city_insights" in data_opt
        assert len(data_opt["city_insights"]) >= 1
        assert "suggested_stops" in data_opt
        assert len(data_opt["suggested_stops"]) >= 1

        visit_stops = [s for s in data_opt["ordered_stops"] if s["action"] == "VISIT"]
        suggestion_visits = [s for s in visit_stops if s.get("is_suggestion") is True]
        assert len(suggestion_visits) >= 1

        # Act 2: POST /api/v1/routing/recalculate (Manejo em Lote P-109 concluído mantendo apenas 1 parada)
        recalc_payload = {
            **payload,
            "discover_suggestions": False,
            "stops": payload["stops"],  # Vendedor removeu as sugestões no manejo em lote
        }
        with patch("urllib.request.urlopen", side_effect=TimeoutError("Offline mode test")):
            resp_recalc = client.post("/api/v1/routing/recalculate", json=recalc_payload)

        # Assert 2: Recalculate NÃO deve reinjetar sugestões descartadas e deve atualizar city_insights
        assert resp_recalc.status_code == 200
        data_recalc = resp_recalc.json()
        recalc_visits = [s for s in data_recalc["ordered_stops"] if s["action"] == "VISIT"]
        assert len(recalc_visits) == 1
        assert recalc_visits[0]["id"] == "stop-1"
        assert len(data_recalc["city_insights"]) >= 1

    def test_pdf_manifest_renders_city_insights_and_hides_raw_coordinates_p105_p107(self):
        # Arrange
        pdf_req = ExportPdfRequest(
            seller_name="Consultor Fitoherb",
            date="05/11/2026",
            total_time_minutes=65.0,
            total_distance_km=28.4,
            ordered_stops=[
                OrderedStopDto(
                    step=0,
                    id="base",
                    name="Matriz Fitoherb",
                    action="DEPARTURE",
                    is_fixed=True,
                    priority="BASE",
                    arrival_time_minutes=0.0,
                    lat=-12.8992,
                    lon=-38.3242,
                    address=Address(
                        street="Rua Itaeté",
                        number="434",
                        neighborhood="Pitangueiras",
                        city="Lauro de Freitas",
                        state="BA",
                    ),
                ),
                OrderedStopDto(
                    step=1,
                    id="sug-1",
                    name="Mundo Verde - Pituba",
                    action="VISIT",
                    is_fixed=False,
                    priority="REGULAR",
                    arrival_time_minutes=30.0,
                    lat=-12.9984,
                    lon=-38.4908,
                    is_suggestion=True,
                    suggestion_category="PRODUTOS_NATURAIS",
                    detour_distance_km=0.9,
                    detour_time_minutes=3.0,
                    address=Address(
                        street="Av. Paulo VI",
                        number="1820",
                        neighborhood="Pituba",
                        city="Salvador",
                        state="BA",
                    ),
                ),
            ],
            city_insights=[
                CityInsightDto(
                    city="Salvador",
                    state="BA",
                    ibge_code="2927408",
                    population=2417678,
                    city_tier="METROPOLIS",
                    city_tier_label="Metrópole (> 1M hab)",
                    demographic_density_hab_km2=3486.5,
                    gdp_per_capita_brl=27540.0,
                    regional_hub_name="Capital / Região Metropolitana (RMS)",
                    commercial_potential_summary="Forte demanda por fitoterápicos e suplementos.",
                    confirmed_stops_count=0,
                    suggested_leads_count=1,
                    estimated_dwell_minutes=20,
                )
            ],
        )

        # Act
        pdf_bytes = PdfReportService.generate_route_manifest(pdf_req)

        # Assert
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000
        # Regra P-105: Coordenadas brutas NUNCA devem constar no PDF
        assert b"-12.9984" not in pdf_bytes
        assert b"-38.4908" not in pdf_bytes
