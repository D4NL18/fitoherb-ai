# Catálogo de Document Loaders no LangChain

Todos os Document Loaders normalizam fontes heterogêneas em `List[Document]`, onde cada objeto expõe `page_content` e `metadata`.

## 1. Mapa de Loaders por Categoria

| Categoria | Loaders Principais | Observações |
| :--- | :--- | :--- |
| **PDFs** | `PyPDFLoader`, `PyMuPDFLoader`, `PDFPlumberLoader`, `UnstructuredPDFLoader`, `PyPDFDirectoryLoader`, `AmazonTextractPDFLoader` | Prefira `PyPDFLoader` / `PyMuPDFLoader` para PDFs com texto selecionável (evita OCR caro). |
| **Cloud / Storage** | `S3FileLoader`, `S3DirectoryLoader`, `GCSDirectoryLoader`, `AzureBlobStorageFileLoader`, `GoogleDriveLoader`, `DropboxLoader` | Requerem credenciais IAM/Service Account via variáveis de ambiente. |
| **Web & Conhecimento** | `WebBaseLoader`, `NewsURLLoader`, `WikipediaLoader`, `YoutubeLoader` | Sempre respeite termos de uso e rate limits. |
| **Produtividade** | `NotionDirectoryLoader`, `SlackDirectoryLoader`, `GithubFileLoader`, `TrelloLoader`, `FigmaFileLoader` | Úteis para bases internas de conhecimento corporativo (RAG interno). |
| **Mensagens** | `TelegramChatFileLoader`, `WhatsAppChatLoader`, `DiscordChatLoader` | **Atenção LGPD:** aplique sanitização de PII antes de indexar conversas. |
| **Arquivos & Bancos** | `CSVLoader`, `JSONLoader`, `TextLoader`, `DirectoryLoader`, `UnstructuredMarkdownLoader`, `BSHTMLLoader`, `SQLDatabase` | `SQLDatabase` integra via SQLAlchemy (use usuário read-only para agentes). |

---

## 2. Snippets Prontos

### PDF + `RecursiveCharacterTextSplitter` + FAISS (`mmr`)
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = PyPDFLoader("manual.pdf").load()
chunks = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""],
).split_documents(docs)

vs = FAISS.from_documents(chunks, OpenAIEmbeddings())
retriever = vs.as_retriever(search_type="mmr")
```

### CSV, Web, Wikipedia, YouTube e Notion
```python
from langchain_community.document_loaders import (
    CSVLoader,
    NotionDirectoryLoader,
    WebBaseLoader,
    WikipediaLoader,
    YoutubeLoader,
)

csv_docs = CSVLoader("dados.csv", encoding="utf-8").load()
web_docs = WebBaseLoader(web_path="https://en.wikipedia.org/wiki/Artificial_intelligence").load()
wiki_docs = WikipediaLoader(query="Inteligência Artificial", load_max_docs=2).load()
yt_docs = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=VIDEO_ID", add_video_info=False).load()
notion_docs = NotionDirectoryLoader("caminho_export_notion").load()
```

### SQLDatabase (Read-Only recomendado)
```python
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

engine = create_engine("sqlite:///exemplo.db")
db = SQLDatabase(engine)
print(db.get_usable_table_names())
```
