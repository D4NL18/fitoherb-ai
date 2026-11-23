# Ollama Local, API HTTP e `Modelfile` Customizado com LangChain

Ideal para privacidade local (LGPD), prototipagem offline e FinOps (custo $0 de API) usando modelos como `llama3.1`, `phi3`, `mistral` e `gemma2`.

## 1. Consumo via API HTTP Local (Porta `11434`)

```python
import json
import requests

url = "http://localhost:11434/api/chat"
payload = {
    "model": "phi3",
    "messages": [{"role": "user", "content": "Explique o que é renda fixa para iniciantes."}],
}

response = requests.post(url, json=payload, timeout=60)
response.raise_for_status()

resposta_completa = ""
for line in response.text.splitlines():
    try:
        chunk = json.loads(line)
        if chunk.get("message", {}).get("role") == "assistant":
            resposta_completa += chunk["message"]["content"]
    except json.JSONDecodeError:
        continue

print(resposta_completa)
```

## 2. Criando um Modelo Especialista com `Modelfile`

Inspecione o `Modelfile` original do modelo base:
```bash
ollama show llama3.1 --modelfile
```

Crie `finance-assistant.modelfile`:
```dockerfile
FROM llama3.1:latest
TEMPLATE """{{ if .System }}System: {{ .System }}{{ end }}
User: {{ .Prompt }}
Assistant:"""
SYSTEM """Você é um assistente especialista em mercado financeiro brasileiro (renda fixa, renda variável e fundos). Responda de forma clara, técnica e objetiva em português."""
PARAMETER stop "User:"
PARAMETER stop "Assistant:"
PARAMETER stop "System:"
```

Compile e execute localmente:
```bash
ollama create finance-assistant --file finance-assistant.modelfile
ollama run finance-assistant
```

## 3. Pipeline Local com LangChain (Leitura de Arquivo + Sentimento + Resumo)

```python
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

llm = Ollama(model="mistral")  # Troque facilmente por "llama3.1" ou "finance-assistant"

chain_sentimento = PromptTemplate.from_template(
    "Classifique o sentimento (Positivo, Negativo ou Neutro) em português:\n{text}"
) | llm

chain_resumo = PromptTemplate.from_template(
    "Gere um resumo objetivo em 1 frase em português:\n{text}"
) | llm

caminho = "noticias.txt"
if not os.path.exists(caminho):
    raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

for doc in TextLoader(caminho, encoding="utf-8").load():
    texto = doc.page_content.strip()
    print("Sentimento:", chain_sentimento.invoke({"text": texto}))
    print("Resumo:", chain_resumo.invoke({"text": texto}))
```
