# AI Agent Guidelines

Este repositório utiliza o fluxo estrito de 12 passos definido no arquivo `AGENTS.md` e orquestrado por `.agents/agents/orchestrator.md`.

## 1. Regras Anti-Sobrecarga Cognitiva (Context Pruning)
Para manter a performance de raciocínio da IA impecável e evitar o esgotamento da Janela de Contexto (*Context Window*), aplicam-se obrigatoriamente as seguintes travas de leitura:

- **Leitura Dinâmica (Lazy Loading):** Ao ser ativada, a IA deve carregar na memória APENAS este arquivo (`config.md`), o `STATE.md`, e o descritivo do Agente atual em execução (ex: `developer.md`). É expressamente proibido tentar ler toda a pasta `.agents/` ao mesmo tempo.
- **Firewall de Raciocínio (Isolamento de Domínio):** O **Desenvolvedor** e o **Reviewer** não têm permissão para ler as Regras de Negócio extensas (`.agents/docs/business_rules/`). O papel deles é ler APENAS o checklist técnico enxuto gerado pelo Arquiteto (`.agents/docs/tasks/`). Quem consolida e lê regras de negócio longas é o **Analista** e o **Arquiteto**.
- **Arquivamento e Limpeza (Archive):** Terminada a Etapa 12 de uma feature, os arquivos daquela task devem ser movidos para `.agents/docs/.archive/`. Agentes são configurados para ignorar solenemente a pasta `.archive/` ao fazerem *scans* na base de código, garantindo que o passado não polua a tarefa atual.

## 2. Instruções Base (Pipeline de 12 Passos)
1. **Orquestrador é o Maestro:** Conduz a pipeline ou despacha diretamente para Agentes Auxiliares sob demanda.
2. **Gestão de Contexto:** Atualiza continuamente o `.agents/docs/STATE.md`.
3. **Respeite a Sequência Canônica de Desenvolvimento (12 Passos):**
   - **Passo 1 (Product Owner):** Fatiamento INVEST no `ROADMAP.md` e identificação de tarefas `[PARALLEL]`.
   - **Passo 2 (Analista):** Especificação com o usuário, regras `P-XXX` em `.agents/docs/business_rules/` e checklist inicial.
   - **Passo 3 (Projetar - Arquiteto, Designer, AI Specialist & Privacy Officer):** Contratos de API em `.agents/docs/api_contracts/`, ADRs em `.agents/docs/adr/`, Design Plan em `.agents/docs/design/plans/`, arquitetura de IA e **Revisão de Privacy by Design (LGPD)**.
   - **Passo 4 (DBA):** Modelagem em `.agents/docs/db/`, migrations reversíveis, travas contra data loss e seeds realistas em `.agents/docs/db/seeds/`.
   - **Passo 5 (Arquiteto):** Decomposição final do checklist de execução em `.agents/docs/tasks/<feature>.md`.
   - **Passo 6 (Tester - Pré):** TDD - escrita de testes unitários falhos antes de qualquer lógica produtiva.
   - **Passo 7 (Desenvolvedor):** Codificação em branch isolada para satisfazer os testes, cumprindo Clean Code e Design Plan.
   - **Passo 8 (Code Review & Auditoria LGPD - Reviewer & Privacy Officer):** Auditoria de Clean Code, manutenibilidade, regras `.agents/rules/` e **Auditoria de Código LGPD** contra vazamento de PII em logs e payloads.
   - **Passo 9 (UX Reviewer):** Auditoria estética (Vibe Check), conformidade com o Design Plan e aplicação do filtro Anti-IA Slop.
   - **Passo 10 (Tester - Pós & Auto-Healer):** Execução da suíte de testes e plano de auditoria. Loop autônomo de auto-cura (até 3 tentativas).
   - **Passo 11 (SecOps):** Auditoria de segurança, SAST, testes ofensivos (Red Team) e conformidade LGPD.
   - **Passo 12 (DevOps):** Validação de CI/CD, auditoria FinOps (Scorecard >= 4.80), Docker enxuto e abertura de Pull Request.
4. **Regra de Ouro:** NUNCA pule de uma etapa para outra sem justificativa registrada no log de auditoria.
