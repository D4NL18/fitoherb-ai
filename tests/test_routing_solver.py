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

