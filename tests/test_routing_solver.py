import pytest
from app.domains.routing.services.routing_solver import RoutingGeneticSolver
from app.domains.routing.infrastructure.osrm_provider import OSRMProvider
from app.domains.routing.services.pdf_service import pdf_service
from app.domains.routing.schemas.routing_dto import ExportPdfRequest, OrderedStopDto
from app.domains.routing.models.point import Address

@pytest.fixture
def mock_matrix():
    # 5 nós: 0 (Base), 1 (Parada 1), 2 (Parada 2), 3 (Parada 3), 4 (Parada 4)
    durations = [
        [0.0, 600.0, 1200.0, 1800.0, 2400.0],
        [600.0, 0.0, 300.0, 900.0, 1500.0],
        [1200.0, 300.0, 0.0, 400.0, 1000.0],
        [1800.0, 900.0, 400.0, 0.0, 500.0],
        [2400.0, 1500.0, 1000.0, 500.0, 0.0]
    ]
    distances = [
        [0.0, 5000.0, 10000.0, 15000.0, 20000.0],
        [5000.0, 0.0, 2000.0, 7000.0, 12000.0],
        [10000.0, 2000.0, 0.0, 3000.0, 8000.0],
        [15000.0, 7000.0, 3000.0, 0.0, 4000.0],
        [20000.0, 12000.0, 8000.0, 4000.0, 0.0]
    ]
    return durations, distances

def test_routing_solver_free_order(mock_matrix):
    durations, distances = mock_matrix
    deliveries = [
        {"id": "del-1", "name": "Cliente A", "demand": 10.0, "fixed_order": None},
        {"id": "del-2", "name": "Cliente B", "demand": 10.0, "fixed_order": None},
        {"id": "del-3", "name": "Cliente C", "demand": 10.0, "fixed_order": None},
        {"id": "del-4", "name": "Cliente D", "demand": 10.0, "fixed_order": None},
    ]

    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        return_to_depot=True,
        generations=20
    )
    result = solver.solve()

    seq = result["ordered_sequence"]
    assert len(seq) == 4
    assert sorted(seq) == [1, 2, 3, 4]
    assert result["total_time_minutes"] > 0
    assert result["total_distance_km"] > 0
    assert len(result["fitness_history"]) > 0

def test_routing_solver_locked_order(mock_matrix):
    durations, distances = mock_matrix
    # Regra P-104: Força Parada 4 na posição 1 (primeira visita) e Parada 2 na posição 3
    deliveries = [
        {"id": "del-1", "name": "Cliente A", "demand": 10.0, "fixed_order": None},
        {"id": "del-2", "name": "Cliente B", "demand": 10.0, "fixed_order": 3}, # 3ª visita
        {"id": "del-3", "name": "Cliente C", "demand": 10.0, "fixed_order": None},
        {"id": "del-4", "name": "Cliente D", "demand": 10.0, "fixed_order": 1}, # 1ª visita
    ]

    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        return_to_depot=True,
        generations=25
    )
    result = solver.solve()

    seq = result["ordered_sequence"]
    assert len(seq) == 4
    # Posição 0 (1ª visita) DEVE ser o nó 4
    assert seq[0] == 4
    # Posição 2 (3ª visita) DEVE ser o nó 2
    assert seq[2] == 2
    # Todos os nós foram visitados sem duplicidade
    assert sorted(seq) == [1, 2, 3, 4]

def test_osrm_fallback_haversine():
    points = [
        (-12.8992, -38.3242), # Fitoherb Lauro
        (-12.9984, -38.4908), # Pituba
        (-13.0090, -38.5300)  # Barra
    ]
    provider = OSRMProvider()
    durations, distances = provider.get_matrix(points)

    assert len(durations) == 3
    assert len(distances) == 3
    assert durations[0][0] == 0.0
    assert distances[0][1] > 0
    assert durations[0][1] > 0

def test_pdf_manifest_generation():
    request = ExportPdfRequest(
        seller_name="João Vendedor",
        date="23/09/2026",
        total_time_minutes=45.0,
        total_distance_km=22.5,
        ordered_stops=[
            OrderedStopDto(
                step=0,
                id="depot",
                name="Base Vendedor",
                action="DEPARTURE",
                is_fixed=True,
                arrival_time_minutes=0.0,
                address=Address(street="Rua Itaeté", number="434", neighborhood="Pitangueiras", city="Lauro de Freitas")
            ),
            OrderedStopDto(
                step=1,
                id="stop-1",
                name="Drogaria FarmaVida",
                action="VISIT",
                is_fixed=True,
                fixed_order=1,
                priority="HIGH",
                arrival_time_minutes=15.0,
                address=Address(street="Av. Oceânica", number="100", neighborhood="Barra", city="Salvador")
            ),
            OrderedStopDto(
                step=2,
                id="depot",
                name="Base Vendedor",
                action="RETURN",
                is_fixed=True,
                arrival_time_minutes=45.0,
                address=Address(street="Rua Itaeté", number="434", neighborhood="Pitangueiras", city="Lauro de Freitas")
            )
        ]
    )

    pdf_bytes = pdf_service.generate_route_manifest(request)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

def test_routing_solver_urgent_priority(mock_matrix):
    durations, distances = mock_matrix
    # Parada 4 é marcada como Urgente (CRITICAL), paradas 1, 2, 3 são REGULAR
    deliveries = [
        {"id": "del-1", "name": "Cliente Regular 1", "priority": "REGULAR", "fixed_order": None},
        {"id": "del-2", "name": "Cliente Regular 2", "priority": "REGULAR", "fixed_order": None},
        {"id": "del-3", "name": "Cliente Regular 3", "priority": "REGULAR", "fixed_order": None},
        {"id": "del-4", "name": "Cliente Urgente 4", "priority": "CRITICAL", "fixed_order": None},
    ]

    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        return_to_depot=True,
        generations=25
    )
    result = solver.solve()
    seq = result["ordered_sequence"]
    
    # Parada 4 (nó 4) deve ser atendida prioritariamente na primeira posição (seq[0] == 4)
    assert seq[0] == 4, f"Parada urgente deveria ser atendida primeiro, mas a ordem foi {seq}"

def test_corridor_anti_overshoot():
    # Base (0, 0), Parada 1: Abrantes (0.05, 0.05), Parada 2: Guarajuba (0.15, 0.15), Parada 3: Salvador (-0.1, -0.1)
    coords = [
        (-12.899, -38.324), # 0: Base Lauro
        (-12.840, -38.250), # 1: Abrantes (~12 km)
        (-12.710, -38.120), # 2: Guarajuba (~32 km mesmo eixo)
        (-13.000, -38.500), # 3: Salvador (~25 km eixo oposto)
    ]
    provider = OSRMProvider()
    durations, distances = provider.get_matrix(coords)
    deliveries = [
        {"id": "del-1", "name": "Abrantes", "priority": "REGULAR", "fixed_order": None},
        {"id": "del-2", "name": "Guarajuba", "priority": "REGULAR", "fixed_order": None},
        {"id": "del-3", "name": "Salvador", "priority": "REGULAR", "fixed_order": None},
    ]

    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        return_to_depot=True,
        coordinates=coords,
        generations=30
    )
    result = solver.solve()
    seq = result["ordered_sequence"]

    # Se visitou Abrantes (1) e Guarajuba (2) antes de Salvador (3),
    # 1 DEVE vir antes de 2 (não deve passar direto por Abrantes para ir a Guarajuba primeiro!)
    idx_abrantes = seq.index(1)
    idx_guarajuba = seq.index(2)
    idx_salvador = seq.index(3)

    if idx_abrantes < idx_salvador and idx_guarajuba < idx_salvador:
        assert idx_abrantes < idx_guarajuba, f"Deveria visitar Abrantes antes de Guarajuba na ida, mas a ordem foi {seq}"

def test_optimize_route_legacy_fallback_when_no_departure_time():
    from app.api.v1.routers.routing_router import optimize_route
    from app.domains.routing.schemas.routing_dto import OptimizeRouteRequest
    from app.domains.routing.models.point import LocationPoint, DeliveryStop

    payload = OptimizeRouteRequest(
        depot=LocationPoint(id="base", name="Base", lat=-12.899, lon=-38.324),
        stops=[
            DeliveryStop(id="s1", name="Ponto 1", lat=-12.840, lon=-38.250, service_duration_minutes=30),
            DeliveryStop(id="s2", name="Ponto 2", lat=-12.710, lon=-38.120, service_duration_minutes=20)
        ],
        departure_time=None, # Sem horário de partida -> deve cair no modo legado
        return_to_depot=True
    )

    resp = optimize_route(payload)
    # No modo legado, relógios reais e trânsito dinâmico não são projetados
    assert resp.departure_clock is None
    assert resp.estimated_finish_clock is None
    assert resp.total_transit_minutes is None
    assert resp.total_service_minutes is None
    assert resp.ordered_stops[0].estimated_arrival_clock is None
    assert resp.ordered_stops[1].traffic_factor is None
    assert resp.ordered_stops[1].service_duration_minutes is None
    assert resp.total_time_minutes > 0

def test_optimize_route_legacy_fallback_when_no_stop_durations():
    from app.api.v1.routers.routing_router import optimize_route
    from app.domains.routing.schemas.routing_dto import OptimizeRouteRequest
    from app.domains.routing.models.point import LocationPoint, DeliveryStop

    payload = OptimizeRouteRequest(
        depot=LocationPoint(id="base", name="Base", lat=-12.899, lon=-38.324),
        stops=[
            DeliveryStop(id="s1", name="Ponto 1", lat=-12.840, lon=-38.250, service_duration_minutes=None),
            DeliveryStop(id="s2", name="Ponto 2", lat=-12.710, lon=-38.120, service_duration_minutes=0)
        ],
        departure_time="08:00",
        return_to_depot=True
    )

    resp = optimize_route(payload)
    # Sem duração em nenhum ponto -> deve cair no modo legado
    assert resp.departure_clock is None
    assert resp.estimated_finish_clock is None
    assert resp.total_transit_minutes is None
    assert resp.total_service_minutes is None

def test_optimize_route_temporal_active_with_average_imputation():
    from app.api.v1.routers.routing_router import optimize_route
    from app.domains.routing.schemas.routing_dto import OptimizeRouteRequest
    from app.domains.routing.models.point import LocationPoint, DeliveryStop

    payload = OptimizeRouteRequest(
        depot=LocationPoint(id="base", name="Base", lat=-12.899, lon=-38.324),
        stops=[
            # Ponto 1 tem 40 min, Ponto 2 não tem duração (deve herdar a média = 40 min)
            DeliveryStop(id="s1", name="Ponto 1", lat=-12.840, lon=-38.250, service_duration_minutes=40),
            DeliveryStop(id="s2", name="Ponto 2", lat=-12.710, lon=-38.120, service_duration_minutes=None)
        ],
        departure_time="08:00",
        return_to_depot=True
    )

    resp = optimize_route(payload)
    assert resp.departure_clock == "08:00"
    assert resp.estimated_finish_clock is not None
    assert resp.total_service_minutes == 80.0 # 40 + 40
    # Verifica que ambas as paradas de visita têm horários e duração de 40 min
    visit_stops = [s for s in resp.ordered_stops if s.action == "VISIT"]
    assert len(visit_stops) == 2
    for s in visit_stops:
        assert s.estimated_arrival_clock is not None
        assert s.estimated_departure_clock is not None
        assert s.service_duration_minutes == 40
        assert s.traffic_factor is not None

def test_route_geometry_feature_collection_legs():
    from app.domains.routing.infrastructure.osrm_provider import osrm_provider
    waypoints = [
        (-12.899, -38.324), # Base
        (-12.840, -38.250), # Ponto 1
        (-12.710, -38.120)  # Ponto 2
    ]
    geojson = osrm_provider.get_route_geometry(waypoints)
    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert len(geojson["features"]) == 2 # 2 trechos
    leg0 = geojson["features"][0]
    assert leg0["properties"]["leg_index"] == 0
    assert leg0["properties"]["color"].startswith("#")
    assert len(leg0["geometry"]["coordinates"]) >= 2



