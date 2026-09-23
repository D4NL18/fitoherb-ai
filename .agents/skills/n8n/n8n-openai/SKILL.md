---
name: n8n-openai
description: Integração avançada com OpenAI no N8N — LLM Chains, Chatbots com memória, Agentes com Tools, GPT-4 Vision, Whisper API e gestão de tokens/erros.
pages: 705-718
---

# N8N com OpenAI — LLMs, Agentes e Multimodalidade

## Objetivo

Capacitar desenvolvedores e arquitetos de automação a integrar modelos de Inteligência Artificial da OpenAI dentro do N8N de forma robusta, segura e otimizada. Cobrindo desde simples cadeias de texto estruturado até agentes autônomos com chamada de ferramentas (*function calling*), chatbots com memória conversacional contínua, visão computacional com GPT-4 Vision e transcrição de áudio com a API Whisper.

---

## Conceitos Fundamentais

### 1. Configuração da Credencial OpenAI no N8N

Para utilizar qualquer nó do ecossistema OpenAI no N8N, a credencial deve ser configurada globalmente na instância:

1. Acesse **Credentials** → **Add Credential** → pesquise por **OpenAI**.
2. Insira a **API Key** gerada no [OpenAI Platform](https://platform.openai.com/api-keys).
3. Opcionalmente configure a **Organization ID** ou troque a **Base URL** (caso utilize proxies de governança, Azure OpenAI ou roteadores compatíveis).

```
[N8N Workflow] ---> [OpenAI Credential: API Key] ---> [api.openai.com/v1]
```

### 2. Família de Modelos e Seleção Estratégica

| Modelo | Casos de Uso Recomendados | Context Window | Custo Relativo | Latência Média |
|---|---|---|---|---|
| **gpt-4o** | Raciocínio complexo, geração de código, tarefas multimodais (imagem + texto) | 128k tokens | Médio-Alto | 1.0s - 2.5s |
| **gpt-4o-mini** | Tarefas rotineiras, classificação, extração de entidades, suporte em massa | 128k tokens | Muito Baixo | 400ms - 900ms |
| **o1 / o3-mini** | Resolução lógica pesada, matemática, planejamento multi-step sem ferramentas | 128k - 200k | Alto | 3.0s - 15.0s |
| **whisper-1** | Transcrição e tradução de arquivos de áudio (mp3, wav, ogg, m4a) | 25 MB/req | \$0.006/min | Variável |
| **text-embedding-3-small** | Embeddings para RAG e busca semântica em base vetorial | 8k tokens | Mínimo | 100ms - 300ms |

### 3. Parâmetros Críticos de Inferência

- **Temperature (0.0 a 2.0)**:
  - `0.0 a 0.2`: Tarefas determinísticas (extração de JSON, classificação, respostas a regras de negócio).
  - `0.7 a 1.0`: Geração de conteúdo, brainstorming, assistentes conversacionais dinâmicos.
- **Max Tokens**: Limite rígido para conter custos e evitar loops infinitos de geração.
- **Top P**: Amostragem por núcleo (usar 1.0 quando temperature estiver ajustada).
- **Frequency & Presence Penalty**: Evitar repetições de jargões em conversas longas.

### 4. Anatomia do Basic LLM Chain no N8N

No ecossistema LangChain dentro do N8N, uma **Basic LLM Chain** compõe-se de sub-nós acoplados:

```
[Trigger Node] 
      │
      ▼
┌──────────────────────────────────────┐
│       Basic LLM Chain Node           │
│                                      │
│  [Prompt Template]                   │
│  "Analise o texto: {{ $json.body }}" │
└───────┬───────────────────────┬──────┘
        │                       │
        ▼ (Model Connection)     ▼ (Output Parser)
┌───────────────┐       ┌────────────────────────┐
│ OpenAI Chat   │       │ Structured Output      │
│ Model (4o)    │       │ Parser (JSON Schema)   │
└───────────────┘       └────────────────────────┘
```

---

## Padrões e Boas Práticas

### 1. Data Pinning para Economia Extrema de Tokens

Durante o desenvolvimento de fluxos no N8N:
- **Nunca** reexecute nós de trigger ou chamadas a APIs pagas para testar nós de lógica subsequentes.
- Execute a chamada OpenAI **uma única vez**, clique no ícone de alfinete (**Pin Data**) na saída do nó.
- Os dados fixados serão reutilizados em todas as execuções de teste na tela de desenho, gerando **custo zero de tokens** durante a prototipação de scripts ou integrações com Slack/Sheets.

### 2. Tratamento Robusto de Falhas e Rate Limits (429)

```
[OpenAI Node]
   │
   ├─ (Success) ──> [Process Data]
   │
   └─ (On Error: Continue) ──> [IF Error Status == 429]
                                  ├─ True  ──> [Wait 5s] ──> [Retry Node]
                                  └─ False ──> [Error Trigger / Slack Alert]
```

- **Configurações do Nó OpenAI**:
  - `Retry On Fail`: Habilitado.
  - `Max Tries`: 3.
  - `Wait Between Tries`: 2000 ms com Exponential Backoff.
  - `Continue On Fail`: Usar quando houver fluxo alternativo de fallback.

### 3. Structured Outputs Determinísticos

Para integrações entre sistemas corporativos, force a saída estritamente em JSON válido utilizando o nó **Structured Output Parser** ou definindo `response_format: { type: "json_object" }` nas opções do nó.

---

## Exemplos de Uso e Projetos Práticos

### Projeto 1: Chatbot com Histórico de Memória (Window Buffer Memory)

Permite manter uma conversa fluida com o usuário, lembrando das últimas `N` interações sem inflar o contexto indefinidamente.

#### Arquitetura de Nós
```
[Webhook / Chat Trigger]
         │
         ▼
┌─────────────────────────────────────────┐
│              AI Agent Node              │
│       Prompt: "Você é o atendente..."   │
└────┬───────────────────────────────┬────┘
     │ (Model)                       │ (Memory)
     ▼                               ▼
┌───────────────┐           ┌────────────────────────┐
│ OpenAI Chat   │           │ Window Buffer Memory   │
│ Model         │           │ Context Window: 10     │
│ (gpt-4o-mini) │           │ Session Key:           │
└───────────────┘           │ {{ $json.session_id }} │
                            └────────────────────────┘
```

#### Expressão N8N para Session Key
```javascript
// Garante o isolamento entre múltiplos usuários simultâneos
{{ $json.headers['x-session-id'] || $json.body.from || 'default-session' }}
```

---

### Projeto 2: Agente de IA com Ferramentas (Tools Agent)

O agente decide autonomamente quando consultar serviços externos para responder à solicitação do usuário.

#### Ferramentas Conectadas ao Nó de Agente:
1. **Calculator Tool**: Efetua cálculos matemáticos precisos sem alucinações de LLM.
2. **SerpAPI / Google Search Tool**: Busca informações atualizadas na web em tempo real.
3. **HTTP Request Tool (Consultar CRM)**:
   - Endpoint: `https://api.empresa.com/v1/pedidos?codigo={codigo}`
   - Description no nó Tool: `"Útil para buscar o status atual de entrega e itens de um pedido pelo seu código alfanumérico."`
4. **Custom Code Tool (JavaScript)**: Converte moedas e aplica regras de tributação local.

#### Configuração do System Message no Agente:
```text
Você é o assistente oficial de pós-vendas da Empresa X.
Sempre que o usuário perguntar sobre o estado de um pedido, use a ferramenta 'consultar_pedido'.
Nunca invente status de faturamento ou prazos de entrega.
Ao retornar respostas, formate as datas no padrão brasileiro DD/MM/AAAA.
```

---

### Projeto 3: Análise de Imagens com GPT-4 Vision

Recebe recibos ou documentos fiscais via Webhook e extrai os campos contábeis estruturados.

#### Configuração do Nó OpenAI Chat Model
- **Model**: `gpt-4o`
- **Input Type**: `Images and Text`
- **Text Prompt**:
  ```text
  Extraia os seguintes campos desta nota fiscal em JSON:
  - cnpj_emissor
  - razao_social
  - data_emissao (YYYY-MM-DD)
  - valor_total (float)
  - itens (array de {descricao, quantidade, valor_unitario})
  ```
- **Image URL or Base64**:
  ```javascript
  // Quando recebido via upload binário no Webhook
  {{ $binary.data.data }}
  // Ou quando recebido como URL pública
  {{ $json.body.image_url }}
  ```

#### Payload JSON de Saída Esperado
```json
{
  "cnpj_emissor": "12.345.678/0001-90",
  "razao_social": "Papelaria Exemplo Ltda",
  "data_emissao": "2026-03-15",
  "valor_total": 142.50,
  "itens": [
    { "descricao": "Caderno Universitário", "quantidade": 2, "valor_unitario": 45.00 },
    { "descricao": "Caneta Esferográfica Azul", "quantidade": 10, "valor_unitario": 5.25 }
  ]
}
```

---

### Projeto 4: Transcrição e Análise de Áudio com Whisper API

Recebe notas de voz do Telegram ou WhatsApp e gera transcrição e resumo acionável.

```
[Telegram Trigger (Voice Note)]
             │
             ▼
[Download File Node (Telegram)]
             │
             ▼
[OpenAI Node: Audio Transcription (whisper-1)]
  - Binary Property: "data"
  - Language: "pt"
             │
             ▼
[OpenAI Node: Text Generation (gpt-4o-mini)]
  - Prompt: "Transcreva a solicitação e classifique a prioridade:
             {{ $('OpenAI Whisper').item.json.text }}"
             │
             ▼
[Create Task in ClickUp / Jira]
```

---

## Checklist de Qualidade

| Item de Verificação | Critério | Status |
|---|---|---|
| **Segurança de Chaves** | As chaves `sk-...` estão salvas em Credentials do N8N e nunca expostas no corpo do fluxo | [ ] |
| **Seleção de Modelo** | `gpt-4o-mini` é priorizado para rotinas simples; `gpt-4o` reservado para visão/raciocínio | [ ] |
| **Limites de Tokens** | Parâmetro `max_tokens` explicitamente configurado em todos os nós | [ ] |
| **Data Pinning** | Mocks pinados em nós de entrada durante desenvolvimento para evitar cobranças indevidas | [ ] |
| **Tolerância a Falhas** | Políticas de `Retry on Fail` ativadas para gerenciar instabilidades e HTTP 429 | [ ] |
| **Isolamento de Sessões** | Memória configurada com `session_key` única e imutável por canal/usuário | [ ] |
