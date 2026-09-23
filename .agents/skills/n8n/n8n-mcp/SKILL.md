---
name: n8n-mcp
description: Integração do Model Context Protocol (MCP) com N8N — atuando como Servidor MCP para expor workflows e como Cliente MCP para consumir ferramentas externas.
pages: 775-780
---

# N8N com Model Context Protocol (MCP) — Servidor e Cliente de Ferramentas

## Objetivo

Implementar a interoperabilidade entre o ecossistema N8N e o Model Context Protocol (MCP), padrão aberto criado pela Anthropic. Esta skill capacita o N8N a operar em duas vias:
1. Como Servidor MCP: Expondo workflows complexos de automação como ferramentas padronizadas para clientes de IA externos (Claude Desktop, Cursor IDE, Windsurf, Claude Code).
2. Como Cliente MCP: Permitindo que Agentes de IA orquestrados dentro do N8N consumam servidores MCP remotos e locais (PostgreSQL, Filesystem, GitHub, Git, Brave Search, etc.).

## Conceitos Fundamentais

O MCP é um protocolo de comunicação baseado em JSON-RPC 2.0 que padroniza a forma como modelos de linguagem interagem com fontes de contexto e ferramentas externas.

## Padrões e Boas Práticas

### 1. N8N Atuando como Servidor MCP

Quando o N8N atua como Servidor MCP, clientes externos (como Claude Desktop ou Cursor) podem enxergar workflows do N8N como ferramentas disponíveis.

```
[Claude Desktop / Cursor]
           │
           │ (POST / JSON-RPC 2.0 via SSE)
           ▼
[N8N Webhook Trigger: /mcp/tools]
           │
           ├─ method: "tools/list" ──> Retorna catálogo de ferramentas disponíveis
           │
           └─ method: "tools/call" ──> Executa nó correspondente e devolve resultado
```

### 2. N8N Atuando como Cliente MCP

Dentro do N8N, um nó AI Agent (LangChain) pode ser conectado a servidores MCP através de conectores HTTP ou nós Custom Tool, consumindo ferramentas de infraestrutura sem reimplementar conectores nativos.

## Exemplos de Uso

### Projeto 1: Servidor MCP no N8N para Gestão de Leads no CRM

Um workflow do N8N expõe um endpoint que implementa o protocolo JSON-RPC 2.0 básico para listar e executar ferramentas.

#### Estrutura do Workflow:
1. Webhook Trigger: HTTP Method POST, Path `/webhook/mcp`, Authentication Header Auth.
2. Switch Node: Roteia baseado em `{{ $json.body.method }}`.
   - Caso `tools/list`: Devolve os schemas JSON das ações disponíveis.
   - Caso `tools/call`: Roteia para o nó específico baseado em `{{ $json.body.params.name }}`.

#### Resposta ao método tools/list:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "criar_lead_crm",
        "description": "Cria um novo prospect no CRM com status inicial de qualificação.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "nome": { "type": "string", "description": "Nome completo do contato" },
            "email": { "type": "string", "description": "E-mail corporativo" },
            "telefone": { "type": "string", "description": "Telefone com DDD" }
          },
          "required": ["nome", "email"]
        }
      }
    ]
  }
}
```

### Projeto 2: Agente N8N consumindo Servidor MCP

Permite que o assistente de IA faça consultas em serviços externos através do conector MCP.
1. Configure o nó AI Agent com modelo de chat (gpt-4o ou llama-3.3).
2. Conecte a ferramenta HTTP Request Tool configurada para o endpoint do servidor MCP.
3. O agente analisa a pergunta em linguagem natural, gera a chamada de ferramenta e sintetiza a resposta.

## Governança e Segurança em MCP

- **Autenticação Obrigatória**: Nunca exponha webhooks MCP abertos para a internet pública. Exija tokens de cabeçalho (`Authorization: Bearer <token>`).
- **Validação de Tipos**: Use o nó Edit Fields ou nó Code para sanitizar strings e números recebidos nos parâmetros da ferramenta antes de invocar bancos de dados ou APIs externas.
- **Princípio do Menor Privilégio**: As ferramentas expostas pelo N8N devem permitir apenas ações idempotentes ou com limites claros de escopo operacional.
- **Transports**: Utilize `stdio` para integrações de processos em máquinas locais e `HTTP com SSE` para servidores N8N hospedados em nuvem/VPS.

---

## Checklist de Qualidade

| Item de Verificação | Critério | Status |
|---|---|---|
| **Formato JSON-RPC 2.0** | Respostas seguem o envelope padrão com campos `jsonrpc`, `id` e `result` | [ ] |
| **Segurança de Acesso** | Autenticação por Header Token configurada no Webhook do servidor MCP | [ ] |
| **Schema Inequívoco** | Cada ferramenta possui `description` detalhada e campos `required` explícitos | [ ] |
| **Tratamento de Exceções** | Respostas de erro retornam `isError: true` com mensagem compreensível para a IA | [ ] |
| **Sanitização de Inputs** | Validação contra injeção de parâmetros nos argumentos recebidos do cliente | [ ] |
| **Compatibilidade de Cliente** | Testado com sucesso em clientes padrão (Claude Desktop / Cursor) | [ ] |
