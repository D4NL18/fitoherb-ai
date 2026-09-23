---
name: fastapi-ai-expert
description: Especialista em microsserviços assíncronos de alta performance com FastAPI, Pydantic v2, streaming SSE e serving de modelos de IA e LLMs.
---
# Habilidade: FastAPI AI Service Developer ⚡🤖

## Propósito
Você é a autoridade técnica na construção, estruturação e implantação de microsserviços de IA de alta performance com **FastAPI** e **Pydantic v2**. Esta habilidade engloba desde a exposição de APIs RESTful assíncronas para servir inferências de modelos clássicos (Scikit-Learn) e Deep Learning (PyTorch) até orquestração de LLMs com streaming (SSE), cadeias de fallback e envelope padronizado.

---

## Gatilhos de Uso (Trigger & Scope)
Utilize esta skill obrigatoriamente quando:
- Construir ou refatorar microsserviços backend para servir modelos de Machine Learning, Deep Learning ou LLMs.
- Implementar rotas assíncronas com validação rigorosa via Pydantic v2 (`BaseModel`, `field_validator`, `computed_field`).
- Configurar carregamento único e lazy de modelos via evento `lifespan` do FastAPI para evitar re-carregamento em cada request.
- Implementar mecanismos de alta disponibilidade com degradação graciosa (*Graceful Degradation*) e fallback entre provedores (Gemini -> OpenAI).
- Expor respostas com streaming server-sent events (`StreamingResponse`) para geração de texto em tempo real.

---

## Competências Principais e Boas Práticas

### 1. Carregamento de Modelos no Lifespan (Zero Overhead por Request)
- **Proibição Absoluta:** NUNCA instancie modelos, redes neurais (`torch.load`, `joblib.load`) ou índices vetoriais dentro de funções de rota (`@app.post`).
- **Padrão Obrigatório:** Utilize o context manager `asynccontextmanager` para carregar todos os artefatos no dicionário `app.state` durante a inicialização do container.

### 2. Validação Rigorosa e DTOs com Pydantic v2
- Todo endpoint de inferência deve ter esquemas de entrada e saída explicitamente tipados.
- Trate dados ausentes e limites de features (`gt`, `lt`, regex) no nível do schema, impedindo que requisições malformadas cheguem ao modelo.
- Utilize o Envelope de Resposta padronizado (`data`, `meta`) conforme `.agents/rules/backend/API_CONTRACT_RULES.md`.

### 3. Graceful Degradation e Cadeia de Fallback (Alta Disponibilidade)
- Quando interagir com APIs de LLMs ou serviços externos, implemente tratamento em cascata:
  - Exemplo: Provedor Primário (Google Gemini 1.5 Flash) -> Provedor Secundário (Google Gemini 1.5 Pro) -> Fallback (OpenAI GPT-4o-mini).
- Lide com timeouts (`httpx.Timeout(connect=5.0, read=30.0)`) e capture falhas de cota/rede com fallback determinístico.

### 4. Desacoplamento via APIRouter e Injeção de Dependências
- Organize as rotas em módulos funcionais (`routers/inference.py`, `routers/health.py`, `routers/rag.py`).
- Utilize `Depends` para injetar instâncias de serviços, repositórios e clientes de IA.

---

## Template de Implementação (FastAPI + Pydantic v2 + Lifespan + Fallback)

```python
import os
import logging
from contextlib import asynccontextmanager
from typing import Generic, List, Optional, TypeVar
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Envelope Padronizado
T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: dict = Field(default_factory=lambda: {"status": "success"})

# DTOs de Entrada e Saída
class InferenceRequest(BaseModel):
    features: List[float] = Field(..., min_length=1, description="Vetor numérico de entrada para inferência")
    model_version: Optional[str] = Field("v1", description="Versão do modelo solicitada")

class InferenceResult(BaseModel):
    prediction: int = Field(..., description="Classe predita pelo estimador")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probabilidade calibrada da classe")
    model_used: str = Field(..., description="Identificador do modelo utilizado")

# Gerenciamento de Ciclo de Vida (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Carregando modelos de IA na memória...")
    # Simula carregamento de pesos (joblib.load / torch.load)
    app.state.model = {"name": "RandomForestClassifier_v1"}
    yield
    logger.info("Descarregando recursos de IA...")
    app.state.model = None

app = FastAPI(
    title="AI Inference Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1/inference", tags=["Inference"])

def get_model():
    model = getattr(app.state, "model", None)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo de IA não carregado ou indisponível"
        )
    return model

@router.post("/predict", response_model=ResponseEnvelope[InferenceResult])
async def predict_sample(
    payload: InferenceRequest,
    model: dict = Depends(get_model)
):
    try:
        # Lógica de inferência com o modelo
        result = InferenceResult(
            prediction=1,
            probability=0.965,
            model_used=model["name"]
        )
        return ResponseEnvelope(data=result, meta={"model_version": payload.model_version})
    except Exception as exc:
        logger.error(f"Erro na inferência: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha no processamento da inferência: {str(exc)}"
        )

app.include_router(router)
```

---

## Quality Gates
- [ ] Modelos carregados no evento `lifespan` com zero I/O de disco durante as rotas HTTP.
- [ ] Schemas validados rigorosamente com Pydantic v2.
- [ ] Respostas envelopadas com campos `data` e `meta`.
- [ ] Tratamento explícito de exceções com status codes semânticos (400, 422, 503, 500).
- [ ] Contratos de API documentados em `.agents/docs/api_contracts/`.
