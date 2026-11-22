# Referência: Cultura CAMS, Métricas DORA, Trunk-Based Development, GitOps e Resiliência

Este documento aprofunda os pilares executivos de DevOps e Engenharia de Plataforma para orientar decisões de liderança técnica, desenho de pipelines e governança de entrega contínua.

---

## 1. Cultura CAMS na Prática Executiva

O acrônimo **CAMS** (cunhado por Damon Edwards e John Willis) sintetiza os quatro pilares que sustentam a transformação DevOps além de ferramentas:

| Pilar | Anti-Padrão Comum | Prática Executiva Recomendada | Indicador de Maturidade |
| :--- | :--- | :--- | :--- |
| **Culture (Cultura)** | Silos ("Dev joga por cima do muro para Ops"), cultura de culpa em incidentes. | Times multidisciplinares (*stream-aligned*), *blameless post-mortems*, autonomia com responsabilidade (*You build it, you run it*). | Tempo médio para resolução sem escalação departamental; engajamento em post-mortems. |
| **Automation (Automação)** | Deploys manuais via runbooks longos, testes regressivos manuais, ClickOps em produção. | CI/CD 100% automatizado, IaC (Terraform/OpenTofu), Quality Gates bloqueantes, provisionamento self-service via IDP. | % de deploys sem intervenção humana; tempo de provisionamento de novo ambiente. |
| **Measurement (Medição)** | Métricas de vaidade (linhas de código, horas trabalhadas, número de commits). | Métricas de fluxo e estabilidade (DORA), SLOs/Error Budgets, telemetria de negócio correlacionada a releases. | Cobertura de telemetria DORA por squad; visibilidade em dashboard executivo. |
| **Sharing (Compartilhamento)** | Conhecimento concentrado em "heróis" individuais; reescrita constante de boilerplates. | Golden Paths, bibliotecas/módulos IaC internos compartilhados, guilds/comunidades de prática e base de lições aprendidas. | Taxa de adoção de Golden Paths da plataforma interna. |

---

## 2. Métricas DORA no Nível C-Level

As 4 métricas DORA equilibram **Velocidade (Throughput)** e **Estabilidade (Stability)**. Otimizar velocidade sem estabilidade gera incidentes; otimizar estabilidade sem velocidade gera estagnação de mercado.

### 2.1 Definições, Fórmulas e Faixas de Performance

| Métrica | Dimensão | Como Medir | Elite | High | Medium | Low |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deployment Frequency (DF)** | Velocidade | Contagem de deploys bem-sucedidos em produção por período. | Múltiplos/dia (sob demanda) | 1x/dia a 1x/semana | 1x/semana a 1x/mês | < 1x a cada 6 meses |
| **Lead Time for Changes (LT)** | Velocidade | Mediana do tempo entre o commit (ou merge na `main`) e a execução em produção. | < 1 hora | 1 dia a 1 semana | 1 semana a 1 mês | > 6 meses |
| **Change Failure Rate (CFR)** | Estabilidade | `(Deploys que causaram incidente/rollback/hotfix) / (Total de deploys) * 100%`. | 0% – 5% | 5% – 10% | 10% – 15% | > 46% |
| **Time to Restore Service (MTTR)** | Estabilidade | Mediana do tempo entre a detecção de um incidente em produção e a restauração completa do serviço. | < 1 hora | < 1 dia | 1 dia a 1 semana | > 1 semana |

### 2.2 Tradução das Métricas DORA para o Board / C-Level
- **Deployment Frequency & Lead Time:** traduzem-se em **Time-to-Market** e capacidade de resposta regulatória ou competitiva.
- **Change Failure Rate:** traduz-se em **Custo da Não-Qualidade** (retrabalho, perda de receita por indisponibilidade, erosão de confiança).
- **MTTR:** traduz-se em **Resiliência Operacional** e proteção de SLA contratual.

> [!IMPORTANT]
> Nunca use métricas DORA para punir indivíduos ou ranquear squads de forma punitiva (Lei de Goodhart: quando uma métrica vira meta punitiva, deixa de ser uma boa métrica). Use-as para identificar gargalos sistêmicos (ex: filas de aprovação manual, testes lentos, acoplamento arquitetural).

---

## 3. Trunk-Based Development (TBD) e Feature Flags

### 3.1 Por que TBD supera o GitFlow
- **Batch Size pequeno:** PRs pequenos (< 300 linhas, vida útil < 24–48h) reduzem drasticamente o risco de conflitos e facilitam revisões profundas.
- **Feedback rápido:** problemas de integração aparecem em minutos no CI, não semanas depois em uma branch `release`.
- **Deploy vs Release desacoplados:** o código sobe para produção continuamente (Deploy técnico), mas só é exposto aos usuários quando o negócio ativa a **Feature Flag** (Release de negócio).

### 3.2 Tipos de Feature Flags e Higiene
1. **Release Toggles:** escondem funcionalidades incompletas na `main`. Vida curta (dias/semanas); devem ser removidas após 100% de rollout.
2. **Experiment Toggles:** testes A/B ou rollout Canary (1% → 10% → 50% → 100%).
3. **Ops Toggles (Kill Switches):** degradam recursos não críticos sob pico extremo de carga.

---

## 4. GitOps e Infraestrutura Imutável

### 4.1 Os 4 Princípios do GitOps (OpenGitOps)
1. **Declarativo:** todo o sistema (infraestrutura, redes, workloads, políticas) é descrito declarativamente.
2. **Versionado e Imutável:** o estado desejado reside no Git com histórico auditável e imutável.
3. **Puxado Automaticamente (Pulled):** controladores (ex.: ArgoCD, Flux) sincronizam o cluster a partir do Git, eliminando credenciais de cluster espalhadas em scripts de CI.
4. **Reconciliado Continuamente:** qualquer *drift* (alteração manual fora do Git) é detectado e revertido automaticamente pelo controlador.

### 4.2 Estratégias de Progressive Delivery
- **Blue/Green:** dois ambientes idênticos; troca instantânea de tráfego com rollback imediato.
- **Canary Release:** exposição gradual (ex.: 5% → 25% → 100%) com análise automática de métricas de erro/latência (rollback automático se violar SLO).

---

## 5. Engenharia de Resiliência e Chaos Engineering

A Engenharia de Resiliência parte do princípio de que **falhas são inevitáveis** em sistemas distribuídos.
- **Padrões Obrigatórios:** Timeouts explícitos, Retries com *Exponential Backoff + Jitter*, Circuit Breakers, Bulkheads (isolamento de pools de recursos) e Graceful Degradation.
- **Game Days e Chaos Engineering:**
  1. Defina o **Steady State** (estado normal mensurável via SLI/SLO).
  2. Formule uma hipótese (ex.: *"se 1 zona de disponibilidade cair, o p99 permanece < 300ms e erro < 0.1%"*).
  3. Injete a falha controlada primeiro em staging e, com maturidade, em janelas controladas de produção com *blast radius* mínimo.
  4. Documente achados e transforme-os em testes automatizados no pipeline.
- **SLIs, SLOs e Error Budget:**
  - **SLI:** indicador mensurável (ex.: % de requisições HTTP 2xx com latência < 250ms).
  - **SLO:** meta acordada (ex.: 99.9% em janela móvel de 30 dias → 43.2 min de indisponibilidade tolerada).
  - **Error Budget:** quando o orçamento de erro se esgota, novas features são pausadas para priorizar estabilidade e dívida técnica.
