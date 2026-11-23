# Referência: DRE, EBITDA, Caixa vs Lucro, Capex vs Opex, OBZ, TCO e Unit Economics

Guia de referência aprofundado para fundamentar decisões arquiteturais, compras de cloud, business cases de engenharia e apresentações ao C-Level/CFO.

---

## 1. DRE Aplicada à Tecnologia e Engenharia

A Demonstração do Resultado do Exercício (DRE) segue o **Regime de Competência** (fato gerador). Para líderes de TI, o ponto crítico é entender **onde** cada gasto cai na DRE, pois isso altera a Margem Bruta, o EBITDA e o múltiplo de valuation da empresa.

| Linha da DRE | O que entra de Tecnologia | Impacto Estratégico |
| :--- | :--- | :--- |
| **CPV / CMV (COGS)** | Cloud de produção (compute, DB, tráfego), APIs de terceiros por transação (LLM tokens, SMS, pagamento), suporte N1/N2 dedicado ao cliente. | Reduz **Margem Bruta**. Empresas SaaS buscam Margem Bruta $\ge 75\%–80\%$. |
| **Despesas de P&D (R&D)** | Salários de engenheiros, QA, PMs, ambientes de dev/staging, ferramentas de engenharia (GitHub, CI/CD, APM de dev). | Reduz **EBITDA**, mas é visto por investidores como investimento em produto. |
| **Despesas de G&A** | TI corporativa (ERP, notebooks, Google Workspace, segurança interna). | Reduz **EBITDA**; alvo constante de eficiência. |
| **Depreciação & Amortização (D&A)** | Amortização de software proprietário capitalizado (CPC 04 / IAS 38) e depreciação de hardware próprio. | **Não afeta EBITDA**, mas reduz EBIT e gera benefício fiscal (escudo fiscal de IRPJ/CSLL). |

### EBITDA vs Margem EBITDA
- $\text{EBITDA} = \text{EBIT} + \text{Depreciação} + \text{Amortização}$
- $\text{Margem EBITDA} = \frac{\text{EBITDA}}{\text{Receita Operacional Líquida (ROL)}}$
- **Armadilha clássica:** EBITDA alto não significa caixa sobrando. Se a empresa tem alto Capex de renovação ou ciclo de recebimento longo (PMR alto), pode quebrar mesmo com EBITDA positivo.

---

## 2. Gestão de Caixa vs Lucro (Regime de Caixa x Competência)

| Dimensão | Lucro (DRE — Competência) | Caixa (DFC — Caixa) |
| :--- | :--- | :--- |
| **Quando reconhece** | Na emissão da nota / entrega do serviço. | Na entrada/saída efetiva na conta bancária. |
| **Exemplo em SaaS** | Contrato anual de R\$ 120k faturado à vista: DRE reconhece R\$ 10k/mês (receita diferida). | DFC registra +R\$ 120k no Mês 1 (excelente para capital de giro). |
| **Risco principal** | "Lucro contábil" com inadimplência ou estoque/WIP parado. | Insolvência imediata por descasamento de prazos (PMR > PMP). |

### Ciclo Operacional, Ciclo Financeiro e NCG
- $\text{Ciclo Operacional} = \text{PME} + \text{PMR}$
- $\text{Ciclo Financeiro} = \text{PME} + \text{PMR} - \text{PMP}$
- **Alavanca Tech/FinOps:** Negociar faturamento anual antecipado (PMR baixo/negativo) e contratos de cloud/fornecedores com pagamento a 60 dias (PMP alto) gera **Ciclo Financeiro Negativo**, financiando o crescimento sem dívida.

---

## 3. Capex vs Opex e Capitalização de Software

| Critério | Capex | Opex |
| :--- | :--- | :--- |
| **Natureza** | Aquisição ou construção de ativo de vida útil > 1 ano. | Consumo recorrente para operar o negócio. |
| **Efeito no EBITDA** | Preserva EBITDA no curto prazo (vai para o Balanço Patrimonial). | Impacta EBITDA imediatamente no mês do gasto. |
| **Efeito no Caixa (Ano 0)** | Alto desembolso inicial. | Desembolso diluído e elástico. |
| **Exemplos em TI** | Datacenter próprio, desenvolvimento de nova plataforma core capitalizável. | Cloud (GCP/AWS/Azure), licenças SaaS, APIs de IA por token, manutenção corretiva. |

> **Regra Contábil (CPC 04 / IAS 38):** Apenas a fase de **desenvolvimento** de novo produto/feature com viabilidade técnica e econômica comprovada pode ser capitalizada. Pesquisa exploratória, correção de bugs e manutenção rotineira são sempre **Opex**.

---

## 4. Orçamento Base Zero (OBZ / Zero-Based Budgeting)

Diferente do orçamento incremental ("ano passado + inflação"), o OBZ parte de **R\$ 0** em cada ciclo:
1. **Pacotes de Decisão:** Cada squad ou plataforma justifica cada linha de custo (cloud, licenças, SaaS, consultorias) vinculando-a a um objetivo de negócio ou SLA.
2. **Ranking por Retorno:** Pacotes são ordenados por ROI/risco evitado.
3. **Alvos imediatos em TI:**
   - Licenças zumbis (usuários inativos há > 30 dias).
   - Ambientes de homologação/dev ligados 24x7 (economia de ~65% desligando fora do horário comercial).
   - Instâncias superdimensionadas e snapshots/logs sem política de retenção (lifecycle).

---

## 5. TCO (Total Cost of Ownership) — Horizonte Mínimo de 3 Anos

Ao comparar **Build vs Buy** ou **On-Premise vs Cloud**, nunca compare apenas o preço da licença ou o custo do sprint inicial:

$$\text{TCO}_{3\text{ anos}} = C_{\text{aquisição/dev}} + \sum_{t=1}^{3} \left( C_{\text{infra/cloud}, t} + C_{\text{licenças}, t} + C_{\text{manutenção/suporte}, t} + C_{\text{segurança/compliance}, t} + C_{\text{downtime/risco}, t} \right) + C_{\text{migração/saída}}$$

- **Regra prática de manutenção:** Software customizado costuma consumir **15% a 25% do custo inicial de desenvolvimento por ano** apenas em manutenção evolutiva, patches de segurança e atualização de dependências.

---

## 6. Unit Economics para Produtos Digitais e SaaS

| Métrica | Fórmula | Benchmark Saudável | Sinal de Alerta |
| :--- | :--- | :--- | :--- |
| **CAC** | $\frac{\text{Despesas Mkt + Vendas}}{\text{Novos Clientes no Período}}$ | Dependente do ticket | Crescendo sem aumento proporcional de LTV |
| **LTV** | $\frac{\text{ARPU} \times \text{Margem Bruta (\%)}}{\text{Churn Mensal (\%)}}$ | $\ge 3\times \text{CAC}$ | Baseado em receita bruta (sem descontar margem) |
| **LTV / CAC** | $\frac{\text{LTV}}{\text{CAC}}$ | $3.0\times \text{ a } 5.0\times$ | $< 3.0\times$ (queima valor); $> 5.0\times$ (subinvestindo em crescimento) |
| **CAC Payback** | $\frac{\text{CAC}}{\text{ARPU} \times \text{Margem Bruta (\%)}}$ | $\le 12 \text{ meses}$ (SMB) / $\le 18 \text{ meses}$ (Enterprise) | $> 24 \text{ meses}$ (alto consumo de caixa) |
| **NRR (Net Revenue Retention)** | $\frac{\text{MRR Inicial} + \text{Expansão} - \text{Contração} - \text{Churn}}{\text{MRR Inicial}}$ | $> 110\%$ (SaaS B2B) | $< 95\%$ ("balde furado") |
| **Rule of 40** | $\text{Crescimento Anual de Receita (\%)} + \text{Margem EBITDA (\%)}$ | $\ge 40\%$ | $< 20\%$ (crescimento lento e baixa rentabilidade) |

---

## 7. Checklist de Apresentação Financeira para o CFO
- [ ] Fluxo de caixa incremental com premissas explícitas (cenário base, conservador e otimista).
- [ ] VPL > 0 à TMA/WACC da companhia, TIR > TMA e Payback Descontado dentro do horizonte estratégico.
- [ ] Separação clara entre Capex e Opex, com impacto projetado no EBITDA e no Caixa.
- [ ] TCO de 3 anos comparando alternativas (incluindo custo de manutenção e cloud).
- [ ] Impacto nos Unit Economics (Margem Bruta, LTV/CAC, CAC Payback).
