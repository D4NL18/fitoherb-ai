---
name: orquestrador
description: "Aciona o Orquestrador Autonomo para conduzir a esteira adaptativa de desenvolvimento (com triagem previa de impacto para evitar etapas/agentes desnecessarios) ou despachar Agentes Auxiliares sob demanda."
---

# Execucao do Workflow /orquestrador

1. Leia imediatamente @.agents/agents/orchestrator.md e @.agents/docs/STATE.md (e @.agents/docs/KNOWLEDGE_GRAPH.md, se existir).
2. Classifique a demanda do usuario:
   - **Categoria B (Consultoria Estrategica / Negocios / Financas / Governanca / N8N):** invoque diretamente o subagente auxiliar correspondente em `.agents/agents/` via `invoke_subagent` (`finance_advisor`, `negotiator`, `strategic_leader`, `privacy_officer`, `ai_governance_auditor`, `innovation_consultant`, `n8n_specialist`).
   - **Categoria A (Engenharia de Software - Features, Bugs, APIs, UI, Banco, DevOps):**
     1. **Triagem Prévia de Escopo & Matriz de Impacto:** Avalie o tipo de demanda (Full Feature, Backend Only, Frontend/UI, Hotfix, DB Only, DevOps, Refactor) e aplique as 7 perguntas de impacto para acionar APENAS os agentes e etapas estritamente necessários:
        - *Backend Only:* Pula `designer` e `ux_reviewer`. Se sem dados pessoais, pula `privacy_officer`.
        - *Frontend / UI / CSS:* Pula `dba`, `privacy_officer` e `security` dedicado. Se for ajuste visual de tela existente, pula `product_owner` e `analyst`.
        - *Hotfix / Bugfix:* Pula PO, Analista, Arquiteto e Designer. Vai direto para diagnóstico $\to$ `tester` (TDD) $\to$ `developer` (fix) $\to$ `reviewer`.
        - *DB / Migrations:* Pula Designer e UX Reviewer. Rota `dba` $\to$ `developer` $\to$ `reviewer`.
        - *DevOps / Infra:* Pula etapas de código. Rota `devops` $\to$ `reviewer`.
        - *Refatoração Técnica:* Pula PO, Analista e Designer. Rota `developer` + `tester` $\to$ `reviewer`.
     2. **Etapas Necessárias:** Execute somente os papéis aplicáveis com testes primeiro (TDD), mantendo commits padronizados (`git-expert`).
3. **Checkpoint Obrigatorio de Arquitetura (se Etapa 2 completa executada):** apresente resumo executivo ao usuario e valide antes de prosseguir para TDD/código (salvo ordem de execucao direta).
4. **Regras permanentes:** veto a documentacao na raiz (tudo em `.agents/docs/`); tarefas `[PARALLEL]` com estados isolados (`STATE_<Frente>.md`) mesclados no `STATE.md`; registrar decisões e bypasses no `STATE.md`.
