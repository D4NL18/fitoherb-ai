---
name: openai-api-fundamentos
description: Fundamentos da OpenAI API — Playground, parâmetros de geração, modelos GPT, estrutura de mensagens e proteção de API Key com variáveis de ambiente.
pages: 323-330
---

# OpenAI API — Fundamentos

## Objetivo

Dominar os conceitos essenciais da OpenAI API: como acessar o Playground, entender e ajustar os parâmetros de geração, escolher o modelo correto para cada caso de uso, estruturar mensagens adequadamente e proteger credenciais com segurança.

---

## Conceitos Fundamentais

### 1. OpenAI Playground

O Playground é uma sandbox gratuita (usando créditos da conta) que permite testar prompts, ajustar parâmetros e experimentar modelos sem escrever código.

- Acesse em: [platform.openai.com/playground](https://platform.openai.com/playground)
- Modos disponíveis: **Chat**, **Assistants**, **Completions (legacy)**
- Exibe o custo estimado de tokens em tempo real

### 2. Gerenciamento de Créditos e Limites

| Tipo de Limite | Comportamento | Recomendação |
|---|---|---|
| **Hard Limit** | Trava a aplicação imediatamente ao atingir o valor | Definir alto o suficiente para não bloquear produção |
| **Soft Limit** | Envia notificação por e-mail quando atingido | Usar como alerta antecipado de gasto elevado |

Configure em: **Settings → Billing → Usage limits**

### 3. Parâmetros-Chave de Geração

| Parâmetro | Range | Descrição |
|---|---|---|
| `temperature` | 0.0 – 2.0 | Controla criatividade/aleatoriedade. 0 = determinístico, 2 = caótico |
| `max_tokens` | 1 – N | Número máximo de tokens na resposta gerada |
| `stop` | lista de strings | Sequências que interrompem a geração imediatamente |
| `top_p` | 0.0 – 1.0 | Nucleus sampling: considera apenas o top P% de probabilidade acumulada |
| `frequency_penalty` | -2.0 – 2.0 | Penaliza tokens proporcionalmente à frequência com que já apareceram |
| `presence_penalty` | -2.0 – 2.0 | Penaliza qualquer token que já apareceu ao menos uma vez |
| `n` | 1 – N | Número de respostas alternativas geradas simultaneamente |

> **Dica:** `temperature` e `top_p` não devem ser usados juntos — escolha apenas um deles para controle de aleatoriedade.

### 4. Modelos Disponíveis e Trade-offs

| Modelo | Custo | Qualidade | Contexto | Uso Ideal |
|---|---|---|---|---|
| `gpt-4o` | Alto | Máxima | 128k tokens | Tarefas complexas, raciocínio, código avançado |
| `gpt-4o-mini` | Baixo | Alta | 128k tokens | Equilíbrio custo-benefício para produção |
| `gpt-3.5-turbo` | Muito baixo | Boa | 16k tokens | Tarefas simples, alto volume, prototipagem |

### 5. Estrutura de Mensagens

A API usa uma lista de mensagens com três papéis:

```python
messages = [
    {
        "role": "system",
        "content": "Você é um assistente especializado em suporte técnico de TI."
    },
    {
        "role": "user",
        "content": "Meu computador não liga. O que devo fazer?"
    },
    {
        "role": "assistant",
        "content": "Vamos diagnosticar o problema passo a passo..."
    },
    {
        "role": "user",
        "content": "Já verifiquei o cabo de energia."
    }
]
```

| Role | Função |
|---|---|
| `system` | Define o comportamento, persona e restrições do modelo |
| `user` | Mensagem enviada pelo usuário final |
| `assistant` | Histórico de respostas anteriores do modelo (contexto) |

---

## Padrões e Boas Práticas

### Proteção da API Key

**NUNCA** coloque a API Key diretamente no código-fonte.

```bash
# .env (adicione ao .gitignore!)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
```

```python
# Carregando a key com python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

```gitignore
# .gitignore
.env
*.env
```

### Código Python Básico com OpenAI SDK

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_resposta(prompt: str, system_prompt: str = "Você é um assistente útil.") -> str:
    """Gera uma resposta usando a OpenAI API."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].message.content

# Uso
resposta = gerar_resposta("Explique o que é machine learning em 3 frases.")
print(resposta)
```

### Extraindo Metadados de Uso

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Olá!"}]
)

print(f"Tokens de entrada:  {response.usage.prompt_tokens}")
print(f"Tokens de saída:    {response.usage.completion_tokens}")
print(f"Total de tokens:    {response.usage.total_tokens}")
print(f"Modelo usado:       {response.model}")
```

---

## Exemplos de Uso

### Geração com Múltiplas Respostas (`n=3`)

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Sugira um nome para uma startup de IA."}],
    n=3,
    temperature=1.2  # Alta criatividade para diversidade de opções
)

for i, choice in enumerate(response.choices, 1):
    print(f"Opção {i}: {choice.message.content}")
```

### Usando Stop Sequences

```python
# O modelo para quando gerar "FIM"
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Liste 3 linguagens de programação:"}],
    stop=["FIM", "\n\n\n"]
)
```

### Configuração Conservadora (respostas precisas)

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Qual é a capital do Brasil?"}],
    temperature=0.0,    # Determinístico
    max_tokens=50,      # Resposta curta
    top_p=1.0
)
```

---

## Checklist de Qualidade

- [ ] API Key carregada via variável de ambiente (nunca hardcode)
- [ ] `.env` listado no `.gitignore`
- [ ] Modelo escolhido de acordo com a complexidade da tarefa
- [ ] `temperature` OU `top_p` configurado (nunca ambos simultaneamente)
- [ ] `max_tokens` definido para evitar respostas excessivamente longas
- [ ] `system` prompt define claramente o comportamento esperado
- [ ] Uso de tokens monitorado via `response.usage`
- [ ] Hard Limit e Soft Limit configurados na conta OpenAI
- [ ] Tratamento de exceções implementado (ex.: `openai.RateLimitError`)
- [ ] Versão do SDK fixada no `requirements.txt` (ex.: `openai==1.x.x`)
