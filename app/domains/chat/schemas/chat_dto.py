from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ChatMessageItem(BaseModel):
    role: str = Field(..., description="Papel da mensagem: user ou assistant")
    content: str = Field(..., max_length=500, description="Conteúdo da mensagem")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("Role deve ser 'user' ou 'assistant'")
        return v


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Mensagem do usuário limitada a 255 caracteres (P-306)"
    )
    history: Optional[List[ChatMessageItem]] = Field(
        default_factory=list,
        description="Histórico recente da conversa"
    )

    @field_validator("message")
    @classmethod
    def sanitize_and_check_message(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Mensagem não pode ser vazia")
        if len(cleaned) > 255:
            raise ValueError("Mensagem excede o limite máximo de 255 caracteres")
        return cleaned


class CatalogFiltersDto(BaseModel):
    category: List[str] = Field(default_factory=list)
    supplier: List[str] = Field(default_factory=list)
    search: str = Field(default="")


class ChatActionDto(BaseModel):
    type: str = Field("NONE", description="Ação a ser executada: NAVIGATE_CATALOG ou NONE")
    auto_redirect: bool = Field(False, description="Se o frontend deve redirecionar automaticamente")
    filters: CatalogFiltersDto = Field(default_factory=CatalogFiltersDto)


class ProductSnippetDto(BaseModel):
    name: str
    slug: str
    image_url: Optional[str] = ""
    category: Optional[str] = ""
    supplier: Optional[str] = ""


class ChatResponseData(BaseModel):
    reply: str
    intent: str
    action: ChatActionDto = Field(default_factory=ChatActionDto)
    products: List[ProductSnippetDto] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    data: ChatResponseData
    meta: Dict[str, Any] = Field(default_factory=dict)
