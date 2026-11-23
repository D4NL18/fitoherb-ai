# Referência: INVEST, Abordagem Híbrida (PMBOK 7), Chaos Report, EVM e Métricas de Fluxo

Guia de referência aprofundado para gestão híbrida de projetos de tecnologia, fatiamento de valor, previsibilidade quantitativa e controle de fluxo.

---

## 1. Fatiamento Vertical e Critérios INVEST

Histórias horizontais ("criar tabelas", "criar API", "criar tela") geram estoque de trabalho inacabado (WIP alto) e atrasam o feedback do usuário. Sempre fatie **verticalmente** (valor de ponta a ponta):

| Critério | Pergunta de Verificação | Anti-Padrão |
| :--- | :--- | :--- |
| **I — Independent** | Pode ser desenvolvida e entregue sem travar outra história? | Dependência circular entre 3 stories na mesma sprint. |
| **N — Negotiable** | O "como" técnico está aberto à discussão com a squad? | Especificação engessada ditando implementação interna. |
| **V — Valuable** | Entrega valor mensurável ao cliente ou reduz risco crítico? | Tarefa técnica isolada sem vínculo com objetivo de negócio. |
| **E — Estimable** | O time consegue estimar esforço com razoável clareza? | Escopo vago sem critérios de aceitação ou spike prévio. |
| **S — Small** | Cabe confortavelmente em poucos dias (1–3 dias de ciclo)? | Épico disfarçado de história que leva 3 semanas. |
| **T — Testable** | Possui critérios objetivos (Given/When/Then) automatizáveis? | "Sistema deve ser rápido e intuitivo" (subjetivo). |

---

## 2. Abordagem Híbrida Ágil-Preditiva (PMBOK 7ª Edição)

A 7ª edição do PMBOK migrou de processos prescritivos para **12 Princípios** e **8 Domínios de Desempenho**, legitimando o **Hibridismo**:
- **Camada Preditiva (Macro):** Governança, orçamento (Capex/Opex), marcos regulatórios (LGPD/compliance), contratos com terceiros e viabilidade econômica.
- **Camada Ágil Adaptativa (Meso/Micro):** Descoberta contínua, sprints/Kanban, entregas incrementais, validação com usuários e adaptação rápida.

### Lições do Chaos Report (Standish Group)
Os dados históricos do Chaos Report reforçam por que o fatiamento pequeno e o hibridismo funcionam:
- **Projetos pequenos** têm taxa de sucesso significativamente maior do que megaprojetos monolíticos.
- **Fatores críticos de sucesso:** Patrocínio executivo ativo, envolvimento contínuo do usuário, maturidade emocional do time, otimização de escopo (foco no essencial) e processo ágil disciplinado.
- **Principais causas de falha:** Escopo inchado (*scope creep*), feedback tardio e falta de clareza nos objetivos de valor.

---

## 3. Análise de Valor Agregado (EVM — Earned Value Management)

O EVM integra **Escopo, Prazo e Custo** em uma única linha de base, sendo essencial em projetos híbridos com orçamento e prazo executivos.

### Variáveis Fundamentais
- **BAC (*Budget at Completion*):** Orçamento total planejado do projeto.
- **PV / VP (*Planned Value*):** Valor orçado do trabalho que *deveria* estar concluído até a data de medição.
- **EV / VA (*Earned Value*):** Valor orçado do trabalho *efetivamente entregue e aceito* até a data.
- **AC / CR (*Actual Cost*):** Custo real gasto até a data.

### Fórmulas de Variação, Desempenho e Previsão

| Métrica | Fórmula | Interpretação |
| :--- | :--- | :--- |
| **SV** (Variação de Prazo) | $\text{EV} - \text{PV}$ | $> 0$: adiantado; $< 0$: atrasado |
| **CV** (Variação de Custo) | $\text{EV} - \text{AC}$ | $> 0$: abaixo do orçamento; $< 0$: acima do orçamento |
| **SPI** (Índice de Prazo) | $\frac{\text{EV}}{\text{PV}}$ | $\ge 1.0$: no prazo/adiantado; $< 1.0$: atrasado |
| **CPI** (Índice de Custo) | $\frac{\text{EV}}{\text{AC}}$ | $\ge 1.0$: eficiente; $< 1.0$: estourando orçamento |
| **EAC** (Estimativa no Término) | $\frac{\text{BAC}}{\text{CPI}}$ *(tendência típica)* | Projeção de custo total final mantendo a eficiência atual |
| **ETC** (Estimativa para Terminar) | $\text{EAC} - \text{AC}$ | Quanto ainda será gasto até concluir o projeto |
| **VAC** (Variação no Término) | $\text{BAC} - \text{EAC}$ | $> 0$: economia projetada; $< 0$: déficit projetado |

---

## 4. Métricas de Fluxo (Kanban / Lean) e Lei de Little

Enquanto o EVM governa o macro (custo/prazo do projeto), as **Métricas de Fluxo** governam a saúde diária da engenharia:

- **WIP (*Work in Progress*):** Quantidade de itens iniciados e ainda não concluídos. Limitar WIP reduz troca de contexto e acelera entregas.
- **Throughput (Vazão):** Quantidade de itens concluídos por unidade de tempo (ex.: 6 stories/semana).
- **Lead Time:** Tempo total desde a solicitação/entrada no backlog até a entrega em produção.
- **Cycle Time:** Tempo ativo de trabalho desde o início do desenvolvimento até a conclusão.
- **Flow Efficiency:** $\frac{\text{Tempo de Trabalho Ativo}}{\text{Lead Time Total}} \times 100\%$ (times tradicionais costumam ficar em 10%–20% devido a filas e esperas).

### Lei de Little
$$\text{Lead Time Médio} = \frac{\text{WIP Médio}}{\text{Throughput Médio}}$$

> **Implicação prática:** Se o time quer reduzir o Lead Time pela metade sem aumentar o número de pessoas, o caminho mais rápido e barato é **reduzir o WIP pela metade** (parar de começar e começar a terminar).
