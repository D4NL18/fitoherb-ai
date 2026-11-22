# LangGraph — Arquitetura em 4 Camadas, Resiliência e Topologias Multi-Agent

## 1. Separação Arquitetural em 4 Camadas (Produção)
Organize repositórios LangGraph separando responsabilidades em pastas dedicadas (`graphs/`, `agents/`, `tools/`, `state/`, `infra/`):

1. **Logic Layer (`agents/` & `tools/`):** Nós especializados com responsabilidade única (chamadas de LLM, regras de negócio determinísticas ou acesso a APIs). Fácil de testar unitariamente sem subir o grafo inteiro.
2. **State Layer (`state/`):** Contratos tipados (`TypedDict`) com agregadores (`Annotated[list, add_messages]`). Cada nó devolve apenas um **delta** (dicionário parcial), preservando imutabilidade e rastreabilidade.
3. **Orchestration Layer (`graphs/`):** Definição declarativa do `StateGraph`, arestas lineares (`add_edge`), condicionais (`add_conditional_edges`), visualização (`app.get_graph().draw_ascii()`) e versionamento de grafos.
4. **Infrastructure Layer (`infra/`):** Checkpointers persistentes (`PostgresSaver` / `RedisSaver`), logging estruturado, métricas de latência, connection pools, retries e autenticação.

---

## 2. Topologias de Sistemas Multiagentes (MAS)

| Topologia | Como Funciona | Quando Usar | Cuidados |
| :--- | :--- | :--- | :--- |
| **Rede (Network)** | Qualquer agente pode encaminhar para qualquer outro. | Exploração aberta sem ordem fixa de execução. | Definir limite global de passos (`recursion_limit`) para evitar ping-pong. |
| **Supervisor** | Um agente supervisor central decide qual especialista chamar a cada turno. | Roteamento dinâmico entre 3–6 especialistas (ex.: finanças, jurídico, suporte). | Evitar sobrecarregar o prompt do supervisor com descrições longas de tools. |
| **Hierárquica** | Supervisores de alto nível coordenam sub-grafos com seus próprios supervisores. | Fluxos corporativos grandes com múltiplos subdomínios independentes. | Isolar esquemas de estado entre sub-grafos para evitar vazamento de contexto. |
| **Workflow Custom** | Combina trechos determinísticos (`A -> B -> C`) com desvios condicionais pontuais. | Pipelines editoriais (`Pesquisador -> Escritor -> Editor`), análises financeiras, RAG adaptativo. | Menor custo de tokens e maior previsibilidade em produção. |

---

## 3. Padrões de Resiliência e Observabilidade de Nós

### Decorator `monitor_node_execution`
- Loga início, `input_keys`, `output_keys`, `execution_time` e status (`success`/`error`).
- **Segurança/LGPD:** Logue apenas nomes das chaves do estado (`list(state.keys())`), nunca o conteúdo bruto de mensagens ou PII.

### Nó de Ferramentas Resiliente (`create_resilient_tool_node`)
- Envolve chamadas externas/tools em loop com `max_retries` (ex.: 3) e **backoff exponencial** (`2 ** attempt`).
- Ao esgotar tentativas, retorna estado estruturado `{"status": "failed", "error": ..., "attempts": ...}` em vez de derrubar o grafo inteiro, permitindo que uma aresta condicional roteie para um nó de fallback gracioso.

---

## 4. Vantagens vs Trade-offs do LangGraph
- **Vantagens:** Modularidade extrema, paralelização de nós independentes, depuração visual, testabilidade isolada, persistência/retomada de estado (*human-in-the-loop* e *time travel*).
- **Trade-offs:** Curva de aprendizado inicial e overhead arquitetural em pipelines triviais de 1 passo (para chamadas simples `prompt | llm | parser`, prefira LCEL puro via `langchain-expert`).
