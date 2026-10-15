from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.domains.chat.schemas.chat_dto import ChatRequest, ChatResponse
from app.domains.chat.services.chat_orchestrator import ChatOrchestrator

router = APIRouter(
    prefix="/chat",
    tags=["Assistente Virtual Inteligente (Chatbot Gemini)"]
)

# Instância singleton do orquestrador
_orchestrator = ChatOrchestrator()


def get_orchestrator() -> ChatOrchestrator:
    return _orchestrator


@router.post("/messages", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator)
):
    """
    Recebe a mensagem do usuário (máx. 255 caracteres) e retorna a resposta
    do assistente virtual com ação de auto-redirecionamento quando aplicável.
    """
    try:
        return orchestrator.process_message(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no processamento do assistente: {str(exc)}"
        )


@router.get("/health")
def chat_health(
    orchestrator: ChatOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Probe de saúde e prontidão do subsistema de chat e do cliente Gemini.
    """
    return {
        "status": "UP",
        "gemini_ready": orchestrator.gemini_client.is_ready,
        "model": orchestrator.gemini_client.model_name,
        "catalog_items": len(orchestrator.catalog_index.products)
    }
