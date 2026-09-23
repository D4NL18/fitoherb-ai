---
name: n8n-fundamentos
description: Fundamentos do N8N — nós, workflows, execuções, triggers, webhooks, expressões e boas práticas de automação. Base obrigatória antes de qualquer skill N8N especializada.
pages: 663-682
---

# N8N Fundamentos — Automação de Workflows com IA

## Objetivo

Dominar os conceitos centrais do N8N para construir, depurar e manter workflows de automação robustos, compreendendo o modelo de execução, os tipos de nós, o sistema de expressões e as práticas que garantem escalabilidade e clareza nos fluxos.

---

## Conceitos Fundamentais

### O que é o N8N?

N8N é uma plataforma de automação de workflows **self-hostable** e **open-source** que permite conectar centenas de serviços e APIs sem escrever código boilerplate. É a alternativa ao Zapier/Make com suporte nativo a IA (LangChain, OpenAI, Groq etc.).

### Anatomia de um Workflow

```
[Trigger Node] → [Action Node 1] → [Logic Node] → [Action Node 2]
```

| Componente      | Descrição                                                              |
|----------------|------------------------------------------------------------------------|
| **Workflow**    | Conjunto de nós conectados que realiza uma automação                   |
| **Node (Nó)**   | Unidade atômica de trabalho — cada nó faz uma coisa específica         |
| **Execution**   | Instância de execução de um workflow (manual ou automática)             |
| **Trigger**     | Nó inicial que dispara o workflow (evento, cron, webhook, etc.)         |
| **Connection**  | Seta que liga a saída de um nó à entrada do próximo                    |
| **Item**        | Unidade de dados que flui entre os nós (objeto JSON)                   |

---

### Tipos de Nós

#### 1. Trigger Nodes (Disparadores)
Iniciam o workflow com base em um evento externo ou agendamento.

```
Webhook Trigger       → recebe POST/GET externo
Cron / Schedule       → executa em horários definidos
Email Trigger         → ao receber um e-mail
Google Sheets Trigger → ao adicionar/editar linha
Telegram Trigger      → ao receber mensagem no bot
```

#### 2. Action Nodes (Ações)
Executam operações em serviços externos.

```
HTTP Request        → chamadas REST genéricas
OpenAI              → chat, imagem, áudio
Google Sheets       → CRUD em planilhas
Send Email (Gmail)  → envio de e-mails
Supabase            → operações no banco via REST
```

#### 3. Logic Nodes (Lógica de Fluxo)

| Nó          | Função                                                          |
|-------------|-----------------------------------------------------------------|
| **IF**      | Bifurca o fluxo com base em uma condição booleana               |
| **Switch**  | Roteia para múltiplos caminhos com base em valor de campo        |
| **Merge**   | Une dados de múltiplas branches em um único fluxo               |
| **Loop**    | Itera sobre uma lista de itens executando sub-fluxo             |
| **Wait**    | Pausa o workflow por tempo definido ou até webhook de resposta   |
| **Filter**  | Remove itens que não atendem a critérios                        |

#### 4. Data Transform Nodes (Transformação de Dados)

| Nó                | Função                                              |
|-------------------|-----------------------------------------------------|
| **Set**           | Define/sobrescreve campos no item JSON              |
| **Edit Fields**   | Renomeia, remove ou adiciona campos                 |
| **Code**          | JavaScript customizado para transformação livre     |
| **Aggregate**     | Agrupa múltiplos itens em um único objeto           |
| **Split Out**     | Divide array em itens individuais                   |

---

## Padrões e Boas Práticas

### Pinning de Dados (Data Pinning)

O **pin** permite fixar a saída de um nó em modo teste, evitando chamadas reais à API durante o desenvolvimento.

**Por que usar:**
- Economiza tokens de LLM em testes repetitivos
- Evita disparos acidentais em serviços externos (e-mail, Slack)
- Acelera o ciclo de iteração

**Como usar:**
1. Execute o nó manualmente uma vez para obter dados reais
2. Clique no nó → botão Pin (ícone de alfinete)
3. O nó passa a usar os dados fixados em execuções seguintes de teste

> Dados pinados NÃO são usados em produção, apenas no Editor.

### Sistema de Expressões N8N

Expressões permitem referenciar dados dinamicamente dentro de campos de configuração de nós.

```javascript
// Acessar campo do item atual
{{ $json.nome }}
{{ $json.email }}

// Acessar campo de um nó específico pelo nome
{{ $node['BuscaCliente'].json.id }}
{{ $node['Webhook'].json.body.mensagem }}

// Acessar todos os itens de um nó
{{ $items('NomeNo') }}

// Funções embutidas
{{ $json.nome.toUpperCase() }}
{{ $json.valor.toFixed(2) }}
{{ $now.toISO() }}
{{ $now.minus({days: 7}).toISO() }}

// Variáveis de ambiente
{{ $env.MINHA_VARIAVEL }}
```

### Variáveis de Ambiente e Credenciais

```bash
# .env / variáveis do container
N8N_HOST=meu-dominio.com
N8N_PORT=5678
N8N_PROTOCOL=https
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost

# Nunca hardcodar API keys nos nós!
# Use sempre o sistema de Credentials do N8N
```

**Configurar Credencial:**
1. Menu lateral → Credentials → Add Credential
2. Selecionar o serviço (OpenAI, Google, etc.)
3. Inserir chaves → Test → Save
4. Referenciar nos nós pelo nome da credencial

### Modo de Execução: Manual vs. Produção

| Aspecto              | Manual (Editor)              | Produção (Ativo)                    |
|----------------------|------------------------------|-------------------------------------|
| Disparado por        | Botão "Execute"              | Evento real (webhook, cron, etc.)   |
| Dados pinados        | Usados                       | Ignorados                           |
| Logs visíveis        | Em tempo real no Editor      | Em Executions do menu lateral       |
| Erros                | Param o workflow              | Registrados, workflow pode continuar|

### Debug de Nós

```
1. Clique no nó com erro → ver output na aba "Output"
2. Ver aba "Error" para mensagem de exceção completa
3. Menu lateral → Executions → selecionar execução → ver cada nó
4. Ativar "Save Successful Executions" em Settings para histórico completo
```

### Nomear Nós de Forma Descritiva

```
Ruim:  HTTP Request, If, Set, HTTP Request 1
Bom:   BuscaClienteAPI, ValidaEmailExiste, MontaPayloadSlack, EnviaNotificacao
```

### Separar Workflows Grandes

Workflows com mais de ~20 nós devem ser divididos:

```
Workflow Principal (Orquestrador)
    → chama via HTTP Request
Workflow: ProcessaDocumento
    → chama via HTTP Request
Workflow: EnviaNotificacoes
```

Use **Webhook** como trigger nos sub-workflows para acoplamento via HTTP interno.

---

## Exemplos de Uso

### Exemplo 1 — Webhook simples com resposta JSON

```
[Webhook Trigger]
  POST /webhook/meu-endpoint
  Corpo: { "nome": "Ana", "email": "ana@email.com" }

[Set Node]
  Define campo "resposta": "Ola, {{ $json.nome }}!"

[Respond to Webhook]
  Retorna: { "resposta": "Ola, Ana!" }
```

### Exemplo 2 — Cron + Google Sheets + Email

```
[Schedule Trigger]
  Todo dia as 08:00

[Google Sheets: Read Rows]
  Ler planilha de tarefas do dia

[IF Node]
  Se "status" == "pendente"
    Branch TRUE: [Send Email] com lista de pendencias
    Branch FALSE: [No Operation]
```

### Exemplo 3 — Uso de expressões no nó HTTP Request

```json
URL: https://api.exemplo.com/clientes/{{ $json.cliente_id }}
Authorization: Bearer {{ $env.API_TOKEN }}
Body:
{
  "nome": "{{ $json.nome }}",
  "email": "{{ $json.email.toLowerCase() }}",
  "timestamp": "{{ $now.toISO() }}"
}
```

### Exemplo 4 — Loop sobre lista de itens

```
[Code Node] retorna array de 50 usuarios

[Split Out]
  transforma array em 50 itens individuais

[Loop Over Items]
  para cada usuario:
    [HTTP Request] POST /api/notificar/{{ $json.id }}

[Aggregate] consolida todos os resultados
```

---

## Checklist de Qualidade

```
WORKFLOW
[ ] Todos os nos tem nomes descritivos (sem "HTTP Request 1")
[ ] Workflow tem nome claro indicando sua funcao
[ ] Workflow tem descricao preenchida no campo Notes
[ ] Nos criticos tem anotacoes (sticky notes) explicando a logica

DADOS E SEGURANCA
[ ] Nenhuma API key ou senha hardcoded em campos de nos
[ ] Credenciais configuradas pelo sistema de Credentials do N8N
[ ] Variaveis de ambiente usadas para configuracoes por ambiente
[ ] Dados sensiveis nao aparecem nos logs de execucao

EXECUCAO E DEBUG
[ ] Pinning ativado nos nos de entrada durante desenvolvimento
[ ] Modo "Save Executions" habilitado para rastreabilidade
[ ] No de erro (Error Trigger) configurado para alertas criticos
[ ] Try/Catch implementado em nos com risco de falha externo

ESTRUTURA
[ ] Workflows com >20 nos divididos em sub-workflows
[ ] Branches de IF/Switch nomeadas com nomes significativos
[ ] Merge nodes usados corretamente para reunir branches
[ ] Sem loops infinitos (condicao de saida sempre presente)

PERFORMANCE
[ ] Pinning usado em testes para nao gastar tokens/requisicoes
[ ] Items processados em batch quando possivel
[ ] Delays adicionados em loops para respeitar rate limits de APIs
```
