# Template: Experimento Lean & MVP (Construir-Medir-Aprender)

Use este template antes de escrever código para qualquer iniciativa de Horizonte 2 ou Horizonte 3.

---

## 1. Contexto e Classificação
- **Nome do Experimento / MVP:** `[Nome curto]`
- **Horizonte de Inovação:** `[ ] H1 (Core)  [ ] H2 (Emergente)  [ ] H3 (Disrupção)`
- **Tipo de Inovação:** `[Incremental / Arquitetural / Radical / Disruptiva]`
- **Responsável (Product / Tech):** `[Nomes]`
- **Janela do Experimento:** `[Data início]` a `[Data fim]` *(recomendado: 1 a 3 semanas)*

---

## 2. Hipótese Falseável (Obrigatória)
> **Acreditamos que** `[segmento específico de usuários]`
> **vai** `[realizar ação observável X]`
> **quando oferecermos** `[proposta de valor / funcionalidade mínima Y]`,
> **porque** `[dor ou motivação central W]`.
> **Saberemos que estamos certos quando** `[métrica acionável Z atingir limiar >= N em T dias]`.

### Suposição Mais Arriscada (*Riskiest Assumption Test — RAT*)
- `[Qual é a premissa que, se for falsa, invalida toda a ideia?]`

---

## 3. Desenho do MVP (Escopo Mínimo)
- **Formato do MVP:** `[ ] Landing Page / Fake Door  [ ] Concierge  [ ] Wizard of Oz  [ ] Protótipo Funcional  [ ] Feature Flag em Produção`
- **O que ENTRA no MVP:**
  - `[Item estritamente necessário para testar a hipótese]`
- **O que FICA FORA (Explicitamente Cortado):**
  - `[Ex: Painel administrativo completo, automação de cobrança, multi-idioma]`
- **Isolamento Arquitetural (Ambidestria):** `[Como garantimos zero impacto no SLA do H1? Ex: serviço isolado, feature flag, limite de tráfego]`

---

## 4. Métricas Acionáveis vs Critério de Decisão
| Métrica Acionável | Baseline Atual | Meta de Sucesso (Perseverar) | Sinal de Alerta (Pivotar / Encerrar) |
| :--- | :--- | :--- | :--- |
| `[Ex: Taxa de ativação em 48h]` | `[N/A ou X%]` | `[>= 25%]` | `[< 10%]` |
| `[Ex: Retenção D7]` | `[N/A ou X%]` | `[>= 15%]` | `[< 5%]` |

*(Métricas de vaidade como pageviews totais ou cadastros inativos são proibidas como critério de decisão.)*

---

## 5. Resultados e Decisão (Preencher ao Final do Ciclo)
- **Dados Coletados:** `[Resumo objetivo dos números e feedbacks qualitativos]`
- **Aprendizado Validado:** `[O que comprovamos ou refutamos sobre o cliente/mercado?]`
- **Decisão Formal:**
  - [ ] **Perseverar** *(avançar para próxima iteração / escala)*
  - [ ] **Pivotar** — Tipo de pivô: `[Segmento / Proposta de Valor / Canal / Zoom-In / Zoom-Out / Monetização]`
  - [ ] **Encerrar** *(arquivar código experimental e documentar aprendizado)*
- **Próximo Passo Imediato:** `[Ação concreta e responsável]`
