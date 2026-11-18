import hmac
import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from app.domains.chat.schemas.chat_dto import (
    CatalogRefreshRequest,
    ChatRequest,
    ChatResponse,
)
from app.domains.chat.services.cache_service import ConversationCacheService
from app.domains.chat.services.chat_orchestrator import ChatOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Assistente Virtual Inteligente (Chatbot Gemini)"],
)

# Instância singleton do orquestrador
_orchestrator = ChatOrchestrator()


def get_orchestrator() -> ChatOrchestrator:
    return _orchestrator


@router.post("/messages", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """
    Recebe a mensagem do usuário (máx. 255 caracteres) e retorna a resposta
    do assistente virtual com ação de auto-redirecionamento quando aplicável.
    """
    try:
        return orchestrator.process_message(payload)
    except Exception as exc:
        logger.error("Erro interno no processamento do assistente (%s).", type(exc).__name__)
        raise HTTPException(
            status_code=500,
            detail="Erro interno no processamento do assistente.",
        )


@router.post("/catalog/refresh")
def refresh_catalog(
    x_internal_refresh_token: Optional[str] = Header(
        default=None, alias="X-Internal-Refresh-Token"
    ),
    payload: Optional[CatalogRefreshRequest] = Body(default=None),
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> Any:
    """
    Recarrega o CatalogIndex diretamente do PostgreSQL (produtos ativos apenas),
    incrementa catalog_version e invalida o cache L1 (0 tokens LLM).
    """
    expected_token = os.getenv("INTERNAL_REFRESH_TOKEN")
    if not expected_token or not expected_token.strip():
        return JSONResponse(
            status_code=503,
            content={
                "status": "SERVICE_UNAVAILABLE",
                "code": "REFRESH_TOKEN_NOT_CONFIGURED",
                "message": "Token interno de refresh não configurado no ambiente.",
            },
        )

    if not x_internal_refresh_token or not x_internal_refresh_token.strip():
        return JSONResponse(
            status_code=401,
            content={
                "status": "UNAUTHORIZED",
                "code": "MISSING_REFRESH_TOKEN",
                "message": "Header X-Internal-Refresh-Token obrigatório.",
            },
        )

    if not hmac.compare_digest(
        x_internal_refresh_token.encode("utf-8"),
        expected_token.encode("utf-8"),
    ):
        return JSONResponse(
            status_code=403,
            content={
                "status": "FORBIDDEN",
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Token interno de refresh inválido.",
            },
        )

    refreshed = orchestrator.catalog_index.load_from_db()
    if not refreshed:
        return JSONResponse(
            status_code=503,
            content={
                "status": "SERVICE_UNAVAILABLE",
                "code": "CATALOG_REFRESH_FAILED",
                "message": "Falha transitória ao recarregar o catálogo; snapshot anterior preservado.",
            },
        )

    new_version = ConversationCacheService.bump_catalog_version()
    orchestrator.catalog_index.set_catalog_version(new_version)
    trigger_reason = payload.reason if payload and payload.reason else "MANUAL_REFRESH"

    return {
        "data": {
            "refreshed": True,
            "catalog_items": len(orchestrator.catalog_index.products),
            "categories_count": len(orchestrator.catalog_index.categories),
            "suppliers_count": len(orchestrator.catalog_index.suppliers),
            "cache_cleared": True,
            "catalog_version": new_version,
            "refreshed_at": orchestrator.catalog_index.last_refresh,
        },
        "meta": {
            "service": "fitoherb-ai-chat",
            "trigger_reason": trigger_reason,
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0},
        },
    }


@router.get("/health")
def chat_health(
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> Dict[str, Any]:
    """
    Probe de saúde e prontidão do subsistema de chat e do cliente Gemini.
    """
    return {
        "data": {
            "status": "UP",
            "catalog_indexed_items": len(orchestrator.catalog_index.products),
            "catalog_last_refresh": orchestrator.catalog_index.last_refresh,
            "catalog_version": ConversationCacheService.get_catalog_version(),
            "gemini_ready": orchestrator.gemini_client.is_ready,
            "active_model": orchestrator.gemini_client.model_name,
        },
        "meta": {
            "service": "fitoherb-ai-chat",
        },
    }
