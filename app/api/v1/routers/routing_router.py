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

from app.domains.routing.traffic_model import TrafficPredictor

@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(payload: OptimizeRouteRequest):
    """
    Otimiza a sequência de visitas de um vendedor único através de Algoritmo Genético TDVRP,
    respeitando estritamente posições fixadas manualmente, mitigando horários de pico conforme porte da cidade,
    eliminando laços de retrocesso e projetando a linha do tempo com horário de partida e atendimento.
    """
    if not payload.stops:
        raise HTTPException(status_code=400, detail="É necessário fornecer ao menos uma parada de visita.")

    # 1. Monta coordenadas: Nó 0 é o Depósito/Base, Nós 1..N são as paradas
    points = [(payload.depot.lat, payload.depot.lon)] + [(s.lat, s.lon) for s in payload.stops]

    # Identificação de Cidades para Previsão de Trânsito Dinâmica
    base_city = payload.depot.address.city if payload.depot.address else None
    points_cities = [base_city or ""]
    for s in payload.stops:
        points_cities.append(s.address.city if s.address and s.address.city else (base_city or ""))

    dep_time_mins = TrafficPredictor.parse_time_str(payload.departure_time)

    # 2. Obtém matrizes de tempo e distância viária via OSRM (com cache e fallback)
    durations_sec, distances_m = osrm_provider.get_matrix(points)

    # 3. Executa o Algoritmo Genético de Vendedor Único TDVRP com Trava de Ordem e 2-Opt
    deliveries_dict = [s.model_dump() for s in payload.stops]
    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations_sec,
        distances_matrix_m=distances_m,
        deliveries_data=deliveries_dict,
        return_to_depot=payload.return_to_depot,
        departure_time_minutes=dep_time_mins,
        default_service_minutes=payload.default_service_minutes,
        base_city=base_city,
        points_cities=points_cities,
        coordinates=points
    )
    result = solver.solve()

    ordered_sequence = result["ordered_sequence"]

    # 4. Constrói a linha do tempo de paradas com relógio real e status de tráfego
    ordered_stops: List[OrderedStopDto] = []
    waypoints_for_geo = [(payload.depot.lat, payload.depot.lon)]

    curr_clock_min = dep_time_mins
    total_transit_sec = 0.0
    total_service_min = 0.0
    peak_count = 0

    departure_clock_str = TrafficPredictor.format_clock(dep_time_mins)

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
        address=payload.depot.address,
        estimated_arrival_clock=departure_clock_str,
        estimated_departure_clock=departure_clock_str,
        service_duration_minutes=0,
        traffic_factor=1.0,
        traffic_condition="LIVRE"
    ))

    prev_node = 0

    for step_num, node_idx in enumerate(ordered_sequence, start=1):
        leg_dist_m = distances_m[prev_node][node_idx]
        leg_dist_km = leg_dist_m / 1000.0
        base_sec = durations_sec[prev_node][node_idx]

        orig_city = points_cities[prev_node]
        dest_city = points_cities[node_idx]

        # Multiplicador dinâmico de trânsito dependente do horário de saída do ponto anterior
        traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
            time_minutes_from_midnight=curr_clock_min,
            distance_km=leg_dist_km,
            origin_city=orig_city,
            dest_city=dest_city,
            base_city=base_city
        )

        if "PICO" in traffic_cond:
            peak_count += 1

        adjusted_leg_sec = base_sec * traffic_k
        total_transit_sec += adjusted_leg_sec
        curr_clock_min += (adjusted_leg_sec / 60.0)

        arrival_clock_str = TrafficPredictor.format_clock(curr_clock_min)

        stop_data = payload.stops[node_idx - 1]
        service_mins = stop_data.service_duration_minutes or payload.default_service_minutes
        total_service_min += service_mins
        curr_clock_min += service_mins

        departure_clock_str = TrafficPredictor.format_clock(curr_clock_min)
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
            arrival_time_minutes=round(total_transit_sec / 60.0, 1),
            address=stop_data.address,
            estimated_arrival_clock=arrival_clock_str,
            estimated_departure_clock=departure_clock_str,
            service_duration_minutes=service_mins,
            traffic_factor=traffic_k,
            traffic_condition=traffic_cond
        ))
        waypoints_for_geo.append((stop_data.lat, stop_data.lon))
        prev_node = node_idx

    # Retorno à base (se habilitado)
    if payload.return_to_depot:
        leg_dist_m = distances_m[prev_node][0]
        leg_dist_km = leg_dist_m / 1000.0
        base_sec = durations_sec[prev_node][0]

        orig_city = points_cities[prev_node]
        dest_city = base_city

        traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
            time_minutes_from_midnight=curr_clock_min,
            distance_km=leg_dist_km,
            origin_city=orig_city,
            dest_city=dest_city,
            base_city=base_city
        )

        if "PICO" in traffic_cond:
            peak_count += 1

        adjusted_leg_sec = base_sec * traffic_k
        total_transit_sec += adjusted_leg_sec
        curr_clock_min += (adjusted_leg_sec / 60.0)

        finish_clock_str = TrafficPredictor.format_clock(curr_clock_min)

        ordered_stops.append(OrderedStopDto(
            step=len(ordered_sequence) + 1,
            id=payload.depot.id,
            name=payload.depot.name,
            action="RETURN",
            lat=payload.depot.lat,
            lon=payload.depot.lon,
            is_fixed=True,
            priority="BASE",
            arrival_time_minutes=round(total_transit_sec / 60.0, 1),
            address=payload.depot.address,
            estimated_arrival_clock=finish_clock_str,
            estimated_departure_clock=finish_clock_str,
            service_duration_minutes=0,
            traffic_factor=traffic_k,
            traffic_condition=traffic_cond
        ))
        waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))

    # 5. Geometria viária curva a curva no formato GeoJSON
    geojson = osrm_provider.get_route_geometry(waypoints_for_geo)

    return OptimizeRouteResponse(
        total_time_minutes=round(total_transit_sec / 60.0, 1),
        total_distance_km=result["total_distance_km"],
        stops_count=len(payload.stops),
        ordered_stops=ordered_stops,
        geojson_geometry=geojson,
        fitness_history=result["fitness_history"],
        departure_clock=TrafficPredictor.format_clock(dep_time_mins),
        estimated_finish_clock=TrafficPredictor.format_clock(curr_clock_min),
        total_transit_minutes=round(total_transit_sec / 60.0, 1),
        total_service_minutes=round(float(total_service_min), 1),
        peak_hours_encountered=peak_count
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

