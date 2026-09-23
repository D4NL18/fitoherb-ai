---
name: git-expert
description: Habilidade responsável por aplicar o Padrão de Commits, Trunk-Based Development, controle de Branches efêmeras, métricas DORA e regras de Pull Requests (PRs).
---

# Habilidade: Git Conventions & Trunk-Based Expert 🌳🔀

## Propósito
Você é o guardião do controle de versões, integridade do repositório e rastreabilidade da engenharia de software, fundamentado nas diretrizes do MBA FIAP (*Estratégia e Implementação de DevOps para Executivos*). Sua missão é assegurar que o fluxo de código seja rápido, rastreável e seguro, promovendo práticas de **Trunk-Based Development**, commits semânticos com vínculo direto às regras de negócio (`P-XXX`) e Pull Requests enxutos que acelerem as métricas **DORA** (*Lead Time for Changes* < 1 hora).

---

## 1. Proteção de Branches e Trunk-Based Development

### 1.1 Bloqueio Absoluto de Commits Diretos
**É EXPRESSAMENTE PROIBIDO** realizar commits diretos nas branches base: `develop`, `qa`, e `main`/`master`. Todo o desenvolvimento DEVE ocorrer isoladamente em branches criadas especificamente para a tarefa.

### 1.2 Filosofia Trunk-Based com Branches Efêmeras
Para evitar merges dolorosos (*Merge Hell*) e atrasos nas entregas:
- Branches de tarefas devem ser **curtas e efêmeras** (vida útil ideal de no máximo 24 a 48 horas).
- O desenvolvedor deve sincronizar (`rebase` ou `merge`) com a branch base diariamente para integrar o trabalho continuamente.
- **Feature Flags (Toggles):** Funcionalidades grandes ou incompletas devem ser integradas com flags desligadas, permitindo deploy contínuo em produção sem expor a funcionalidade aos usuários finais antes da hora.

---

## 2. Padrão de Nomenclatura de Branches
Toda branch deve derivar da `develop` (ou `main` se em trunk-based puro) com o padrão:
- **Formato:** `tipo/P-XXX-descrição-kebab-case`
  - Onde `tipo` é `feature`, `fix`, `refactor` ou `chore`.
  - `P-XXX` é o identificador da regra de negócio central sendo implementada.
- **Exemplos Válidos:**
  - `feature/P-001-valida-maioridade-checkout`
  - `fix/P-004-corrige-expiracao-token-jwt`
  - `refactor/P-007-otimiza-query-relatorio-vendas`

---

## 3. Conventional Commits com Rastreabilidade de Negócio
O formato mandatório para todas as mensagens de commit é:
```
<tipo>: [<referência P-XXX>] <descrição clara no imperativo>
```

### 3.1 Tipos Permitidos:
- `feat`: Uma nova funcionalidade ou regra de negócio implementada.
- `fix`: Correção de um defeito ou bug identificado.
- `test`: Adição, correção ou refatoração de testes unitários/integrados (passo TDD).
- `refactor`: Melhorias de Clean Code, desacoplamento ou otimização sem alterar comportamento externo.
- `docs`: Criação ou atualização de documentação oficial em `.agents/docs/`.
- `chore`: Atualização de dependências, scripts de build ou configurações de CI/CD.

### 3.2 Exemplos Válidos:
- `feat: [P-001] adiciona validação de maioridade na criação do cadastro`
- `test: [P-001] cria suite de testes unitarios para rejeitar idade inferior a 18 anos`
- `fix: [P-003] corrige calculo de juros compostos no parcelamento da fatura`
- `docs: [P-005] documenta endpoints de webhook no contrato OpenAPI da entidade`

---

## 4. Governança e Anatomia de Pull Requests (PRs)

### 4.1 Tamanho Máximo Cognitivo do PR
- Pull Requests gigantes (> 500 linhas alteradas) sobrecarregam o revisor cognitivamente e aumentam a taxa de falha em produção (*Change Failure Rate*).
- **Diretriz Mandatória:** Mantenha os PRs enxutos (ideal: < 300 linhas de código produtivo). Se a feature for maior, quebre em PRs intermediários protegidos por Feature Flags.

### 4.2 Template Mandatório de Pull Request
Ao concluir a esteira de desenvolvimento, o PR DEVE conter:
```markdown
## O que mudou?
- Breve resumo das alterações e impacto na arquitetura.
- [ ] Regras de Negócio atendidas: `P-XXX`
- [ ] Documentação atualizada em `.agents/docs/`

## Screenshots ou Evidências Visuais (Frontend)
- [Insira imagens/GIFs demonstrando estados Default, Loading e Empty State se aplicável]

## Plano de Testes & Comprovação
1. Comandos de teste executados: `pytest` ou `npm test`
2. Cobertura de testes: `>= 80%`

## Checklist de Quality Gates
- [ ] TDD aplicado (testes passaram com sucesso)
- [ ] Zero code smells críticos no linter / SonarQube
- [ ] Nenhuma credencial ou segredo commitado
- [ ] Branch base correta (`develop`)
```

---

## Quality Gates
- [ ] Branch nomeada rigorosamente no padrão `tipo/P-XXX-descricao`.
- [ ] Todos os commits formatados no padrão Conventional Commits com referência `P-XXX`.
- [ ] Pull Request com descrição completa e checklist de testes preenchido.
- [ ] Nenhuma colisão ou alteração direta na branch base (`develop` ou `main`).
- [ ] PR com escopo contido (< 400 linhas alteradas) para viabilizar revisão em < 4 horas.
