---
description: "Use quando integrar LLMs, prompts estruturados, defesas contra Prompt Injection, RAG, embeddings, bancos vetoriais, MLOps e deploy de modelos de ML/Deep Learning."
trigger: model_decision
---

# Regras de Engenharia de IA, RAG & MLOps 🤖🧠

**ATENÇÃO ESPECIALISTA EM IA, ARQUITETOS, DEVOPS E REVIEWERS:**
Aplicações baseadas em Inteligência Artificial exigem rigor absoluto em segurança contra manipulação de contexto, contenção de alucinações, governança de dados e controle de custos de tokens.

---

## 1. Integração de LLMs & Defesa contra Prompt Injection
- ❌ **Concatenação Insegura de Strings:** NUNCA concatene inputs crus de usuários diretamente dentro de instruções de sistema (`system`). A entrada do usuário DEVE ser enviada sob `"role": "user"`.
- ❌ **Requisições Sem Limite de Tokens:** É proibido permitir o envio de payloads de texto ou arquivos ilimitados para APIs de LLM sem sanitização de tamanho. Conte tokens e aplique limites máximos por requisição para evitar ataques de DDoS financeiro.
- ✅ **Controle de Temperatura & Saídas Estruturadas:**
  - Para geração de código, formatação JSON, classificações ou RAG: use `temperature: 0.0` ou `0.1` e utilize `response_format: { type: "json_object" }` ou esquemas Pydantic / Zod validados.
  - Para criatividade, brainstorming ou redação publicitária: use `temperature: 0.7` a `0.9`.

---

## 2. Arquiteturas RAG & Bancos Vetoriais
- ❌ **Confiança Cega no Contexto Recuperado (Indirect Prompt Injection):** Documentos externos (PDFs, sites, prontuários, uploads de terceiros) indexados no banco vetorial podem conter instruções maliciosas ocultas.
- ✅ **Delimitação e Desconfiança:** Delimite claramente o contexto com blocos estruturados (ex: `<context>...</context>`). No system prompt, ordene explicitamente que o bloco é apenas fonte factual de consulta e que qualquer instrução imperativa contida nele deve ser sumariamente ignorada.
- ✅ **Grounding Estrito:** Se a informação necessária não estiver contida de forma inequívoca nos documentos recuperados, o modelo DEVE responder que não dispõe de dados suficientes, sendo vetada a criação de respostas especulativas.
- ✅ **Deduplicação e Caching de Embeddings:** Nunca regenere embeddings para trechos de texto imutáveis a cada requisição. Armazene vetores persistidos (ChromaDB / pgvector) e deduplique por hash SHA-256 do conteúdo do chunk.

---

## 3. MLOps, Deploy & Prevenção de Drift
- ❌ **Datasets e Treino em Imagem Docker de Produção:** É proibido empacotar scripts de experimentação, datasets brutos ou notebooks de treino na imagem Docker produtiva. O código de treino reside em `training_scripts/` (adicionado ao `.dockerignore`); o container de produção deve conter apenas o código de inferência e os pesos serializados (`weights/`).
- ✅ **Monitoramento Contínuo de Drift:** Implemente monitoramento de *Data Drift* (alteração na distribuição estatística das features de entrada) e *Concept Drift* (alteração na relação entre features e o target de negócio). Dispare alertas para retreinamento quando desvios forem detectados.
- ✅ **Versionamento de Modelos:** Todo artefato de modelo em produção deve possuir tag de versão semântica imutável registrada em registry oficial (MLflow, Hugging Face Hub ou Vertex AI Model Registry).
