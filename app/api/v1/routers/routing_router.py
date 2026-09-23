from fastapi import APIRouter, HTTPException, Response
from typing import List, Dict, Any, Optional
from app.domains.routing.schemas.routing_dto import (
    OptimizeRouteRequest,
    OptimizeRouteResponse,
    OrderedStopDto,
    ExportPdfRequest
)
from app.domains.routing.models.point import Address
from app.domains.routing.infrastructure.osrm_provider import osrm_provider
from app.domains.routing.services.routing_solver import RoutingGeneticSolver
from app.domains.routing.services.pdf_service import pdf_service

router = APIRouter(
    prefix="/routing",
    tags=["Roteirização Comercial com Algoritmo Genético"]
)

@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(payload: OptimizeRouteRequest):
    """
    Otimiza a sequência de visitas de um vendedor único através de Algoritmo Genético (Locked-OX),
    respeitando estritamente posições fixadas manualmente e minimizando tempo viário e quilometragem.
    """
    if not payload.stops:
        raise HTTPException(status_code=400, detail="É necessário fornecer ao menos uma parada de visita.")

    # 1. Monta coordenadas: Nó 0 é o Depósito/Base, Nós 1..N são as paradas
    points = [(payload.depot.lat, payload.depot.lon)] + [(s.lat, s.lon) for s in payload.stops]

    # 2. Obtém matrizes de tempo e distância viária via OSRM (com cache e fallback)
    durations_sec, distances_m = osrm_provider.get_matrix(points)

    # 3. Executa o Algoritmo Genético de Vendedor Único com Trava de Ordem
    deliveries_dict = [s.model_dump() for s in payload.stops]
    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations_sec,
        distances_matrix_m=distances_m,
        deliveries_data=deliveries_dict,
        return_to_depot=payload.return_to_depot
    )
    result = solver.solve()

    ordered_sequence = result["ordered_sequence"]

    # 4. Constrói a lista ordenada de paradas enriquecida com tempos e endereços legíveis
    ordered_stops: List[OrderedStopDto] = []
    waypoints_for_geo = [(payload.depot.lat, payload.depot.lon)]

    # Ponto de Partida (Step 0)
    ordered_stops.append(OrderedStopDto(
        step=0,
        id=payload.depot.id,
        name=payload.depot.name,
        action="DEPARTURE",
        lat=payload.depot.lat,
        lon=payload.depot.lon,
        is_fixed=True,
        priority="BASE",
        arrival_time_minutes=0.0,
        address=payload.depot.address
    ))

    accumulated_time_sec = 0.0
    prev_node = 0

    for step_num, node_idx in enumerate(ordered_sequence, start=1):
        accumulated_time_sec += durations_sec[prev_node][node_idx]
        stop_data = payload.stops[node_idx - 1]
        is_locked = stop_data.fixed_order is not None

        ordered_stops.append(OrderedStopDto(
            step=step_num,
            id=stop_data.id,
            name=stop_data.name,
            action="VISIT",
            lat=stop_data.lat,
            lon=stop_data.lon,
            is_fixed=is_locked,
            fixed_order=stop_data.fixed_order,
            priority=stop_data.priority,
            arrival_time_minutes=round(accumulated_time_sec / 60.0, 1),
            address=stop_data.address
        ))
        waypoints_for_geo.append((stop_data.lat, stop_data.lon))
        prev_node = node_idx

    # Retorno à base (se habilitado)
    if payload.return_to_depot:
        accumulated_time_sec += durations_sec[prev_node][0]
        ordered_stops.append(OrderedStopDto(
            step=len(ordered_sequence) + 1,
            id=payload.depot.id,
            name=payload.depot.name,
            action="RETURN",
            lat=payload.depot.lat,
            lon=payload.depot.lon,
            is_fixed=True,
            priority="BASE",
            arrival_time_minutes=round(accumulated_time_sec / 60.0, 1),
            address=payload.depot.address
        ))
        waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))

    # 5. Geometria viária curva a curva no formato GeoJSON
    geojson = osrm_provider.get_route_geometry(waypoints_for_geo)

    return OptimizeRouteResponse(
        total_time_minutes=result["total_time_minutes"],
        total_distance_km=result["total_distance_km"],
        stops_count=len(payload.stops),
        ordered_stops=ordered_stops,
        geojson_geometry=geojson,
        fitness_history=result["fitness_history"]
    )

@router.post("/export-pdf")
def export_route_pdf(payload: ExportPdfRequest):
    """
    Gera e faz o download do manifesto comercial de visitas em PDF oficial Fitoherb (Regra P-105).
    """
    pdf_bytes = pdf_service.generate_route_manifest(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=roteiro_fitoherb_{payload.date.replace('/', '-')}.pdf"
        }
    )

@router.get("/search-address")
def search_address_proxy(
    q: str, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
):
    """
    Proxy de busca de endereços no Nominatim com priorização de proximidade geográfica:
    Quando lat/lon da base do vendedor são fornecidos, aplica viewbox e ordena os resultados
    mais próximos da base em primeiro lugar (ex: Feira de Santana, Salvador, etc).
    """
    import urllib.parse
    import urllib.request
    import json
    import math

    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    if not q or not q.strip():
        return []

    encoded = urllib.parse.quote(q.strip())
    
    if lat is not None and lon is not None:
        delta = 1.5
        min_lon = lon - delta
        max_lon = lon + delta
        min_lat = lat - delta
        max_lat = lat + delta
        viewbox_str = f"{min_lon},{max_lat},{max_lon},{min_lat}"
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&addressdetails=1&countrycodes=br&viewbox={viewbox_str}&bounded=0&limit=12"
    else:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&addressdetails=1&countrycodes=br&limit=10"

    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "FitoherbCommercialRouting/1.0 (contato@fitoherb.com.br)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            items = json.loads(response.read().decode('utf-8'))
            if lat is not None and lon is not None and items:
                for it in items:
                    try:
                        it["_distance_km"] = _haversine(lat, lon, float(it["lat"]), float(it["lon"]))
                    except (ValueError, KeyError):
                        it["_distance_km"] = 99999.0
                items.sort(key=lambda x: x.get("_distance_km", 99999.0))
            return items
    except Exception as e:
        return []

@router.get("/reverse-geocode")
def reverse_geocode_proxy(lat: float, lon: float):
    """
    Proxy de geocodificação reversa no Nominatim com User-Agent corporativo.
    """
    import urllib.request
    import json

    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "FitoherbCommercialRouting/1.0 (contato@fitoherb.com.br)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {}

