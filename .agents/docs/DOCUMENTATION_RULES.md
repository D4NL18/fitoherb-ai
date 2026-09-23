# Governança de Documentação do Projeto 📚

## REGRA DE OURO (VETO À RAIZ)
> [!CAUTION]
> **É TERMINANTEMENTE PROIBIDO SALVAR ARQUIVOS DE DOCUMENTAÇÃO, TAREFAS, REGRAS DE NEGÓCIO, SCHEMAS OU ARTEFATOS DE DESIGN NA RAIZ DO REPOSITÓRIO (`/`).**
> Todos os arquivos de documentação técnica gerados pelos agentes DEVEM obrigatoriamente residir dentro do diretório `.agents/docs/` nas suas respectivas subpastas. Nenhuma exceção é tolerada.

---

## 1. Mapeamento Mandatório de Diretórios

| Tipo de Documentação | Diretório Obrigatório | Template a Seguir | Agente Responsável | Skill Associada |
| :--- | :--- | :--- | :--- | :--- |
| **Design System Mestre** | `.agents/docs/design/DESIGN_SYSTEM.md` | `.agents/docs/design/TEMPLATE_DESIGN_SYSTEM.md` | **Designer** | `uiux-expert` |
| **Design Plan de Features** | `.agents/docs/design/plans/<feature>.md` | `.agents/docs/design/TEMPLATE_DESIGN_PLAN.md` | **Designer** | `uiux-expert` |
| **Banco de Dados (Schema)** | `.agents/docs/db/<modulo>.md` | `.agents/docs/db/TEMPLATE.md` | **DBA** | `dba-expert` |
| **Seeds de Teste (Mock Data)** | `.agents/docs/db/seeds/<modulo>_seeds.sql` | Definido em `dba-expert` | **DBA** | `dba-expert` |
| **Regras de Negócio (P-XXX)** | `.agents/docs/business_rules/<feature>.md` | `.agents/docs/business_rules/TEMPLATE.md` | **Analista** | `business-rules-expert` |
| **Contratos de API (REST)** | `.agents/docs/api_contracts/<entidade>.md` | `.agents/docs/api_contracts/TEMPLATE.md` | **Arquiteto** | `api-contract-expert` |
| **Checklist de Tarefas (Tasks)** | `.agents/docs/tasks/<feature>.md` | `.agents/docs/tasks/TEMPLATE.md` | **Arquiteto** / **Analista** | `agile-coach` |
| **Decisões de Arquitetura (ADR)** | `.agents/docs/adr/ADR-<num>-<nome>.md` | `.agents/docs/adr/TEMPLATE.md` | **Arquiteto** | N/A |
| **Arquitetura Base** | `.agents/docs/architecture/ARCHITECTURE.md` | Padrão arquitetural | **Arquiteto** | N/A |
| **Estado da Pipeline (STATE)** | `.agents/docs/STATE.md` | Estado da execução | **Orquestrador** | N/A |
| **Backlog e Roadmap** | `.agents/docs/ROADMAP.md` | Template do Roadmap | **Product Owner** | `agile-coach` |

---

## 2. Diretrizes de Preenchimento Obrigatório

1. **Nunca Criar Arquivos em Branco:** Todo arquivo criado deve conter o template completamente preenchido e adaptado para o domínio da demanda.
2. **Nomenclatura Padrão:**
   - Nomes de arquivos sempre em `snake_case` ou `kebab-case` sem espaços e sem caracteres especiais (ex: `gestao_usuarios.md`, `faturamento_mensal.md`).
3. **Consistência Ubíqua (DDD):**
   - Os termos utilizados nas colunas de banco, contratos de API, regras de negócio e planos de design devem obrigatoriamente bater com o dicionário definido em `.agents/skills/domain-expert/GLOSSARY.md`.
4. **Validação pelo Reviewer, UX Reviewer e Orquestrador:**
   - Os agentes de auditoria devem bloquear a esteira de desenvolvimento se qualquer artefato de documentação estiver faltando ou tiver sido salvo fora de `.agents/docs/`.
