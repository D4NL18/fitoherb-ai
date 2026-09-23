---
name: openai-api-chatbot
description: Construção de chatbots com OpenAI API — streaming, gerenciamento de histórico, sessões por usuário, interface web e estratégias de controle de contexto.
pages: 338-344
---

# OpenAI API — Chatbot

## Objetivo

Construir chatbots completos com a OpenAI API, dominando streaming de respostas, gerenciamento inteligente de histórico de mensagens, controle de sessões por usuário e integração com interfaces web usando FastAPI ou Flask.

---

## Conceitos Fundamentais

### 1. Streaming de Respostas

Streaming entrega a resposta token a token, como o ChatGPT faz, melhorando drasticamente a percepção de velocidade pelo usuário.

```python
from openai import OpenAI

client = OpenAI()

def responder_com_streaming(messages: list[dict]) -> str:
    """Gera resposta com streaming, imprimindo token a token."""
    resposta_completa = ""

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,           # ← Habilita streaming
        temperature=0.7
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            resposta_completa += delta.content

    print()  # Nova linha ao final
    return resposta_completa
```

### 2. Gerenciamento de Histórico de Mensagens

O histórico mantém o contexto da conversa, mas cada mensagem adiciona tokens ao custo.

```python
class GerenciadorHistorico:
    """Gerencia o histórico de mensagens com estratégias de controle de tamanho."""

    def __init__(self, system_prompt: str, max_mensagens: int = 20):
        self.system_prompt = system_prompt
        self.max_mensagens = max_mensagens
        self.historico: list[dict] = []

    def adicionar_usuario(self, conteudo: str):
        self.historico.append({"role": "user", "content": conteudo})
        self._limitar_historico()

    def adicionar_assistente(self, conteudo: str):
        self.historico.append({"role": "assistant", "content": conteudo})

    def _limitar_historico(self):
        """Mantém apenas as últimas N mensagens (Window Buffer)."""
        if len(self.historico) > self.max_mensagens:
            # Remove as mensagens mais antigas, preservando a primeira (contexto inicial)
            self.historico = self.historico[-self.max_mensagens:]

    def get_messages(self) -> list[dict]:
        """Retorna as mensagens completas incluindo o system prompt."""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self.historico

    def limpar(self):
        """Limpa todo o histórico da conversa."""
        self.historico = []

    def __len__(self) -> int:
        return len(self.historico)
```

### 3. Estratégias de Controle de Contexto

| Estratégia | Como funciona | Vantagem | Desvantagem |
|---|---|---|---|
| **Window Buffer** | Mantém as últimas N mensagens | Simples, previsível | Perde contexto antigo |
| **Resumo Automático** | Sumariza mensagens antigas | Preserva contexto essencial | Custo extra de sumarização |
| **Limpar Histórico** | Zera o histórico por comando | Controle explícito do usuário | Perde todo o contexto |
| **Histórico por Sessão** | Isola por `session_id` | Múltiplos usuários simultâneos | Precisa de armazenamento |

```python
def resumir_historico(historico_antigo: list[dict], client: OpenAI) -> str:
    """Sumariza mensagens antigas para economizar tokens."""
    if not historico_antigo:
        return ""

    historico_texto = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in historico_antigo
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Modelo barato para sumarização
        messages=[
            {
                "role": "user",
                "content": f"Resuma esta conversa em até 100 palavras, preservando os pontos principais:\n\n{historico_texto}"
            }
        ],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content
```

---

## Padrões e Boas Práticas

### API com FastAPI — Endpoint de Chat com Streaming

```python
# chatbot_api.py
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chatbot API")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Armazenamento de sessões em memória (use Redis em produção)
sessoes: dict[str, GerenciadorHistorico] = {}

SYSTEM_PROMPT = """Você é um assistente virtual da TechStore.
Ajude clientes com dúvidas sobre produtos, pedidos e suporte técnico.
Seja cordial, objetivo e profissional."""


class MensagemRequest(BaseModel):
    session_id: str | None = None
    mensagem: str


@app.post("/chat")
async def chat(request: MensagemRequest):
    """Endpoint de chat com streaming."""
    # Criar ou recuperar sessão
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessoes:
        sessoes[session_id] = GerenciadorHistorico(SYSTEM_PROMPT, max_mensagens=20)

    gerenciador = sessoes[session_id]
    gerenciador.adicionar_usuario(request.mensagem)

    def gerar_stream():
        resposta_completa = ""
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=gerenciador.get_messages(),
            stream=True,
            temperature=0.7
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                resposta_completa += delta.content
                yield delta.content

        gerenciador.adicionar_assistente(resposta_completa)

    return StreamingResponse(
        gerar_stream(),
        media_type="text/plain",
        headers={"X-Session-ID": session_id}
    )


@app.delete("/chat/{session_id}")
async def limpar_historico(session_id: str):
    """Limpa o histórico de uma sessão."""
    if session_id in sessoes:
        sessoes[session_id].limpar()
        return {"message": "Histórico limpo com sucesso."}
    raise HTTPException(status_code=404, detail="Sessão não encontrada")


@app.get("/chat/{session_id}/info")
async def info_sessao(session_id: str):
    """Retorna informações da sessão."""
    if session_id not in sessoes:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    gerenciador = sessoes[session_id]
    return {
        "session_id": session_id,
        "total_mensagens": len(gerenciador),
        "max_mensagens": gerenciador.max_mensagens
    }
```

### Frontend Simples com EventSource (SSE)

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Chatbot</title>
</head>
<body>
    <div id="chat-container">
        <div id="mensagens"></div>
        <input type="text" id="input" placeholder="Digite sua mensagem..." />
        <button onclick="enviar()">Enviar</button>
    </div>

    <script>
        let sessionId = null;

        async function enviar() {
            const input = document.getElementById('input');
            const mensagem = input.value.trim();
            if (!mensagem) return;

            adicionarMensagem('user', mensagem);
            input.value = '';

            const divAssistente = adicionarMensagem('assistant', '');

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: sessionId,
                    mensagem: mensagem
                })
            });

            sessionId = response.headers.get('X-Session-ID');
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const {done, value} = await reader.read();
                if (done) break;
                divAssistente.textContent += decoder.decode(value);
            }
        }

        function adicionarMensagem(role, conteudo) {
            const div = document.createElement('div');
            div.className = `mensagem ${role}`;
            div.textContent = conteudo;
            document.getElementById('mensagens').appendChild(div);
            return div;
        }

        document.getElementById('input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') enviar();
        });
    </script>
</body>
</html>
```

---

## Exemplos de Uso

### Chatbot de Terminal Interativo

```python
def chatbot_terminal():
    """Chatbot interativo no terminal com histórico."""
    gerenciador = GerenciadorHistorico(
        system_prompt="Você é um assistente de programação Python.",
        max_mensagens=30
    )

    print("Chatbot iniciado! Digite 'sair' para encerrar, 'limpar' para novo contexto.")
    print("-" * 50)

    while True:
        user_input = input("Você: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "sair":
            print("Encerrando chatbot. Até logo!")
            break
        if user_input.lower() == "limpar":
            gerenciador.limpar()
            print("Histórico limpo. Começando nova conversa.")
            continue

        gerenciador.adicionar_usuario(user_input)
        print(f"\nAssistente (histórico: {len(gerenciador)} msgs): ", end="")
        resposta = responder_com_streaming(gerenciador.get_messages())
        gerenciador.adicionar_assistente(resposta)
        print()
```

---

## Checklist de Qualidade

- [ ] `stream=True` habilitado para melhor UX em respostas longas
- [ ] `session_id` único por usuário para isolar históricos
- [ ] Window Buffer implementado para limitar tamanho do histórico
- [ ] Endpoint `/clear` ou comando "limpar" disponível ao usuário
- [ ] Sumarização automática implementada para históricos muito longos
- [ ] System prompt define claramente a persona e limitações do chatbot
- [ ] Tratamento de erro quando a API falha durante streaming
- [ ] Persistência de sessão em Redis ou banco de dados (não apenas memória) para produção
- [ ] Rate limiting por `session_id` para evitar abuso
- [ ] Timeout configurado para evitar streams travados
- [ ] Frontend exibe indicador de "digitando..." durante streaming
- [ ] Anti-padrão evitado: histórico ilimitado crescendo indefinidamente
