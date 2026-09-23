# Fluxo de Desenvolvimento com IA (AI Agents Workflow) 🤖🚀

Este documento define o fluxo obrigatório para qualquer tarefa de desenvolvimento assistida por Inteligência Artificial neste projeto. O diretório `.agents/` contém o detalhamento individual de cada papel, skill, template e regra de governança.

---

## REGRA DE OURO: Governança de Documentação (.agents/docs/)
> [!CAUTION]
> **É TERMINANTEMENTE PROIBIDO SALVAR ARQUIVOS DE DOCUMENTAÇÃO NA RAIZ DO REPOSITÓRIO (`/`).**
> Todos os artefatos de documentação, esquemas, regras de negócio, tarefas e planos de design DEVEM residir exclusivamente dentro de `.agents/docs/`, seguindo os templates oficiais:
> - **Design System Mestre:** `.agents/docs/design/DESIGN_SYSTEM.md` (Template: `.agents/docs/design/TEMPLATE_DESIGN_SYSTEM.md`)
> - **Design Plan por Feature:** `.agents/docs/design/plans/<feature>.md` (Template: `.agents/docs/design/TEMPLATE_DESIGN_PLAN.md`)
> - **Banco de Dados (Schema & Seeds):** `.agents/docs/db/<modulo>.md` (Template: `.agents/docs/db/TEMPLATE.md` e seeds em `.agents/docs/db/seeds/`)
> - **Regras de Negócio (P-XXX):** `.agents/docs/business_rules/<feature>.md` (Template: `.agents/docs/business_rules/TEMPLATE.md`)
> - **Contratos de API REST:** `.agents/docs/api_contracts/<entidade>.md` (Template: `.agents/docs/api_contracts/TEMPLATE.md`)
> - **Tarefas e Checklists:** `.agents/docs/tasks/<feature>.md` (Template: `.agents/docs/tasks/TEMPLATE.md`)
> - **Decisões de Arquitetura (ADR):** `.agents/docs/adr/ADR-<num>-<nome>.md` (Template: `.agents/docs/adr/TEMPLATE.md`)
> - **Arquitetura Base:** `.agents/docs/architecture/ARCHITECTURE.md`
> - **Backlog e Roadmap:** `.agents/docs/ROADMAP.md`

---

## Princípio do Roteamento Autônomo e Repertórios de Skills Delimitados 🚦🧠
> [!IMPORTANT]
> **Zero Chamadas Manuais de Skills:** O usuário **NÃO** precisa se preocupar em lembrar nomes de skills ou invocar comandos manuais de skills.
> 1. **O Orquestrador Roteia Autonomamente:** Ao receber um prompt, o Orquestrador analisa a natureza da demanda e despacha para o Agente especialista correto.
> 2. **Cada Agente tem seu Repertório Fechado:** Cada agente carrega **apenas** as skills homologadas para o seu domínio (ex: o DBA só acessa modelagem e auditoria de banco; o Desenvolvedor acessa linguagens e frameworks; o Conselheiro Financeiro acessa DRE e FinOps). Isso impede context bloat, alucinações e desperdício massivo de tokens.
> 3. **Agentes da Pipeline vs. Agentes Auxiliares Sob Demanda:** Demandas de engenharia seguem a esteira linear de 12 passos. Já demandas estratégicas, financeiras, de governança de IA, LGPD ou negociação acionam diretamente os Agentes Auxiliares de forma pontual e consultiva.

---

## Fluxo de Trabalho de Desenvolvimento (Pipeline 12 Passos)

Todo prompt ou nova requisição de engenharia de software deve obrigatoriamente seguir as seguintes etapas na ordem estabelecida:

1. **Quebra de Escopo (Product Owner)**
   - O **PO** recebe a demanda abstrata, fatiando-a em User Stories menores, independentes e gerenciáveis dentro de `.agents/docs/ROADMAP.md`. Identifica tarefas com potencial de execução paralela `[PARALLEL]`.

2. **Especificar (Specification)**
   - O **Analista** conduz brainstorming com o usuário, amarra as regras de negócio sequenciais (**P-XXX**) dentro de `.agents/docs/business_rules/<feature>.md` e define o escopo no checklist de `.agents/docs/tasks/<feature>.md`.

3. **Projetar (Design, Architecture & Privacy by Design)**
   - O **Arquiteto** define a arquitetura técnica, banco de dados e contratos de API padronizados em `.agents/docs/api_contracts/<entidade>.md` (com envelope `data`/`meta`).
   - O **Designer** (se envolver Frontend) conduz brainstorming com o usuário, projeta a interface e gera obrigatoriamente o **Design Plan da funcionalidade** em `.agents/docs/design/plans/<feature>.md` seguindo o `DESIGN_SYSTEM.md` e aplicando o filtro Anti-IA (`UI_ANTI_PATTERNS.md`).
   - O **AI Specialist** (se envolver IA) desenha a esteira de ML, prompts modulares, RAG e orquestração de tokens.
   - O **Privacy Officer** conduz a **Revisão de Privacy by Design (LGPD)**: valida a minimização nos contratos de API (anti-overfetching), audita o enquadramento nas 10 Bases Legais (Art. 7º e 11), exige RIPD/DPIA em `.agents/docs/privacy/` se houver dados sensíveis ou IA automatizada, e assegura Privacy by Default na concepção da UI.

4. **Modelagem de Dados Segura (DBA)**
   - O **DBA** traduz o design em arquivos de *Migrations* seguras, aplica travas contra perda de dados, documenta o schema em `.agents/docs/db/<modulo>.md` e gera dados de teste realistas em `.agents/docs/db/seeds/`.

5. **Planejar as Tarefas (Task Planning)**
   - O **Arquiteto** decompõe a solução no checklist detalhado da Tarefa em `.agents/docs/tasks/<feature>.md`, integrando referências aos contratos e ao Design Plan.

6. **Desenvolver Testes Unitários (TDD)**
   - O **Tester** cria a suíte de testes (em código) antes de qualquer lógica produtiva.

7. **Executar (Execution)**
   - O **Desenvolvedor** programa focado em fazer os testes passarem em uma branch isolada da feature, consumindo estritamente os tokens do `DESIGN_SYSTEM.md` e o `Design Plan` (no front), respeitando as convenções de commit da skill `git-expert` e todas as regras em `.agents/rules/`.

8. **Code Review & Auditoria LGPD (Manutenibilidade, Governança & Privacidade)**
   - O **Reviewer** inspeciona o código caçando falhas de Clean Code, complexidade cognitiva (SonarQube), conformidade com as regras em `.agents/rules/` e valida se toda a documentação foi salva corretamente em `.agents/docs/` (vetando arquivos na raiz).
   - O **Privacy Officer** executa a **Auditoria de Código LGPD**: audita controllers, services e DTOs contra vazamento de dados pessoais (PII), veta logs contendo CPFs, cartões, e-mails ou senhas em texto puro, valida o isolamento entre inquilinos (multi-tenancy) e tem **poder de veto imediato** caso identifique violação da LGPD.

9. **UX Review / Vibe Check (Frontend & Filtro Anti-IA)**
   - O **UX Reviewer** valida se as implementações HTML/SCSS estão de acordo com o `Design Plan` da feature e o `DESIGN_SYSTEM.md`. Se faltarem Skeleton Loaders, Empty States, ou tiverem "cara de IA / bootstrap genérico", ele devolve para o Desenvolvedor.

10. **Testar e Auto-Healer Loop (Validation)**
    - O **Tester** roda os testes automatizados e o plano de Auditoria manual para evitar regressões.
    - **Auto-Healer:** Se os testes quebrarem ou o código não compilar, o Orquestrador fará o Desenvolvedor conversar diretamente com o Tester para ler o *Stack Trace* e tentar corrigir o código de forma autônoma por até 3 vezes, antes de devolver para o usuário humano.

11. **Auditoria de Segurança (SecOps)**
    - O **Especialista de Segurança** varre o código aprovado atrás de vulnerabilidades (Injections, Indirect Prompt Injections em RAG, vazamento de credenciais, LGPD) e bloqueia a esteira se houver brechas.

12. **Release via Pull Request (DevOps & FinOps)**
    - O **Engenheiro DevOps** valida a esteira de CI/CD, audita as diretrizes de FinOps (Scale-to-Zero, ciclo de vida GCS, Scorecard >= 4.80), assegura Docker multi-stage enxuto e gera o PR da feature para a branch base com descrição pré-preenchida.

---

## Catálogo de Papéis dos Agentes

### Agentes da Pipeline de Desenvolvimento (Fixos na Esteira)
O **Orquestrador** não escreve código. Sua função é alternar entre os agentes e garantir que o `.agents/docs/STATE.md` esteja atualizado com o contexto atual.

- `.agents/agents/orchestrator.md`: Coordenador da pipeline, memória de contexto e governança.
- `.agents/agents/product_owner.md`: Fatiador de escopo e gestor do backlog no `ROADMAP.md`.
- `.agents/agents/analyst.md`: Mapeador de requisitos e regras de negócio (`business_rules/`).
- `.agents/agents/architect.md`: Projetista de soluções, contratos de API (`api_contracts/`) e ADRs (`adr/`).
- `.agents/agents/designer.md`: Criador de interfaces, fluxos, Design System e Design Plans (`.agents/docs/design/`).
- `.agents/agents/privacy_officer.md`: Encarregado de dados e DPO (Revisão de Privacy by Design no Passo 3 e Auditoria de Código LGPD no Passo 8).
- `.agents/agents/dba.md`: Administrador de banco, modelagem segura (`db/`) e seeds (`db/seeds/`).
- `.agents/agents/developer.md`: Engenheiro de software executor de código sob TDD, Clean Code e Design Plans.
- `.agents/agents/reviewer.md`: Auditor de manutenibilidade, clean code, rules e documentação.
- `.agents/agents/tester.md`: Engenheiro de QA, testes automatizados e guardião do TDD.
- `.agents/agents/security.md`: Auditor de cibersegurança, SAST, DAST e defesas de IA.
- `.agents/agents/devops.md`: Engenheiro de infraestrutura, CI/CD, FinOps e MLOps.
- `.agents/agents/ai_specialist.md`: Especialista em IA, Machine Learning, RAG, Tokenomics e Visão Computacional.
- `.agents/agents/ux_reviewer.md`: Especialista em auditoria visual, fidelidade ao Design Plan e filtro Anti-IA.

### Agentes Auxiliares Transversais (Sob Demanda / Não Fixos na Pipeline)
Agentes acionados pontualmente pelo Orquestrador para análises consultivas, estratégicas, regulatórias ou de negócios:

- `.agents/agents/finance_advisor.md`: Conselheiro financeiro de tecnologia (DRE, EBITDA, Capex vs Opex, VPL, TIR, Payback e Unit Economics).
- `.agents/agents/negotiator.md`: Negociador estratégico e mediador de conflitos via Método de Harvard e Matriz de Mendelow.
- `.agents/agents/strategic_leader.md`: Líder estratégico e mentor técnico (SAM de Henderson-Venkatraman, Liderança Situacional, SPACE, 1:1 e Dívida Técnica).
- `.agents/agents/privacy_officer.md`: Atua também de forma consultiva sob demanda em RIPDs corporativos de larga escala, políticas de privacidade e resposta a incidentes ANPD.
- `.agents/agents/ai_governance_auditor.md`: Auditor de IA responsável e ética (WEF Playbook 2025, viés algorítmico, XAI/SHAP, EU AI Act e PL 2338/2023).
- `.agents/agents/innovation_consultant.md`: Consultor de inovação e plataformas (Três Horizontes de McKinsey, Lean Startup, MVP e Efeitos de Rede).
- `.agents/agents/n8n_specialist.md`: Especialista em automação low-code com N8N (workflows, bots de Telegram/Slack, integrações Google, RAG com Pinecone, MultiAgentes e MCPs).

---

## Matriz de Agentes e seus Repertórios de Skills Autorizadas

Cada agente só tem permissão para carregar as skills estritamente homologadas para a sua função:

| Agente | Tipo | Repertório de Skills Autorizadas |
| :--- | :--- | :--- |
| **Orquestrador** | Pipeline | `context-compressor`, `agent-creator`, `agent-manager-skill` |
| **Product Owner** | Pipeline (Passo 1) | `agile-coach`, `pm-skills`, `copywriting`, `ai-seo` |
| **Analista** | Pipeline (Passo 2) | `business-rules-expert`, `domain-expert`, `pm-skills`, `gemini-deep-research` |
| **Arquiteto** | Pipeline (Passos 3 e 5) | `api-contract-expert`, `springboot-expert`, `fastapi-expert`, `domain-expert`, `springboot-swagger`, `architecture-patterns`, `architect-review`, `cloud-architect`, `framework-migration-legacy-modernize`, `auth-implementation-patterns`, `n8n/n8n-deploy`, `gcp-finops-expert` |
| **Designer** | Pipeline (Passo 3) | `uiux-expert`, `animejs-animation`, `image-generator` |
| **Privacy Officer** | Pipeline (Passos 3 e 8) & Auxiliar | `lgpd-privacy-expert` |
| **DBA** | Pipeline (Passo 4) | `dba-expert`, `springboot-jpa-audit`, `database-architect`, `database-admin` |
| **Desenvolvedor** | Pipeline (Passo 7) | `angular-expert`, `springboot-expert`, `springboot-dto-mapper`, `springboot-error-handling`, `springboot-security`, `springboot-jpa-audit`, `springboot-swagger`, `fastapi-expert`, `fastapi-ai-expert`, `git-expert`, `fastapi-pro`, `fastapi-router-py`, `async-python-patterns`, `frontend-optimistic-mutations`, `frontend-data-contracts`, `framework-migration-code-migrate`, `auth-implementation-patterns`, `n8n/n8n-fundamentos`, `n8n/n8n-openai`, `openai-api/openai-api-fundamentos`, `openai-api/openai-api-chatbot` |
| **Reviewer** | Pipeline (Passo 8) | `git-expert`, `springboot-dto-mapper`, `springboot-error-handling`, `clean-code-guard`, `code-reviewer` |
| **UX Reviewer** | Pipeline (Passo 9) | `uiux-expert`, `frontend-lighthouse` |
| **Tester** | Pipeline (Passos 6 e 10) | `springboot-unit-testing`, `angular-expert`, `e2e-testing-patterns` |
| **Especialista de Segurança** | Pipeline (Passo 11) | `cybersecurity-infra-expert`, `springboot-security`, `lgpd-privacy-expert`, `api-security-best-practices`, `auth-implementation-patterns` |
| **DevOps** | Pipeline (Passo 12) | `devops-executive`, `gcp-finops-expert`, `git-expert`, `mlops-lifecycle-expert`, `gcp-cloud-run`, `cloud-devops`, `geminiignore-finops` |
| **AI Specialist** | Pipeline (Passos 3 e 7) | `ai-expert`, `rag-expert`, `ml-pipeline-expert`, `deep-learning-cv-expert`, `fastapi-ai-expert`, `mlops-lifecycle-expert`, `gemini-live-api-dev`, `gemini-omni-flash-api`, `hybrid-search-implementation`, `embedding-strategies`, `hugging-face-model-trainer`, `image-generator`, `openai-api/*`, `nlp-expert/*`, `generative-ai/*`, `genetic-algorithm/*`, `gcp-finops-expert`, `cloud-architect` |
| **Finance Advisor** | Auxiliar | `tech-finance-expert`, `gcp-finops-expert` |
| **Negotiator** | Auxiliar | `negotiation-stakeholder-expert` |
| **Strategic Leader** | Auxiliar | `strategic-tech-leader`, `tech-lead-mentor` |
| **AI Governance Auditor** | Auxiliar | `responsible-ai-governance` |
| **Innovation Consultant** | Auxiliar | `tech-innovation-expert`, `pm-skills`, `copywriting`, `ai-seo` |
| **N8N Specialist** | **Auxiliar (Sob Demanda)** | `n8n/n8n-fundamentos`, `n8n/n8n-deploy`, `n8n/n8n-openai`, `n8n/n8n-groq-deepseek`, `n8n/n8n-google-slack-telegram-supabase`, `n8n/n8n-rag-memory`, `n8n/n8n-multi-agents`, `n8n/n8n-mcp`, `openai-api/openai-api-fundamentos` |

---

### Catálogo de Skills Disponíveis (97 Skills)

| Skill | Localização | Especialidade |
| :--- | :--- | :--- |
| **`pm-skills`** | `.agents/skills/pm-skills/` | Suíte completa de Product Management (68 skills, 42 workflows): Discovery, Lean Canvas, PRDs, Histórias INVEST, RICE e GTM. |
| **`strategic-tech-leader`** | `.agents/skills/strategic-tech-leader/` | Alinhamento TI-Negócio (SAM), 5 Forças de Porter, Cadeia de Valor, MTP e Arquitetura Corporativa. |
| **`tech-finance-expert`** | `.agents/skills/tech-finance-expert/` | DRE, EBITDA, Gestão de Caixa vs Lucro, Capex/Opex, VPL, TIR, Payback, TCO, OBZ e Unit Economics. |
| **`tech-lead-mentor`** | `.agents/skills/tech-lead-mentor/` | Liderança Situacional (Hersey-Blanchard), 4 Arquétipos do Tech Lead, 1:1s, SBI, SPACE e Dívida Técnica. |
| **`negotiation-stakeholder-expert`** | `.agents/skills/negotiation-stakeholder-expert/` | Método de Harvard (BATNA, ZOPA, Critérios Objetivos), Trade-offs Técnicos e Matriz de Mendelow. |
| **`lgpd-privacy-expert`** | `.agents/skills/lgpd-privacy-expert/` | Privacy by Design & Default (7 princípios), 10 Bases Legais, RIPD/DPIA e Classificação de Dados LGPD. |
| **`cybersecurity-infra-expert`** | `.agents/skills/cybersecurity-infra-expert/` | Arquitetura Zero Trust, Framework NIST CSF 2.0, Modelagem STRIDE, CIS Controls e RTO/RPO. |
| **`tech-innovation-expert`** | `.agents/skills/tech-innovation-expert/` | Três Horizontes de McKinsey, Ambidestria, Lean Startup (MVP, Pivô), Design Thinking e Plataformas. |
| **`responsible-ai-governance`** | `.agents/skills/responsible-ai-governance/` | Governança WEF Playbook 2025, Mitigação de Viés, XAI (SHAP), Red Teaming e Enquadramento EU AI Act. |
| **`devops-executive`** | `.agents/skills/devops-executive/` | Cultura CAMS, Métricas DORA no C-Level, Trunk-Based Development, Quality Gates e GitOps. |
| **`uiux-expert`** | `.agents/skills/uiux-expert/` | Design Systems, Design Plans, Design Thinking (Duplo Diamante), métricas UX e filtro Anti-IA (Nutlope/hallmark). |
| **`ai-expert`** | `.agents/skills/ai-expert/` | Tokenomics extrema, Matriz McKinsey de IA, ROI de IA 2025, Raciocínio Autônomo e ToolsDispatcher. |
| **`rag-expert`** | `.agents/skills/rag-expert/` | Ingestão com sanitização de PII (LGPD), ChromaDB/pgvector, defesa anti-injection e métricas Ragas. |
| **`ml-pipeline-expert`** | `.agents/skills/ml-pipeline-expert/` | Esteiras Scikit-Learn/XGBoost, anti-leakage, K-Fold GridSearchCV e `.joblib`. *(+ML Avançado: feature engineering, KNN scaling, SHAP)* |
| **`deep-learning-cv-expert`** | `.agents/skills/deep-learning-cv-expert/` | Redes Neurais PyTorch, CNNs, U-Net, detecção dinâmica de GPU e `.pth`. *(+OCR, grayscale, blur, YOLO, rastreamento de objetos)* |
| **`fastapi-ai-expert`** | `.agents/skills/fastapi-ai-expert/` | Serving de IA com FastAPI, Lifespan lazy-loading, Pydantic v2 e SSE streaming. |
| **`mlops-lifecycle-expert`** | `.agents/skills/mlops-lifecycle-expert/` | Separação física treino vs inferência, Docker multi-stage, Hugging Face Hub e Drift. |
| **`gcp-finops-expert`** | `.agents/skills/gcp-finops-expert/` | GCP Scale-to-Zero, DRE de Nuvem, ROI de IA (Google Cloud 2025), Lifecycle e Scorecard >= 4.80. *(+Vertex AI, BigQuery ML, Feature Store, Matching Engine)* |
| **`cloud-architect`** | `.agents/skills/cloud-architect/` | Arquitetura de nuvem corporativa (GCP/multi-cloud), IaC com Terraform, topologia de rede e resiliência. *(+ML pipelines: SageMaker, Azure ML, Vertex AI)* |
| **`business-rules-expert`** | `.agents/skills/business-rules-expert/` | Redação de regras estruturadas `P-XXX` em `.agents/docs/business_rules/`. |
| **`api-contract-expert`** | `.agents/skills/api-contract-expert/` | Padronização de APIs e envelope de dados em `.agents/docs/api_contracts/`. |
| **`dba-expert`** | `.agents/skills/dba-expert/` | Dicionários em `.agents/docs/db/`, conformidade LGPD (anonimização/pseudonimização) e seeds. |
| **`agile-coach`** | `.agents/skills/agile-coach/` | Fatiamento INVEST, Hibridismo Ágil-Preditivo (PMBOK 7), Análise de Valor Agregado (EVM) e Riscos. |
| **`git-expert`** | `.agents/skills/git-expert/` | Trunk-Based Development, Conventional Commits com rastreabilidade `P-XXX` e métricas DORA. |
| **`domain-expert`** | `.agents/skills/domain-expert/` | Gestão de Linguagem Ubíqua e consistência de termos em `GLOSSARY.md`. |
| **`fastapi-expert`** | `.agents/skills/fastapi-expert/` | APIs RESTful assíncronas com Python. |
| **`springboot-expert`** | `.agents/skills/springboot-expert/` | Arquitetura corporativa Java Spring Boot e orquestração do backend. |
| **`springboot-swagger`** | `.agents/skills/springboot-swagger/` | Documentação OpenAPI 3 com Springdoc, schemas, exemplos e segurança JWT. |
| **`springboot-unit-testing`** | `.agents/skills/springboot-unit-testing/` | Testes unitários com JUnit 5, Mockito, suítes aninhadas @Nested e @DataJpaTest. |
| **`springboot-security`** | `.agents/skills/springboot-security/` | Spring Security, Stateless JWT (Auth0), dual token (Cookie/Bearer) e @PreAuthorize. |
| **`springboot-error-handling`** | `.agents/skills/springboot-error-handling/` | @RestControllerAdvice, envelopes RestErrorMessage e validação de campos. |
| **`springboot-jpa-audit`** | `.agents/skills/springboot-jpa-audit/` | Entidades UUID, auditoria automática (AuditingEntityListener) e Specifications. |
| **`springboot-dto-mapper`** | `.agents/skills/springboot-dto-mapper/` | DTOs (requests/responses), Bean Validation declarativa e MapStruct 1.5+. |
| **`angular-expert`** | `.agents/skills/angular-expert/` | SPAs modernas em Angular (v17+), Signals, Signal Forms, SSR e SCSS (oficial Angular). |
| **`context-compressor`** | `.agents/skills/context-compressor/` | Sumarização de decisões em KNOWLEDGE_GRAPH para poupar memória. |
| **`gemini-live-api-dev`** | `.agents/skills/gemini-live-api-dev/` | Padrões de desenvolvimento para streaming bidirecional em tempo real com Gemini Live API (áudio/vídeo/WebSockets). |
| **`gemini-omni-flash-api`** | `.agents/skills/gemini-omni-flash-api/` | Geração e edição de vídeo, multimodalidade Flash e otimização extrema de tokenomics com google-genai SDK. |
| **`geminiignore-finops`** | `.agents/skills/geminiignore-finops/` | Otimização de arquivos .geminiignore para eficiência de janela de contexto e corte de custos de tokens (FinOps). |
| **`gemini-deep-research`** | `.agents/skills/gemini-deep-research/` | Pesquisa autônoma recursiva em múltiplos passos com Gemini para benchmarking, literatura e análise de mercado. |
| **`gcp-cloud-run`** | `.agents/skills/gcp-cloud-run/` | Deploy serverless resiliente no Google Cloud Run, concorrência otimizada e integração scale-to-zero. |
| **`fastapi-pro`** | `.agents/skills/fastapi-pro/` | Arquitetura corporativa assíncrona com FastAPI, SQLAlchemy 2.0 async, lifespan events e Pydantic v2. |
| **`fastapi-router-py`** | `.agents/skills/fastapi-router-py/` | Modularização profissional de APIRouter, autenticação, status codes REST e tipagem defensiva. |
| **`async-python-patterns`** | `.agents/skills/async-python-patterns/` | Padrões avançados de concorrência Python (asyncio, semáforos, tarefas em background, anti-bloqueio de loop). |
| **`frontend-optimistic-mutations`** | `.agents/skills/frontend-optimistic-mutations/` | Disciplina de mutações otimistas na UI com rollback automático de cache em caso de erro de rede. |
| **`frontend-lighthouse`** | `.agents/skills/frontend-lighthouse/` | Quality gate CI com Lighthouse, orçamentos de Core Web Vitals e auditoria de performance de build. |
| **`frontend-data-contracts`** | `.agents/skills/frontend-data-contracts/` | Contratos de dados estritos no frontend, validação na borda de rede e tipagem imutável anti-overfetching. |
| **`hybrid-search-implementation`** | `.agents/skills/hybrid-search-implementation/` | Busca híbrida combinando densa (vetorial) e esparsa (BM25) com Reciprocal Rank Fusion (RRF). |
| **`embedding-strategies`** | `.agents/skills/embedding-strategies/` | Estratégias avançadas de chunking, seleção de modelos de embeddings e redução de dimensionalidade. |
| **`hugging-face-model-trainer`** | `.agents/skills/hugging-face-model-trainer/` | Treinamento e fine-tuning com TRL/Unsloth (LoRA/QLoRA/DPO) e exportação GGUF para inferência local. |
| **`api-security-best-practices`** | `.agents/skills/api-security-best-practices/` | Guia de segurança defensiva em APIs: OWASP API Top 10, proteção BOLA/IDOR, rate limit e validação de borda. |
| **`e2e-testing-patterns`** | `.agents/skills/e2e-testing-patterns/` | Arquitetura de testes End-to-End resilientes, Page Object Model, eliminação de flakiness e mocks de rede. |
| **`clean-code-guard`** | `.agents/skills/clean-code-guard/` | Auditoria de Clean Code, SOLID, DRY/KISS/YAGNI, métricas de complexidade ciclomática e falhas de LLM. |
| **`framework-migration-code-migrate`** | `.agents/skills/framework-migration-code-migrate/` | Estratégias de migração de código, atualização de frameworks e scripts automatizados com plano de rollback. |
| **`copywriting`** | `.agents/skills/copywriting/` | Copywriting rigoroso orientado à conversão para landing pages, onboarding e e-mails, sem métricas falsas. |
| **`agent-creator`** | `.agents/skills/agent-creator/` | Scaffolding e criação de subagentes com personas especializadas, delimitação de permissões e skills. |
| **`agent-manager-skill`** | `.agents/skills/agent-manager-skill/` | Gerenciamento, despacho paralelo e monitoramento da execução de múltiplos agentes locais. |
| **`ai-seo`** | `.agents/skills/ai-seo/` | Otimização de conteúdo para busca generativa e citações em LLMs (Google AI Overviews, Perplexity, Gemini). |
| **`animejs-animation`** | `.agents/skills/animejs-animation/` | Animações fluidas de alto padrão com Anime.js, timelines sincronizadas, micro-interações e efeitos SVG. |
| **`architecture-patterns`** | `.agents/skills/architecture-patterns/` | Padrões corporativos: Clean Architecture, Arquitetura Hexagonal, Domain-Driven Design (DDD) e CQRS. |
| **`architect-review`** | `.agents/skills/architect-review/` | Revisão e validação arquitetural de alto nível para escalabilidade, resiliência e integridade sistêmica. |
| **`auth-implementation-patterns`** | `.agents/skills/auth-implementation-patterns/` | Padrões seguros de Autenticação e Autorização: JWT/OIDC, sessões, RBAC/ABAC e proteção de credenciais. |
| **`cloud-devops`** | `.agents/skills/cloud-devops/` | Workflow de infraestrutura em nuvem, orquestração de containers, automação de CI/CD e observabilidade. |
| **`code-reviewer`** | `.agents/skills/code-reviewer/` | Revisão de código especializada em qualidade de IA, análise estática de vulnerabilidades e manutenibilidade. |
| **`database-architect`** | `.agents/skills/database-architect/` | Design e modelagem do data layer, seleção de tecnologias (SQL/NoSQL), particionamento e ciclo de vida. |
| **`database-admin`** | `.agents/skills/database-admin/` | Administração e confiabilidade de bancos de dados em nuvem, alta disponibilidade, DR, backups e tuning. |
| **`framework-migration-legacy-modernize`** | `.agents/skills/framework-migration-legacy-modernize/` | Modernização de sistemas legados via Strangler Fig Pattern, mapeamento de riscos e substituição gradual. |
| **`image-generator`** | `.agents/skills/image-generator/` | Geração e edição visual de imagens e mockups com o modelo multimodal Gemini (gemini-3-pro-image-preview). |
| 🆕 **`n8n/n8n-fundamentos`** | `.agents/skills/n8n/n8n-fundamentos/` | Nós, triggers, webhooks, expressões, execuções, pinning de dados e boas práticas de organização de workflows. |
| 🆕 **`n8n/n8n-deploy`** | `.agents/skills/n8n/n8n-deploy/` | Instalação e operação do N8N em Cloud, VPS (Hostinger), Docker local, ngrok e Google Cloud Run. |
| 🆕 **`n8n/n8n-openai`** | `.agents/skills/n8n/n8n-openai/` | Integração OpenAI no N8N: LLM Chain, Agente de IA com ferramentas, análise de imagem e transcrição de áudio. |
| 🆕 **`n8n/n8n-groq-deepseek`** | `.agents/skills/n8n/n8n-groq-deepseek/` | Integração Groq (baixa latência) e DeepSeek (baixo custo): LLM Chain e pipeline de análise de sentimentos. |
| 🆕 **`n8n/n8n-google-slack-telegram-supabase`** | `.agents/skills/n8n/n8n-google-slack-telegram-supabase/` | Google Workspace, bots Slack, bots Telegram com BotFather e banco de dados Supabase via API REST. |
| 🆕 **`n8n/n8n-rag-memory`** | `.agents/skills/n8n/n8n-rag-memory/` | RAG com Pinecone (upsert, query, namespaces), memória persistente em PostgreSQL/Supabase e tipos de memória. |
| 🆕 **`n8n/n8n-multi-agents`** | `.agents/skills/n8n/n8n-multi-agents/` | Sistemas MultiAgentes no N8N: padrão Supervisor, sub-agentes como ferramentas e paralelismo. |
| 🆕 **`n8n/n8n-mcp`** | `.agents/skills/n8n/n8n-mcp/` | MCPs no N8N: N8N como servidor ou cliente MCP, transports HTTP/SSE e integração com Claude/Cursor. |
| 🆕 **`openai-api/openai-api-fundamentos`** | `.agents/skills/openai-api/openai-api-fundamentos/` | Playground, parâmetros (temperatura, top_p, stop, n), créditos, modelos e proteção de API Key. |
| 🆕 **`openai-api/openai-api-prompt-engineering`** | `.agents/skills/openai-api/openai-api-prompt-engineering/` | Prompt Templates dinâmicos, few-shot, chain-of-thought, output estruturado e mitigação de injeção. |
| 🆕 **`openai-api/openai-api-chatbot`** | `.agents/skills/openai-api/openai-api-chatbot/` | Streaming, histórico de mensagens (window buffer, resumo), sessões por usuário e integração frontend. |
| 🆕 **`openai-api/openai-api-otimizacao`** | `.agents/skills/openai-api/openai-api-otimizacao/` | Rate limiting com exponential backoff, tiktoken, caching e monitoramento de custo por chamada. |
| 🆕 **`nlp-expert/nlp-fundamentos`** | `.agents/skills/nlp-expert/nlp-fundamentos/` | Pipeline NLP clássica, aplicações (Alexa, buscadores, recomendação) e métricas de avaliação. |
| 🆕 **`nlp-expert/nlp-vetorizacao`** | `.agents/skills/nlp-expert/nlp-vetorizacao/` | Bag of Words, TF-IDF, N-grams com CountVectorizer e TfidfVectorizer do scikit-learn. |
| 🆕 **`nlp-expert/nlp-embeddings`** | `.agents/skills/nlp-expert/nlp-embeddings/` | Word2Vec, GloVe, FastText, similaridade semântica cosine e tratamento de palavras OOV. |
| 🆕 **`nlp-expert/nlp-preprocessamento`** | `.agents/skills/nlp-expert/nlp-preprocessamento/` | Tokenização (NLTK, SpaCy), stop words, stemming RSLP, lematização e normalização de texto em PT. |
| 🆕 **`generative-ai/genai-fundamentos`** | `.agents/skills/generative-ai/genai-fundamentos/` | IAs Generativas: modalidades, foundation models, zero-shot/few-shot/fine-tuning e latent space. |
| 🆕 **`generative-ai/genai-arquitetura`** | `.agents/skills/generative-ai/genai-arquitetura/` | GANs (Gerador+Discriminador), VAEs (Encoder+Decoder), Diffusion Models e Transformers para geração. |
| 🆕 **`generative-ai/genai-aplicacoes`** | `.agents/skills/generative-ai/genai-aplicacoes/` | Geração de código (Copilot), imagens (DALL-E, SD), vídeos (Runway) e projetos práticos com FastAPI. |
| 🆕 **`generative-ai/genai-etica`** | `.agents/skills/generative-ai/genai-etica/` | Deepfakes, direitos autorais, bias, desinformação, watermarking e EU AI Act / PL 2338/2023. |
| 🆕 **`genetic-algorithm/ga-fundamentos`** | `.agents/skills/genetic-algorithm/ga-fundamentos/` | Conceitos base: indivíduos, genes, população, fitness e pipeline evolucionário completo. |
| 🆕 **`genetic-algorithm/ga-selecao`** | `.agents/skills/genetic-algorithm/ga-selecao/` | Operadores de seleção: Torneio, Roleta e Rank-based — pressão seletiva vs diversidade. |
| 🆕 **`genetic-algorithm/ga-crossover-mutacao`** | `.agents/skills/genetic-algorithm/ga-crossover-mutacao/` | Crossover (1 ponto, 2 pontos, uniforme) e mutação (bit-flip, Gaussiana) com elitismo. |
| 🆕 **`genetic-algorithm/ga-otimizacao-ml`** | `.agents/skills/genetic-algorithm/ga-otimizacao-ml/` | Hyperparameter tuning com AG, NeuroEvolution/NEAT e biblioteca DEAP como alternativa ao Optuna. |
| 🆕 **`genetic-algorithm/ga-aplicacoes`** | `.agents/skills/genetic-algorithm/ga-aplicacoes/` | AG em TSP, portfólio financeiro, scheduling de rotas e otimização de arquiteturas neurais. |

---

## Atalhos Opcionais (Slash Commands)

> O Orquestrador sabe selecionar os agentes automaticamente. No entanto, se o usuário desejar forçar a execução direta de um agente isoladamente, os seguintes atalhos estão disponíveis:

- `/init`: Inicia a fase de Fundação do Projeto (Kickoff).
- `/orquestrador`: Inicia o fluxo completo de desenvolvimento sequencial autônomo (12 passos).
- `/po`: Atua isoladamente como Product Owner.
- `/analyst`: Atua isoladamente como Analista.
- `/architect`: Atua isoladamente como Arquiteto.
- `/designer`: Atua isoladamente como Designer de UI/UX.
- `/dba`: Atua isoladamente como DBA.
- `/developer`: Atua isoladamente como Desenvolvedor.
- `/reviewer`: Atua isoladamente como Revisor de Código.
- `/tester`: Atua isoladamente como Testador (QA/TDD).
- `/security`: Atua isoladamente focando em segurança (SecOps).
- `/devops`: Atua isoladamente na configuração de PRs, CI/CD, FinOps e MLOps.
- `/ai_specialist`: Atua isoladamente como Especialista em IA.
- `/finance`: Atua isoladamente como Conselheiro Financeiro (Finance Advisor).
- `/negotiator`: Atua isoladamente como Especialista em Negociação & Stakeholders.
- `/leader`: Atua isoladamente como Líder Estratégico & Mentor de Engenharia.
- `/privacy`: Atua isoladamente como Encarregado de Privacidade (DPO / LGPD).
- `/responsible_ai`: Atua isoladamente como Auditor de Governança de IA Responsável.
- `/innovation`: Atua isoladamente como Consultor de Inovação & Plataformas.
- `/n8n`: Atua isoladamente como Especialista N8N (automação de workflows, bots, integrações e MultiAgentes).
