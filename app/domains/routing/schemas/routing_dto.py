from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domains.routing.models.point import LocationPoint, DeliveryStop, Address

class OptimizeRouteRequest(BaseModel):
    depot: LocationPoint = Field(..., description="Ponto de partida do vendedor (Base ou Fitoherb HQ)")
    stops: List[DeliveryStop] = Field(..., description="Lista de clientes ou drogarias a serem visitadas")
    return_to_depot: bool = Field(True, description="Define se o itinerário deve retornar à base ao final")
    departure_time: Optional[str] = Field(None, description="Horário planejado de saída da base (formato HH:MM, opcional)")
    default_service_minutes: Optional[int] = Field(None, ge=1, description="Tempo padrão ou fallback (opcional)")

class OrderedStopDto(BaseModel):
    step: int = Field(..., description="Número da etapa (0 é partida, 1..N são visitas, N+1 é retorno)")
    id: str = Field(..., description="ID da parada ou base")
    name: str = Field(..., description="Nome do local")
    action: str = Field(..., description="DEPARTURE, VISIT ou RETURN")
    is_fixed: bool = Field(False, description="Verdadeiro se a posição foi fixada manualmente pelo vendedor")
    fixed_order: Optional[int] = Field(None, description="Ordem fixada solicitada")
    priority: str = Field("REGULAR", description="Nível de prioridade")
    arrival_time_minutes: float = Field(..., description="Tempo de viagem acumulado em minutos")
    lat: Optional[float] = Field(None, description="Latitude do ponto")
    lon: Optional[float] = Field(None, description="Longitude do ponto")
    address: Optional[Address] = Field(None, description="Endereço legível (rua, número, bairro, cidade)")
    estimated_arrival_clock: Optional[str] = Field(None, description="Horário projetado de chegada no relógio (HH:MM)")
    estimated_departure_clock: Optional[str] = Field(None, description="Horário projetado de partida após atendimento (HH:MM)")
    service_duration_minutes: Optional[int] = Field(None, description="Tempo de atendimento nesta parada")
    traffic_factor: Optional[float] = Field(None, description="Multiplicador de trânsito aplicado no trecho de chegada")
    traffic_condition: Optional[str] = Field(None, description="Status do trânsito: LIVRE, MODERADO, PICO_MANHA, etc.")

class OptimizeRouteResponse(BaseModel):
    total_time_minutes: float
    total_distance_km: float
    stops_count: int
    ordered_stops: List[OrderedStopDto]
    geojson_geometry: Dict[str, Any]
    fitness_history: List[float]
    departure_clock: Optional[str] = Field(None, description="Horário de partida inicial da base")
    estimated_finish_clock: Optional[str] = Field(None, description="Horário previsto de término e retorno à base")
    total_transit_minutes: Optional[float] = Field(None, description="Tempo total gasto em deslocamento viário")
    total_service_minutes: Optional[float] = Field(None, description="Tempo total gasto em atendimentos a clientes")
    peak_hours_encountered: Optional[int] = Field(0, description="Quantidade de trechos percorridos sob horário de pico")

class ExportPdfRequest(BaseModel):
    seller_name: str = Field("Vendedor Fitoherb", description="Nome do vendedor")
    date: str = Field(..., description="Data do roteiro (dd/MM/yyyy)")
    total_time_minutes: float
    total_distance_km: float
    ordered_stops: List[OrderedStopDto]
    map_image_base64: Optional[str] = Field(None, description="Screenshot da tela do mapa em base64 PNG")
