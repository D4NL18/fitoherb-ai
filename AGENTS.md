# Fluxo de Desenvolvimento com IA (AI Agents Workflow) 🤖🚀

Fluxo obrigatório para qualquer tarefa assistida por IA neste projeto. O diretório `.agents/` é a fonte única da verdade: `agents/` (subagentes), `skills/` (1º nível, `<nome>/SKILL.md`, servindo também como slash commands), `rules/` (regras consolidadas) e `docs/` (documentação e estado).

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

## Triagem Prévia de Escopo & Roteamento Adaptativo 🚦
> [!IMPORTANT]
> **Zero chamadas manuais de skills e zero execução cega de etapas:**
> O **Orquestrador** (`.agents/agents/orchestrator.md`) avalia a demanda ANTES de disparar qualquer agente. Etapas e agentes só são acionados se houver real necessidade comprovada:

### Matriz de Triagem por Tipo de Demanda:
1. **T1: Nova Feature Completa (Full-Stack):** Executa as etapas completas de produto, arquitetura, design, testes, implementação e quality gate.
2. **T2: Backend Only (API, Service, Regra de Negócio, Query):**
   - **Bypass Automático:** NÃO passa por `designer` nem `ux_reviewer`. Se não coleta nem manipula dados pessoais (PII), NÃO passa por `privacy_officer`.
   - Rota: `architect` (se houver novo contrato) $\to$ `tester` + `developer` $\to$ `reviewer` $\to$ `devops`.
3. **T3: Frontend / UI / CSS / Estilização:**
   - **Bypass Automático:** NÃO passa por `dba` (sem banco), NÃO passa por `privacy_officer` (sem coleta nova de dados), NÃO passa por `security` dedicado (validação padrão no `reviewer`). Se for ajuste de estilo ou componente existente, dispensa `product_owner` e `analyst`.
   - Rota: `designer` (se exigir novo mockup) $\to$ `developer` $\to$ `tester` + `ux_reviewer` $\to$ `reviewer`.
4. **T4: Hotfix / Bugfix Pontual:**
   - **Bypass Automático:** Dispensa PO, Analista, Arquiteto e Designer.
   - Rota Direta: Diagnóstico $\to$ `tester` (reproduz com teste) $\to$ `developer` (corrige) $\to$ `reviewer` (validação e commit).
5. **T5: Database / Migrations Only:**
   - **Bypass Automático:** Dispensa Designer, UX Reviewer e PO/Analista se for técnico.
   - Rota: `dba` (migration com travas anti-perda) $\to$ `developer` (executa/testa) $\to$ `reviewer`.
6. **T6: DevOps / CI/CD / Infra Only:**
   - **Bypass Automático:** Dispensa todas as etapas de produto/código.
   - Rota Direta: `devops` $\to$ `reviewer`.
7. **T7: Refatoração Técnica Interna:**
   - **Bypass Automático:** Dispensa PO, Analista e Designer.
   - Rota: `developer` + `tester` $\to$ `reviewer`.

---

## Esteira Consolidada de 5 Macro-Etapas (Execução Condicional)

**ETAPA 1 — Descoberta, Escopo e Especificação** (`product_owner` + `analyst`)
*(Acionada apenas quando houver novo escopo funcional de produto)*
- **PO:** fatia a demanda em User Stories INVEST em `.agents/docs/ROADMAP.md` e sincroniza com Jira via `twg-setup`.
- **Analista:** discovery com o usuário, regras `P-XXX` em `.agents/docs/business_rules/<feature>.md`, linguagem ubíqua e escopo em `.agents/docs/tasks/<feature>.md`.

**ETAPA 2 — Arquitetura, UI Design Plan, Modelagem Segura e Privacy by Design**
*(Apenas os papéis impactados pela demanda participam)*
- **Arquiteto (se Backend/Arquitetura):** arquitetura, ADRs (`.agents/docs/adr/`), contratos REST com envelope `data`/`meta` (`.agents/docs/api_contracts/<entidade>.md`) e checklist técnico atômico em `.agents/docs/tasks/<feature>.md`.
- **Designer (se houver Frontend):** Design Plan obrigatório em `.agents/docs/design/plans/<feature>.md` via `uiux-expert`, Figma, Canva, Mobbin, seguindo `DESIGN_SYSTEM.md`, 8 estados interativos e filtro Hallmark Anti-IA.
- **DBA (se houver Banco):** Migrations seguras com travas anti-perda de dados, schema em `.agents/docs/db/<modulo>.md` e suporte a Supabase/PostgreSQL.
- **AI Specialist (se houver IA):** esteira de ML, RAG, prompts modulares e orquestração de tokens.
- **Privacy Officer (se houver Dados Pessoais/PII):** Privacy by Design — minimização nos contratos, 10 Bases Legais e RIPD/DPIA em `.agents/docs/privacy/`.
- **Checkpoint Obrigatório:** resumo executivo ao usuário e validação antes da Etapa 3 (salvo ordem de execução direta).

**ETAPA 3 — TDD e Execução** (`tester` + `developer` + `ai_specialist`)
- **Tester (TDD First):** suíte de testes unitários e de contrato ANTES de qualquer lógica produtiva.
- **Desenvolvedor (+ AI Specialist):** código em branch isolada até os testes passarem, consumindo tokens do `DESIGN_SYSTEM.md`, Figma to Code, contratos de API e regras de `.agents/rules/`; commits via `git-expert` rastreando `P-XXX`.

**ETAPA 4 — Quality Gate 360, Auditorias e Auto-Healer**
*(Auditorias especializadas acionadas estritamente por impacto)*
- **Reviewer:** Clean Code, SOLID, complexidade cognitiva, conformidade com `.agents/rules/` e veto a documentação fora de `.agents/docs/`.
- **Privacy Officer (se PII/dados sensíveis):** Auditoria de Código LGPD em controllers, DTOs e logs com **poder de veto imediato**.
- **UX Reviewer (se houver Frontend):** fidelidade ao Design Plan, Figma, Mobbin, `DESIGN_SYSTEM.md`, filtro Anti-IA e acessibilidade.
- **Security (se Auth/Cripto/Superfície Crítica):** varredura OWASP (injections, XSS, cookies HttpOnly, indirect prompt injection).
- **Tester ↔ Developer (Auto-Healer):** testes e linters; em falha, correção autônoma guiada pelo Stack Trace por até **3 tentativas**.

**ETAPA 5 — Release, CI/CD, FinOps e Compressão de Contexto** (`devops` + `orchestrator`)
- **DevOps:** CI/CD, Docker multi-stage enxuto, FinOps (Scale-to-Zero, GCP, Supabase, Scorecard >= 4.80) e Pull Request com descrição pré-preenchida.
- **Orquestrador:** `context-compressor` consolida decisões em `.agents/docs/KNOWLEDGE_GRAPH.md` e reseta o `.agents/docs/STATE.md`.

---

## Matriz de Agentes x Repertório Autorizado & Integrações

| Agente | Atuação | Repertório de Skills e Integrações Autorizadas |
| :--- | :--- | :--- |
| `orchestrator` | Coordenador | `context-compressor`, `agent-creator`, `agent-manager-skill`, `twg-setup` (Atlassian TWG / Jira) |
| `product_owner` | Etapa 1 | `agile-coach`, `pm-skills`, `copywriting`, `ai-seo`, `twg-setup` (Jira), `mobbin` (search, best-practices), `canva` (decks) |
| `analyst` | Etapa 1 | `business-rules-expert`, `domain-expert`, `pm-skills`, `gemini-deep-research`, `twg-setup` (Jira), `mobbin` |
| `architect` | Etapa 2 | `api-contract-expert`, `architecture-patterns`, `springboot-expert`, `fastapi-expert`, `domain-expert`, `springboot-swagger`, `cloud-architect`, `framework-migration-legacy-modernize`, `auth-implementation-patterns`, `n8n-workflow-expert`, `gcp-finops-expert`, `gcp-cloud-run`, `langgraph-expert`, GCP (`gcloud`, `finding-google-skills`), Supabase (`supabase`, `supabase-postgres-best-practices`) |
| `designer` | Etapa 2 | `uiux-expert`, `animejs-animation`, `image-generator`, Figma MCP & Skills (`figma-generate-design`, `figma-create-new-file`, `figma-spec`, `figma-shaders`, `figma-implement-motion`), Canva MCP & Skills (`edit-design`, `brand-check`, `bulk-create`, `get-design-feedback`), Mobbin (`search`, `redesign-screen`, `best-practices`), Stitch MCP (`generate_screen_from_text`, `create_design_system`, `create_project`) |
| `dba` | Etapa 2 | `dba-expert`, `springboot-jpa-audit`, Supabase MCP & Skills (`supabase`, `supabase-postgres-best-practices`, migrations, RLS), Postgres MCP (`query`) |
| `privacy_officer` | Etapas 2 e 4 + Auxiliar | `lgpd-privacy-expert` (acionado estritamente quando há dados pessoais/PII ou decisões de IA) |
| `ai_specialist` | Etapas 2 e 3 | `ai-expert`, `rag-expert`, `langchain-expert`, `langgraph-expert`, `genai-expert`, `openai-api-expert`, `nlp-expert`, `genetic-algorithms-expert`, `ml-pipeline-expert`, `deep-learning-cv-expert`, `fastapi-expert`, `mlops-lifecycle-expert`, `hybrid-search-implementation`, `embedding-strategies`, `hugging-face-model-trainer`, `image-generator`, `gemini-live-api-dev`, `gemini-omni-flash-api`, Gemini API Docs (`gemini_search_docs`, `gemini_get_doc`), `gcp-finops-expert`, `cloud-architect` |
| `tester` | Etapas 3 e 4 | `springboot-unit-testing`, `angular-expert`, `e2e-testing-patterns`, Chrome DevTools MCP (`a11y-debugging`, `troubleshooting`, `memory-leak-debugging`) |
| `developer` | Etapa 3 | `angular-expert`, `springboot-expert`, `springboot-dto-mapper`, `springboot-error-handling`, `springboot-security`, `springboot-jpa-audit`, `springboot-swagger`, `fastapi-expert`, `git-expert`, `async-python-patterns`, `frontend-optimistic-mutations`, `frontend-data-contracts`, `framework-migration-code-migrate`, `auth-implementation-patterns`, `n8n-workflow-expert`, `openai-api-expert`, `langchain-expert`, `langgraph-expert`, Figma to Code (`figma-design-to-code`, `figma-code-connect`), Supabase (`supabase`, `supabase-postgres-best-practices`) |
| `reviewer` | Etapa 4 | `code-reviewer`, `git-expert`, `springboot-dto-mapper`, `springboot-error-handling` |
| `ux_reviewer` | Etapa 4 | `uiux-expert`, `frontend-lighthouse`, Figma MCP (`get_design_context`, `get_screenshot`), Mobbin (`best-practices`), Chrome DevTools (`a11y-debugging`) |
| `security` | Etapa 4 | `cybersecurity-infra-expert`, `springboot-security`, `lgpd-privacy-expert`, `api-security-best-practices`, `auth-implementation-patterns`, Supabase Security (`get_advisors`, `query_logs`) |
| `devops` | Etapa 5 | `devops-executive`, `cloud-architect`, `gcp-finops-expert`, `gcp-cloud-run`, `geminiignore-finops`, `git-expert`, `mlops-lifecycle-expert`, GCP (`gcloud`, `finding-google-skills`, `google-cloud-recipe-auth`), Supabase Deploy |
| `finance_advisor` | Auxiliar | `tech-finance-expert`, `gcp-finops-expert` |
| `negotiator` | Auxiliar | `negotiation-stakeholder-expert` |
| `strategic_leader` | Auxiliar | `strategic-tech-leader`, `tech-lead-mentor` |
| `ai_governance_auditor` | Auxiliar | `responsible-ai-governance` |
| `innovation_consultant` | Auxiliar | `tech-innovation-expert`, `pm-skills`, `copywriting`, `ai-seo`, Canva MCP |
| `n8n_specialist` | Auxiliar | `n8n-workflow-expert`, `n8n-ai-advanced`, `openai-api-expert` |

---

## Slash Commands (Atalhos Nativos via `.agents/skills/<nome>/`)
- `/orquestrador`, `/orquestrar`, `/o` — esteira adaptativa de desenvolvimento ou despacho de auxiliares · `/init` — kickoff/fundação do projeto.
- Pipeline: `/po`, `/analyst`, `/architect`, `/designer`, `/dba`, `/developer`, `/reviewer`, `/tester`, `/security`, `/devops`, `/ai_specialist`, `/privacy`.
- Auxiliares: `/finance`, `/negotiator`, `/leader`, `/responsible_ai`, `/innovation`, `/n8n`.
