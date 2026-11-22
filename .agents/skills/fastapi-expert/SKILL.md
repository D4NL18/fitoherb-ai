---
name: fastapi-expert
description: "Use quando a tarefa envolver: Desenvolvimento completo de APIs assincronas de alta performance com Python FastAPI, Pydantic v2, SQLAlchemy 2.0 async, APIRouters modulares, streaming SSE e serving de modelos de IA."
---

# Habilidade: FastAPI & Async Python Expert 🐍⚡

## Propósito
Desenvolver microsserviços e APIs RESTful assíncronas de altíssima performance utilizando o ecossistema moderno de **FastAPI**, **Pydantic v2** e **SQLAlchemy 2.0 async**, desde a modelagem de rotas desacopladas até serving de modelos de Machine Learning e streaming de respostas de IA.

---

## 1. Arquitetura Modular & Isolamento de Camadas
A aplicação FastAPI DEVE seguir estrutura limpa e desacoplada:
```
app/
├── main.py              # Apenas instancia a FastAPI app, middlewares e inclui routers
├── api/
│   ├── v1/
│   │   ├── routers/     # Endpoints isolados via APIRouter (ex: auth.py, users.py)
│   │   └── dependencies.py # Injeção de dependências compartilhadas (Depends)
├── core/
│   ├── config.py        # Settings via pydantic-settings (lê variáveis .env)
│   └── security.py      # Hashing, autenticação e tokens
├── models/              # Modelos declarativos SQLAlchemy 2.0
├── schemas/             # Schemas e DTOs tipados Pydantic v2
├── services/            # Camada de regras de negócio puras (Use Cases)
└── repositories/        # Acesso assíncrono a dados (Repository Pattern)
```
- **Proibição de Lógica no `main.py`:** É terminantemente proibido declarar rotas ou lógica de negócio diretamente no `main.py`.
- **Roteamento Limpo:** Use sempre `APIRouter(prefix="/recurso", tags=["Recurso"])`.

---

## 2. Pydantic v2 & Validação de Entrada/Saída
- **Tipagem Estrita:** Todos os corpos de requisição e respostas DEVEM ser modelados com `BaseModel` do Pydantic v2.
- **Validadores Modernos:** Utilize decoradores `@field_validator` e `@model_validator(mode='after')`.
- **Campos Calculados:** Utilize `@computed_field` para propriedades dinâmicas de saída.
- **Envelope Padronizado:** Respostas 2xx devem retornar sob o envelope `{ "data": ..., "meta": ... }`.

---

## 3. Persistência Assíncrona com SQLAlchemy 2.0
- **Driver Assíncrono:** Utilize `asyncpg` para PostgreSQL com `create_async_engine()`.
- **Sessões Isoladas:** Injeção de `AsyncSession` por requisição via `Depends(get_async_session)`.
- **Sintaxe 2.0 Style:** Uso estrito de `select()`, `where()`, `joinedload()` e `selectinload()` para carregar relacionamentos sem disparar N+1 queries.

---

## 4. Serving de IA & Streaming em Tempo Real (SSE)
- **Streaming de Tokens:** Uso de `StreamingResponse(generator(), media_type="text/event-stream")` para streaming de completions de LLM caractere a caractere.
- **Lifespan Context Manager:** Carregamento de modelos pesados (PyTorch / Scikit-Learn weights) no evento `lifespan` do FastAPI, mantendo os pesos em memória no estado da aplicação (`app.state.model`), evitando recarga a cada requisição.
- **Execução Bloqueante:** Se for necessário executar operações de CPU-bound pesadas, utilize `run_in_threadpool()` do Starlette para não bloquear o Event Loop do asyncio.
