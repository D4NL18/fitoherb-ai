---
name: fastapi-expert
description: Especialista em Python FastAPI, tipagem Pydantic e processamento assíncrono.
---
# Habilidade: FastAPI Expert

## Propósito
Garantir a criação de APIs em Python usando FastAPI de forma moderna, segura e de altíssima performance, aproveitando ao máximo a tipagem forte e a assincronicidade.

## Diretrizes Obrigatórias
1. **Estrutura de Pastas e Isolamento de Rotas (Obrigatório):**
   A aplicação DEVE seguir este padrão arquitetural:
   - **`app/main.py`**: Apenas monta a aplicação e inclui os roteadores. É **proibido** declarar lógicas diretas ou funções de rota neste arquivo.
   - **`app/api/routers/`**: Todas as rotas devem viver aqui (ex: `routers/admin.py`, `routers/anamnesis.py`) e serem expostas via `APIRouter`.
   - **`app/services/`**: Arquivos contendo as regras de negócio isoladas (ex: `services/inference.py`).
   - **`app/models/`**: Onde residem os schemas (ex: `schemas.py`) de Pydantic.
2. **Esquemas e Tipagem (Pydantic):**
   - Todo Request Body e Response Body DEVE ser tipado e validado usando modelos Pydantic na pasta `app/models/`. Deixe o FastAPI cuidar da validação de payload automaticamente.
3. **Assincronicidade e Injeção de Dependência:**
   - Use `async def` para endpoints que realizam operações de I/O.
   - Utilize o poderoso sistema de `Depends()` do FastAPI nas rotas.
   - **Sessões de Banco de Dados:** Sessões de conexão (ex: Session do SQLAlchemy) DEVEM ser obrigatoriamente passadas para os endpoints via `Depends(get_db)` e injetadas nos `Services`. Jamais instancie conexões globais soltas dentro de arquivos de serviço.
