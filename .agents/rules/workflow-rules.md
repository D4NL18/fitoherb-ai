---
description: "Governança global de workflow: proibição de documentação na raiz (tudo em .agents/docs/) e padrão Git de Conventional Commits atômicos."
trigger: always_on
---

# Governança de Workflow e Git 📑📜

**ATENÇÃO TODOS OS AGENTES (PO, ANALISTA, ARQUITETO, DBA, DEV, TESTER, REVIEWER, ORQUESTRADOR):**
A integridade da memória do projeto e a qualidade do histórico de versão são inegociáveis.

---

## 1. Regra de Ouro da Documentação: Veto à Raiz (`/`)
- ❌ **Poluição da Raiz:** É TERMINANTEMENTE PROIBIDO salvar arquivos de documentação, regras de negócio, contratos, schemas ou checklists soltos na raiz do repositório (ex: `/tasks.md`, `/api_contract.md`, `/rules.md`).
- ✅ **A Solução Canônica:** Todo e qualquer artefato de documentação DEVE residir em `.agents/docs/<subpasta>/`:
  - **Schemas e Tabelas de Banco:** `.agents/docs/db/<modulo>.md` (Seeds em `.agents/docs/db/seeds/`)
  - **Regras de Negócio (P-XXX):** `.agents/docs/business_rules/<feature>.md`
  - **Contratos de API REST:** `.agents/docs/api_contracts/<entidade>.md`
  - **Tarefas de Execução e DoD:** `.agents/docs/tasks/<feature>.md`
  - **Decisões de Arquitetura (ADR):** `.agents/docs/adr/ADR-<num>-<nome>.md`
  - **Design System & Plans:** `.agents/docs/design/DESIGN_SYSTEM.md` e `.agents/docs/design/plans/<feature>.md`
  - **Privacidade & RIPD:** `.agents/docs/privacy/`
  - **Backlog & Roadmap:** `.agents/docs/ROADMAP.md` · **Estado:** `.agents/docs/STATE.md` · **Memória:** `.agents/docs/KNOWLEDGE_GRAPH.md`
- 🚫 **Bloqueio no Code Review:** O Reviewer e o Orquestrador DEVEM vetar imediatamente qualquer commit ou PR com arquivos fora dessa estrutura.

---

## 2. Padrão Git: Conventional Commits Atômicos
- ❌ **Mensagens Vagas:** É EXPRESSAMENTE PROIBIDO fazer commits como `git commit -m "update"`, `"fix typo"`, `"wip"` ou commits aglutinados com múltiplos escopos.
- ✅ **Conventional Commits Obrigatório:**
  - `feat: adiciona login com oauth`
  - `fix(auth): corrige validacao de jwt nulo`
  - `docs(readme): atualiza variaveis de ambiente`
  - `chore(deps): atualiza versao do angular`
  - `refactor(billing): extrai calculo de juros para domain service`
  - `test(order): adiciona testes unitarios de calculo de frete`
- ✅ **A Lei do Commit Atômico:** Cada commit deve representar uma, e apenas UMA mudança lógica independente e funcional (ex: migration em um commit, use case em outro, endpoint em outro).
- ⚠️ **Breaking Changes Explícitas:** Qualquer alteração que quebre compatibilidade de API deve adicionar `!` (ex: `feat!: altera payload de resposta da api de auth`) com rodapé explicando o que precisa ser migrado.
- 🎯 **Rastreabilidade:** Sempre que aplicável, mencione o identificador da regra de negócio (`P-XXX`) ou ticket no corpo do commit.
