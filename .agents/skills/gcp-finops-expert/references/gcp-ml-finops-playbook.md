# Playbook de FinOps para ML e IA no Google Cloud (GCP)

Guia prático para arquitetar e auditar cargas de Machine Learning e IA Generativa no GCP com foco em eficiência financeira, **Scale-to-Zero** e **FinOps Scorecard >= 4.80 / 5.00**.

---

## 1. Matriz de Decisão FinOps: Vertex AI vs BigQuery ML vs Cloud Run

| Critério | BigQuery ML (BQML) | Cloud Run (Serverless Serving) | Vertex AI (Custom Training & Endpoints) |
| :--- | :--- | :--- | :--- |
| **Melhor Uso** | Modelos tabulares (XGBoost, regressão, clustering, séries temporais) sobre dados já no BigQuery | Serving de modelos leves/médios (ONNX, Scikit-Learn, APIs de LLM/RAG) com tráfego intermitente | Deep Learning pesado, fine-tuning com GPU/TPU, pipelines KFP e Feature Store gerenciado |
| **Modelo de Cobrança** | Por TB processado ou slots BigQuery (Zero Data Movement) | Pay-per-use por segundo de CPU/RAM/GPU apenas durante requisições | Por hora de VM/GPU provisionada (treino e endpoint) |
| **Custo em Repouso** | **\$0** (paga apenas armazenamento do modelo no BigQuery) | **\$0** com `--min-instances=0` e `--cpu-throttling` | **\$0** apenas com `--min-replica-count=0` (endpoints dedicados 24/7 custam caro) |
| **Alavanca Principal de Economia** | Elimina ETL, egress e clusters Spark dedicados | Scale-to-Zero + alta concorrência por contêiner (até 80 reqs) | Spot/Preemptible GPUs (até 70–80% OFF) + auto-shutdown de Workbench |

### Regra Prática de Escolha
1. **Os dados já estão no BigQuery e o problema é tabular?** Comece sempre por **BigQuery ML**.
2. **Precisa expor uma API de inferência (ONNX, FastAPI, wrapper de LLM/RAG) com tráfego variável?** Use **Cloud Run** com `--min-instances=0`.
3. **Precisa de treino distribuído em GPU/TPU ou MLOps completo (Model Registry + Drift + Feature Store)?** Use **Vertex AI** com Spot VMs e checkpoints em GCS.

---

## 2. Política de Ciclo de Vida no Cloud Storage (`gcs_lifecycle.json`)

Todo bucket usado para datasets temporários, mídias de IA, checkpoints e logs deve aplicar ciclo de vida automatizado:

```json
{
  "rule": [
    {
      "action": { "type": "Delete" },
      "condition": { "age": 7, "matchesPrefix": ["tmp/", "media/", "uploads/"] }
    },
    {
      "action": { "type": "AbortIncompleteMultipartUpload" },
      "condition": { "age": 1 }
    },
    {
      "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
      "condition": { "age": 30, "matchesPrefix": ["logs/", "audit/", "checkpoints/"] }
    },
    {
      "action": { "type": "SetStorageClass", "storageClass": "ARCHIVE" },
      "condition": { "age": 90, "matchesPrefix": ["logs/", "audit/"] }
    }
  ]
}
```

Aplicação via CLI:
```bash
gcloud storage buckets update gs://SEU_BUCKET --lifecycle-file=gcs_lifecycle.json
```

---

## 3. Roteamento Inteligente de LLMs (Tokenomics)

| Tier de Tarefa | Modelo Alvo | Impacto FinOps |
| :--- | :--- | :--- |
| Classificação, extração simples, triagem, resumo curto | **Gemini Flash-Lite / Flash** | Redução de até 80% no custo por requisição |
| Raciocínio complexo, geração de código crítica, revisão profunda | **Gemini Pro** (sob demanda via roteador) | Reserva orçamento de tokens para alto valor |
| Consultas repetitivas / prompts estáticos longos | **Context Caching + Cache L1/Redis** | Evita reprocessamento de tokens de entrada |

---

## 4. FinOps Scorecard (Meta: >= 4.80 / 5.00)

Critérios auditáveis para o endpoint `GET /api/finops-scorecard` e revisão de release (Etapa 5):

| Pilar | Peso | Critério de Nota Máxima (5.00) |
| :--- | :---: | :--- |
| **1. Computação Scale-to-Zero** | 25% | 100% dos serviços Cloud Run com `--min-instances=0`, `--cpu-throttling` e `--max-instances` limitado; Workbench com auto-shutdown (15–30 min). |
| **2. GCS Lifecycle & Storage** | 20% | Todos os buckets com `gcs_lifecycle.json` ativo (expurgo de temporários em 7d, abort multipart em 1d, Coldline 30d / Archive 90d). |
| **3. Eficiência de ML/IA** | 25% | Treino pesado em Spot/Preemptible GPUs com checkpoints; roteamento Flash-Lite/Flash como padrão; BQML usado quando aplicável. |
| **4. Observabilidade & Logs** | 15% | Retenção de logs configurada (30 dias), sem log de payloads gigantes ou PII, alertas de Billing em 50%, 80%, 100% e 120%. |
| **5. Governança & Unit Economics** | 15% | Labels obrigatórios (`env`, `service`, `owner`, `cost_center`) em 100% dos recursos e custo unitário por inferência monitorado. |

> **Bloqueio de Release:** Qualquer ambiente com score abaixo de **4.80** deve remediar os itens faltantes antes do merge para produção.
