# Fluxo de Desenvolvimento com IA (AI Agents Workflow) 🤖🚀

Fluxo obrigatório para qualquer tarefa assistida por IA neste projeto. O diretório `.agents/` é a fonte única da verdade: `agents/` (subagentes), `skills/` (1º nível, `<nome>/SKILL.md`, servindo também como slash commands), `rules/` (flat, com frontmatter de trigger) e `docs/` (documentação e estado).

---

## REGRA DE OURO: Governança de Documentação (`.agents/docs/`)
> [!CAUTION]
> **É TERMINANTEMENTE PROIBIDO SALVAR ARQUIVOS DE DOCUMENTAÇÃO NA RAIZ DO REPOSITÓRIO (`/`).** Todo artefato reside em `.agents/docs/`, seguindo os templates oficiais:
> - **Design System Mestre:** `.agents/docs/design/DESIGN_SYSTEM.md` (Template: `design/TEMPLATE_DESIGN_SYSTEM.md`)
> - **Design Plan por Feature:** `.agents/docs/design/plans/<feature>.md` (Template: `design/TEMPLATE_DESIGN_PLAN.md`)
> - **Banco de Dados (Schema & Seeds):** `.agents/docs/db/<modulo>.md` (Template: `db/TEMPLATE.md`; seeds em `db/seeds/`)
> - **Regras de Negócio (P-XXX):** `.agents/docs/business_rules/<feature>.md` (Template: `business_rules/TEMPLATE.md`)
> - **Contratos de API REST:** `.agents/docs/api_contracts/<entidade>.md` (Template: `api_contracts/TEMPLATE.md`)
> - **Tarefas e Checklists:** `.agents/docs/tasks/<feature>.md` (Template: `tasks/TEMPLATE.md`)
> - **Decisões de Arquitetura (ADR):** `.agents/docs/adr/ADR-<num>-<nome>.md` (Template: `adr/TEMPLATE.md`)
> - **Privacidade (RIPD/DPIA):** `.agents/docs/privacy/`
> - **Arquitetura Base:** `.agents/docs/architecture/ARCHITECTURE.md` · **Glossário:** `.agents/docs/GLOSSARY.md`
> - **Backlog e Roadmap:** `.agents/docs/ROADMAP.md` · **Estado:** `.agents/docs/STATE.md` · **Memória:** `.agents/docs/KNOWLEDGE_GRAPH.md`

---

## Roteamento Autônomo e Repertórios Delimitados 🚦
> [!IMPORTANT]
> 1. **Zero chamadas manuais de skills:** o **Orquestrador** (`.agents/agents/orchestrator.md`) classifica a demanda e invoca o subagente correto via `invoke_subagent`.
> 2. **Repertório fechado:** cada subagente (`subagent: true`) executa seu **Boot Protocol** e lê apenas os `SKILL.md` homologados para seu domínio (anti context bloat).
> 3. **Categoria A (Engenharia)** segue a Esteira de 5 Macro-Etapas. **Categoria B (Consultoria)** — finanças, negociação, liderança, LGPD corporativa, governança de IA, inovação, N8N — aciona diretamente o agente auxiliar.

---

## Esteira Consolidada de Desenvolvimento (5 Macro-Etapas)

**ETAPA 1 — Descoberta, Escopo e Especificação** (`product_owner` + `analyst`)
- **PO:** fatia a demanda em User Stories INVEST em `.agents/docs/ROADMAP.md` e marca tarefas paralelizáveis com `[PARALLEL]`.
- **Analista:** discovery com o usuário, regras `P-XXX` em `.agents/docs/business_rules/<feature>.md`, linguagem ubíqua e escopo inicial em `.agents/docs/tasks/<feature>.md`.

**ETAPA 2 — Arquitetura, UI Design Plan, Modelagem Segura e Privacy by Design** (`architect` + `designer` + `dba` + `ai_specialist` + `privacy_officer`)
- **Arquiteto:** arquitetura, ADRs (`.agents/docs/adr/`), contratos REST com envelope `data`/`meta` (`.agents/docs/api_contracts/<entidade>.md`) e checklist técnico atômico em `.agents/docs/tasks/<feature>.md`.
- **Designer (se Frontend):** Design Plan obrigatório em `.agents/docs/design/plans/<feature>.md` via `uiux-expert`, seguindo `DESIGN_SYSTEM.md`, 8 estados interativos e filtro Hallmark Anti-IA (`frontend-ui-anti-patterns.md`).
- **DBA (se Banco):** Migrations seguras com travas anti-perda de dados, schema em `.agents/docs/db/<modulo>.md` e seeds em `.agents/docs/db/seeds/`.
- **AI Specialist (se IA):** esteira de ML, RAG, prompts modulares e orquestração de tokens.
- **Privacy Officer:** Privacy by Design — minimização/anti-overfetching nos contratos, 10 Bases Legais (Art. 7º e 11), Privacy by Default na UI e RIPD/DPIA em `.agents/docs/privacy/` se houver dados sensíveis ou decisões automatizadas de IA.
- **Checkpoint Obrigatório:** resumo executivo ao usuário e validação antes da Etapa 3 (salvo ordem de execução direta).

**ETAPA 3 — TDD e Execução** (`tester` + `developer` + `ai_specialist`)
- **Tester (TDD First):** suíte de testes unitários e de contrato ANTES de qualquer lógica produtiva.
- **Desenvolvedor (+ AI Specialist):** código em branch isolada até os testes passarem, usando tokens do `DESIGN_SYSTEM.md`, Design Plan, contratos de API e `.agents/rules/`; commits via `git-expert` rastreando `P-XXX`.

**ETAPA 4 — Quality Gate 360, Auditorias e Auto-Healer** (`reviewer` + `privacy_officer` + `ux_reviewer` + `security` + `tester`)
- **Reviewer:** Clean Code, SOLID, complexidade cognitiva, conformidade com `.agents/rules/` e veto a documentação fora de `.agents/docs/`.
- **Privacy Officer:** Auditoria de Código LGPD (PII em controllers, services, DTOs e logs; isolamento multi-tenant) com **poder de veto imediato**.
- **UX Reviewer (se Frontend):** fidelidade ao Design Plan e `DESIGN_SYSTEM.md`, filtro Anti-IA, Skeleton Loaders, Empty States e 8 estados.
- **Security:** OWASP (Injections, XSS, JWT no localStorage, Indirect Prompt Injection em RAG, secrets expostos) — bloqueia a esteira.
- **Tester ↔ Developer (Auto-Healer):** testes e linters; em falha, correção autônoma guiada pelo Stack Trace por até **3 tentativas** antes de escalar ao humano.

**ETAPA 5 — Release, CI/CD, FinOps e Compressão de Contexto** (`devops` + `orchestrator`)
- **DevOps:** CI/CD, Docker multi-stage enxuto, FinOps (Scale-to-Zero, ciclo de vida GCS, Scorecard >= 4.80) e Pull Request com descrição pré-preenchida.
- **Orquestrador:** `context-compressor` consolida decisões em `.agents/docs/KNOWLEDGE_GRAPH.md` e reseta o `.agents/docs/STATE.md`.

---

## Diretrizes Operacionais
- **Paralelismo Seguro (`[PARALLEL]`):** subagentes paralelos via `invoke_subagent`, cada um com estado isolado (ex.: `STATE_Frontend.md`, `STATE_Backend.md`), mesclados no `STATE.md` ao final.
- **Infra Dinâmica (Hooks e MCP):** o Orquestrador mantém `.agents/mcp_config.json` e `.agents/hooks.json` sincronizados com a stack.
- **Bypass Justificado:** pular sub-etapa só se comprovadamente irrelevante (sem tela → sem Designer/UX Reviewer; sem banco → sem DBA), registrando o motivo no `STATE.md`.

---

## Matriz de Agentes x Repertório Autorizado (`.agents/agents/` · skills em `.agents/skills/<nome>/SKILL.md`)

| Agente | Atuação | Repertório de Skills Autorizadas |
| :--- | :--- | :--- |
| `orchestrator` | Coordenador | `context-compressor`, `agent-creator`, `agent-manager-skill` |
| `product_owner` | Etapa 1 | `agile-coach`, `pm-skills`, `copywriting`, `ai-seo` |
| `analyst` | Etapa 1 | `business-rules-expert`, `domain-expert`, `pm-skills`, `gemini-deep-research` |
| `architect` | Etapa 2 | `api-contract-expert`, `springboot-expert`, `fastapi-expert`, `domain-expert`, `springboot-swagger`, `architecture-patterns`, `architect-review`, `cloud-architect`, `framework-migration-legacy-modernize`, `auth-implementation-patterns`, `n8n-deploy`, `gcp-finops-expert` |
| `designer` | Etapa 2 | `uiux-expert`, `animejs-animation`, `image-generator` |
| `dba` | Etapa 2 | `dba-expert`, `springboot-jpa-audit`, `database-architect`, `database-admin` |
| `privacy_officer` | Etapas 2 e 4 + Auxiliar | `lgpd-privacy-expert` |
| `ai_specialist` | Etapas 2 e 3 | `ai-expert`, `rag-expert`, `ml-pipeline-expert`, `deep-learning-cv-expert`, `fastapi-ai-expert`, `mlops-lifecycle-expert`, `gemini-live-api-dev`, `gemini-omni-flash-api`, `hybrid-search-implementation`, `embedding-strategies`, `hugging-face-model-trainer`, `image-generator`, `openai-api-*` (4), `nlp-*` (4), `genai-*` (4), `ga-*` (5), `gcp-finops-expert`, `cloud-architect` |
| `tester` | Etapas 3 e 4 | `springboot-unit-testing`, `angular-expert`, `e2e-testing-patterns` |
| `developer` | Etapa 3 | `angular-expert`, `springboot-expert`, `springboot-dto-mapper`, `springboot-error-handling`, `springboot-security`, `springboot-jpa-audit`, `springboot-swagger`, `fastapi-expert`, `fastapi-ai-expert`, `git-expert`, `fastapi-pro`, `fastapi-router-py`, `async-python-patterns`, `frontend-optimistic-mutations`, `frontend-data-contracts`, `framework-migration-code-migrate`, `auth-implementation-patterns`, `n8n-fundamentos`, `n8n-openai`, `openai-api-fundamentos`, `openai-api-chatbot` |
| `reviewer` | Etapa 4 | `git-expert`, `springboot-dto-mapper`, `springboot-error-handling`, `clean-code-guard`, `code-reviewer` |
| `ux_reviewer` | Etapa 4 | `uiux-expert`, `frontend-lighthouse` |
| `security` | Etapa 4 | `cybersecurity-infra-expert`, `springboot-security`, `lgpd-privacy-expert`, `api-security-best-practices`, `auth-implementation-patterns` |
| `devops` | Etapa 5 | `devops-executive`, `gcp-finops-expert`, `git-expert`, `mlops-lifecycle-expert`, `gcp-cloud-run`, `cloud-devops`, `geminiignore-finops` |
| `finance_advisor` | Auxiliar | `tech-finance-expert`, `gcp-finops-expert` |
| `negotiator` | Auxiliar | `negotiation-stakeholder-expert` |
| `strategic_leader` | Auxiliar | `strategic-tech-leader`, `tech-lead-mentor` |
| `ai_governance_auditor` | Auxiliar | `responsible-ai-governance` |
| `innovation_consultant` | Auxiliar | `tech-innovation-expert`, `pm-skills`, `copywriting`, `ai-seo` |
| `n8n_specialist` | Auxiliar | `n8n-fundamentos`, `n8n-deploy`, `n8n-openai`, `n8n-groq-deepseek`, `n8n-google-slack-telegram-supabase`, `n8n-rag-memory`, `n8n-multi-agents`, `n8n-mcp`, `openai-api-fundamentos` |

> As descrições de cada skill vivem no frontmatter do respectivo `SKILL.md` (gatilho semântico "Use quando..."); não são duplicadas aqui para evitar context bloat.

---

## Slash Commands (Atalhos Nativos via `.agents/skills/<nome>/`)
- `/orquestrador`, `/orquestrar`, `/o` — esteira completa de 5 Macro-Etapas ou despacho de auxiliares · `/init` — kickoff/fundação do projeto.
- Pipeline: `/po`, `/analyst`, `/architect`, `/designer`, `/dba`, `/developer`, `/reviewer`, `/tester`, `/security`, `/devops`, `/ai_specialist`, `/privacy`.
- Auxiliares: `/finance`, `/negotiator`, `/leader`, `/responsible_ai`, `/innovation`, `/n8n`.
