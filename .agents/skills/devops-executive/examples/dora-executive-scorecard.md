# Exemplo: Scorecard Executivo DORA & Maturidade DevOps

> **Período de Referência:** Q[X] / 202[X]  
> **Unidade de Negócio / Tribo:** [Nome da Tribo ou Plataforma]  
> **Responsável Executivo:** [CTO / VP Engineering / Head of Platform]

---

## 1. Resumo Executivo (C-Level)

| Métrica DORA | Baseline Anterior | Resultado Atual | Meta Trimestral | Faixa Atual | Tendência |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Deployment Frequency** | 2x / semana | 1.8x / dia | >= 2x / dia | High → Elite | ↗️ |
| **Lead Time for Changes** | 4.5 dias | 6 horas | < 2 horas | High | ↗️ |
| **Change Failure Rate (CFR)** | 14.0% | 4.2% | <= 5.0% | **Elite** | ↗️ |
| **Time to Restore (MTTR)** | 3h 20min | 38 min | < 1 hora | **Elite** | ↗️ |

**Síntese para o Board:** A adoção de Trunk-Based Development + Quality Gates automatizados reduziu o Lead Time em 94% e derrubou o CFR para a faixa Elite (< 5%), liberando capacidade estimada de 18% da engenharia anteriormente gasta em correções emergenciais.

---

## 2. Detalhamento por Squad / Serviço

| Squad / Serviço | DF | Lead Time | CFR | MTTR | Error Budget Consumido | Principal Gargalo Identificado |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pagamentos Core** | 2.5x/dia | 45 min | 2.1% | 22 min | 28% | Nenhum crítico (manter Canary) |
| **Onboarding & KYC** | 1.2x/dia | 5h | 4.8% | 40 min | 45% | Suíte E2E levando 32 min no CI |
| **Portal Corporativo** | 3x/semana | 18h | 7.5% | 1h 15min | 82% ⚠️ | Aprovação manual de CAB + PRs > 800 linhas |

---

## 3. Maturidade CAMS, GitOps e Quality Gates

| Dimensão | Status | Evidência / Indicador | Ação Corretiva (Próximo Ciclo) |
| :--- | :---: | :--- | :--- |
| **Trunk-Based Development** | 🟡 Parcial | 78% das branches com vida < 48h | Ativar alerta automático para PRs abertos > 48h |
| **Quality Gates (CI)** | 🟢 Ativo | Cobertura >= 80%, SonarQube e Trivy bloqueantes | Nenhuma ação imediata |
| **GitOps (Zero ClickOps)** | 🟢 Ativo | 100% produção reconciliada via ArgoCD/Terraform | Remover permissões de escrita manual no console em staging |
| **Feature Flags** | 🟡 Parcial | 60% das novas features protegidas por toggles | Criar rotina mensal de limpeza de flags expiradas |
| **Chaos / Resiliência** | 🔴 Inicial | 1 Game Day realizado no semestre | Agendar Game Days trimestrais para serviços Tier-1 |

---

## 4. Plano de Ação Executivo (Próximos 90 Dias)

1. **Reduzir Lead Time do Portal Corporativo (< 4h):** substituir aprovação manual de CAB por *Change Advisory automatizado* baseado nos Quality Gates do pipeline e Canary Rollout.
2. **Otimizar Pipeline de Onboarding:** paralelizar suíte E2E para baixar tempo de CI de 32 min para < 10 min.
3. **Proteger Error Budget:** aplicar política de congelamento de features quando consumo de Error Budget ultrapassar 85% na janela de 30 dias.
