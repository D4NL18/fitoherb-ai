# Regras de Governança de Documentação 📑🚫

**ATENÇÃO TODOS OS AGENTES (ANALISTA, ARQUITETO, DBA, DEV, REVIEWER, ORQUESTRADOR):**
A integridade da memória do projeto depende da organização impecável dos arquivos de documentação técnica.

---

## 1. Proibição Terminante de Arquivos na Raiz do Repositório
- ❌ **Poluição da Raiz:** É PROIBIDO criar ou salvar arquivos de documentação, tasks, contratos, schemas ou regras soltos na raiz do projeto (ex: `/tasks.md`, `/api_contract.md`, `/rules.md`).
- ✅ **A Solução:** Qualquer documentação DEVE ser salva dentro de `.agents/docs/<subpasta>/`.

---

## 2. Padrão de Caminhos por Responsabilidade

1. **Schemas e Tabelas de Banco:**
   - Pasta obrigatória: `.agents/docs/db/<modulo>.md`
   - Template: `.agents/docs/db/TEMPLATE.md`
   - Seeds de teste: `.agents/docs/db/seeds/<modulo>_seeds.sql`

2. **Regras de Negócio (P-XXX):**
   - Pasta obrigatória: `.agents/docs/business_rules/<feature>.md`
   - Template: `.agents/docs/business_rules/TEMPLATE.md`

3. **Contratos de API REST:**
   - Pasta obrigatória: `.agents/docs/api_contracts/<entidade>.md`
   - Template: `.agents/docs/api_contracts/TEMPLATE.md`

4. **Tarefas de Execução e DoD:**
   - Pasta obrigatória: `.agents/docs/tasks/<feature>.md`
   - Template: `.agents/docs/tasks/TEMPLATE.md`

5. **Decisões de Arquitetura (ADR):**
   - Pasta obrigatória: `.agents/docs/adr/ADR-<num>-<nome>.md`
   - Template: `.agents/docs/adr/TEMPLATE.md`

---

## 3. Bloqueio no Code Review e Orquestração
- Se um agente salvar um documento fora desse padrão ou deixar de criá-lo, o **Reviewer** e o **Orquestrador** DEVEM vetar a tarefa e forçar a correção para o caminho canônico antes de qualquer avanço na esteira.
