# Entidade / Feature: [Nome da Entidade ou Feature]

Este documento centraliza todo o planejamento, as especificações e as etapas de execução para as tarefas relacionadas a esta feature específica.

## 1. Dúvidas Resolvidas (Especificação)
[Registro histórico de todas as perguntas levantadas pelo Analista e as decisões definidas em conjunto com o usuário. Fundamental para justificar regras de negócio e não perder o contexto.]
- **Dúvida:** [Pergunta do Analista]
  - **Decisão:** [O que foi acordado com o usuário]

---

## 2. Tarefas e Etapas de Desenvolvimento

### Tarefa 1: [Nome da Tarefa - ex: Criação do CRUD de Usuários]

**Descritivo Detalhado:**
[Descrição completa e aprofundada do que precisa ser desenvolvido nesta tarefa específica e o contexto associado a ela.]

**Critérios de Aceite:**
[Condições que pautarão a escrita dos Testes (TDD) e a validação do QA. Devem garantir que as regras P-XXX associadas sejam cumpridas.]
- [ ] O sistema deve...
- [ ] Quando X ocorrer, Y deve ser retornado...

**Etapas de Execução (Checklist Técnico):**
[A ser preenchido pelo Arquiteto na fase de planejamento. O Arquiteto divide a Tarefa 1 em etapas menores técnicas, insere um descritivo para cada uma e um checkbox para o Desenvolvedor marcar conforme o avanço.]
- [ ] **Etapa 1:** [Nome, ex: Criar migrações e entidade no Banco de Dados]
  - *Descritivo:* Mapear os campos nome, email e data_nascimento.
- [ ] **Etapa 2:** [Nome, ex: Desenvolver a lógica do Service e Repository]
  - *Descritivo:* Fazer os testes unitários passarem.

**Audit (Testes e Validação):**
[A ser preenchido pelo Tester (QA). Um passo a passo detalhado contendo todos os cenários práticos e de uso que deverão ser testados para assegurar que a funcionalidade foi implementada corretamente, cobrindo o Happy Path e os Edge Cases.]
- [ ] **Cenário 1:** Acessar a rota passando token expirado; deve retornar HTTP 401.
- [ ] **Cenário 2:** Cadastrar usuário informando data de nascimento menor de 18 anos sem base legal; a regra P-003 deve barrar e retornar erro.
- [ ] **Cenário 3:** [Outro teste a ser executado]

---

### Tarefa 2: [Nome de uma próxima tarefa na mesma entidade...]
*(Repetir a estrutura de Descritivo, Critérios, Etapas e Audit)*
