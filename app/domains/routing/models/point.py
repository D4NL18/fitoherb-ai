from typing import Optional
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: Optional[str] = Field(None, description="Logradouro / Rua")
    number: Optional[str] = Field(None, description="Número")
    neighborhood: Optional[str] = Field(None, description="Bairro")
    city: Optional[str] = Field(None, description="Município")
    state: Optional[str] = Field("BA", description="Estado")
    postal_code: Optional[str] = Field(None, description="CEP")
    full_address: Optional[str] = Field(None, description="Endereço formatado legível")

class LocationPoint(BaseModel):
    id: str = Field(..., description="Identificador único")
    name: str = Field(..., description="Nome do estabelecimento ou base")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    address: Optional[Address] = Field(default=None, description="Dados do endereço legível")

class DeliveryStop(LocationPoint):
    priority: str = Field("REGULAR", description="CRITICAL, HIGH ou REGULAR")
    fixed_order: Optional[int] = Field(
        None, 
        ge=1, 
        description="Posição fixa desejada na sequência da rota (1-indexed: 1 para 1ª parada, etc.)"
    )
    demand: float = Field(10.0, description="Demanda/Carga estimada (neutro)")
    service_duration_minutes: Optional[int] = Field(
        None, 
        ge=0, 
        description="Tempo de atendimento no cliente em minutos (dwell time)"
    )
