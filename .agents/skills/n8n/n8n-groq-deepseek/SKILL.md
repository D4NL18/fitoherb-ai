---
name: n8n-groq-deepseek
description: Execução de IA de ultra-baixa latência com Groq LPU e raciocínio de alto custo-benefício com DeepSeek no N8N, incluindo fallbacks resilientes e processamento em batch.
pages: 719-728
---

# N8N com Groq & DeepSeek — Ultra-Velocidade e Raciocínio de Baixo Custo

## Objetivo

Implementar esteiras de processamento de linguagem natural no N8N tirando proveito da ultra-baixa latência das LPUs (Language Processing Units) da **Groq** e da alta capacidade analítica de baixo custo do **DeepSeek** (V3 e R1). O foco é desenhar arquiteturas tolerantes a falhas (*resilient fallback patterns*), processamento em lote (*batch processing*) com alto throughput e otimização drástica de custos operacionais (FinOps).

---

## Conceitos Fundamentais

### 1. Groq: Inferência em LPUs (Language Processing Units)

Diferente de GPUs tradicionais projetadas para processamento gráfico em paralelo com memória HBM, as **LPUs da Groq** são circuitos integrados de aplicação específica (ASIC) otimizados para fluxo sequencial e acesso instantâneo à memória SRAM on-chip:
- **Throughput Extremo**: 300 a 800+ tokens por segundo.
- **Time-to-First-Token (TTFT)**: < 150ms.
- **Modelos Homologados**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma2-9b-it`.

#### Configuração da Credencial Groq no N8N
1. Obtenha a chave em [console.groq.com/keys](https://console.groq.com/keys).
2. No N8N, adicione uma credencial do tipo **Groq API** ou utilize o nó **OpenAI Chat Model** apontando a Base URL para `https://api.groq.com/openai/v1`.
3. Conecte o sub-nó **Groq Chat Model** diretamente ao nó **Basic LLM Chain** ou **AI Agent**.

### 2. DeepSeek: Raciocínio Profundo a Custo Disruptivo

A família DeepSeek revolucionou o mercado com sua arquitetura MoE (Mixture of Experts) e aprendizado por reforço puro:
- **DeepSeek-V3**: Modelo geral de 671B parâmetros (37B ativos por token), equivalente ou superior ao GPT-4o em tarefas gerais a uma fração do preço.
- **DeepSeek-R1**: Modelo de raciocínio lógico profundo que expõe tags `<think>` (*chain of thought*), ideal para análise forense, matemática, validação de regras complexas e auditoria de código.

#### Configuração do DeepSeek no N8N
Como a API da DeepSeek é 100% compatível com a especificação da OpenAI:
1. Obtenha a chave em [platform.deepseek.com](https://platform.deepseek.com).
2. No N8N, crie uma credencial **OpenAI API**:
   - **API Key**: `sk-deepseek-...`
   - **Base URL**: `https://api.deepseek.com`
3. No nó OpenAI Chat Model, informe manualmente o nome do modelo: `deepseek-chat` (V3) ou `deepseek-reasoner` (R1).

---

## Padrões e Boas Práticas

### 1. Tabela Comparativa de Performance e Custos

| Critério | Groq (LLaMA 3.3 70B) | OpenAI (GPT-4o) | DeepSeek (DeepSeek-V3 / R1) |
|---|---|---|---|
| **Velocidade (Tokens/s)** | **400 - 800 tps** (Ultra-rápido) | 70 - 110 tps (Médio) | 40 - 80 tps (Moderado) |
| **Latência TTFT** | **< 150ms** | 600ms - 1.2s | 800ms - 2.0s |
| **Custo Entrada (1M tokens)** | ~ \$0.59 | \$2.50 | **\$0.14** (Cache hit: \$0.014) |
| **Custo Saída (1M tokens)** | ~ \$0.79 | \$10.00 | **\$0.28** (R1: \$2.19) |
| **Capacidade de Raciocínio** | Alta (Open Source SOTA) | Muito Alta | **Excepcional (R1 supera o1)** |
| **Limites de Taxa (RPM/TPM)** | Restritivo no tier gratuito | Elevado | Sujeito a fila em picos globais |
| **Melhor Aplicação** | UX síncrona, Chat ao vivo, Slacks | Multimodalidade nativa, Tools | Análise pesada, Batch, Code Review |

---

### 2. Estratégia de Fallback Resiliente (Groq → DeepSeek → OpenAI)

Devido aos limites de taxa agressivos da Groq (Rate Limit 429) e ocasionais instabilidades de servidores da DeepSeek, desenhe uma topologia com redundância tripla automática:

```
                  ┌───────────────────────────────────────────┐
                  │ 1. Tentativa Primária: Groq (Ultra-Speed) │
                  └─────────────────────┬─────────────────────┘
                                        │
                         (Status == 200)│(Erro 429 / Timeout / 5xx)
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
               [Processar Resposta]          [Nó IF / Switch Error]
                                                        │
                                                        ▼
                                        ┌───────────────────────────────┐
                                        │ 2. Secundário: DeepSeek (Fin) │
                                        └───────────────┬───────────────┘
                                                        │
                                         (Sucesso) ┌────┴────┐ (Falha)
                                                   ▼         ▼
                                         [Processar]  ┌─────────────────────────┐
                                                      │ 3. Terciário: GPT-4o    │
                                                      └─────────────────────────┘
```

---

## Exemplos de Uso

### Projeto: Pipeline de Análise de Sentimentos em Batch

Analisa centenas de avaliações de clientes vindas de uma planilha ou banco de dados com altíssimo throughput e custo ínfimo.

#### Fluxo Completo de Nós
```
[Google Sheets / DB Trigger (1000 reviews)]
                   │
                   ▼
[Split In Batches (Batch Size: 20)]
                   │
                   ▼
[Groq Chat Model + Basic LLM Chain]
  - Model: llama-3.3-70b-versatile
  - Output: JSON com sentiment e score
                   │
                   ▼
[IF Condition: Score < 40 (Crítico)]
     ├─ True  ──> [Slack Alert: Cliente em Risco!]
     └─ False ──> [Supabase / DB Update: Status Processado]
                   │
                   ▼
[Loop Back to Split In Batches]
```

#### Prompt do Sistema Estruturado para Groq
```text
Você é um classificador de sentimento de alta precisão para e-commerce.
Analise a avaliação fornecida e responda ESTRITAMENTE em formato JSON com o seguinte schema:
{
  "sentiment": "POSITIVO" | "NEGATIVO" | "NEUTRO",
  "score": <número inteiro de 0 a 100>,
  "topics": [<tags de assuntos mencionados, ex: 'entrega', 'preço', 'qualidade'>],
  "urgency": "BAIXA" | "MEDIA" | "ALTA"
}
Não inclua introduções, explicações ou blocos markdown de código além do JSON puro.
```

#### Expressão N8N no Nó de Condição IF
```javascript
// Identifica avaliações com sentimento negativo agudo
{{ JSON.parse($json.response.text).sentiment === 'NEGATIVO' && JSON.parse($json.response.text).score <= 35 }}
```

---

### Exemplo 2: Tratamento de Raciocínio Chain of Thought com DeepSeek-R1

Quando o modelo `deepseek-reasoner` é invocado, ele inclui a chave `<think>...</think>` que pode ser extraída via nó **Code (JavaScript)** no N8N:

```javascript
// Nó Code após invocação do DeepSeek-R1
const rawText = $input.first().json.text || '';

const thinkMatch = rawText.match(/<think>([\s\S]*?)<\/think>/);
const reasoningChain = thinkMatch ? thinkMatch[1].trim() : '';
const finalAnswer = rawText.replace(/<think>[\s\S]*?<\/think>/, '').trim();

return [{
  json: {
    finalAnswer: finalAnswer,
    reasoningLog: reasoningChain,
    hasChainOfThought: Boolean(reasoningChain)
  }
}];
```

---

## Checklist de Qualidade

| Item de Verificação | Critério | Status |
|---|---|---|
| **Base URL Personalizada** | DeepSeek configurado com endpoint `https://api.deepseek.com` | [ ] |
| **Estratégia de Fallback** | Fluxo possui tratamento de erro chaveando entre Groq e DeepSeek/OpenAI | [ ] |
| **Controle de Lote** | Split In Batches dimensionado adequadamente para não estourar TPM do Groq | [ ] |
| **Sanitização de Saída** | Expressões de JSON.parse protegidas com fallback ou Structured Output Parser | [ ] |
| **FinOps Audit** | Custo por milhão de tokens validado e alinhado com a meta orçamentária do projeto | [ ] |
| **Limpeza de Chain-of-Thought** | Tags `<think>` isoladas ou expurgadas antes de responder ao usuário final | [ ] |
