# Template: Strategic Alignment Canvas (Diagnóstico Estratégico de TI)

Preencha este canvas antes de aprovar grandes iniciativas de arquitetura, reestruturações de times ou planos anuais de tecnologia.

---

## 1. Identificação e MTP
- **Iniciativa / Programa:** `[Nome da iniciativa]`
- **Horizonte / Trimestre:** `[Ex: Q3–Q4 / 2026]`
- **Sponsor de Negócio:** `[Nome / Diretoria]`
- **Líder Técnico Responsável:** `[Nome / Papel]`
- **MTP (Propósito Transformador Massivo):** `[Qual transformação de longo prazo esta iniciativa habilita?]`

---

## 2. Alinhamento no Modelo SAM (Henderson & Venkatraman)
- **Perspectiva Dominante (marque uma):**
  - [ ] Execução da Estratégia *(Negócio → Organização → TI)*
  - [ ] Potencial Tecnológico *(Negócio → Estratégia de TI → Infraestrutura de TI)*
  - [ ] Vantagem Competitiva *(Estratégia de TI → Negócio → Organização)*
  - [ ] Nível de Serviço *(Estratégia de TI → Infraestrutura de TI → Organização)*
- **Lacuna Atual (As-Is vs To-Be):**
  - *Onde há desalinhamento hoje?* `[Descreva o gargalo entre negócio e TI]`
  - *O que muda na arquitetura e nos times?* `[Descreva o estado alvo]`

---

## 3. Posicionamento na Cadeia de Valor (Build vs Buy)
| Componente / Capacidade | Atividade (Primária ou Apoio) | Decisão (Build / Buy / Partner) | Justificativa Estratégica |
| :--- | :--- | :--- | :--- |
| `[Ex: Motor de precificação dinâmica]` | `Primária (Operações)` | `Build` | `Diferencial direto de margem` |
| `[Ex: Folha de pagamento / ERP]` | `Apoio (RH / Finanças)` | `Buy (SaaS)` | `Commodity; integrar via API` |

---

## 4. Análise das 5 Forças de Porter (Impacto Tecnológico)
- **Rivalidade:** `[Como reduzimos Lead Time ou aumentamos resiliência frente aos concorrentes?]`
- **Poder dos Fornecedores (Vendor Lock-in):** `[Quais dependências críticas existem e qual o plano de mitigação/saída?]`
- **Poder dos Clientes:** `[Como a solução aumenta valor percebido e custos de troca positivos?]`
- **Novos Entrantes (Moat):** `[Quais dados proprietários, IA ou efeitos de rede fortalecemos?]`
- **Substitutos:** `[Quão modular é a arquitetura caso precisemos pivotar o produto?]`

---

## 5. Conexão com OKRs de Engenharia e FinOps
- **Objetivo Estratégico (O):** `[Objetivo qualitativo claro conectado ao negócio]`
- **Resultados-Chave (KRs):**
  - **KR1 (Performance / Qualidade):** `[Ex: Latência p99 < 250ms | Disponibilidade >= 99.95%]`
  - **KR2 (Velocidade / Fluxo):** `[Ex: Lead Time for Changes < 1 dia]`
  - **KR3 (Custo / Eficiência):** `[Ex: Reduzir custo unitário por transação em 25%]`

---

## 6. Lei de Conway, Dívida Técnica e Riscos
- **Topologia de Times:** `[Os limites das squads refletem os domínios DDD / Value Streams?]`
- **Fitness Functions Automatizadas:** `[Quais regras serão verificadas no CI/CD?]`
- **Dívida Técnica Mapeada (em linguagem de negócio):** `[Ex: Acoplamento no módulo X custa ~R$ Y/mês em retrabalho e atrasa releases em Z%]`
- **Principais Riscos e Mitigações:**
  1. `[Risco 1]` → `[Mitigação]`
  2. `[Risco 2]` → `[Mitigação]`
