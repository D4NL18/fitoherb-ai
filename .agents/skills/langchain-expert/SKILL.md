---
name: langchain-expert
description: "Use quando a tarefa envolver: Desenvolvimento de aplicações com LangChain — LCEL, Document Loaders, PromptTemplate, PydanticOutputParser, SequentialChain, Router Chain, Agents/Tools customizadas com Pydantic, streaming e integração multi-provedor (OpenAI, HuggingFaceEndpoint e Ollama local com Modelfile)."
---

# Habilidade: LangChain Expert (Chains, Loaders, Tools & Ollama Local) 🔗🤖

## Propósito
Projetar e implementar pipelines, integrações multi-provedor e agentes com **LangChain** de forma modular, tipada e segura — cobrindo desde carregamento de documentos heterogêneos, engenharia e composição de prompts, parsers estruturados com Pydantic e roteamento dinâmico com LCEL até execução de modelos locais com **Ollama** e criação de ferramentas customizadas (`@tool`).

---

## 1. Integração Multi-Provedor (OpenAI, Hugging Face e Ollama Local)

### 1.1 OpenAI com Streaming
```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)

for chunk in llm.stream("Explique o conceito de renda fixa de forma objetiva."):
    print(chunk.content, end="", flush=True)
```

### 1.2 Hugging Face (`HuggingFaceEndpoint` / Inference API)
Permite consumir modelos open-source (ex.: `mistralai/Mixtral-8x7B-Instruct-v0.1`) com `HUGGINGFACEHUB_API_TOKEN` via `.env`:
```python
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1")
prompt = PromptTemplate.from_template("{role}: {content}")
chain = prompt | llm
resposta = chain.invoke({"role": "user", "content": "Resuma o que é aprendizado por reforço."})
```

### 1.3 Modelos Locais com Ollama (Custo $0 e Privacidade Local)
Ideal para desenvolvimento offline, dados sensíveis (LGPD) e redução de custos FinOps (`llama3.1`, `phi3`, `mistral`, `gemma2`):
```python
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm_local = Ollama(
    model="llama3.1",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
)
resposta = llm_local.invoke("Explique o conceito de aprendizado por reforço.")
```

**API HTTP Local do Ollama (porta `11434`):**
```bash
curl --location 'http://localhost:11434/api/chat' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "phi3",
    "messages": [{ "role": "user", "content": "Explique renda fixa para iniciantes." }]
  }'
```

**Customizando um Modelo no Ollama com `Modelfile`:**
```dockerfile
# Inspecionar base: ollama show llama3.1 --modelfile
FROM llama3.1:latest
TEMPLATE """{{ if .System }}System: {{ .System }}{{ end }}
User: {{ .Prompt }}
Assistant:"""
SYSTEM """Você é um assistente especialista em domínio financeiro brasileiro. Responda de forma clara, objetiva e fundamentada."""
PARAMETER stop "User:"
PARAMETER stop "Assistant:"
PARAMETER stop "System:"
```
```bash
ollama create modelo-especialista --file custom.modelfile
ollama run modelo-especialista
```

---

## 2. Document Loaders (Ingestão Padronizada)

Os **Document Loaders** normalizam fontes heterogêneas em objetos `Document(page_content, metadata)`:

| Categoria | Exemplos de Loaders |
| :--- | :--- |
| **PDFs** | `PyPDFLoader`, `PyMuPDF`, `PDFPlumber`, `UnstructuredPDFLoader`, `PyPDFDirectory`, `AmazonTextract` |
| **Cloud / Storage** | `S3DirectoryLoader`, `S3FileLoader`, `GCSDirectoryLoader`, `AzureBlobStorageFileLoader`, `GoogleDriveLoader` |
| **Web / Conhecimento** | `WebBaseLoader`, `WikipediaLoader`, `YoutubeLoader`, `NewsURLLoader` |
| **Produtividade** | `NotionDirectoryLoader`, `SlackDirectoryLoader`, `GithubFileLoader`, `TrelloLoader`, `FigmaFileLoader` |
| **Dados & Arquivos** | `CSVLoader`, `JSONLoader`, `DirectoryLoader`, `TextLoader`, `UnstructuredMarkdownLoader`, `BSHTMLLoader` |
| **Bancos Relacionais** | `SQLDatabase` (SQLAlchemy) |

### Padrão de Ingestão + Splitting + FAISS (MMR)
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

docs = PyPDFLoader("documento.pdf").load()
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""],
)
chunks = splitter.split_documents(docs)

vectorstore = FAISS.from_documents(documents=chunks, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_type="mmr")  # Relevância + Diversidade
```

---

## 3. Prompts, Composição e Output Parsers Tipados

### 3.1 Estrutura de Prompt e Composição de Templates
Estruture prompts em 4 blocos: **Contexto (Persona)**, **Instrução**, **Input** e **Output (Formato esperado)**.
Templates podem ser compostos de forma modular com `+`:
```python
from langchain_core.prompts import PromptTemplate

limite = PromptTemplate.from_template("Responda em até {max_palavras} palavras.\n")
idioma = PromptTemplate.from_template("Idioma obrigatório: {idioma}.\n")
tarefa = PromptTemplate.from_template("Explique o conceito: {pergunta}")

template_composto = limite + idioma + tarefa
```

### 3.2 Saída Estruturada com Pydantic (`with_structured_output` e `PydanticOutputParser`)
Prefira `llm.with_structured_output(Schema)` em modelos que suportam structured outputs; use `PydanticOutputParser` para modelos legados/locais:
```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class Pessoa(BaseModel):
    nome: str = Field(..., description="Nome completo da pessoa")
    idade: int = Field(..., description="Idade em anos")
    profissao: str = Field(..., description="Profissão atual")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
structured_llm = llm.with_structured_output(Pessoa)
resultado: Pessoa = structured_llm.invoke("Maria tem 30 anos e trabalha como Engenheira.")
```

---

## 4. Chains e Roteamento Dinâmico (LCEL)

### 4.1 Quando usar LCEL vs `SequentialChain`
- **LCEL (`prompt | llm | parser`)**: padrão moderno, suporta streaming nativo, `ainvoke` assíncrono, batch e roteamento declarativo.
- **`SequentialChain` + `SimpleMemory`**: útil em bases legadas para encadear `LLMChain`s passando variáveis intermediárias e metadados fixos de contexto.

### 4.2 Router Chain com LCEL e `with_structured_output`
Roteia dinamicamente a consulta para o prompt especialista correto sem `if/else` frágil por string:
```python
from operator import itemgetter
from typing import Literal
from typing_extensions import TypedDict
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

chain_acoes = (
    ChatPromptTemplate.from_messages([
        ("system", "Você é um especialista em renda variável e ações."),
        ("human", "{query}"),
    ]) | llm | StrOutputParser()
)
chain_renda_fixa = (
    ChatPromptTemplate.from_messages([
        ("system", "Você é um especialista em renda fixa."),
        ("human", "{query}"),
    ]) | llm | StrOutputParser()
)

class RouteQuery(TypedDict):
    destination: Literal["acoes", "renda_fixa"]

route_prompt = ChatPromptTemplate.from_messages([
    ("system", "Roteie a pergunta do usuário para 'acoes' ou 'renda_fixa'."),
    ("human", "{query}"),
])
route_chain = route_prompt | llm.with_structured_output(RouteQuery) | itemgetter("destination")

router = {
    "destination": route_chain,
    "query": itemgetter("query"),
} | RunnableLambda(lambda x: chain_acoes if x["destination"] == "acoes" else chain_renda_fixa)
```

---

## 5. Agents e Tools Customizadas

### 5.1 Criando Tools Tipadas com `@tool` + Pydantic
- Sempre declare `args_schema` com `BaseModel` e descrições curtas e claras.
- Nunca exponha chaves de API como argumento preenchível pelo LLM — injete credenciais via variáveis de ambiente dentro da função da tool.
- Em consultas SQL (ex.: PostgreSQL via `psycopg2` / SQLAlchemy), **sempre use parâmetros vinculados** (`%s` / bind parameters) — nunca concatene strings do usuário.

```python
import os
import statistics
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class DadosAcaoArgs(BaseModel):
    simbolo: str = Field(description="Ticker da ação (ex: AAPL, MSFT)")

@tool(args_schema=DadosAcaoArgs)
def analisar_media_fechamento(simbolo: str) -> str:
    """Consulta a série diária na Alpha Vantage e retorna a média de fechamento."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "TIME_SERIES_DAILY", "symbol": simbolo, "apikey": api_key},
        timeout=15,
    )
    dados = resp.json().get("Time Series (Daily)")
    if not dados:
        return f"Não foi possível obter dados para {simbolo}."
    media = statistics.mean(float(d["4. close"]) for d in dados.values())
    return f"A média de fechamento de {simbolo} é {media:.2f}"
```

### 5.2 Ferramentas de Busca Web (Tavily) e Transição para LangGraph
- Para busca web em tempo real com agentes, utilize `TavilySearchResults` (`TAVILY_API_KEY`).
- Para fluxos com múltiplos ramos condicionais, ciclos, memória persistente por `thread_id` ou múltiplos agentes colaborando, **evolua a orquestração para `langgraph-expert`** em vez de empilhar `if/else` ou `AgentExecutor` monolítico.

---

## Quality Gates
- [ ] Credenciais (`OPENAI_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`, `TAVILY_API_KEY`) carregadas via variáveis de ambiente (nunca hardcoded ou passadas como argumento do LLM).
- [ ] Pipelines novos escritos preferencialmente com **LCEL** (`|`) e `with_structured_output` / Pydantic v2.
- [ ] Consultas a banco de dados dentro de tools protegidas com bind parameters (zero concatenação SQL).
- [ ] Timeouts explícitos em chamadas HTTP dentro de tools customizadas.
- [ ] Avaliação de uso de **Ollama local** quando houver requisito de custo zero ou restrição estrita de privacidade/LGPD.

---

## Exemplos e Referências Complementares (Carregar sob Demanda)
- `references/document-loaders-catalog.md` — Catálogo completo de Document Loaders (PDF, Cloud/Storage, Web, Produtividade, Mensagens, SQL) com snippets prontos.
- `examples/ollama_local_and_modelfile.md` — Consumo via API HTTP local (`:11434`), criação de `Modelfile` customizado e pipeline local de sentimento/resumo.
- `examples/lcel_router_and_tools.py` — Router Chain com LCEL + `with_structured_output`, `@tool` tipada com Pydantic, consulta SQL parametrizada em PostgreSQL e busca web com Tavily.
