---
name: pm-skills
description: Suíte completa de Product Management (PM Skills Marketplace). Da descoberta à estratégia, execução, lançamento e métricas — PRDs, User Stories, Lean Canvas, Priorização, OKRs, GTM, Discovery e Análise de Produto.
---

# Habilidade: Product Management Operating System (PM-Skills) 🧭🚀

## Propósito
Esta skill consolida o conjunto completo de competências, ferramentas, frameworks e comandos do ecossistema **PM Skills Marketplace** (baseado em `phuryn/pm-skills`). Ela transforma agentes de produto em líderes analíticos e estratégicos de alto impacto, cobrindo o ciclo de vida de produto de ponta a ponta: da ideação e validação de problemas até a execução ágil, go-to-market, métricas de crescimento e qualidade de entrega.

---

## Os 9 Pilares de Product Management

```
+----------------------------------------------------------------------------------------------------+
|                                PM SKILLS OPERATING SYSTEM (9 PILARES)                              |
+--------------------------+--------------------------+----------------------------------------------+
| 1. Product Discovery     | 2. Product Strategy      | 3. Execution & Delivery                      |
|    - Opportunity Tree    |    - Lean & Business Mod.|    - PRDs & User/Job Stories                 |
|    - Interview Scripts   |    - Porter, SWOT, PESTLE|    - Outcome Roadmaps                        |
|    - Assumption Testing  |    - Pricing & Monetiz.  |    - RICE, MoSCoW, Pre-Mortem, OKRs          |
+--------------------------+--------------------------+----------------------------------------------+
| 4. Market Research       | 5. Growth & Positioning  | 6. Go-To-Market (GTM)                        |
|    - Competitive Analysis|    - North Star Metric   |    - Ideal Customer Profile (ICP)            |
|    - Journey Mapping     |    - Value Proposition   |    - Beachhead Segment                       |
|    - TAM / SAM / SOM     |    - Growth Loops        |    - Battlecards & GTM Motions               |
+--------------------------+--------------------------+----------------------------------------------+
| 7. Data Analytics        | 8. AI Shipping & Quality | 9. Professional Toolkit                      |
|    - A/B Test Analysis   |    - Intended vs Implem. |    - Privacy & Regulatory Templates          |
|    - Cohort Retention    |    - Static QA Audits    |    - Executive Communications                |
+--------------------------+--------------------------+----------------------------------------------+
```

---

## 1. Pilar de Descoberta de Produto (Product Discovery)
Localização: `.agents/skills/pm-skills/references/discovery/`

- **Opportunity Solution Tree (`opportunity-solution-tree`):** Mapeamento do resultado desejado (Outcome) ➔ Oportunidades do cliente ➔ Soluções potenciais ➔ Experimentos de validação (Metodologia Teresa Torres).
- **Roteiro e Sumarização de Entrevistas (`interview-script`, `summarize-interview`):** Criação de perguntas abertas livres de viés confirmatório (The Mom Test) e síntese de dores em *insights* acionáveis.
- **Mapeamento e Priorização de Premissas (`identify-assumptions-new`, `identify-assumptions-existing`, `prioritize-assumptions`):** Matriz de Risco vs Certeza para isolar premissas mais perigosas antes de qualquer linha de código.
- **Triagem e Análise de Pedidos de Features (`analyze-feature-requests`, `prioritize-features`):** Conversão de ruído de clientes em oportunidades reais de produto.

---

## 2. Pilar de Estratégia de Produto (Product Strategy)
Localização: `.agents/skills/pm-skills/references/strategy/`

- **Lean Canvas & Startup Canvas (`lean-canvas`, `startup-canvas`):** Decomposição do modelo em 1 página: Problema, Solução, Proposta Única de Valor, Vantagem Injusta, Segmentos, Métricas Chave e Estrutura de Custos.
- **Estratégia de Monetização e Precificação (`monetization-strategy`, `pricing-strategy`):** Modelos de precificação (Freemium, Tiered, Usage-based, Flat-rate) e métricas de elasticidade de preço.
- **Análise Competitiva e de Mercado (`porters-five-forces`, `swot-analysis`, `pestle-analysis`, `ansoff-matrix`):** Diagnóstico estrutural de atratividade da indústria e direcionamento estratégico.
- **Visão e Proposta de Valor (`product-vision`, `value-proposition`):** Formulação da tese inspiradora de longo prazo e alinhamento do Value Proposition Canvas (Gains, Pains, Customer Jobs vs Gain Creators, Pain Relievers, Products & Services).

---

## 3. Pilar de Execução e Entrega (Execution & Delivery)
Localização: `.agents/skills/pm-skills/references/execution/`

- **PRDs de Alto Impacto (`create-prd`):** Especificação completa de produto contendo Contexto, Problema, Métricas de Sucesso, Não-Escopo, Requisitos Funcionais, Requisitos Não-Funcionais e Riscos.
- **Histórias de Usuário & Critérios de Aceite (`user-stories`):** Formato INVEST (Independente, Negociável, Valiosa, Estimável, Pequena, Testável) com critérios de aceite estruturados sob BDD (`Given-When-Then`).
- **Job Stories / Jobs to be Done (`job-stories`):** `Quando [situação], Eu quero [motivação/ação], Para que [resultado esperado]`.
- **Roadmap Orientado a Resultados (`outcome-roadmap`):** Substituição de listas de funcionalidades por colunas *Now / Next / Later* ancoradas em métricas e problemas a resolver.
- **Frameworks de Priorização (`prioritization-frameworks`):**
  - **RICE Score:** $\frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$.
  - **MoSCoW:** Must have, Should have, Could have, Won't have.
  - **Valor vs Esforço:** Matriz $2 \times 2$ (Quick Wins, Major Projects, Fill-ins, Time Sinks).
- **Pre-Mortem e Red Team de Estratégia (`pre-mortem`, `strategy-red-team`):** *"Estamos a 6 meses no futuro e o produto fracassou catastroficamente. O que deu errado?"* - antecipação implacável de riscos.
- **OKRs e Planejamento de Sprint (`brainstorm-okrs`, `sprint-plan`):** Objetivos qualitativos inspiradores atrelados a Key Results quantitativos mensuráveis.

---

## 4. Pilar de Pesquisa de Mercado (Market Research)
Localização: `.agents/skills/pm-skills/references/market-research/`

- **Análise Competitiva (`competitor-analysis`):** Mapeamento de concorrentes diretos, indiretos e substitutos com análise de gaps.
- **Customer Journey Map (`customer-journey-map`):** Etapas (Awareness, Consideration, Purchase, Onboarding, Retention, Advocacy), pontos de contato, emoções e pontos de atrito.
- **Dimensionamento de Mercado (`market-sizing`):** Estimativa top-down e bottom-up de TAM (Total Addressable Market), SAM (Serviceable Addressable Market) e SOM (Serviceable Obtainable Market).
- **User Personas & Segmentação (`user-personas`, `user-segmentation`, `market-segments`):** Criação de arquétipos comportamentais com dores, motivações e hábitos reais.

---

## 5. Pilar de Crescimento e Posicionamento (Growth & Marketing)
Localização: `.agents/skills/pm-skills/references/growth/`

- **North Star Metric (`north-star-metric`):** Identificação da métrica única que melhor captura o valor entregue aos clientes e o motor de crescimento do negócio.
- **Declaração de Proposta de Valor (`value-prop-statements`):** `Para [público-alvo] que [necessidade/dor], o [produto] é uma [categoria] que [benefício principal]. Diferente de [concorrente], nós [diferencial único]`.
- **Growth Loops & Posicionamento (`growth-loops`, `positioning-ideas`, `marketing-ideas`):** Ciclos virtuosos sustentáveis onde um usuário ativo atrai novos usuários.

---

## 6. Pilar de Go-To-Market (GTM)
Localização: `.agents/skills/pm-skills/references/gtm/`

- **Estratégia e Movimentos de GTM (`gtm-strategy`, `gtm-motions`):** Escolha de modelo: Product-Led Growth (PLG), Sales-Led Growth (SLG), Marketing-Led ou Community-Led.
- **Ideal Customer Profile & Beachhead (`ideal-customer-profile`, `beachhead-segment`):** Definição cirúrgica do primeiro segmento a conquistar antes da expansão em massa.
- **Competitive Battlecards (`competitive-battlecard`):** Guia rápido de diferenciação contra rivais: Como vencemos, Onde perdemos, Objeções comuns e Landmines para os concorrentes.

---

## 7. Pilar de Dados e Métricas (Data Analytics)
Localização: `.agents/skills/pm-skills/references/analytics/`

- **Análise de Testes A/B (`ab-test-analysis`):** Significância estatística ($p\text{-value} < 0.05$), poder estatístico, tamanho amostral mínimo e cálculo de MDE.
- **Análise de Coortes (`cohort-analysis`):** Curvas de retenção temporal $M+0, M+1, \dots, M+12$ para detectar se o produto atingiu Product-Market Fit (curva flat) ou leaky bucket.

---

## 8. Pilar de AI Shipping & Qualidade de Entrega
Localização: `.agents/skills/pm-skills/references/ai-shipping/`

- **Intended vs. Implemented (`intended-vs-implemented`):** Auditoria semântica cruzando o PRD original com o código efetivamente comitado, impedindo omissão de requisitos ou escopo fantasma.
- **Artefatos de Lançamento (`shipping-artifacts`):** Geração de checklist de release, release notes amigáveis e documentação de suporte ao cliente.

---

## 9. Pilar de Governança e Ferramentas (Toolkit)
Localização: `.agents/skills/pm-skills/references/toolkit/`

- Templates contratuais e regulatórios rápidos para validação de conceitos (`privacy-policy`, `draft-nda`).

---

## Diretrizes de Uso pelos Agentes Autorizados

| Agente | Como consome a skill `pm-skills` |
| :--- | :--- |
| **Product Owner (`product_owner.md`)** | **Usuário Primário.** Fatiamento de histórias INVEST (`user-stories`), priorização RICE/MoSCoW (`prioritization-frameworks`), roadmaps (`outcome-roadmap`), elaboração de PRDs (`create-prd`), OKRs e condução de Pre-Mortems. |
| **Analista (`analyst.md`)** | Mapeamento de problemas e descoberta de valor (`opportunity-solution-tree`), roteiros de entrevista (`interview-script`), cenários e critérios de aceite detalhados. |
| **Consultor de Inovação (`innovation_consultant.md`)** | Formulação de hipóteses e validação de teses via Lean Canvas (`lean-canvas`, `startup-canvas`), Proposta de Valor, 5 Forças de Porter e estratégias de GTM. |
| **Conselheiro Financeiro (`finance_advisor.md`)** | Análise de precificação (`pricing-strategy`), monetização e dimensionamento de mercado (`market-sizing`). |

---

## Comandos Rápidos Disponíveis nas Referências
Os fluxos prontos em markdown estão disponíveis em `.agents/skills/pm-skills/references/<pilar>/commands/`:
- `write-prd.md` / `write-stories.md` / `sprint.md` / `plan-okrs.md` / `pre-mortem.md`
- `discover.md` / `brainstorm.md` / `interview.md` / `triage-requests.md`
- `strategy.md` / `business-model.md` / `pricing.md` / `value-proposition.md`
- `plan-launch.md` / `battlecard.md` / `growth-strategy.md`
- `analyze-test.md` / `analyze-cohorts.md`
- `ship-check.md` / `derive-tests.md`
