from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domains.routing.models.point import LocationPoint, DeliveryStop, Address


class CityInsightDto(BaseModel):
    city: str = Field(..., description="Nome oficial do município")
    state: str = Field("BA", description="UF do município")
    ibge_code: str = Field(..., description="Código oficial IBGE de 7 dígitos")
    population: int = Field(..., description="População estimada oficial (IBGE)")
    city_tier: str = Field(
        ...,
        description="Classificação de porte: METROPOLIS, REGIONAL_HUB, MEDIUM_CITY ou SMALL_TOWN",
    )
    city_tier_label: str = Field(..., description="Rótulo legível do porte demográfico")
    demographic_density_hab_km2: float = Field(
        ..., description="Densidade demográfica em hab/km²"
    )
    gdp_per_capita_brl: float = Field(
        ..., description="PIB per capita estimado em R$"
    )
    regional_hub_name: str = Field(
        ..., description="Polo econômico ou região geográfica de influência"
    )
    commercial_potential_summary: str = Field(
        ..., description="Síntese estratégica e recomendação de foco comercial Fitoherb"
    )
    confirmed_stops_count: int = Field(
        0, description="Total de paradas confirmadas do vendedor na cidade"
    )
    suggested_leads_count: int = Field(
        0, description="Total de novas sugestões descobertas na cidade"
    )
    estimated_dwell_minutes: int = Field(
        0, description="Tempo total estimado de atendimento comercial no município (min)"
    )


class SuggestedStopDto(BaseModel):
    id: str = Field(..., description="Identificador único da sugestão (ex: sug-1)")
    name: str = Field(..., description="Nome comercial do estabelecimento sugerido")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    address: Optional[Address] = Field(None, description="Endereço legível estruturado")
    suggestion_category: str = Field(
        ..., description="FARMACIA ou PRODUTOS_NATURAIS"
    )
    category_label: str = Field(
        ..., description="Rótulo amigável da categoria comercial"
    )
    detour_distance_km: float = Field(
        0.0, description="Distância adicional de desvio estimada em km"
    )
    detour_time_minutes: float = Field(
        0.0, description="Tempo adicional de desvio estimado em minutos"
    )
    nearest_stop_id: Optional[str] = Field(
        None, description="ID da parada da rota mais próxima"
    )
    nearest_stop_name: Optional[str] = Field(
        None, description="Nome da parada da rota mais próxima"
    )
    is_suggestion: bool = Field(
        True, description="Identificador booleano fixo de sugestão proativa (P-108)"
    )


class OptimizeRouteRequest(BaseModel):
    depot: LocationPoint = Field(
        ..., description="Ponto de partida do vendedor (Base ou Fitoherb HQ)"
    )
    stops: List[DeliveryStop] = Field(
        ..., description="Lista de clientes ou drogarias a serem visitadas"
    )
    return_to_depot: bool = Field(
        True, description="Define se o itinerário deve retornar à base ao final"
    )
    departure_time: Optional[str] = Field(
        None, description="Horário planejado de saída da base (formato HH:MM, opcional)"
    )
    default_service_minutes: Optional[int] = Field(
        None, ge=1, description="Tempo padrão ou fallback (opcional)"
    )
    discover_suggestions: bool = Field(
        True,
        description="Quando verdadeiro, descobre farmácias e lojas de produtos naturais no trajeto (P-108)",
    )
    max_suggestions: int = Field(
        5,
        ge=1,
        le=12,
        description="Quantidade máxima de sugestões de leads injetadas na rota",
    )
    excluded_locations: List[LocationPoint] = Field(
        default_factory=list,
        description="Locais salvos/favoritos ou descartados pelo vendedor que não devem ser sugeridos",
    )


class OrderedStopDto(BaseModel):
    step: int = Field(
        ..., description="Número da etapa (0 é partida, 1..N são visitas, N+1 é retorno)"
    )
    id: str = Field(..., description="ID da parada ou base")
    name: str = Field(..., description="Nome do local")
    action: str = Field(..., description="DEPARTURE, VISIT ou RETURN")
    is_fixed: bool = Field(
        False, description="Verdadeiro se a posição foi fixada manualmente pelo vendedor"
    )
    fixed_order: Optional[int] = Field(None, description="Ordem fixada solicitada")
    priority: str = Field("REGULAR", description="Nível de prioridade")
    arrival_time_minutes: float = Field(
        ..., description="Tempo de viagem acumulado em minutos"
    )
    lat: Optional[float] = Field(None, description="Latitude do ponto")
    lon: Optional[float] = Field(None, description="Longitude do ponto")
    address: Optional[Address] = Field(
        None, description="Endereço legível (rua, número, bairro, cidade)"
    )
    estimated_arrival_clock: Optional[str] = Field(
        None, description="Horário projetado de chegada no relógio (HH:MM)"
    )
    estimated_departure_clock: Optional[str] = Field(
        None, description="Horário projetado de partida após atendimento (HH:MM)"
    )
    service_duration_minutes: Optional[int] = Field(
        None, description="Tempo de atendimento nesta parada"
    )
    traffic_factor: Optional[float] = Field(
        None, description="Multiplicador de trânsito aplicado no trecho de chegada"
    )
    traffic_condition: Optional[str] = Field(
        None, description="Status do trânsito: LIVRE, MODERADO, PICO_MANHA, etc."
    )
    target_arrival_time: Optional[str] = Field(
        None, description="Horário marcado para a visita (HH:MM)"
    )
    has_time_conflict: bool = Field(
        False,
        description="Verdadeiro se houve atraso ou conflito em relação ao horário marcado",
    )
    time_conflict_message: Optional[str] = Field(
        None, description="Mensagem de alerta detalhada sobre atraso ou conflito viário"
    )
    is_suggestion: bool = Field(
        False,
        description="Verdadeiro se a parada é uma sugestão proativa descoberta pela IA (P-108)",
    )
    suggestion_category: Optional[str] = Field(
        None, description="FARMACIA ou PRODUTOS_NATURAIS"
    )
    detour_distance_km: Optional[float] = Field(
        None, description="Desvio viário estimado em km"
    )
    detour_time_minutes: Optional[float] = Field(
        None, description="Tempo adicional estimado do desvio em minutos"
    )


class OptimizeRouteResponse(BaseModel):
    total_time_minutes: float
    total_distance_km: float
    stops_count: int
    ordered_stops: List[OrderedStopDto]
    geojson_geometry: Dict[str, Any]
    fitness_history: List[float]
    departure_clock: Optional[str] = Field(
        None, description="Horário de partida inicial da base"
    )
    estimated_finish_clock: Optional[str] = Field(
        None, description="Horário previsto de término e retorno à base"
    )
    total_transit_minutes: Optional[float] = Field(
        None, description="Tempo total gasto em deslocamento viário"
    )
    total_service_minutes: Optional[float] = Field(
        None, description="Tempo total gasto em atendimentos a clientes"
    )
    peak_hours_encountered: Optional[int] = Field(
        0, description="Quantidade de trechos percorridos sob horário de pico"
    )
    has_any_time_conflict: bool = Field(
        False,
        description="Verdadeiro se há pelo menos um conflito/atraso de horário no itinerário",
    )
    time_conflict_count: int = Field(
        0, description="Quantidade total de paradas com conflito/atraso de horário"
    )
    city_insights: List[CityInsightDto] = Field(
        default_factory=list,
        description="Relatório de inteligência demográfica e comercial por cidade da rota (P-107)",
    )
    suggested_stops: List[SuggestedStopDto] = Field(
        default_factory=list,
        description="Lista de oportunidades sugeridas no corredor da rota (P-108)",
    )


class ExportPdfRequest(BaseModel):
    seller_name: str = Field("Vendedor Fitoherb", description="Nome do vendedor")
    date: str = Field(..., description="Data do roteiro (dd/MM/yyyy)")
    total_time_minutes: float
    total_distance_km: float
    ordered_stops: List[OrderedStopDto]
    map_image_base64: Optional[str] = Field(
        None, description="Screenshot da tela do mapa em base64 PNG"
    )
    city_insights: List[CityInsightDto] = Field(
        default_factory=list,
        description="Dados demográficos e comerciais das cidades da rota para o PDF (P-107)",
    )
