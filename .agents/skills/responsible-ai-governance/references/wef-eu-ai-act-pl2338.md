# Referência Técnica: WEF Playbook 2025, EU AI Act, PL 2338/2023, Fairness, XAI e Privacidade em LLMs

Guia de consulta aprofundada para governança, conformidade regulatória e engenharia de IA Responsável.

---

## 1. WEF Responsible AI Playbook 2025 — Estrutura Operacional

O **World Economic Forum (WEF) Responsible AI Playbook 2025** traduz princípios éticos em governança executável ao longo de todo o ciclo de vida de IA (*Design → Build → Deploy → Monitor*):

| Pilar WEF | Artefatos e Controles Esperados | Responsável Primário |
| :--- | :--- | :--- |
| **1. Governança & Liderança** | Comitê de Ética em IA, Política de Uso Aceitável, Inventário de Sistemas de IA, Matriz RACI de accountability. | Liderança Executiva / DPO / AI Governance |
| **2. Equidade & Não-Viés** | Auditoria de representatividade de datasets, métricas de fairness por subgrupo, mitigação pré/in/pós-processamento. | Cientista de Dados / AI Specialist |
| **3. Transparência & XAI** | Model Cards, System Cards, explicabilidade local/global (SHAP/LIME), rotulagem clara de conteúdo sintético. | AI Specialist / Produto |
| **4. Segurança & Robustez** | Red Teaming adversarial, guardrails de entrada/saída, defesa contra Prompt Injection, avaliação de alucinação e drift. | SecOps / AI Specialist / QA |
| **5. Privacidade & Governança de Dados** | Minimização de dados, sanitização de PII em RAG/prompts, contratos Zero Data Retention, conformidade LGPD/GDPR. | DPO / Arquiteto / DBA |
| **6. Impacto Humano & Social** | Human-in-the-Loop (HITL) ou Human-on-the-Loop (HOTL) para decisões críticas, mecanismo de contestação e override humano. | Produto / Operações |

---

## 2. Classificação de Risco: EU AI Act vs. PL 2338/2023 (Marco Legal da IA no Brasil)

| Nível de Risco | EU AI Act (Regulamento UE 2024/1689) | PL 2338/2023 (Brasil — alinhamento conceitual) | Obrigações Técnicas Mínimas |
| :--- | :--- | :--- | :--- |
| **Risco Excessivo / Inaceitável (Proibido)** | Social scoring, manipulação subliminar explorando vulnerabilidades, identificação biométrica remota em tempo real em espaços públicos (salvo exceções estritas), inferência de emoções no trabalho/escola. | Sistemas que induzam comportamento prejudicial à saúde/segurança, explorem vulnerabilidades (idade, deficiência), pontuação social pelo poder público para negar acesso a bens/serviços. | **Veto absoluto** na arquitetura e no roadmap. |
| **Alto Risco** | Infraestrutura crítica, educação/avaliação, emprego/RH, crédito/seguros, saúde/dispositivos médicos, justiça e aplicação da lei, migração. | Infraestrutura crítica, educação, recrutamento/RH, avaliação de crédito, saúde, administração da justiça, veículos autônomos, biometria. | Avaliação de Impacto Algorítmico (AIA), gestão de riscos contínua, governança de dados e testes de viés, logs auditáveis, documentação técnica (Model Card), supervisão humana efetiva e direito à explicação/contestação. |
| **Risco Específico / Propósito Geral (GPAI / LLMs)** | Modelos de IA de propósito geral (GPAI) e sistemas com risco sistêmico; chatbots e geradores de mídia sintética. | Sistemas de IA generativa e de propósito geral com obrigações de transparência, direitos autorais e mitigação de riscos sistêmicos. | Aviso explícito de interação com IA, marca d'água/metadados em conteúdo sintético, resumo de dados de treino, testes adversariais (Red Teaming). |
| **Risco Mínimo / Baixo** | Filtros de spam, recomendações simples, NPCs em jogos. | Sistemas fora das listas de alto risco ou proibição. | Boas práticas voluntárias, códigos de conduta e higiene básica de segurança/LGPD. |

---

## 3. Mitigação de Viés Algorítmico (Fairness)

### 3.1 Fontes Comuns de Viés
- **Viés Histórico:** Dados passados refletem discriminações estruturais (ex.: histórico desigual de aprovação de crédito ou promoções).
- **Viés de Representação / Amostragem:** Subgrupos minoritários sub-representados no conjunto de treino.
- **Proxy Discrimination:** Mesmo removendo atributos protegidos (raça, gênero), variáveis correlacionadas (ex.: CEP, escola) reproduzem a discriminação.

### 3.2 Métricas e Estratégias de Mitigação
- **Métricas principais:**
  - *Disparate Impact Ratio (Regra dos 80%):* $\text{DIR} = \frac{P(\hat{Y}=1 \mid A=\text{desfavorecido})}{P(\hat{Y}=1 \mid A=\text{referência})} \ge 0{,}80$.
  - *Equal Opportunity Difference:* diferença de *True Positive Rate (TPR)* entre grupos próxima de 0.
  - *Equalized Odds:* paridade simultânea de TPR e FPR entre grupos.
- **Intervenções por estágio:**
  - *Pré-processamento:* reamostragem balanceada, *reweighing*, remoção de proxies indevidos.
  - *In-processamento:* restrições de equidade na função de perda (*adversarial debiasing*).
  - *Pós-processamento:* calibração de limiares (*threshold optimization*) por subgrupo quando legalmente permitido e auditado.

---

## 4. Explicabilidade (XAI) com SHAP e LIME

| Método | Escopo | Como Funciona | Quando Usar |
| :--- | :--- | :--- | :--- |
| **SHAP (SHapley Additive exPlanations)** | Global e Local | Calcula a contribuição marginal exata (ou aproximada via TreeSHAP) de cada feature usando teoria dos jogos cooperativos. | Modelos tabulares (XGBoost, LightGBM, Random Forest), crédito, risco e auditorias regulatórias. |
| **LIME (Local Interpretable Model-agnostic Explanations)** | Local | Perturba a entrada em torno de uma instância específica e ajusta um modelo linear interpretável localmente. | Explicações rápidas agnósticas a modelo (texto, imagem, tabular) quando SHAP for computacionalmente caro. |
| **Explicabilidade em LLMs / RAG** | Local (Grounding) | Citação explícita dos trechos/documentos recuperados (*source attribution*) e score de fidelidade (*faithfulness*). | Assistentes corporativos, RAG jurídico/médico e automações baseadas em documentos. |

> **Requisito Prático (LGPD Art. 20 + EU AI Act):** Em decisões automatizadas de alto impacto, exponha na API/UI os **3 principais fatores** que influenciaram o resultado em linguagem compreensível ao titular, preservando segredos comerciais.

---

## 5. Privacidade em LLMs e Arquiteturas RAG

1. **Sanitização de Entrada (PII Redaction):** Mascarar/tokenizar CPF, CNPJ, e-mail, telefone, cartão de crédito e dados de saúde antes de enviar prompts para APIs externas.
2. **Contratos de Dados (Zero Data Retention):** Garantir cláusula contratual impedindo que o provedor de LLM utilize prompts ou outputs para retreinamento de modelos fundacionais.
3. **Isolamento no Banco Vetorial (RAG Multi-Tenant):** Aplicar filtro obrigatório de `tenant_id` e ACL/RBAC **antes** da busca vetorial (*pre-filtering*) para impedir vazamento de documentos entre clientes ou perfis sem permissão.
4. **Prevenção de Memorização e Extração:** Não fazer *fine-tuning* com PII bruto; preferir RAG com controle de acesso granular para dados corporativos e pessoais.
