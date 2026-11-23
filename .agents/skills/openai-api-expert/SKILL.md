---
name: openai-api-expert
description: "Use quando a tarefa envolver: Integracao completa com OpenAI API — setup seguro de chaves, Chat Completions, streaming SSE, prompt engineering estruturado, chatbots com gestao de historico, function calling e otimizacao de custos/tokens."
---

# Habilidade: OpenAI API Expert 🤖⚡

## Propósito
Desenvolvimento profissional com a API da OpenAI em ambientes corporativos de alta escala, cobrindo autenticação segura via variáveis de ambiente, engenharia de prompts avançada, Structured Outputs (Pydantic), streaming em tempo real, chatbots com memória conversacional e gestão rigorosa de custos e rate limits.

---

## 1. Segurança & Autenticação
- **Proteção Absoluta de Credenciais:** Proibido expor `OPENAI_API_KEY` em código fonte. Utilize injeção via variáveis de ambiente (`os.environ["OPENAI_API_KEY"]` / `python-dotenv`).
- **Instanciação Segura:** Inicialização assíncrona recomendada via `AsyncOpenAI(api_key=...)`.

---

## 2. Engenharia de Prompts Estruturada
- **Arquitetura de Mensagens:**
  - `system`: Diretrizes comportamentais, identidade, formato de saída e regras invioláveis.
  - `user`: Pergunta ou dados pontuais da requisição (sanitizados contra Prompt Injection).
  - `assistant`: Histórico de respostas do modelo para continuidade de contexto.
- **Structured Outputs (Strict JSON):** Uso de `client.beta.chat.completions.parse` com esquemas tipados Pydantic (`strict=True`), eliminando alucinações de schema.
- **Técnicas de Inferência:** Few-shot prompting, Chain-of-Thought (CoT) para raciocínio complexo e delimitação rígida de blocos de contexto externo.

---

## 3. Chatbots de Alta Performance & Streaming
- **Streaming em Tempo Real (SSE):** Consumo assíncrono via `stream=True` com `async for chunk in response:` para latência percibida imediata (*Time to First Token* reduzido).
- **Gestão de Histórico & Context Window:**
  - Janela deslizante (*Sliding Window*): retenção das últimas $K$ interações.
  - Sumarização progressiva de turnos antigos para manter o prompt dentro do orçamento de tokens.
  - Deduplicação de sessões por ID de usuário (`conversation_id`).

---

## 4. Otimização de Custos (FinOps) & Rate Limiting
- **Seleção Inteligente de Modelos:** Roteamento de tarefas triviais (resumos, triagem) para modelos ultra-rápidos e econômicos (`gpt-4o-mini`) e tarefas complexas para raciocínio denso (`gpt-4o` / `o1` / `o3-mini`).
- **Resiliência a Rate Limits:** Implementação de retentativas com *Exponential Backoff* e *Jitter* (`tenacity` em Python).
- **Contagem e Caching de Tokens:** Pré-contagem com biblioteca `tiktoken` antes do envio e aproveitamento de *Prompt Caching* automático da OpenAI em blocos repetidos.
