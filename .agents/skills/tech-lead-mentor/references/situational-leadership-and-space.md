# Referência: Liderança Situacional, Arquétipos, Segurança Psicológica, SPACE e Dívida Técnica

Guia de aprofundamento para Tech Leads e líderes de engenharia multiplicarem o impacto de seus times.

---

## 1. Os 4 Arquétipos do Tech Lead (Quando Alternar)

Um erro comum é ficar preso ao arquétipo de conforto (geralmente o **Arquiteto Hands-on**). O Tech Lead maduro lê o contexto da squad e ajusta sua alocação:

| Arquétipo | Sintoma que Exige Este Modo | Risco do Excesso |
| :--- | :--- | :--- |
| **Arquiteto (Hands-on)** | Decisões técnicas críticas, início de produto, migração de alto risco. | Virar gargalo de código e impedir o crescimento técnico do time. |
| **Gestor de Pessoas** | Conflitos, queda de moral, onboarding intenso, falta de clareza de carreira. | Distanciar-se demais da realidade técnica e perder credibilidade arquitetural. |
| **Facilitador (Agile Coach)** | PRs parados, dependências externas travando entregas, rituais improdutivos. | Atuar apenas como secretário de cerimônias sem direcionamento técnico. |
| **Estratégico (Evangelista)** | Desalinhamento com Produto/C-Level, pressão irreal de prazos, roadmap técnico ignorado. | Desconectar-se do dia a dia da squad e dos problemas práticos de execução. |

---

## 2. Liderança Situacional (Hersey & Blanchard)

A maturidade é **específica da tarefa**, não um rótulo fixo da pessoa. Um engenheiro sênior em backend (M4) pode estar em M1 ao assumir pela primeira vez infraestrutura Kubernetes ou liderança de projeto.

- **E1 — Direção (para M1):** alta direção, baixo apoio emocional. Checklist claro, pareamento inicial, checkpoints curtos.
- **E2 — Orientação (para M2):** alta direção, alto apoio. Explica o *porquê*, valida frustrações da curva de aprendizado, constrói confiança.
- **E3 — Apoio (para M3):** baixa direção, alto apoio. Perguntas abertas (*"Que trade-offs você vê entre A e B?"*), decisão compartilhada.
- **E4 — Delegação (para M4):** baixa direção, baixo apoio operacional. Alinha resultado esperado, restrições e prazo; delega o *como*.

---

## 3. Segurança Psicológica (Amy Edmondson & Projeto Aristóteles)

No Projeto Aristóteles do Google, **Segurança Psicológica** foi o fator #1 de times de alta performance — acima de senioridade individual ou composição técnica.

### O que É e o que NÃO É
- **É:** poder admitir erros, fazer perguntas "básicas", discordar de decisões técnicas e propor ideias sem medo de humilhação ou retaliação.
- **NÃO é:** ausência de cobrança, permissividade ou falta de padrões técnicos. Segurança psicológica alta + padrões altos = **zona de aprendizado e alta performance**.

### Práticas Concretas
1. **Blameless Post-Mortem:** foco em processos, alertas, testes e arquitetura que permitiram o incidente — nunca em culpados individuais.
2. **Modelagem pelo Líder:** diga explicitamente *"Eu não sei, vamos descobrir juntos"* ou *"Errei nessa decisão de arquitetura"*.
3. **Code Review Construtivo:** critique o código e os trade-offs, nunca o autor; separe bloqueadores objetivos de sugestões de estilo.

---

## 4. SPACE Framework (Complementando DORA)

Criado por pesquisadoras do GitHub, Microsoft e UVic (Forsgren et al.), o **SPACE** evita a armadilha de medir produtividade por uma única métrica manipulável (como LOC ou número de commits).

- **S — Satisfaction & Well-being:** pesquisas de pulso, eNPS interno, sinais de burnout e sustentabilidade do ritmo.
- **P — Performance:** confiabilidade em produção, impacto no cliente, taxa de falhas em mudanças (Change Failure Rate).
- **A — Activity:** commits, PRs, deploys, incidentes tratados *(usar sempre em conjunto com outras dimensões, nunca como meta individual)*.
- **C — Communication & Collaboration:** tempo de revisão de PRs, qualidade de onboarding, compartilhamento de conhecimento (bus factor).
- **E — Efficiency & Flow:** tempo ininterrupto de foco (*deep work*), Lead Time, redução de handoffs e retrabalho.

**Regra de ouro:** selecione **no máximo 3 dimensões** por ciclo (misturando percepção qualitativa e telemetria) e meça no nível do **time**, não para ranquear indivíduos.

---

## 5. Gestão da Dívida Técnica (Martin Fowler + Linguagem de Negócio)

- **Classificação:** separe dívida **Prudente/Deliberada** (atalho consciente para validar hipótese, com plano de pagamento) de dívida **Imprudente** (falta de testes/padrões que precisa ser estancada imediatamente).
- **Regra dos 20%:** proteja 20% da capacidade de cada sprint para amortização contínua (refatoração, atualização de dependências, observabilidade).
- **Como Negociar com Produto/C-Level:** traduza sintomas técnicos em custo de atraso, risco operacional e impacto financeiro (ex.: *"O acoplamento no módulo de faturamento dobra o tempo de qualquer nova feature e gerou 4 incidentes críticos no último trimestre"*).
