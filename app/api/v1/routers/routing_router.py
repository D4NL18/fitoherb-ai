from fastapi import APIRouter, HTTPException, Response
from typing import List, Dict, Any, Optional
from app.domains.routing.schemas.routing_dto import (
    OptimizeRouteRequest,
    OptimizeRouteResponse,
    OrderedStopDto,
    SuggestedStopDto,
    ExportPdfRequest,
)
from app.domains.routing.models.point import Address, DeliveryStop
from app.domains.routing.infrastructure.osrm_provider import osrm_provider
from app.domains.routing.services.routing_solver import RoutingGeneticSolver
from app.domains.routing.services.pdf_service import pdf_service
from app.domains.routing.services.city_insights_service import city_insights_service
from app.domains.routing.services.poi_discovery_service import poi_discovery_service
from app.domains.routing.traffic_model import TrafficPredictor

router = APIRouter(
    prefix="/routing",
    tags=["Roteirização Comercial com Algoritmo Genético"],
)


@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(payload: OptimizeRouteRequest):
    """
    Otimiza a sequência de visitas de um vendedor único através de Algoritmo Genético TDVRP,
    respeitando estritamente posições fixadas manualmente, mitigando horários de pico conforme porte da cidade,
    descobrindo oportunidades comerciais no corredor da rota (P-108) e gerando o Relatório de Cidades (P-107).
    """
    if not payload.stops:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer ao menos uma parada de visita.",
        )

    # Identifica paradas originais com duração de atendimento explícita e positiva
    explicit_durations = [
        s.service_duration_minutes
        for s in payload.stops
        if s.service_duration_minutes is not None and s.service_duration_minutes > 0
    ]

    dep_time_mins = TrafficPredictor.parse_time_str(payload.departure_time)

    # O cálculo temporal e trânsito dinâmico só é ativado se houver horário de partida E ao menos um ponto com tempo
    is_temporal_active = (dep_time_mins is not None) and (len(explicit_durations) > 0)

    if is_temporal_active:
        avg_service_min = int(round(sum(explicit_durations) / len(explicit_durations)))
    else:
        dep_time_mins = None
        avg_service_min = 0

    # Descoberta proativa de leads (P-108) quando solicitada ou quando os pontos possuem contexto de endereço
    should_discover = bool(payload.discover_suggestions) and (
        "discover_suggestions" in payload.model_fields_set
        or payload.depot.address is not None
        or any(s.address is not None for s in payload.stops)
    )

    suggested_stops: List[SuggestedStopDto] = []
    effective_stops: List[DeliveryStop] = list(payload.stops)

    if should_discover:
        suggested_stops = poi_discovery_service.discover_along_route(
            depot=payload.depot,
            stops=payload.stops,
            excluded_locations=payload.excluded_locations,
            max_suggestions=payload.max_suggestions,
        )
        existing_ids = {s.id for s in effective_stops}
        suggestion_service_mins = (
            payload.default_service_minutes
            or (avg_service_min if is_temporal_active else 15)
        )
        for sug in suggested_stops:
            if sug.id not in existing_ids:
                effective_stops.append(
                    DeliveryStop(
                        id=sug.id,
                        name=sug.name,
                        lat=sug.lat,
                        lon=sug.lon,
                        address=sug.address,
                        priority="REGULAR",
                        fixed_order=None,
                        demand=5.0,
                        service_duration_minutes=suggestion_service_mins if is_temporal_active else None,
                        is_suggestion=True,
                        suggestion_category=sug.suggestion_category,
                        detour_distance_km=sug.detour_distance_km,
                        detour_time_minutes=sug.detour_time_minutes,
                    )
                )
                existing_ids.add(sug.id)

    # 1. Monta coordenadas: Nó 0 é o Depósito/Base, Nós 1..N são as paradas (confirmadas + sugestões)
    points = [(payload.depot.lat, payload.depot.lon)] + [
        (s.lat, s.lon) for s in effective_stops
    ]

    # Identificação de Cidades para Previsão de Trânsito Dinâmica
    base_city = payload.depot.address.city if payload.depot.address else None
    points_cities = [base_city or ""]
    for s in effective_stops:
        points_cities.append(
            s.address.city if s.address and s.address.city else (base_city or "")
        )

    # 2. Obtém matrizes de tempo e distância viária via OSRM (com cache e fallback)
    durations_sec, distances_m = osrm_provider.get_matrix(points)

    # 3. Executa o Algoritmo Genético de Vendedor Único TDVRP com Trava de Ordem e 2-Opt
    deliveries_dict = []
    for s in effective_stops:
        d = s.model_dump()
        if is_temporal_active:
            if not d.get("service_duration_minutes") or d["service_duration_minutes"] <= 0:
                d["service_duration_minutes"] = avg_service_min
        else:
            d["service_duration_minutes"] = 0
        deliveries_dict.append(d)

    solver = RoutingGeneticSolver(
        durations_matrix_sec=durations_sec,
        distances_matrix_m=distances_m,
        deliveries_data=deliveries_dict,
        return_to_depot=payload.return_to_depot,
        departure_time_minutes=dep_time_mins,
        default_service_minutes=avg_service_min if is_temporal_active else 0,
        base_city=base_city,
        points_cities=points_cities,
        coordinates=points,
    )
    result = solver.solve()

    return _evaluate_ordered_route(
        payload=payload,
        effective_stops=effective_stops,
        suggested_stops=suggested_stops,
        ordered_sequence=result["ordered_sequence"],
        total_distance_km=result["total_distance_km"],
        fitness_history=result["fitness_history"],
        points_cities=points_cities,
        base_city=base_city,
        durations_sec=durations_sec,
        distances_m=distances_m,
        is_temporal_active=is_temporal_active,
        dep_time_mins=dep_time_mins,
        avg_service_min=avg_service_min,
    )


@router.post("/recalculate", response_model=OptimizeRouteResponse)
def recalculate_route(payload: OptimizeRouteRequest):
    """
    Recalcula as métricas viárias, horários projetados, relatório de cidades (P-107) e rota GeoJSON
    mantendo rigorosamente a lista e a ordem das paradas fornecidas após o manejo em lote (P-109),
    sem reinjetar sugestões descartadas.
    """
    if not payload.stops:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer ao menos uma parada de visita.",
        )

    effective_stops: List[DeliveryStop] = list(payload.stops)

    # 1. Monta coordenadas: Nó 0 é o Depósito/Base, Nós 1..N são as paradas na ordem enviada
    points = [(payload.depot.lat, payload.depot.lon)] + [
        (s.lat, s.lon) for s in effective_stops
    ]

    base_city = payload.depot.address.city if payload.depot.address else None
    points_cities = [base_city or ""]
    for s in effective_stops:
        points_cities.append(
            s.address.city if s.address and s.address.city else (base_city or "")
        )

    explicit_durations = [
        s.service_duration_minutes
        for s in effective_stops
        if s.service_duration_minutes is not None and s.service_duration_minutes > 0
    ]
    dep_time_mins = TrafficPredictor.parse_time_str(payload.departure_time)
    is_temporal_active = (dep_time_mins is not None) and (len(explicit_durations) > 0)

    if is_temporal_active:
        avg_service_min = int(round(sum(explicit_durations) / len(explicit_durations)))
    else:
        dep_time_mins = None
        avg_service_min = 0

    # 2. Matrizes OSRM
    durations_sec, distances_m = osrm_provider.get_matrix(points)

    # 3. Sequência idêntica à ordem recebida das paradas: [1, 2, ..., N]
    ordered_sequence = list(range(1, len(effective_stops) + 1))

    # Calcula distância viária real acumulada
    total_dist_m = 0.0
    prev = 0
    for node in ordered_sequence:
        total_dist_m += distances_m[prev][node]
        prev = node
    if payload.return_to_depot:
        total_dist_m += distances_m[prev][0]
    total_dist_km = round(total_dist_m / 1000.0, 2)

    return _evaluate_ordered_route(
        payload=payload,
        effective_stops=effective_stops,
        suggested_stops=[],
        ordered_sequence=ordered_sequence,
        total_distance_km=total_dist_km,
        fitness_history=[],
        points_cities=points_cities,
        base_city=base_city,
        durations_sec=durations_sec,
        distances_m=distances_m,
        is_temporal_active=is_temporal_active,
        dep_time_mins=dep_time_mins,
        avg_service_min=avg_service_min,
    )


def _evaluate_ordered_route(
    payload: OptimizeRouteRequest,
    effective_stops: List[DeliveryStop],
    suggested_stops: List[SuggestedStopDto],
    ordered_sequence: List[int],
    total_distance_km: float,
    fitness_history: List[float],
    points_cities: List[str],
    base_city: Optional[str],
    durations_sec: List[List[float]],
    distances_m: List[List[float]],
    is_temporal_active: bool,
    dep_time_mins: Optional[int],
    avg_service_min: int,
) -> OptimizeRouteResponse:
    # 4. Constrói a linha do tempo de paradas com relógio real e status de tráfego
    ordered_stops: List[OrderedStopDto] = []
    waypoints_for_geo = [(payload.depot.lat, payload.depot.lon)]

    curr_clock_min = dep_time_mins
    total_transit_sec = 0.0
    total_service_min = 0.0
    peak_count = 0
    time_conflict_count = 0

    departure_clock_str = (
        TrafficPredictor.format_clock(dep_time_mins) if is_temporal_active else None
    )

    # Ponto de Partida (Step 0)
    ordered_stops.append(
        OrderedStopDto(
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
            service_duration_minutes=0 if is_temporal_active else None,
            traffic_factor=1.0 if is_temporal_active else None,
            traffic_condition="LIVRE" if is_temporal_active else None,
        )
    )

    prev_node = 0

    for step_num, node_idx in enumerate(ordered_sequence, start=1):
        leg_dist_m = distances_m[prev_node][node_idx]
        leg_dist_km = leg_dist_m / 1000.0
        base_sec = durations_sec[prev_node][node_idx]

        orig_city = points_cities[prev_node]
        dest_city = points_cities[node_idx]

        if is_temporal_active:
            traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
                time_minutes_from_midnight=curr_clock_min,
                distance_km=leg_dist_km,
                origin_city=orig_city,
                dest_city=dest_city,
                base_city=base_city,
            )
            if "PICO" in traffic_cond:
                peak_count += 1
        else:
            traffic_k, traffic_cond = 1.0, None

        adjusted_leg_sec = base_sec * traffic_k
        total_transit_sec += adjusted_leg_sec

        actual_arrival_min = None
        if is_temporal_active and curr_clock_min is not None:
            curr_clock_min += adjusted_leg_sec / 60.0
            actual_arrival_min = curr_clock_min
            arrival_clock_str = TrafficPredictor.format_clock(curr_clock_min)
        else:
            arrival_clock_str = None

        stop_data = effective_stops[node_idx - 1]

        has_time_conflict = False
        time_conflict_message = None

        # Verificação de Inviabilidade / Conflito em relação ao horário marcado (Regra P-106)
        if (
            is_temporal_active
            and stop_data.target_arrival_time
            and actual_arrival_min is not None
        ):
            target_mins = TrafficPredictor.parse_time_str(stop_data.target_arrival_time)
            if target_mins is not None:
                if actual_arrival_min > target_mins:
                    delay = int(round(actual_arrival_min - target_mins))
                    has_time_conflict = True
                    time_conflict_message = f"Previsão de chegada às {arrival_clock_str} ({delay} min após o horário marcado de {stop_data.target_arrival_time})"
                    time_conflict_count += 1
                elif actual_arrival_min < target_mins:
                    curr_clock_min = float(target_mins)

        if is_temporal_active:
            service_mins = (
                stop_data.service_duration_minutes
                if (
                    stop_data.service_duration_minutes
                    and stop_data.service_duration_minutes > 0
                )
                else avg_service_min
            )
            total_service_min += service_mins
            if curr_clock_min is not None:
                curr_clock_min += service_mins
            departure_clock_str = TrafficPredictor.format_clock(curr_clock_min)
        else:
            service_mins = None
            departure_clock_str = None

        is_locked = stop_data.fixed_order is not None

        ordered_stops.append(
            OrderedStopDto(
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
                traffic_factor=traffic_k if is_temporal_active else None,
                traffic_condition=traffic_cond,
                target_arrival_time=stop_data.target_arrival_time,
                has_time_conflict=has_time_conflict,
                time_conflict_message=time_conflict_message,
                is_suggestion=bool(stop_data.is_suggestion),
                suggestion_category=stop_data.suggestion_category,
                detour_distance_km=stop_data.detour_distance_km,
                detour_time_minutes=stop_data.detour_time_minutes,
            )
        )
        waypoints_for_geo.append((stop_data.lat, stop_data.lon))
        prev_node = node_idx

    # Retorno à base (se habilitado)
    if payload.return_to_depot:
        leg_dist_m = distances_m[prev_node][0]
        leg_dist_km = leg_dist_m / 1000.0
        base_sec = durations_sec[prev_node][0]

        orig_city = points_cities[prev_node]
        dest_city = base_city

        if is_temporal_active:
            traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
                time_minutes_from_midnight=curr_clock_min,
                distance_km=leg_dist_km,
                origin_city=orig_city,
                dest_city=dest_city,
                base_city=base_city,
            )
            if "PICO" in traffic_cond:
                peak_count += 1
        else:
            traffic_k, traffic_cond = 1.0, None

        adjusted_leg_sec = base_sec * traffic_k
        total_transit_sec += adjusted_leg_sec

        if is_temporal_active and curr_clock_min is not None:
            curr_clock_min += adjusted_leg_sec / 60.0
            finish_clock_str = TrafficPredictor.format_clock(curr_clock_min)
        else:
            finish_clock_str = None

        ordered_stops.append(
            OrderedStopDto(
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
                service_duration_minutes=0 if is_temporal_active else None,
                traffic_factor=traffic_k if is_temporal_active else None,
                traffic_condition=traffic_cond,
            )
        )
        waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))

    # 5. Geometria viária curva a curva no formato GeoJSON
    geojson = osrm_provider.get_route_geometry(waypoints_for_geo)

    # 6. Inteligência Demográfica e Comercial por Cidade (Regra P-107)
    default_srv = (
        avg_service_min
        if (is_temporal_active and avg_service_min > 0)
        else (payload.default_service_minutes or 20)
    )
    city_insights = city_insights_service.build_city_insights(
        depot=payload.depot,
        ordered_stops=ordered_stops,
        suggested_stops=suggested_stops,
        default_service_minutes=default_srv,
    )

    return OptimizeRouteResponse(
        total_time_minutes=round(total_transit_sec / 60.0, 1),
        total_distance_km=total_distance_km,
        stops_count=len(effective_stops),
        ordered_stops=ordered_stops,
        geojson_geometry=geojson,
        fitness_history=fitness_history,
        departure_clock=(
            TrafficPredictor.format_clock(dep_time_mins) if is_temporal_active else None
        ),
        estimated_finish_clock=(
            TrafficPredictor.format_clock(curr_clock_min) if is_temporal_active else None
        ),
        total_transit_minutes=(
            round(total_transit_sec / 60.0, 1) if is_temporal_active else None
        ),
        total_service_minutes=(
            round(float(total_service_min), 1) if is_temporal_active else None
        ),
        peak_hours_encountered=peak_count if is_temporal_active else 0,
        has_any_time_conflict=(time_conflict_count > 0),
        time_conflict_count=time_conflict_count,
        city_insights=city_insights,
        suggested_stops=suggested_stops,
    )


@router.post("/export-pdf")
def export_route_pdf(payload: ExportPdfRequest):
    """
    Gera e faz o download do manifesto comercial de visitas em PDF oficial Fitoherb (Regra P-105 e P-107).
    """
    pdf_bytes = pdf_service.generate_route_manifest(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=roteiro_fitoherb_{payload.date.replace('/', '-')}.pdf"
        },
    )


@router.get("/search-address")
def search_address_proxy(
    q: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
):
    """
    Proxy de busca de endereços inteligente com tolerância a erros (fuzzy) e priorização
    por proximidade geográfica (Photon OSM + Nominatim com fallback).
    """
    import urllib.parse
    import urllib.request
    import json
    import math

    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _format_photon_feature(feature):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [0, 0])
        f_lon = float(coords[0])
        f_lat = float(coords[1])
        name = props.get("name") or props.get("street") or ""
        street = props.get("street", "")
        house_num = props.get("housenumber", "")
        suburb = props.get("district") or props.get("suburb", "")
        city = props.get("city", "")
        state = props.get("state", "")
        postcode = props.get("postcode", "")
        country = props.get("country", "Brasil")

        address = {
            "road": street,
            "house_number": house_num,
            "suburb": suburb,
            "city": city,
            "state": state,
            "postcode": postcode,
            "country": country,
        }

        parts = [
            p
            for p in [
                name,
                f"{street} {house_num}".strip() if street else "",
                suburb,
                city,
                state,
                country,
            ]
            if p
        ]
        display_name = ", ".join(dict.fromkeys(parts))

        return {
            "lat": str(f_lat),
            "lon": str(f_lon),
            "name": name,
            "display_name": display_name,
            "address": address,
        }

    def _normalize_pt(text: str) -> str:
        if not text:
            return ""
        import unicodedata

        s = unicodedata.normalize("NFD", text)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower().strip()

    def _generate_pt_variants(text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []
        variants = [cleaned]
        norm = _normalize_pt(cleaned)
        if norm and norm not in variants:
            variants.append(norm)

        expanded = set(variants)
        for v in list(variants):
            if "ua" in v:
                expanded.add(v.replace("ua", "oa"))
            if "oa" in v:
                expanded.add(v.replace("oa", "ua"))
            if v.endswith("oan"):
                expanded.add(v[:-3] + "uan")
                expanded.add(v[:-3] + "ua")
                expanded.add(v[:-3] + "uã")
            elif v.endswith("uan"):
                expanded.add(v[:-3] + "oan")
                expanded.add(v[:-3] + "ua")
                expanded.add(v[:-3] + "uã")
            elif v.endswith("ua") or v.endswith("uã"):
                stem = v[:-2]
                expanded.add(stem + "oan")
                expanded.add(stem + "uan")
                expanded.add(stem + "ua")
                expanded.add(stem + "uã")

            if "ç" in v:
                expanded.add(v.replace("ç", "ss"))
                expanded.add(v.replace("ç", "s"))
            if "ss" in v:
                expanded.add(v.replace("ss", "ç"))
                expanded.add(v.replace("ss", "s"))
            if "z" in v:
                expanded.add(v.replace("z", "s"))
            if "s" in v:
                expanded.add(v.replace("s", "z"))

        result_variants = [cleaned]
        for v in expanded:
            if v and v not in result_variants:
                result_variants.append(v)
        return result_variants

    q_clean = q.strip() if q else ""
    if not q_clean:
        return []

    queries = _generate_pt_variants(q_clean)
    items = []
    seen_coords = set()

    def _add_item(item):
        try:
            coord_key = f"{round(float(item['lat']), 4)}_{round(float(item['lon']), 4)}"
            if coord_key not in seen_coords:
                seen_coords.add(coord_key)
                items.append(item)
        except (ValueError, KeyError, TypeError):
            items.append(item)

    for query_variant in queries:
        encoded = urllib.parse.quote(query_variant)
        photon_url = f"https://photon.komoot.io/api/?q={encoded}&limit=15"
        if lat is not None and lon is not None:
            photon_url += f"&lat={lat}&lon={lon}"

        req_photon = urllib.request.Request(
            photon_url,
            headers={
                "User-Agent": "FitoherbCommercialRouting/1.0 (contato@fitoherb.com.br)"
            },
        )
        try:
            with urllib.request.urlopen(req_photon, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict) and "features" in data:
                    for feat in data["features"]:
                        _add_item(_format_photon_feature(feat))
                elif isinstance(data, list):
                    for d in data:
                        _add_item(d)
        except Exception:
            pass

    if not items:
        for query_variant in queries[:3]:
            encoded = urllib.parse.quote(query_variant)
            if lat is not None and lon is not None:
                delta = 1.5
                viewbox_str = (
                    f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}"
                )
                nom_url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&addressdetails=1&countrycodes=br&viewbox={viewbox_str}&bounded=0&limit=12"
            else:
                nom_url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&addressdetails=1&countrycodes=br&limit=10"

            req_nom = urllib.request.Request(
                nom_url,
                headers={
                    "User-Agent": "FitoherbCommercialRouting/1.0 (contato@fitoherb.com.br)"
                },
            )
            try:
                with urllib.request.urlopen(req_nom, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list):
                        for d in data:
                            _add_item(d)
            except Exception:
                pass

            if items:
                break

    if lat is not None and lon is not None and items:
        for it in items:
            try:
                it["_distance_km"] = _haversine(
                    lat, lon, float(it["lat"]), float(it["lon"])
                )
            except (ValueError, KeyError, TypeError):
                it["_distance_km"] = 99999.0
        items.sort(key=lambda x: x.get("_distance_km", 99999.0))

    return items


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
        headers={
            "User-Agent": "FitoherbCommercialRouting/1.0 (contato@fitoherb.com.br)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}
