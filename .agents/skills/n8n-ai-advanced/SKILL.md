---
name: n8n-ai-advanced
description: "Use quando a tarefa envolver: Inteligencia Artificial avancada no N8N — AI Agents, integracao OpenAI/Groq/DeepSeek, RAG com bancos vetoriais (Pinecone/Supabase), memoria conversacional, multi-agentes e MCP (Model Context Protocol)."
---

# Habilidade: N8N Advanced AI, RAG & Multi-Agents 🤖🔗

## Propósito
Projetar e orquestrar fluxos inteligentes de última geração no N8N utilizando os nós nativos de IA (LangChain / Advanced AI), integrando múltiplos provedores de LLMs (OpenAI, Groq LPU, DeepSeek), recuperação vetorial RAG, memória conversacional resiliente, arquiteturas multi-agentes e o protocolo MCP (*Model Context Protocol*).

---

## 1. Provedores de LLM & Ultra-Baixa Latência
- **OpenAI Node:** GPT-4o e GPT-4o-mini com function calling determinístico, structured output e Whisper para áudio.
- **Groq LPU:** Execução de modelos open-source (Llama 3.3, Mixtral) com velocidade ultra-rápida (>500 tokens/segundo) para tarefas em tempo real (triagem, parsing).
- **DeepSeek:** Raciocínio denso (DeepSeek-R1 / V3) com excelente relação custo-benefício para análises complexas e cadeias lógicas.
- **Estratégia de Fallback:** Configuração de cadeias de contingência (Groq $\to$ OpenAI $\to$ Claude) para tolerância a falhas e picos de demanda.

---

## 2. RAG (Retrieval-Augmented Generation) & Memória
- **Vector Stores Integrados:** Ingestão de documentos, chunking e indexação em Pinecone, Qdrant ou Supabase Vector (pgvector).
- **Embeddings:** Geração de vetores via OpenAI Embeddings (`text-embedding-3-small`) ou modelos abertos.
- **Memória Conversacional:** Implementação de memória persistente baseada em sessão (`Window Buffer Memory` ou persistência em PostgreSQL / Redis) para manter contexto sem estourar o limite de tokens.

---

## 3. Arquitetura Multi-Agentes & Ferramentas (Tools)
- **AI Agent Node com Ferramentas:** Criação de agentes autônomos equipados com sub-workflows atuando como Tools customizadas (pesquisa, consulta a CRM, disparo de e-mail).
- **Padrão Orquestrador Supervisor:** Agente coordenador que interpreta a intenção do usuário e roteia subtarefas para fluxos ou subagentes especializados, consolidando a resposta final.

---

## 4. Model Context Protocol (MCP) no N8N
- **N8N como Servidor MCP:** Expor workflows de automação corporativos como ferramentas universais consumíveis por agentes externos (Claude Desktop, Cursor, Antigravity).
- **N8N como Cliente MCP:** Consumir ferramentas e fontes de dados expostas por servidores MCP externos para enriquecer as capacidades de raciocínio dos agentes N8N.
