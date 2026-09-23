---
name: genai-fundamentos
description: Fundamentos de IA Generativa — diferença discriminativa vs generativa, modalidades principais, Foundation Models, zero-shot/few-shot/fine-tuning, espaço latente e tokens.
pages: 568-575
---

# IA Generativa — Fundamentos

## Objetivo

Compreender os conceitos fundamentais da IA Generativa: o que a diferencia da IA Discriminativa, as principais modalidades de conteúdo gerado, Foundation Models como base tecnológica, e o espectro de adaptação de modelos (zero-shot, few-shot e fine-tuning).

---

## Conceitos Fundamentais

### 1. O que é IA Generativa?

IA Generativa é a família de modelos de IA capazes de **criar novos conteúdos** (texto, imagem, áudio, vídeo, código) a partir de padrões aprendidos em grandes volumes de dados.

```
Entrada (Prompt) → [Modelo Generativo] → Novo Conteúdo Original
"Crie uma logo para startup" → DALL-E → [Imagem gerada]
"Escreva uma função Python" → GPT-4 → [Código gerado]
```

### 2. IA Discriminativa vs IA Generativa

| Aspecto | IA Discriminativa | IA Generativa |
|---|---|---|
| **Objetivo** | Classificar/predizer | Criar/gerar |
| **Pergunta** | "Isso é gato ou cachorro?" | "Como seria um gato azul?" |
| **Saída** | Label, probabilidade, valor | Texto, imagem, áudio, vídeo |
| **Exemplos** | SVM, CNN classificadora, BERT fine-tuned | GPT-4, DALL-E, Stable Diffusion, Sora |
| **Treinamento** | Aprende fronteiras de decisão | Aprende distribuição dos dados |
| **Dados** | Milhares de exemplos rotulados | Bilhões de dados não rotulados |

```
Discriminativo:
["gato", "cachorro"] → CNN → P(gato) = 0.92

Generativo:
"um gato astronauta na lua" → DALL-E → [imagem]
```

### 3. Principais Modalidades de IA Generativa

```
TEXTO
├── GPT-4 / GPT-4o (OpenAI)
├── Claude 3.5 Sonnet (Anthropic)
├── Gemini 1.5 Pro (Google)
└── Llama 3 (Meta, open-source)

IMAGEM
├── DALL-E 3 (OpenAI)
├── Stable Diffusion (Stability AI, open-source)
├── Midjourney
└── Adobe Firefly

VÍDEO
├── Sora (OpenAI)
├── Runway Gen-2
└── Pika Labs

ÁUDIO/VOZ
├── Whisper (transcrição, OpenAI)
├── ElevenLabs (síntese de voz)
└── MusicGen (Meta, geração musical)

CÓDIGO
├── GitHub Copilot (OpenAI Codex)
├── Claude (Anthropic)
└── Gemini Code Assist (Google)
```

### 4. Foundation Models

Foundation Models são modelos pré-treinados em escalas massivas de dados (bilhões de parâmetros, trilhões de tokens), que servem como **base** para múltiplas tarefas downstream via adaptação.

```
Dados da Internet (trilhões de tokens)
        ↓ Pré-treinamento (meses, milhões de $)
    [Foundation Model]
        ↓ Adaptação
┌───────────────────────────────┐
│ Fine-tuning → Modelo especializado
│ RAG → Contexto de documentos externos
│ Prompting → Sem modificação de pesos
└───────────────────────────────┘
```

**Exemplos de Foundation Models:**

| Modelo | Empresa | Parâmetros | Tipo |
|---|---|---|---|
| GPT-4 | OpenAI | ~1.8T (estimado) | Proprietário |
| Gemini Ultra | Google | Desconhecido | Proprietário |
| Llama 3 70B | Meta | 70B | Open-source |
| Mistral 7B | Mistral AI | 7B | Open-source |
| Claude 3 Opus | Anthropic | Desconhecido | Proprietário |

### 5. Zero-shot, Few-shot e Fine-tuning

O espectro de adaptação de um Foundation Model:

```
Menos dados ←————————————————————————→ Mais dados
Zero-shot → Few-shot → Fine-tuning
Menos custo                             Mais custo
```

```python
from openai import OpenAI
client = OpenAI()

# ZERO-SHOT: Sem exemplos, direto ao ponto
def zero_shot(tarefa: str, texto: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"{tarefa}:\n\n{texto}"}]
    )
    return response.choices[0].message.content


# FEW-SHOT: Com 2-5 exemplos para guiar o formato
def few_shot(texto: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""
Classifique o sentimento:

Exemplo 1:
Texto: "Ótimo produto, chegou rápido!"
Sentimento: POSITIVO

Exemplo 2:
Texto: "Horrível, não funciona!"
Sentimento: NEGATIVO

Agora classifique:
Texto: "{texto}"
Sentimento:"""
        }]
    )
    return response.choices[0].message.content
```

| Técnica | Dados necessários | Custo | Quando usar |
|---|---|---|---|
| **Zero-shot** | Nenhum | Mínimo | Tarefas gerais, LLMs capazes |
| **Few-shot** | 2-10 exemplos no prompt | Baixo | Formato específico, consistência |
| **Fine-tuning** | Centenas a milhares | Alto | Domínio específico, performance máxima |

### 6. Espaço Latente (Latent Space)

O espaço latente é a representação interna comprimida que o modelo aprende durante o treinamento.

```
Texto real → [Encoder] → Vetor no Espaço Latente → [Decoder] → Conteúdo gerado

Exemplo VAE:
"gato preto" → [Encoder] → [0.32, -0.15, 0.87, 0.44, ...] → [Decoder] → Imagem
"gato branco" → [Encoder] → [0.31, -0.14, 0.86, 0.12, ...] → [Decoder] → Imagem

# Interpolação no espaço latente:
latente_preto + 0.5 * (latente_branco - latente_preto) → "gato cinza"
```

### 7. Tokens — A Unidade Básica dos LLMs

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

texto = "Olá, como vai você?"
tokens = enc.encode(texto)
print(f"Texto: '{texto}'")
print(f"Tokens IDs: {tokens}")
print(f"Número de tokens: {len(tokens)}")

# Decodificar cada token
for token_id in tokens:
    print(f"  {token_id} → '{enc.decode([token_id])}'")
```

**Regras práticas de tokenização:**

| Regra | Exemplo |
|---|---|
| 1 palavra comum ≈ 1-2 tokens | "produto" → 1 token |
| 1 palavra longa ≈ 2-4 tokens | "extraordinário" → 3 tokens |
| 1 caractere especial ≈ 1 token | "!" → 1 token |
| 100 tokens ≈ 75 palavras | |
| 1 página A4 ≈ 400-500 tokens | |

---

## Padrões e Boas Práticas

### Escolha do Modelo por Caso de Uso

```python
def escolher_modelo_genai(
    modalidade: str,
    complexidade: str,
    privacidade: str,
    orcamento: str
) -> dict:
    """Guia de seleção de modelo generativo."""
    recomendacoes = {
        ("texto", "alta", "baixa", "alto"): {
            "modelo": "gpt-4o",
            "alternativa": "claude-3-5-sonnet",
            "justificativa": "Máxima qualidade para tarefas complexas"
        },
        ("texto", "media", "baixa", "medio"): {
            "modelo": "gpt-4o-mini",
            "alternativa": "gemini-1.5-flash",
            "justificativa": "Equilíbrio custo-benefício"
        },
        ("texto", "baixa", "alta", "baixo"): {
            "modelo": "llama-3-8b (local)",
            "alternativa": "mistral-7b (local)",
            "justificativa": "Open-source, dados privados, baixo custo"
        },
        ("imagem", "alta", "baixa", "alto"): {
            "modelo": "dall-e-3",
            "alternativa": "midjourney",
            "justificativa": "Melhor qualidade de imagem via API"
        },
    }
    chave = (modalidade, complexidade, privacidade, orcamento)
    return recomendacoes.get(chave, {"modelo": "gpt-4o-mini", "justificativa": "Default seguro"})
```

---

## Exemplos de Uso

### Geração de Texto com Streaming

```python
def gerar_texto_stream(prompt: str, max_tokens: int = 500) -> str:
    """Geração de texto com feedback visual token a token."""
    resposta = ""
    print("Gerando: ", end="", flush=True)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um redator criativo especializado."},
            {"role": "user", "content": prompt}
        ],
        stream=True,
        max_tokens=max_tokens,
        temperature=0.8
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            print(token, end="", flush=True)
            resposta += token

    print("\n")
    return resposta


resultado = gerar_texto_stream(
    "Escreva uma tagline impactante para um produto de IA que ajuda desenvolvedores."
)
```

---

## Checklist de Qualidade

- [ ] Modalidade correta escolhida para o problema (texto/imagem/áudio)
- [ ] Foundation Model selecionado por custo, qualidade e privacidade
- [ ] Zero-shot testado antes de investir em fine-tuning
- [ ] Tokens contados para estimar custo antes de enviar
- [ ] Temperature ajustada: baixa para precisão, alta para criatividade
- [ ] Dados sensíveis não enviados a APIs proprietárias (privacidade)
- [ ] Modelos open-source (Llama, Mistral) avaliados para casos com dados privados
- [ ] Streaming habilitado para melhor experiência do usuário
- [ ] Latent space entendido para interpolações em VAE/GAN quando necessário
- [ ] Diferença entre discriminativo e generativo documentada na ADR do projeto
