---
name: orquestrador
description: "Aciona o Orquestrador Autonomo para conduzir a esteira enxuta de 5 Macro-Etapas ou despachar Agentes Auxiliares sob demanda."
---

# Execucao do Workflow /orquestrador

1. Leia imediatamente @.agents/agents/orchestrator.md e @.agents/docs/STATE.md (e @.agents/docs/KNOWLEDGE_GRAPH.md, se existir).
2. Classifique a demanda do usuario:
   - **Categoria B (Consultoria Estrategica / Negocios / Financas / Governanca / N8N):** invoque diretamente o subagente auxiliar correspondente em `.agents/agents/` via `invoke_subagent` (`finance_advisor`, `negotiator`, `strategic_leader`, `privacy_officer`, `ai_governance_auditor`, `innovation_consultant`, `n8n_specialist`).
   - **Categoria A (Engenharia de Software - Features, Bugs, APIs, UI, Banco):** execute a Esteira Consolidada de 5 Etapas, atualizando o `.agents/docs/STATE.md` a cada etapa e invocando os subagentes especialistas via `invoke_subagent`:
     1. **Etapa 1 - Descoberta, Escopo e Especificacao:** `product_owner` -> `analyst`.
     2. **Etapa 2 - Arquitetura, UI Design Plan, Modelagem Segura e Privacy by Design:** `architect`, `designer` (se Frontend), `dba` (se Banco), `ai_specialist` (se IA), `privacy_officer`.
     3. **Etapa 3 - TDD e Execucao:** `tester` (testes primeiro) -> `developer` (+ `ai_specialist`).
     4. **Etapa 4 - Quality Gate 360 e Auto-Healer:** `reviewer`, `privacy_officer`, `ux_reviewer` (se Frontend), `security`, `tester` <-> `developer` (ate 3 tentativas).
     5. **Etapa 5 - Release, CI/CD, FinOps e Compressao:** `devops` -> orquestrador (`context-compressor`, reset do `STATE.md`).
3. **Checkpoint Obrigatorio de Arquitetura (Fim da Etapa 2):** apos gerar as especificacoes, contratos de API, modelagem de banco, validacao LGPD e Design Plan na Etapa 2, apresente um resumo executivo ao usuario e valide antes de prosseguir para a Etapa 3 (TDD e Codigo), a menos que o usuario tenha ordenado execucao direta sem pausas.
4. **Regras permanentes:** veto a documentacao na raiz (tudo em `.agents/docs/`); tarefas `[PARALLEL]` com estados isolados (`STATE_<Frente>.md`) mesclados no `STATE.md`; bypass de sub-etapa apenas com justificativa registrada no `STATE.md`; manter `.agents/hooks.json` e `.agents/mcp_config.json` sincronizados com a stack.
