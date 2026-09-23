# Contrato de API — E-mail de Contato (Mail)

> **Entidade / Recurso:** Envio de E-mails e Notificações  
> **Base Path:** `/email`  
> **Status:** Ativo / Produção

---

## 1. Endpoints

### `POST /email/send`
Dispara e-mail para a central de vendas da distribuidora a partir do formulário de contato público.

- **Autenticação:** Nenhuma (Acesso público)
- **Content-Type:** `application/json`

#### Request Body (`MailReq`)
```json
{
  "name": "João da Silva",
  "email": "joao.silva@farmacia.com.br",
  "phone": "(71) 99999-8888",
  "message": "Olá, tenho interesse em revender a linha de fitoterápicos em minha loja."
}
```

| Campo | Tipo | Obrigatório | Descrição / Validação |
|---|---|---|---|
| `name` | string | Sim | Nome completo (min 3, max 150 caracteres) |
| `email` | string | Sim | E-mail válido para resposta |
| `phone` | string | Sim | Telefone de contato comercial com DDD |
| `message` | string | Sim | Mensagem do lead (min 10, max 2000 caracteres) |

#### Respostas
- `200 OK`: `{"message": "Email sent successfully"}`
- `400 Bad Request`: `{"status": "BAD_REQUEST", "message": "Validation failed", "errors": {"email": "must be a well-formed email address"}}`
- `500 Internal Server Error`: `{"status": "INTERNAL_SERVER_ERROR", "message": "Failed to send email due to mail server error."}`
