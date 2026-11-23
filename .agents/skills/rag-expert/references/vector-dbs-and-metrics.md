# Referência: Bancos Vetoriais, Estratégias de Retrieval e Métricas de RAG

Material de apoio detalhado para decisões arquiteturais de RAG em produção.

---

## 1. Comparativo de Bancos Vetoriais (Vector DBs)

| Banco Vetorial | Arquitetura / Índices | Escalabilidade | Multi-Tenancy / LGPD | Custo / Operação | Quando Escolher |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ChromaDB** | Embutido (local/SQLite+Parquet) ou cliente-servidor; HNSW padrão. | Pequena a média (até centenas de milhares de vetores em nó único). | Coleções separadas por tenant ou filtro por metadados (`tenant_id`). | Open-source ($0 local); baixíssimo atrito de setup. | Prototipagem rápida, POCs, ferramentas internas e bases locais. |
| **FAISS** | Biblioteca em memória (CPU/GPU): `Flat` (exato), **IVF** (particionamento por centróides), **HNSW** (grafo hierárquico ANN) e **PQ/SQ** (quantização). | Alta em memória/sharding manual (milhões a bilhões de vetores). | Isolamento manual (um índice por tenant ou pós-filtragem). | Open-source ($0); exige gerenciar persistência, metadados e concorrência. | Busca de ultra-baixa latência, controle fino de memória/recall e workloads offline/batch. |
| **pgvector (PostgreSQL / Supabase)** | Extensão nativa do Postgres com índices `IVFFlat` e `HNSW`. | Média a alta (milhões de vetores com particionamento). | **Excelente:** Row-Level Security (RLS) + JOINs transacionais + auditoria LGPD no mesmo banco. | Baixo/médio (reaproveita Postgres existente; sem infra extra). | Sistemas SaaS que já usam PostgreSQL e precisam de consistência ACID, RLS e filtros SQL complexos. |
| **Pinecone** | Gerenciado (Serverless / Pods), suporte nativo a métricas `cosine`, `dotproduct` e `euclidean`. | Muito alta (escala elástica gerenciada para bilhões de vetores). | **Nativo via `namespace`:** segregação lógica rígida por cliente (`namespace="tenant_123"`) sem multiplicar índices físicos. | Pago por uso (storage + read/write units); zero ops. | Produção SaaS multi-tenant com alta disponibilidade, SLA gerenciado e zero manutenção de infra. |

### Notas Rápidas de Tuning de Índices
- **FAISS IVF:** defina `nlist` (clusters) proporcional a $\sqrt{N}$ e ajuste `nprobe` para equilibrar latência vs recall.
- **HNSW (FAISS / pgvector / Chroma):** parâmetros principais `M` (conexões por nó), `efConstruction` (qualidade na indexação) e `efSearch` (qualidade na consulta).
- **Quantização (PQ/SQ):** reduz drasticamente RAM em índices muito grandes com perda controlada de recall; valide sempre com benchmark de `Recall@k`.

---

## 2. Estratégias de Retrieval

| Estratégia | Como Funciona | Pontos Fortes | Limitações / Trade-offs | Caso de Uso Ideal |
| :--- | :--- | :--- | :--- | :--- |
| **Dense Retrieval** | Embeddings densos + similaridade vetorial (`cosine`/`dotproduct`). | Captura semântica, sinônimos e paráfrases. | Pode falhar em códigos exatos, siglas, SKUs ou termos jurídicos raros. | Perguntas conceituais e linguagem natural aberta. |
| **Sparse Retrieval (BM25)** | Busca léxica baseada em frequência de termos (TF-IDF/BM25). | Alta precisão em termos exatos, códigos, IDs e jargão técnico. | Não entende sinônimos nem intenção semântica. | Catálogos técnicos, normas com artigos/cláusulas, busca por código. |
| **Hybrid Retrieval** | Combina Dense + BM25 (ex.: fusão por *Reciprocal Rank Fusion — RRF* ou pesos configuráveis). | Une recall semântico com precisão léxica. | Exige manter índice vetorial + índice invertido e calibrar pesos. | Padrão ouro para RAG corporativo em produção. |
| **MMR (Maximum Marginal Relevance)** | Penaliza chunks redundantes já selecionados (`search_type="mmr"`, `fetch_k` > `k`). | Aumenta diversidade de evidências no contexto sem estourar tokens. | Custo computacional ligeiramente maior no pós-processamento dos candidatos. | Documentos extensos com trechos repetitivos ou sínteses amplas. |
| **HyDE (Hypothetical Document Embeddings)** | LLM gera uma resposta hipotética para a pergunta; o embedding dessa resposta é usado na busca. | Reduz o *gap* semântico entre perguntas curtas e documentos técnicos longos. | Adiciona 1 chamada de LLM (latência e custo extras) antes do retrieval. | Consultas curtas/ambíguas sobre bases altamente técnicas. |
| **Reranker (Cross-Encoder)** | Recupera `top-k` amplo (ex.: 20) e reordena pares `(pergunta, chunk)` com Cross-Encoder (ex.: BGE-Reranker, Cohere Rerank) mantendo os melhores (ex.: 4–5). | Grande ganho em `Context Precision` e redução de ruído no prompt. | Latência adicional proporcional ao número de pares reordenados. | Sempre recomendado quando `top-k > 5` ou em domínios críticos. |
| **Adaptive Retrieval** | Classifica a intenção da consulta e ajusta `k`, `fetch_k` e `score_threshold` dinamicamente. | Factual (`k=3`, threshold $\ge 0.8$) evita ruído; Analítica (`k=8`, `fetch_k=30`) amplia cobertura. | Requer roteador leve ou heurística bem calibrada. | Assistentes multi-propósito (FAQ + análises aprofundadas). |

---

## 3. Métricas de Avaliação e Monitoramento em Produção

### 3.1 Framework Ragas (Qualidade End-to-End de RAG)
| Métrica | O que Mede | Alvo Recomendado | Ação se Abaixo do Alvo |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Fidelidade)** | Proporção das afirmações da resposta que são 100% inferíveis do contexto recuperado (anti-alucinação). | `>= 0.90` | Reduzir `temperature` para `0.0`, endurecer prompt de groundedness, melhorar reranking. |
| **Answer Relevance** | Grau em que a resposta atende diretamente à pergunta feita pelo usuário (sem rodeios ou desvios). | `>= 0.85` | Refinar instruções do prompt, revisar chunking e testar HyDE/Query Expansion. |
| **Context Precision** | Proporção de chunks recuperados (especialmente no topo do ranking) que realmente contêm informação relevante. | `>= 0.80` | Ativar Hybrid Search, adicionar Reranker Cross-Encoder, ajustar `chunk_size` e `score_threshold`. |

### 3.2 Métricas Clássicas de Retrieval e Geração (`RAGEvaluator`)
- **Retrieval:**
  - `Precision@k`: fração dos `k` documentos recuperados que são relevantes.
  - `Recall@k`: fração de todos os documentos relevantes que apareceram nos `k` recuperados.
  - `F1@k`: média harmônica entre `Precision@k` e `Recall@k`.
  - `MRR` (*Mean Reciprocal Rank*): quão cedo o primeiro documento relevante aparece no ranking.
  - `NDCG` (*Normalized Discounted Cumulative Gain*): qualidade do ordenamento considerando relevância gradual.
- **Geração (comparação contra *golden dataset*):**
  - `ROUGE-1`: sobreposição de unigramas (cobertura de termos-chave).
  - `ROUGE-2`: sobreposição de bigramas (fluência e precisão de expressões).
  - `ROUGE-L`: maior subsequência comum (estrutura e fidelidade sequencial).

### 3.3 Alertas de Anomalia em Tempo Real (`RAGMonitor`)
Registre em log estruturado (sem PII) para cada requisição: `retrieval_time`, `generation_time`, `confidence_score`, `num_documents_retrieved` e `tenant_id`.

| Regra de Alerta | Condição | Severidade | Causa Provável / Mitigação |
| :--- | :--- | :--- | :--- |
| **Baixa Confiança / Risco de Alucinação** | `confidence_score < 0.3` | Alta | Base desatualizada ou pergunta fora de domínio; acionar fallback seguro (*"Não há evidências suficientes..."*) e revisar cobertura. |
| **Degradação do Índice Vetorial** | `retrieval_time > 5.0s` | Alta | Índice sem HNSW/IVF, excesso de `efSearch`/`nprobe`, cold start ou gargalo de rede/DB; otimizar índice e ativar `SmartEmbeddingCache`. |
| **Falha de Cobertura / Zero Docs** | `num_documents_retrieved == 0` | Crítica | Filtro de metadados/namespace incorreto, `score_threshold` alto demais ou falha na ingestão; validar pipeline de indexação. |
