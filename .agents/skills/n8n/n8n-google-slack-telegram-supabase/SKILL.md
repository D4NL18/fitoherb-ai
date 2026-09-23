---
name: n8n-google-slack-telegram-supabase
description: "Integracoes do N8N com Google Sheets, Drive, Gmail, Slack, Telegram e Supabase — leitura/escrita de dados, bots, notificacoes e persistencia. Fluxo completo Telegram -> IA -> resposta + log."
pages: 729-757
---

# n8n-google-slack-telegram-supabase

## Objetivo

Conectar o N8N aos principais servicos de produtividade e comunicacao para construir automacoes completas — desde bots de Telegram com IA ate pipelines de dados com Supabase e Google Sheets.

---

## Conceitos Fundamentais

### Tabela de Servicos e Operacoes Principais

| Servico        | Operacoes Principais                                                        |
|----------------|-----------------------------------------------------------------------------|
| Google Sheets  | Read Rows, Append Row, Update Row, Delete Row, Trigger (Sheet Modified)     |
| Google Drive   | Upload File, Download File, List Files, Create Folder, Move File            |
| Gmail          | Send Email, Get Messages, Reply to Thread, Add Label, Download Attachment   |
| Slack          | Send Message, Post to Channel, Slash Command (Webhook), Create Channel      |
| Telegram       | Send Message, Send Photo, Send Document, Send Location, Telegram Trigger    |
| Supabase       | INSERT, SELECT, UPDATE, DELETE via REST API, Storage Upload/Download        |

### Configurar Credenciais OAuth2 para Google (Sheets, Drive, Gmail)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative as APIs: Sheets API, Drive API, Gmail API
3. Va em "Credentials" -> "Create Credentials" -> "OAuth 2.0 Client ID"
4. Tipo: Web Application
5. Authorized redirect URIs: `https://seu-n8n.com/rest/oauth2-credential/callback`
6. Copie Client ID e Client Secret
7. No N8N: Settings -> Credentials -> New -> Google OAuth2 API
8. Cole Client ID e Client Secret -> Connect -> autorize a conta Google

### Configurar Bot no Telegram com BotFather

1. Abra o Telegram e busque por `@BotFather`
2. Envie `/newbot`
3. Digite o nome do bot (ex: "Meu Assistente Bot")
4. Digite o username do bot (ex: `meu_assistente_bot` — deve terminar em `bot`)
5. O BotFather retorna o **Token de Acesso** (guarde com seguranca)
6. No N8N: Credentials -> New -> Telegram API -> cole o Token

### Configurar Supabase com Anon Key

1. Acesse [supabase.com](https://supabase.com) e crie um projeto
2. Va em Settings -> API
3. Copie a **Project URL** (ex: `https://xyzabc.supabase.co`)
4. Copie a **anon (public) key**
5. No N8N, use node **HTTP Request** com headers:
   - `apikey: SUA_ANON_KEY`
   - `Authorization: Bearer SUA_ANON_KEY`
   - `Content-Type: application/json`

---

## Padroes e Boas Praticas

### 1. Google Sheets — CRUD Completo

```
READ ROWS
  Node: Google Sheets
  Operation: Read Rows
  Spreadsheet ID: cole o ID da URL
  Sheet Name: Sheet1
  Filters: pode usar "Filters" para buscar linha especifica

APPEND ROW
  Operation: Append or Update Row
  Columns: mapeie campos do input para colunas

UPDATE ROW
  Operation: Update Row
  Row Number: numero da linha (use lookup primeiro)

DELETE ROW
  Operation: Delete Row
  Row Number: linha a deletar

TRIGGER AO EDITAR
  Node: Google Sheets Trigger
  Event: Row Added ou Row Updated
  Polling every: 1 minuto (minimo no N8N)
```

### 2. Google Drive — Gerenciamento de Arquivos

```
UPLOAD FILE
  Node: Google Drive
  Operation: Upload
  File: dados binarios do node anterior
  Parent Folder: ID da pasta de destino
  File Name: nome do arquivo

DOWNLOAD FILE
  Operation: Download
  File ID: ID do arquivo no Drive

LISTAR ARQUIVOS
  Operation: Search
  Query: "mimeType = 'application/pdf' and parents in 'FOLDER_ID'"
  Fields: id, name, createdTime, size

CRIAR PASTA
  Operation: Create
  Name: nome da pasta
  Folder ID: pasta pai (opcional)

MOVER ARQUIVO
  Operation: Move
  File ID: arquivo a mover
  Add Parents: ID da pasta destino
  Remove Parents: ID da pasta origem
```

### 3. Gmail — Leitura e Envio de Emails

```
ENVIAR EMAIL
  Node: Gmail
  Operation: Send
  To: destinatario@email.com
  Subject: Assunto do email
  Message: corpo em HTML ou texto
  Attachments: (opcional) arquivo binario

LER INBOX
  Operation: Get Many
  Filters -> Label: INBOX, UNREAD
  Limit: 10

RESPONDER THREAD
  Operation: Reply
  Thread ID: ID da conversa original
  Message: texto da resposta

PROCESSAR ANEXO
  Apos Gmail Get: use node "Extract from File" para PDFs
  ou salve no Drive com "Google Drive: Upload"
```

### 4. Slack — Mensagens e Bots

```
ENVIAR MENSAGEM PARA CANAL
  Node: Slack
  Operation: Message -> Send
  Channel: #nome-do-canal ou ID do canal
  Text: mensagem em texto simples ou Markdown Slack

SLASH COMMANDS VIA WEBHOOK
  1. Em Slack App -> Slash Commands -> Create New Command
  2. Request URL: URL do Webhook Trigger no N8N
  3. No N8N: Webhook Trigger -> processa o payload do Slack
  4. Responda com JSON: {"text": "Resposta para o usuario"}

BOT INTERATIVO (Block Kit)
  Text: use blocos JSON para botoes e menus
  Exemplo de bloco:
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "Escolha uma opcao:" },
      "accessory": {
        "type": "button",
        "text": { "type": "plain_text", "text": "Confirmar" },
        "action_id": "btn_confirmar"
      }
    }
```

### 5. Telegram Bot — Implementacao Completa

#### 5.1 Criar Bot com BotFather

```
1. @BotFather -> /newbot
2. Nome: "Assistente IA"
3. Username: "assistente_ia_bot"
4. Token: 123456:ABC-DEF... (guarde com seguranca)
5. Comandos: /setcommands -> lista de comandos
   start - Iniciar o bot
   ajuda - Ver ajuda
   status - Ver status
```

#### 5.2 Configurar Telegram Trigger no N8N (Webhook Mode)

```
Node: Telegram Trigger
Updates: message, callback_query
Webhook: modo automatico (N8N registra o webhook no Telegram)

Para desenvolvimento local com ngrok:
  1. Instale ngrok: https://ngrok.com/download
  2. Execute: ngrok http 5678
  3. Copie a URL HTTPS gerada (ex: https://abc123.ngrok.io)
  4. Configure N8N_WEBHOOK_URL=https://abc123.ngrok.io no .env
  5. Reinicie o N8N
```

#### 5.3 Comandos e Menus Inline

```
DETECTAR COMANDO /start
  Node: IF
  Condition: {{message.text}} starts with "/start"
  -> True: enviar mensagem de boas-vindas

DETECTAR COMANDO /ajuda
  Condition: {{message.text}} starts with "/ajuda"
  -> True: enviar menu de opcoes

MENU INLINE COM BOTOES
  Node: Telegram -> Send Message
  Additional Fields -> Reply Markup:
  {
    "inline_keyboard": [
      [
        {"text": "Opcao 1", "callback_data": "opcao_1"},
        {"text": "Opcao 2", "callback_data": "opcao_2"}
      ]
    ]
  }

CAPTURAR CALLBACK DE BOTAO
  Telegram Trigger -> Updates: callback_query
  Acessar: {{callback_query.data}} para saber qual botao clicou
  Responder: Telegram -> answerCallbackQuery
```

#### 5.4 Enviar Foto, Arquivo e Localizacao

```
ENVIAR FOTO
  Node: Telegram -> Send Photo
  Chat ID: {{message.chat.id}}
  Photo: URL publica ou arquivo binario

ENVIAR ARQUIVO/DOCUMENTO
  Node: Telegram -> Send Document
  Chat ID: {{message.chat.id}}
  Document: arquivo binario do node anterior

ENVIAR LOCALIZACAO
  Node: Telegram -> Send Location
  Chat ID: {{message.chat.id}}
  Latitude: -23.5505
  Longitude: -46.6333
```

### 6. Supabase via HTTP Request

#### 6.1 Configurar Headers Padrao

```
Headers obrigatorios para todas as requisicoes:
  apikey: SUA_ANON_KEY_AQUI
  Authorization: Bearer SUA_ANON_KEY_AQUI
  Content-Type: application/json
  Prefer: return=representation  (para INSERT/UPDATE retornarem o registro)
```

#### 6.2 Operacoes CRUD via REST

```
INSERT (POST)
  Method: POST
  URL: https://xyzabc.supabase.co/rest/v1/nome_tabela
  Body: {"campo1": "valor1", "campo2": "valor2"}

SELECT (GET)
  Method: GET
  URL: https://xyzabc.supabase.co/rest/v1/nome_tabela
  Query Params: select=*

SELECT COM FILTRO
  URL: https://xyzabc.supabase.co/rest/v1/usuarios
  Query Params:
    select: id,nome,email
    email: eq.usuario@email.com

UPDATE (PATCH)
  Method: PATCH
  URL: https://xyzabc.supabase.co/rest/v1/nome_tabela
  Query Params: id=eq.123
  Body: {"campo": "novo_valor"}

DELETE
  Method: DELETE
  URL: https://xyzabc.supabase.co/rest/v1/nome_tabela
  Query Params: id=eq.123
```

#### 6.3 Tabela de Memoria de Conversacao

```sql
-- Criar tabela conversations no Supabase
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indice para busca rapida por usuario
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

---

## Fluxo Completo: Telegram -> GPT-4o -> Resposta + Log Google Sheets

```
[Telegram Trigger]
  Evento: message
  Captura: {{message.text}} e {{message.chat.id}}
    |
[Basic LLM Chain]
  Modelo: OpenAI GPT-4o
  System Prompt: "Voce e um assistente pessoal amigavel."
  Human Message: {{message.text}}
    |
    |--- Ramo A ---> [Telegram: Send Message]
    |                  Chat ID: {{message.chat.id}}
    |                  Text: resposta do LLM
    |
    |--- Ramo B ---> [Google Sheets: Append Row]
                       Spreadsheet: Log de Conversas
                       Linha: [data, user_id, pergunta, resposta]
```

**Nodes necessarios:**
1. `Telegram Trigger` — recebe mensagem
2. `Basic LLM Chain` — conectado ao OpenAI Chat Model
3. `Merge` (modo: Multiplex) — junta as rotas de saida
4. `Telegram: Send Message` — responde ao usuario
5. `Google Sheets: Append Row` — loga a conversa

---

## Exemplos de Uso

### Exemplo 1 — Bot de Agendamento via Telegram + Google Sheets

```
Fluxo:
  Telegram Trigger -> detecta "/agendar DATA HORA"
  -> Parse da mensagem (Function node)
  -> Google Sheets: verificar disponibilidade
  -> IF disponivel:
       Google Sheets: Append Row (novo agendamento)
       Telegram: "Agendado para DATA as HORA!"
  -> IF indisponivel:
       Telegram: "Horario indisponivel. Tente outro."
```

### Exemplo 2 — Notificacao de Novo Lead: Gmail -> Slack

```
Fluxo:
  Gmail Trigger: novo email na label "Leads"
  -> Extract: nome, email, mensagem do corpo
  -> Slack: Send Message no canal #vendas
     "Novo lead: NOME (EMAIL) — MENSAGEM"
  -> Google Sheets: Append Row no CRM
```

### Exemplo 3 — Upload de Arquivo Telegram -> Google Drive + Supabase

```
Fluxo:
  Telegram Trigger: updates = document
  -> Telegram: getFile (obter URL do arquivo)
  -> HTTP Request: download do arquivo em binario
  -> Google Drive: Upload para pasta "Recebidos"
  -> Supabase HTTP: INSERT no registro de arquivos
     {user_id, nome_arquivo, drive_id, created_at}
  -> Telegram: Send Message "Arquivo salvo com sucesso!"
```

---

## Checklist de Qualidade

- [ ] Credenciais OAuth2 do Google configuradas e testadas
- [ ] Token do Telegram validado com @BotFather
- [ ] Supabase anon key e URL corretos
- [ ] Webhook do Telegram Trigger ativo (verde no N8N)
- [ ] Ngrok ativo para desenvolvimento local (se aplicavel)
- [ ] Tratamento de erro em cada node critico (node Error Trigger)
- [ ] Chat ID dinamico (nunca fixo em producao)
- [ ] Logs de conversas sendo salvos corretamente
- [ ] Testes com mensagens reais antes de ir para producao
- [ ] Variavel de ambiente para tokens sensiveis (N8N_ENV)
- [ ] Rate limits do Telegram respeitados (30 msg/seg por bot)
- [ ] Respostas do bot em menos de 3 segundos
