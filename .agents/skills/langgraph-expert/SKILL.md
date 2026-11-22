---
name: langgraph-expert
description: "Use quando a tarefa envolver: Orquestração stateful de agentes e workflows de IA com LangGraph — StateGraph, TypedDict com add_messages, arestas condicionais, checkpointers (MemorySaver), RAG adaptativo com roteamento por confiança, resiliência/observabilidade de nós e arquiteturas Multi-Agent (ReAct, Supervisor, Hierárquica)."
---

# Habilidade: LangGraph Expert (Stateful Graphs, Adaptive RAG & Multi-Agent) 🕸️🤖

## Propósito
Substituir fluxos lineares rígidos e `if/else hell` por **grafos de estado declarativos, modulares e resilientes** usando **LangGraph**. Domina modelagem de estado tipado, roteamento condicional, persistência de estado (`checkpointer`), RAG adaptativo com validação de qualidade e sistemas multiagentes (MAS) seguindo o padrão **ReAct**.

---

## 1. Quando Evoluir de LangChain Linear para LangGraph

| Conceito | LangChain Isolado (Pipeline) | LangGraph (Grafo de Estado) |
| :--- | :--- | :--- |
| **Estrutura** | Sequencial linear (`prompt \| llm`) | Grafo direcionado com nós, arestas condicionais e ciclos |
| **Estado / Memória** | Reenvio manual do histórico inteiro | Estado compartilhado (`TypedDict`) atualizado incrementalmente por delta |
| **Fluxos Condicionais** | `if/else` espalhado e acoplado | Arestas condicionais declarativas (`add_conditional_edges`) |
| **VectorStore / RAG** | Busca manual fora da cadeia | Nó dedicado (`retrieve`) gravando documentos e scores no estado |
| **Modularidade / Testes** | Alto acoplamento | Cada nó é uma função pura testável isoladamente |
| **Visualização / Produção** | Limitada | `app.get_graph().draw_ascii()`, checkpointers, paralelismo e retomada |

---

## 2. Arquitetura em 4 Camadas e Componentes Core

Separe projetos LangGraph em 4 camadas claras (organizando pastas separadas para `graphs/`, `agents/`, `tools/` e `data/`):
1. **Logic Layer:** Nós especializados com responsabilidade única (chamadas de LLM, ferramentas ou funções Python determinísticas).
2. **State Layer:** Esquemas tipados (`TypedDict`) tratados como imutáveis — cada nó retorna apenas o **delta** (chaves atualizadas), sem mutação destrutiva inesperada.
3. **Orchestration Layer:** Montagem do `StateGraph`, arestas lineares (`add_edge`), condicionais (`add_conditional_edges`), `START`/`END` e compilação com checkpointer.
4. **Infrastructure Layer:** Logging estruturado por nó, métricas de latência, retries com backoff exponencial, autenticação e persistência de checkpoints.

### Padrão Base: Estado Tipado + Agregador `add_messages` + Arestas Condicionais
```python
from typing import Dict
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class AtendimentoState(TypedDict, total=False):
    mensagem: str
    cliente: Dict
    intencao: str
    fatura: Dict
    oferta: str
    resposta: str
    erro: str
    # Agregador permite múltiplas escritas acumulativas sem sobrescrever histórico
    historico: Annotated[list, add_messages]

def rota_intencao(state: AtendimentoState) -> str:
    return state.get("intencao", "faq")

def rota_cancelamento(state: AtendimentoState) -> str:
    return "vip" if state.get("cliente", {}).get("vip") else "normal"

grafo = StateGraph(AtendimentoState)
grafo.add_node("classificar", classificar_intencao)
grafo.add_node("responder_faq", responder_faq)
grafo.add_node("consultar_fatura", consultar_fatura)
grafo.add_node("resumir_fatura", resumir_fatura)
grafo.add_node("decidir_cancelamento", decidir_cancelamento)
grafo.add_node("gerar_oferta", gerar_oferta)
grafo.add_node("registrar_cancelamento", registrar_cancelamento)

grafo.add_edge(START, "classificar")
grafo.add_conditional_edges(
    "classificar",
    rota_intencao,
    {
        "faq": "responder_faq",
        "fatura": "consultar_fatura",
        "cancelar": "decidir_cancelamento",
    },
)
grafo.add_edge("consultar_fatura", "resumir_fatura")
grafo.add_conditional_edges(
    "decidir_cancelamento",
    rota_cancelamento,
    {"vip": "gerar_oferta", "normal": "registrar_cancelamento"},
)
for terminal in ("responder_faq", "resumir_fatura", "gerar_oferta", "registrar_cancelamento"):
    grafo.add_edge(terminal, END)

app = grafo.compile()
print(app.get_graph().draw_ascii())  # Inspeção visual da topologia
```

---

## 3. Observabilidade e Resiliência em Produção

### 3.1 Decorator de Monitoramento de Nós
Registre início, chaves de entrada/saída, latência e falhas sem vazar PII (logue apenas `keys()`, nunca o payload bruto completo):
```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_node_execution(func):
    @wraps(func)
    def wrapper(state: dict) -> dict:
        start = time.time()
        node_name = func.__name__
        logger.info("Iniciando nó", extra={"node": node_name, "input_keys": list(state.keys())})
        try:
            result = func(state)
            logger.info(
                "Nó concluído",
                extra={
                    "node": node_name,
                    "output_keys": list(result.keys()),
                    "execution_time_s": round(time.time() - start, 3),
                    "status": "success",
                },
            )
            return result
        except Exception as exc:
            logger.error(
                "Erro na execução do nó",
                extra={
                    "node": node_name,
                    "error": str(exc),
                    "execution_time_s": round(time.time() - start, 3),
                    "status": "error",
                },
            )
            raise
    return wrapper
```

### 3.2 Nó de Ferramentas Resiliente (Retry + Backoff Exponencial)
Proteja chamadas externas contra falhas transitórias de rede/rate limit e devolva estado degradado estruturado ao esgotar tentativas:
```python
import time

def execute_with_backoff(fn, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            return {"status": "success", "data": fn(), "attempts": attempt}
        except Exception as exc:
            logger.warning("Tentativa %d/%d falhou: %s", attempt, max_retries, exc)
            if attempt >= max_retries:
                return {"status": "failed", "error": str(exc), "attempts": attempt}
            time.sleep(2 ** attempt)
```

---

## 4. RAG Adaptativo com LangGraph

Em vez de um RAG cego (`retrieve -> generate`), modele a qualidade da recuperação no grafo:
1. **Adaptive Retrieval:** Classifica a consulta (`factual`, `analytical`, `balanced`) e ajusta `k`, `fetch_k` e `score_threshold` dinamicamente.
2. **Validação de Qualidade:** Calcula score composto (`relevance * 0.5 + completeness * 0.3 + coherence * 0.2`) e filtra chunks abaixo do limiar.
3. **Roteamento por Confiança (`confidence_router`):**
   - `confidence > 0.8` → `"generate_answer"`
   - `0.5 < confidence <= 0.8` → `"expand_search"` (Query Expansion / aumento de `k` com limite de tentativas para evitar loop infinito!)
   - `confidence <= 0.5` → `"fallback_strategy"` (recusa honesta / escalonamento humano)
4. **Processamento Paralelo:** Use `asyncio.gather` para extrair relevância, sentimento ou entidades de múltiplos chunks concorrentemente.

```python
def confidence_router(state: dict) -> str:
    confidence = state.get("confidence_score", 0.0)
    retries = state.get("search_retries", 0)
    if confidence > 0.8:
        return "generate_answer"
    if confidence > 0.5 and retries < 2:
        return "expand_search"
    return "fallback_strategy"
```

---

## 5. Sistemas Multiagentes (MAS) e Padrão ReAct

### 5.1 Topologias Multiagentes
1. **Rede (Network):** Todos os agentes podem encaminhar para qualquer outro (problemas exploratórios sem ordem fixa).
2. **Supervisor:** Um agente supervisor decide qual especialista acionar em cada passo até concluir.
3. **Hierárquica:** Supervisores coordenam sub-supervisores (domínios corporativos complexos).
4. **Workflow Custom:** Combinação híbrida de trechos determinísticos (ex.: `Pesquisador -> Analista -> Relatório`) com desvios condicionais de erro/revisão.

### 5.2 Ciclo ReAct (`Thought -> Action -> Observation`)
Cada agente especializado alterna raciocínio explícito (`Thought`), invocação de ferramenta (`Action`) e análise do retorno (`Observation`), registrando o rastro em `historico_decisoes` para auditabilidade e interpretabilidade.

### 5.3 Persistência de Estado com Checkpointer (`MemorySaver` / PostgresSaver)
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # Em produção distribuída, use PostgresSaver / RedisSaver
app = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": f"session_{tenant_id}_{conversation_id}"}}
resultado = app.invoke(estado_inicial, config=config)
```

---

## Quality Gates
- [ ] Estado do grafo estritamente tipado com `TypedDict` (usando `Annotated[..., add_messages]` para listas acumulativas).
- [ ] Nós retornam apenas deltas parciais e mantêm responsabilidade única.
- [ ] Todo ciclo condicional (ex.: `expand_search` ou loop ReAct) possui **contador máximo de iterações** para prevenir loops infinitos e estouro de tokens.
- [ ] Topologia validada visualmente (`draw_ascii()` ou Mermaid) e caminhos de erro (`etapa_atual == "erro"`) roteados explicitamente para `END` ou nó de fallback.
- [ ] Logging estruturado por nó sem exposição de PII ou segredos.
- [ ] Checkpointer configurado com `thread_id` isolado por sessão/tenant quando houver estado conversacional persistente.

---

## Exemplos e Referências Complementares (Carregar sob Demanda)
- `references/architecture-and-resilience.md` — Separação em 4 camadas, comparativo de topologias Multi-Agent (Rede, Supervisor, Hierárquica, Workflow Custom) e padrões de resiliência/observabilidade.
- `examples/multi_agent_financial_react.py` — Sistema multiagente completo (`StateGraph`, `MemorySaver`, `@tool`, `yfinance`, ciclo ReAct `Pesquisador -> Analista -> Relatório`).
- `examples/adaptive_rag_langgraph.py` — Pipeline RAG adaptativo com FAISS, `confidence_router`, `SmartEmbeddingCache`, `RAGEvaluator`, `RAGMonitor` e enriquecimento paralelo assíncrono.
