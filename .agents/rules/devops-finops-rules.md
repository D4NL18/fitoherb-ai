---
description: "Use quando configurar infraestrutura cloud, FinOps, Scale-to-Zero, logging estruturado JSON, observabilidade, CI/CD, Docker multi-stage e gestao de secrets."
trigger: model_decision
---

# Regras de DevOps, FinOps & Observabilidade ⚙️💰

**ATENÇÃO ENGENHEIROS DEVOPS, ARQUITETOS E DESENVOLVEDORES:**
A esteira de release e a infraestrutura devem operar sob os pilares de automação, resiliência, segurança e eficiência de custos (FinOps Scorecard >= 4.80).

---

## 1. FinOps & Eficiência de Custos na Nuvem
- ❌ **Retentativas Infinitas em Mensageria (Poison Messages):** Proibido processar filas (Pub/Sub, SQS, RabbitMQ) em loops de erro sem parada, gerando milhões de requisições inúteis. Configure obrigatoriamente *Dead Letter Queues (DLQ)* com *Exponential Backoff* e limite de retentativas (ex: 3 vezes).
- ❌ **Storage Sem Ciclo de Vida:** Proibido criar Buckets (GCS / S3) com dados temporários sem regras de ciclo de vida (*Object Lifecycle Policies*) para expiração automática.
- ❌ **Provisionamento Cego Sem Limites:** Nunca suba containers (Cloud Run, ECS, Kubernetes) com recursos irrestritos. Aplique orçamentos estritos de CPU/RAM (ex: 512MB RAM / 0.5 CPU inicial) e adote **Scale-to-Zero** em ambientes não-produtivos.

---

## 2. Observabilidade & Logging Estruturado
- ❌ **Console Logs em Texto Puro:** Proibido o uso de `console.log("texto")` em produção. Todos os logs devem ser emitidos em formato **JSON estruturado** com campos padronizados: `timestamp`, `severity`/`level`, `event`, `message`.
- ✅ **Correlation ID Obrigatório:** Toda requisição DEVE receber/propagar um `x-correlation-id` (UUID) injetado em todas as chamadas de banco, serviços externos e linhas de log para rastreabilidade ponta a ponta.
- ✅ **Sanitização de PII em Logs (Redaction):** Configure a camada de logging para ofuscar automaticamente campos sensíveis (`password`, `token`, `cpf`, `creditCard`).
- ✅ **Fadiga de Alertas:** Notificações no Slack/PagerDuty devem ser disparadas exclusivamente para erros sistêmicos reais (`ERROR` e `FATAL`), nunca para `INFO` ou `WARN`.

---

## 3. Pipelines de CI/CD & Segurança de Infraestrutura
- ❌ **Segredos Hardcoded:** É TOTALMENTE PROIBIDO commitar senhas, chaves de API ou certificados no repositório. Siga o *12-Factor App*: use variáveis de ambiente com arquivo `.env.example` versionado e Secret Manager na nuvem (GCP Secret Manager / AWS Secrets Manager).
- ❌ **Deploy Direto Sem Quality Gate:** Nenhuma alteração entra nas branches principais (`main`/`develop`) sem passar pelo pipeline automatizado contendo:
  1. Linter e verificação de tipagem estrita.
  2. Execução da suíte completa de testes automatizados com bloqueio em caso de falha.
  3. Build/compilação validada da imagem Docker (multi-stage enxuto).
- ❌ **Bancos Expostos à Internet:** Portas de banco de dados (5432, 3306) nunca devem ser expostas para `0.0.0.0/0`. Isole em VPC privada com acesso via bastions ou Cloud SQL Auth Proxy.
