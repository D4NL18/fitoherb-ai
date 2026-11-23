# Canvas de Preparação de Negociação Técnica / Executiva

Use este template antes de reuniões críticas de escopo, prazo, orçamento, arquitetura ou contratos com fornecedores.

---

## 1. Contexto e Objetivo da Negociação
- **Tema / Demanda:** `[Ex.: Entrega do módulo de faturamento recorrente até o fim do Q3]`
- **Data da Reunião:** `[DD/MM/AAAA]`
- **Partes Envolvidas:** `[Ex.: Engenharia, Produto, Diretoria Comercial]`
- **Resultado Ideal (Aspiração):** `[O que seria um excelente acordo para nós?]`

---

## 2. Mapeamento de Stakeholders (Matriz de Mendelow)

| Stakeholder | Papel | Poder (A/B) | Interesse (A/B) | Quadrante Mendelow | Estratégia de Abordagem |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `[Nome / Área]` | `[Sponsor]` | Alto | Alto | Gerenciar de Perto | `[Alinhar trade-offs 1:1 antes da reunião]` |
| `[Nome / Área]` | `[Financeiro]` | Alto | Baixo | Manter Satisfeito | `[Enviar resumo de impacto no orçamento]` |
| `[Nome / Área]` | `[Squad X]` | Baixo | Alto | Manter Informado | `[Compartilhar contrato de API e cronograma]` |

---

## 3. Posições vs Interesses (Método de Harvard)

| Dimensão | Nossa Perspectiva (Engenharia/Tech) | Perspectiva da Outra Parte (Negócio/Fornecedor) |
| :--- | :--- | :--- |
| **Posição Declarada** | `[Ex.: Precisamos de 6 semanas para entregar com qualidade]` | `[Ex.: Precisamos no ar em 3 semanas]` |
| **Interesses Reais (Por quê?)** | `[Ex.: Evitar incidentes em produção, manter cobertura de testes e SLA]` | `[Ex.: Apresentar a feature no evento anual para fechar 3 contas enterprise]` |
| **Interesses Compartilhados** | `[Ex.: Crescimento de receita sem perda de credibilidade técnica perante clientes]` | `[Mesmo interesse compartilhado]` |

---

## 4. BATNA (MAANA), Ponto de Reserva e ZOPA

- **Nosso BATNA (Plano B real se não houver acordo):**
  - `[Ex.: Escalar formalmente o risco de qualidade ao CTO / usar fornecedor B já cotado em R$ X]`
- **Nosso Ponto de Reserva (Limite inegociável):**
  - `[Ex.: Nunca abrir mão de testes de segurança/LGPD ou deploy sem rollback]`
- **BATNA Estimado da Outra Parte:**
  - `[Ex.: Adiar anúncio no evento ou apresentar protótipo clicável]`
- **ZOPA Estimada (Zona de Acordo Possível):**
  - `[Ex.: Entrega do fluxo core em 3 semanas via feature flag + fluxos secundários em +2 semanas]`

---

## 5. Pacotes de Opções de Ganho Mútuo (Trade-offs)

Nunca leve apenas uma resposta ("sim" ou "não"). Apresente 3 pacotes claros:

| Opção | Escopo | Prazo | Custo / Esforço | Risco / Qualidade |
| :--- | :--- | :--- | :--- | :--- |
| **Opção A — MVP Focado (Recomendada)** | Fluxo principal (80/20 de Pareto) em produção sob feature flag | 3 semanas | Time atual | Qualidade e testes intactos |
| **Opção B — Escopo Completo** | Todos os fluxos + relatórios + integrações secundárias | 6 semanas | Time atual | Qualidade intacta; maior prazo |
| **Opção C — Aceleração com Reforço** | Fluxo principal + relatórios prioritários | 4 semanas | +1 especialista temporário | Requer pausa na iniciativa Y |

---

## 6. Critérios Objetivos de Suporte
Liste os dados independentes que fundamentam sua posição (evite opiniões pessoais):
- [ ] Velocidade / Throughput histórico da squad nos últimos 3 ciclos.
- [ ] Métricas DORA atuais (Change Failure Rate, MTTR) e impacto histórico de cortes de QA.
- [ ] Requisitos obrigatórios (SLA contratual, OWASP, LGPD).
- [ ] Benchmarks de mercado ou cotações comparativas de fornecedores.

---

## 7. Fechamento e Próximos Passos (Acordo Registrado)
- **Decisão Acordada:** `[Registrar opção escolhida e concessões mútuas]`
- **O que entra / O que sai do escopo:** `[Lista explícita]`
- **Responsáveis e Prazos:** `[Quem faz o quê até quando]`
- **Critério de Revisão / Check-in:** `[Data de validação intermediária]`
