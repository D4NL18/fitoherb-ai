# Contrato de API: Fitoherb AI Assistente Virtual (Chatbot)

Serviço: `fitoherb-ai` (FastAPI)  
Porta: `8000` (Local) / `8080` (Cloud Run)  
Prefixo: `/api/v1/chat`  
Padrão de Resposta: Envelope REST padronizado (`data` e `meta`)

---

### 1. `POST /api/v1/chat/messages`
Processa a mensagem do usuário, gerencia histórico, aplica roteamento de intenção, busca produtos no catálogo indexado e retorna a resposta formatada juntamente com eventual ação de navegação automática.

#### Headers:
- `Content-Type: application/json`
- `X-Correlation-Id: <uuid>` (Opcional, gerado automaticamente se ausente)

#### Request Body (`ChatRequest`):
```json
{
  "message": "quais as opções de whey 100%?",
  "history": [
    {
      "role": "user",
      "content": "olá"
    },
    {
      "role": "assistant",
      "content": "Olá! Como posso ajudar você hoje?"
    }
  ]
}
```

**Regras de Validação do Payload:**
- `message`: String obrigatória, mín. 1 caracter, máx. 255 caracteres (`P-306`).
- `history`: Lista opcional de objetos de mensagem. Cada objeto contém `role` (`"user"` ou `"assistant"`) e `content` (máx. 500 caracteres).
- Histórico com mais de 5 itens é compactado automaticamente pelo servidor (`P-307`).

---

#### Resposta de Sucesso (`200 OK`):
```json
{
  "data": {
    "reply": "Encontrei opções de Whey 100% no catálogo. Estou direcionando você para a lista completa.",
    "intent": "PRODUCT_SEARCH",
    "action": {
      "type": "NAVIGATE_CATALOG",
      "auto_redirect": true,
      "filters": {
        "category": [],
        "supplier": [],
        "search": "whey 100%"
      }
    },
    "products": [
      {
        "name": "100% Pure Whey 900g",
        "slug": "100-pure-whey-900g",
        "image_url": "https://fitoherb.com.br/images/whey.png",
        "category": "Suplementação",
        "supplier": "Probiótica"
      }
    ],
    "suggestions": [
      "Onde fica a Fitoherb?",
      "Falar com o comercial"
    ]
  },
  "meta": {
    "cache": "MISS",
    "model": "gemini-2.5-flash",
    "tokens": {
      "prompt_tokens": 1120,
      "completion_tokens": 68
    },
    "latency_ms": 1150,
    "catalog_version": "v1.2",
    "degraded": false,
    "correlation_id": "a9b2c3d4-1234-5678-abcd-ef0123456789"
  }
}
```

#### Possíveis Ações (`action.type`):
- `NAVIGATE_CATALOG`: Comanda o front-end a navegar imediatamente para `/produtos` com os parâmetros fornecidos em `filters` (`auto_redirect: true`).
- `NONE`: Interação puramente conversacional ou informativa (ex: endereço, dúvidas institucionais), sem navegação.

---

### 2. `GET /api/v1/chat/health`
Verifica a disponibilidade do subsistema de chat, status de carregamento do índice do catálogo e conectividade da API Gemini.

#### Resposta (`200 OK`):
```json
{
  "data": {
    "status": "UP",
    "catalog_indexed_items": 1840,
    "catalog_last_refresh": "2026-10-15T13:30:00Z",
    "gemini_ready": true,
    "active_model": "gemini-2.5-flash"
  },
  "meta": {
    "service": "fitoherb-ai-chat"
  }
}
```

---

### 3. Códigos de Erro Padronizados

| Código HTTP | Motivo | Exemplo de Retorno |
| :--- | :--- | :--- |
| `400 BAD REQUEST` | Mensagem excede 255 caracteres ou payload malformado | `{"status": "BAD_REQUEST", "message": "Mensagem excede o limite máximo de 255 caracteres."}` |
| `429 TOO MANY REQUESTS` | Rate limit por IP excedido (> 20 req/min) | `{"status": "TOO_MANY_REQUESTS", "message": "Muitas requisições. Aguarde alguns instantes."}` |
| `503 SERVICE UNAVAILABLE` | Chat desativado por flag ou indisponibilidade total do catálogo | `{"status": "SERVICE_UNAVAILABLE", "message": "O assistente virtual está temporariamente indisponível."}` |
