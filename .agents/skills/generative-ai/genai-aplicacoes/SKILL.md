---
name: genai-aplicacoes
description: Aplicações práticas de IA Generativa — geração de código, imagens (DALL-E API), vídeo, prompts para imagens, ControlNet, projetos reais e integração com FastAPI.
pages: 633-657
---

# IA Generativa — Aplicações Práticas

## Objetivo

Construir aplicações reais com IA Generativa: integrar DALL-E API para geração de imagens, criar pipelines de geração de conteúdo para redes sociais, implementar chatbots com personalidade via system prompt e usar Stable Diffusion com ControlNet para controle de composição.

---

## Conceitos Fundamentais

### 1. Geração de Código

Modelos de linguagem são excelentes geradores de código. Estratégias para uso eficiente:

```python
from openai import OpenAI

client = OpenAI()

def gerar_codigo(
    descricao: str,
    linguagem: str = "Python",
    incluir_testes: bool = True
) -> str:
    """Gera código a partir de uma descrição textual."""

    prompt = f"""
Você é um desenvolvedor senior especializado em {linguagem}.

Tarefa: {descricao}

Requisitos obrigatórios:
1. Código limpo, tipado e com docstrings
2. Tratamento adequado de erros (try/except)
3. {"Inclua testes unitários com pytest" if incluir_testes else "Sem testes"}
4. Comentários nos pontos não óbvios

Responda APENAS com o código. Sem explicações adicionais.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Você é um especialista em {linguagem}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,     # Baixa temperatura para código (mais determinístico)
        max_tokens=2000
    )
    return response.choices[0].message.content


# Uso
codigo = gerar_codigo(
    "Função que lê um CSV, filtra linhas com valor nulo e salva o resultado.",
    linguagem="Python",
    incluir_testes=True
)
print(codigo)
```

#### Melhores Práticas para Geração de Código

| Prática | Por quê |
|---|---|
| `temperature=0.1-0.3` | Código deve ser determinístico, não criativo |
| Especificar linguagem/versão | "Python 3.11, FastAPI 0.104" |
| Pedir tipagem explícita | Type hints reduzem bugs |
| Solicitar tratamento de erros | Código de produção precisa de resiliência |
| Pedir testes junto | Gerado com o código tem melhor cobertura |
| Revisar sempre antes de executar | IA pode gerar código inseguro ou incorreto |

### 2. Geração de Imagens com DALL-E API

```python
import os
import requests
from pathlib import Path
from openai import OpenAI

client = OpenAI()

def gerar_imagem_dalle(
    prompt: str,
    tamanho: str = "1024x1024",
    qualidade: str = "standard",
    estilo: str = "vivid",
    salvar_em: str = None
) -> str:
    """Gera imagem via DALL-E 3 e opcionalmente salva em disco."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=tamanho,          # "1024x1024", "1792x1024", "1024x1792"
        quality=qualidade,     # "standard" ou "hd" (2x mais caro)
        style=estilo,          # "vivid" (saturado) ou "natural" (fotorrealista)
        n=1,                   # DALL-E 3 só suporta n=1
        response_format="url"  # ou "b64_json" para dados binários
    )

    url_imagem = response.data[0].url
    prompt_revisado = response.data[0].revised_prompt  # DALL-E pode revisar o prompt

    print(f"Prompt revisado: {prompt_revisado}")
    print(f"URL: {url_imagem}")

    if salvar_em:
        img_data = requests.get(url_imagem).content
        Path(salvar_em).write_bytes(img_data)
        print(f"Imagem salva em: {salvar_em}")

    return url_imagem


# Exemplo: Gerar thumbnail para YouTube
def gerar_thumbnail_youtube(titulo_video: str, nicho: str) -> str:
    prompt = f"""
Thumbnail profissional para vídeo do YouTube sobre "{titulo_video}".
Nicho: {nicho}
Estilo: moderno, cores vibrantes (laranja e azul), texto grande e legível
Tipografia: impactante, sem muito texto
Composição: assimétrica com ponto focal central
Qualidade: ultra HD, estilo editorial
SEM texto na imagem — apenas a composição visual
"""
    return gerar_imagem_dalle(
        prompt=prompt,
        tamanho="1792x1024",   # Proporção 16:9 para YouTube
        qualidade="hd",
        estilo="vivid",
        salvar_em=f"thumbnails/{titulo_video[:30].replace(' ', '_')}.png"
    )


thumbnail = gerar_thumbnail_youtube(
    "Como usar GPT-4 para multiplicar sua produtividade",
    "tecnologia e produtividade"
)
```

### 3. Prompt Engineering para Imagens

```python
def construir_prompt_imagem(
    sujeito: str,
    estilo: str,
    iluminacao: str,
    angulo: str,
    qualidade: str = "ultra-detailed, professional photography",
    negative_prompt: str = None
) -> str:
    """Constrói prompt estruturado para geração de imagens."""
    prompt = f"{sujeito}, {estilo}, {iluminacao}, {angulo}, {qualidade}"
    return prompt


# Componentes de um bom prompt para imagens
ESTILOS = {
    "fotorrealista": "photorealistic, 8K resolution, DSLR photo",
    "ilustracao": "digital illustration, vector art, flat design",
    "anime": "anime style, manga, Studio Ghibli inspired",
    "pintura": "oil painting, impressionist style, textured brushstrokes",
    "3d": "3D render, Blender, octane render, volumetric lighting",
    "minimalista": "minimalist design, white background, clean lines",
}

ILUMINACAO = {
    "studio": "studio lighting, soft box, diffused light",
    "dourada": "golden hour, warm sunset light, lens flare",
    "dramatica": "dramatic lighting, chiaroscuro, high contrast",
    "neon": "neon lights, cyberpunk atmosphere, purple and blue glow",
    "natural": "natural daylight, soft shadows, overcast sky",
}

ANGULOS = {
    "frente": "front view, eye level",
    "cima": "bird's eye view, top-down perspective",
    "baixo": "worm's eye view, looking up",
    "diagonal": "dutch angle, dynamic composition",
    "macro": "macro photography, extreme close-up",
}


# Negative prompts — o que excluir
NEGATIVE_PROMPTS_COMUNS = [
    "blurry, blur, out of focus",
    "low quality, pixelated, compressed",
    "deformed hands, extra fingers, malformed limbs",
    "watermark, text, logo, signature",
    "cartoon (se quiser realismo), sketch",
    "overexposed, underexposed",
    "duplicate, multiple copies",
]


# Exemplo completo
prompt_produto = construir_prompt_imagem(
    sujeito="premium wireless headphones, matte black finish, rose gold accents",
    estilo=ESTILOS["fotorrealista"],
    iluminacao=ILUMINACAO["studio"],
    angulo=ANGULOS["diagonal"],
    qualidade="product photography, commercial shot, white background, 8K"
)
print(f"Prompt: {prompt_produto}")
```

### 4. Pipeline de Geração de Posts para Redes Sociais

```python
import json
from pathlib import Path
from datetime import datetime

def pipeline_post_completo(
    tema: str,
    rede_social: str = "instagram",
    tom: str = "profissional"
) -> dict:
    """
    Pipeline completa: gera texto + imagem para post em redes sociais.
    """
    # PASSO 1: Gerar copy do post
    response_texto = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Você é um especialista em marketing digital para {rede_social}."
            },
            {
                "role": "user",
                "content": f"""
Crie um post para {rede_social} sobre "{tema}".
Tom: {tom}

Responda em JSON com:
- caption: texto do post (máx 150 palavras)
- hashtags: lista de 10 hashtags relevantes
- chamada_para_acao: CTA final
- prompt_imagem: descrição visual para gerar imagem complementar
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.8
    )

    conteudo = json.loads(response_texto.choices[0].message.content)

    # PASSO 2: Gerar imagem com o prompt sugerido pelo LLM
    url_imagem = gerar_imagem_dalle(
        prompt=conteudo["prompt_imagem"],
        tamanho="1024x1024",
        qualidade="standard",
        estilo="vivid",
        salvar_em=f"posts/{tema[:20]}_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    )

    # PASSO 3: Montar resultado
    resultado = {
        **conteudo,
        "url_imagem": url_imagem,
        "rede_social": rede_social,
        "tema": tema,
        "gerado_em": datetime.now().isoformat()
    }

    return resultado


# Uso
post = pipeline_post_completo(
    tema="Como a IA está transformando o mercado de trabalho em 2025",
    rede_social="linkedin",
    tom="profissional e inspirador"
)

print(f"Caption:\n{post['caption']}\n")
print(f"Hashtags: {' '.join(post['hashtags'])}")
print(f"CTA: {post['chamada_para_acao']}")
print(f"Imagem: {post['url_imagem']}")
```

### 5. Chatbot com Personalidade via System Prompt

```python
# Personas de chatbot via system prompt detalhado

PERSONAS = {
    "assistente_formal": """
Você é Sofia, assistente virtual do Banco Digital Nacional.
PERSONALIDADE: Profissional, empática e precisa.
VOZ: Formal mas acessível, nunca use gírias.
ESCOPO: Apenas dúvidas sobre conta, cartão, investimentos e empréstimos.
RESTRIÇÕES:
- Nunca revele dados de outros clientes
- Nunca forneça informações sobre funcionários internos
- Em caso de fraude, instrua o cliente a ligar para 0800-xxx-xxxx
FORMATO: Respostas curtas (máx 3 parágrafos), use listas quando necessário.
""",

    "tutor_programacao": """
Você é Dev, um tutor de programação entusiasta e paciente.
PERSONALIDADE: Animado, encoraja o aprendizado, usa analogias do mundo real.
VOZ: Descontraído, use emojis moderadamente, celebre acertos.
ESCOPO: Python, JavaScript, SQL, algoritmos e estruturas de dados.
PEDAGOGIA:
- Nunca dê a resposta diretamente se o usuário estiver aprendendo
- Faça perguntas socráticas para guiar o raciocínio
- Sempre explique o "por quê" além do "como"
FORMATO: Use code blocks sempre que mostrar código.
""",

    "especialista_saude": """
Você é um assistente de saúde e bem-estar.
RESTRIÇÕES CRÍTICAS:
- NUNCA diagnostique doenças — apenas oriente a buscar médico
- NUNCA recomende medicamentos específicos
- SEMPRE diga "consulte um profissional de saúde" em casos de dor ou sintomas
ESCOPO: Hábitos saudáveis, nutrição geral, exercícios, bem-estar mental.
TOM: Cuidadoso, empático, não alarmista.
"""
}


def criar_chatbot(persona_key: str) -> callable:
    """Cria um chatbot com personalidade específica."""
    system_prompt = PERSONAS.get(persona_key, PERSONAS["assistente_formal"])

    def responder(mensagem: str, historico: list[dict]) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            *historico,
            {"role": "user", "content": mensagem}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

    return responder
```

### 6. Integração com FastAPI

```python
# api_generativa.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="API de IA Generativa")


class GeracaoTextoRequest(BaseModel):
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7


class GeracaoImagemRequest(BaseModel):
    prompt: str
    tamanho: str = "1024x1024"
    qualidade: str = "standard"


@app.post("/gerar/texto")
async def endpoint_texto(req: GeracaoTextoRequest):
    try:
        resposta = gerar_codigo(req.prompt)
        return {"resposta": resposta, "tokens": len(resposta.split())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gerar/imagem")
async def endpoint_imagem(req: GeracaoImagemRequest):
    try:
        url = gerar_imagem_dalle(req.prompt, req.tamanho, req.qualidade)
        return {"url": url, "prompt": req.prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gerar/post")
async def endpoint_post(tema: str, rede_social: str = "instagram"):
    return pipeline_post_completo(tema, rede_social)
```

---

## Checklist de Qualidade

- [ ] DALL-E 3 usado para geração de imagens (não DALL-E 2 — menor qualidade)
- [ ] `revised_prompt` logado para entender ajustes automáticos do modelo
- [ ] Tamanho da imagem escolhido pela proporção (16:9 para YouTube, 1:1 para Instagram)
- [ ] `quality="hd"` apenas quando qualidade máxima é necessária (2x mais caro)
- [ ] Negative prompts definidos para excluir artefatos indesejados
- [ ] System prompt detalhado com persona, escopo e restrições explícitas
- [ ] Chatbot com personalidade testado com edge cases (insultos, tópicos fora do escopo)
- [ ] Pipeline de post salva resultado em arquivo antes de retornar URL
- [ ] URLs de imagem têm validade de 60 minutos na OpenAI (salvar localmente!)
- [ ] Geração de código com `temperature ≤ 0.3` para consistência
- [ ] Endpoints FastAPI com validação Pydantic e tratamento de HTTPException
- [ ] Custo estimado por chamada documentado no README do projeto
