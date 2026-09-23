from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domains.routing.models.point import LocationPoint, DeliveryStop, Address

class OptimizeRouteRequest(BaseModel):
    depot: LocationPoint = Field(..., description="Ponto de partida do vendedor (Base ou Fitoherb HQ)")
    stops: List[DeliveryStop] = Field(..., description="Lista de clientes ou drogarias a serem visitadas")
    return_to_depot: bool = Field(True, description="Define se o itinerário deve retornar à base ao final")

class OrderedStopDto(BaseModel):
    step: int = Field(..., description="Número da etapa (0 é partida, 1..N são visitas, N+1 é retorno)")
    id: str = Field(..., description="ID da parada ou base")
    name: str = Field(..., description="Nome do local")
    action: str = Field(..., description="DEPARTURE, VISIT ou RETURN")
    is_fixed: bool = Field(False, description="Verdadeiro se a posição foi fixada manualmente pelo vendedor")
    fixed_order: Optional[int] = Field(None, description="Ordem fixada solicitada")
    priority: str = Field("REGULAR", description="Nível de prioridade")
    arrival_time_minutes: float = Field(..., description="Tempo de viagem acumulado em minutos")
    address: Optional[Address] = Field(None, description="Endereço legível (rua, número, bairro, cidade)")

class OptimizeRouteResponse(BaseModel):
    total_time_minutes: float
    total_distance_km: float
    stops_count: int
    ordered_stops: List[OrderedStopDto]
    geojson_geometry: Dict[str, Any]
    fitness_history: List[float]

class ExportPdfRequest(BaseModel):
    seller_name: str = Field("Vendedor Fitoherb", description="Nome do vendedor")
    date: str = Field(..., description="Data do roteiro (dd/MM/yyyy)")
    total_time_minutes: float
    total_distance_km: float
    ordered_stops: List[OrderedStopDto]
    map_image_base64: Optional[str] = Field(None, description="Screenshot da tela do mapa em base64 PNG")
