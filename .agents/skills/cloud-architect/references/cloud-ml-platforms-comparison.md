# Comparativo Prático: Plataformas de ML em Nuvem (AWS vs Azure vs GCP)

Referência arquitetural para escolha e desenho de soluções de Machine Learning e MLOps entre **AWS SageMaker**, **Azure Machine Learning** e **GCP Vertex AI**.

---

## 1. Matriz Comparativa por Capacidade

| Capacidade | AWS SageMaker | Azure Machine Learning (Studio / AutoML) | GCP Vertex AI |
| :--- | :--- | :--- | :--- |
| **Ambiente de Desenvolvimento** | SageMaker Studio (JupyterLab gerenciado, Canvas no-code) | Azure ML Studio (Notebooks, Designer visual drag-and-drop) | Vertex AI Workbench (JupyterLab integrado ao BigQuery/GCS) |
| **Treinamento Gerenciado** | SageMaker Training Jobs (Managed Spot até 90% OFF, distribuição nativa) | Azure ML Compute Clusters (Low-priority VMs, auto-scale até 0) | Vertex AI Custom Training (Preemptible/Spot GPUs e TPUs nativas) |
| **AutoML** | SageMaker Autopilot (tabular, gera notebooks auditáveis) | Azure Automated ML (tabular, visão, NLP, séries temporais — forte em enterprise) | Vertex AI AutoML (tabular, imagem, vídeo, texto) + BigQuery ML (SQL-first) |
| **Feature Store** | SageMaker Feature Store (Online DynamoDB/Redis-like + Offline S3/Glue) | Azure ML Feature Store (Spark-backed, integração com Synapse/ADLS) | Vertex AI Feature Store (Online Bigtable/Optimized + Offline BigQuery) |
| **Serving / Endpoints** | Real-Time, Serverless Inference, Async Inference, Multi-Model Endpoints | Managed Online Endpoints (Blue/Green nativo), Batch Endpoints | Vertex AI Endpoints (Traffic Splitting, Scale-to-Zero) + Cloud Run (GPU/CPU) |
| **Orquestração de Pipelines** | SageMaker Pipelines (DSL Python nativa, integração Step Functions) | Azure ML Pipelines (YAML/SDK v2, integração Azure DevOps/GitHub) | Vertex AI Pipelines (Serverless Kubeflow Pipelines / TFX) |
| **Model Registry** | SageMaker Model Registry (Model Packages, aprovação por estágio) | Azure ML Registry (compartilhamento cross-workspace) | Vertex AI Model Registry (versionamento semântico + integração BQML) |
| **Governança & Responsible AI** | SageMaker Clarify (viés e explicabilidade SHAP) + Model Monitor | Responsible AI Dashboard (fairness, error analysis, counterfactuals, SHAP) | Vertex AI Explainable AI + Model Monitoring (skew/drift) + ML Metadata |

---

## 2. Pontos Fortes e Trade-offs por Provedor

### AWS SageMaker
- **Pontos Fortes:** Ecossistema mais maduro para inferência multi-modelo (Multi-Model Endpoints reduzem custo quando há dezenas de modelos pequenos), excelente suporte a Managed Spot Training e integração profunda com S3, Glue, EMR e Bedrock.
- **Trade-offs:** Curva de aprendizado inicial mais íngreme devido à granularidade de IAM Roles, VPC Endpoints e múltiplos sub-serviços.

### Azure Machine Learning (Studio & AutoML)
- **Pontos Fortes:** Melhor experiência corporativa integrada ao Microsoft Entra ID (AD), Azure DevOps e **Responsible AI Dashboard** pronto para auditorias de conformidade. AutoML e Designer facilitam adoção por times híbridos.
- **Trade-offs:** Dependência forte do ecossistema Azure (Synapse/Fabric, ADLS Gen2) para extrair o máximo de governança e performance.

### GCP Vertex AI
- **Pontos Fortes:** Experiência mais coesa entre dados e ML (integração nativa com **BigQuery** e **BigQuery ML** sem movimentação de dados), pipelines 100% serverless baseados em padrão aberto (Kubeflow/KFP), suporte nativo a TPUs e serving ultra-enxuto com **Cloud Run**.
- **Trade-offs:** Menor variedade de tipos de instâncias especializadas que a AWS em algumas regiões; exige atenção a cotas de GPU por região.

---

## 3. Critérios de Decisão Arquitetural

1. **Onde residem os dados (Data Gravity):** Priorize a nuvem onde o Data Lake / Data Warehouse já opera (S3 → SageMaker, ADLS/Fabric → Azure ML, BigQuery/GCS → Vertex AI) para evitar custos de egress e latência.
2. **Perfil do Time:**
   - Time focado em SQL/Analytics → **GCP (BigQuery ML + Vertex AI)**.
   - Time corporativo com forte exigência de auditoria/low-code → **Azure ML Studio + Responsible AI Dashboard**.
   - Time de engenharia MLOps com alta escala de endpoints/modelos → **AWS SageMaker**.
3. **Portabilidade e Anti-Lock-in:**
   - Empacote modelos em contêineres Docker padrão (FastAPI / Triton / ONNX Runtime).
   - Use formatos abertos (ONNX, MLflow, Kubeflow Pipelines) quando houver requisito explícito de multi-cloud.
