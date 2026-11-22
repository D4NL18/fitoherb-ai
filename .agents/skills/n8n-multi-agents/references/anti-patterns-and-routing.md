# Anti-Padrões e Estratégias de Roteamento Multi-Agente no N8N

Guia de referência rápida para evitar falhas arquiteturais comuns e escolher a estratégia de roteamento adequada em sistemas multi-agente no N8N.

---

## 1. Matriz de Estratégias de Roteamento

| Estratégia | Como Funciona no N8N | Quando Usar | Trade-offs |
|---|---|---|---|
| **Switch Determinístico (LLM Classifier + Switch Node)** | LLM retorna JSON `{ "categoria": "..." }` com `temperature: 0` e um nó `Switch` encaminha para o sub-workflow | Domínios bem definidos (ex: vendas, suporte, técnico) com baixa latência e alto controle | Exige manutenção manual das rotas quando novos agentes surgem |
| **Tool Calling (AI Agent + Call n8n Workflow Tool)** | O próprio `AI Agent` decide qual sub-workflow invocar com base na descrição das ferramentas | Demandas híbridas que podem exigir 2 ou mais sub-agentes em sequência | Maior custo de tokens e menos previsibilidade que `Switch` |
| **Fan-Out / Fan-In Paralelo (HTTP Request + Merge)** | Múltiplos `HTTP Request` ou `Execute Workflow` disparam em paralelo e convergem em um nó `Merge (Wait for All)` | Tarefas decomponíveis independentes (ex: pesquisa + SEO, preço + viabilidade técnica) | Requer tratamento explícito de falha parcial e timeout individual |
| **Cascata com Escalonamento (L1 → Avaliador → L2)** | Agente rápido/barato tenta resolver; avaliador valida qualidade e só escala para agente caro ou humano se reprovado | Suporte técnico, triagem de tickets e otimização FinOps de tokens | Adiciona 1 salto de latência quando há escalonamento |

---

## 2. Catálogo de Anti-Padrões e Mitigações

### A. God Agent (Agente Monolítico)
- **Sintoma:** Um único `AI Agent` com 10+ ferramentas e system prompt gigante.
- **Impacto:** Alucinação na escolha de tools, estouro de janela de contexto e custo elevado por turno.
- **Mitigação:** Quebrar em sub-agentes com no máximo 3 a 5 ferramentas coesas por domínio.

### B. Loop Infinito de Feedback
- **Sintoma:** Agente avaliador devolve a tarefa ao executor sem contador de tentativas.
- **Impacto:** Execuções travadas e consumo descontrolado de API de LLM.
- **Mitigação:** Propagar `attempt` no payload e impor guarda obrigatória `attempt >= 3` com rota de fallback.

### C. Vazamento de Contexto entre Sessões ou Tenants
- **Sintoma:** Memória compartilhada sem `session_id` ou sem isolamento por `tenant_id`.
- **Impacto:** Incidente de privacidade/LGPD com mistura de histórico entre usuários.
- **Mitigação:** Propagar `session_id` e `tenant_id` em todos os payloads HTTP/`Execute Workflow` e isolar a tabela/namespace de memória.

### D. Chamadas Síncronas sem Timeout ou Fallback
- **Sintoma:** `HTTP Request` para sub-agente sem `timeout` e sem `continueOnFail` / ramo de erro.
- **Impacto:** Um sub-agente lento ou offline derruba toda a orquestração.
- **Mitigação:** Configurar timeout explícito (`15000`–`30000 ms`), header de autenticação (`x-agent-token`) e resposta degradada controlada.

### E. Orquestrador com Efeitos Colaterais
- **Sintoma:** O supervisor escreve diretamente no banco/CRM além de rotear.
- **Impacto:** Acoplamento alto, difícil depuração e risco de duplicidade em retries.
- **Mitigação:** Manter o supervisor estritamente como roteador e consolidador; delegar mutações apenas a sub-agentes especializados e idempotentes.

---

## 3. Contrato Mínimo Recomendado entre Supervisor e Sub-Agentes

```json
{
  "request": {
    "input": "string",
    "session_id": "uuid",
    "tenant_id": "string",
    "attempt": 1,
    "metadata": { "origin": "webhook", "trace_id": "uuid" }
  },
  "response": {
    "output": "string",
    "agente": "vendas|suporte|tecnico",
    "status": "sucesso|erro|fallback",
    "duracao_ms": 0
  }
}
```
