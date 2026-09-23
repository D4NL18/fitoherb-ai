---
name: n8n-multi-agents
description: Arquitetura multi-agente no N8N — orquestrador supervisor, sub-agentes especializados, comunicacao via HTTP/Webhook, paralelismo e anti-padroes.
pages: 768-774
---

# n8n-multi-agents

## Objetivo

Projetar e implementar sistemas multi-agente no N8N onde um **orquestrador central** roteia demandas para **sub-agentes especializados**, com suporte a paralelismo, loop de feedback e isolamento de contexto.

Use esta skill sempre que a demanda envolver mais de um domínio de conhecimento, exigir especialização isolada por tarefa, ou quando um único agente genérico produziria respostas de baixa qualidade por acúmulo de responsabilidades.

---

## Conceitos Fundamentais

### O que é Arquitetura Multi-Agente?

Um sistema multi-agente é composto por **múltiplos workflows de IA independentes**, cada um especializado em um domínio, que cooperam para resolver uma tarefa complexa. O ponto de entrada é sempre um **orquestrador**, que analisa a intenção e delega para o sub-agente correto.

### Quando usar Multi-Agente vs Agente Único?

| Critério | Agente Único | Multi-Agente |
|---|---|---|
| Domínio da tarefa | Único e homogêneo | Múltiplos e heterogêneos |
| Volume de ferramentas | Até ~5 ferramentas | Mais de 5 ferramentas no total |
| Contexto por sessão | Pequeno (~8k tokens) | Grande ou segmentado por domínio |
| Complexidade | Baixa a média | Alta — envolve decisão de roteamento |
| Isolamento de falhas | Não necessário | Necessário (falha em um não derruba tudo) |
| Time to market | Rápido | Mais planejamento inicial |

### Papel do Orquestrador

- Recebe o input bruto do usuário
- Analisa a intenção e classifica o domínio
- Decide qual sub-agente(s) chamar
- Consolida as respostas parciais em uma resposta final
- **Não executa ações diretas**: apenas roteia e agrega

### Papel dos Sub-Agentes

- Especializados em um domínio específico (vendas, suporte, técnico)
- Possuem apenas as ferramentas do seu domínio
- Operam de forma isolada (sem acesso ao contexto dos demais)
- Respondem em formato estruturado e padronizado
- Expõem endpoint via **Webhook Trigger** para serem chamados

---

## Padrões e Boas Práticas

### 1. Padrão Supervisor (Orquestrador + Sub-Agentes)

O orquestrador recebe o input, analisa a intenção com um LLM e usa um nó Switch para rotear para o sub-agente correto.

**Diagrama de Fluxo:**

```
[Webhook Input]
      |
[AI Agent Orquestrador]
      |
   [Switch]
   /   |   \
[Vendas] [Suporte] [Técnico]
   \   |   /
[Merge / Consolidador]
      |
[Resposta Final]
```

**System Prompt do Orquestrador (exemplo):**

```
Você é um roteador inteligente. Analise a mensagem do usuário e classifique
a intenção em UMA das categorias abaixo. Responda APENAS com o JSON indicado.

Categorias:
- "vendas": perguntas sobre preços, planos, compras, upgrade
- "suporte": problemas, erros, falhas, reclamações
- "tecnico": dúvidas de configuração, integração, API, documentação

Formato de resposta:
{ "categoria": "<vendas|suporte|tecnico>", "resumo": "<resumo em 1 linha>" }
```

**Configuração do nó Switch:**
- Condição 1: `{{ $json.categoria === 'vendas' }}` → rota Vendas
- Condição 2: `{{ $json.categoria === 'suporte' }}` → rota Suporte
- Condição 3: `{{ $json.categoria === 'tecnico' }}` → rota Técnico

---

### 2. Comunicação entre Agentes via HTTP

Cada sub-agente expõe um **Webhook Trigger** com URL interna. O orquestrador chama via **HTTP Request Node**.

**Payload padrão enviado pelo orquestrador:**

```json
{
  "input": "mensagem original do usuário",
  "session_id": "uuid-da-sessao",
  "contexto": {
    "usuario_id": "usr_123",
    "historico_resumido": "últimas 3 trocas da conversa"
  },
  "metadata": {
    "origem": "whatsapp",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

**Resposta padrão do sub-agente:**

```json
{
  "output": "resposta gerada pelo sub-agente",
  "agente": "suporte",
  "tokens_usados": 842,
  "duracao_ms": 1340,
  "status": "sucesso"
}
```

**Configuração do HTTP Request Node (orquestrador):**
- Method: `POST`
- URL: `{{ $env.N8N_BASE_URL }}/webhook/agente-suporte`
- Body: JSON com payload acima
- Timeout: `30000 ms`
- Headers: `{ "x-agent-token": "{{ $env.AGENT_SECRET }}" }`

---

### 3. Sub-Agentes como Ferramentas (Tool Call)

O N8N permite registrar outro workflow como **ferramenta do AI Agent**. Neste padrão, o LLM decide automaticamente quando chamar cada sub-agente.

**Como configurar:**
1. No workflow orquestrador, adicione nó **AI Agent**
2. Em "Tools", adicione nó **Call n8n Workflow**
3. Configure: Workflow ID do sub-agente, nome da ferramenta e descrição
4. O LLM usará a descrição para decidir quando chamar

**Exemplo de descrição de ferramenta:**

```
Nome: consultar_catalogo_produtos
Descrição: Use esta ferramenta quando o usuário perguntar sobre preços,
produtos disponíveis, planos, promoções ou quiser fazer um orçamento.
Parâmetros: { "query": "string — o que o usuário quer saber sobre produtos" }
```

**Vantagem**: o LLM pode chamar múltiplas ferramentas em sequência automaticamente, sem lógica de Switch manual.

---

### 4. Exemplo Completo: Sistema de Atendimento Multi-Agente

**Arquitetura:**

| Agente | Responsabilidade | Ferramentas |
|---|---|---|
| Roteador | Classifica intenção e delega | Apenas LLM (sem ferramentas externas) |
| Agente Vendas | Consulta catálogo, cria orçamento | HTTP → API Produtos, Google Sheets |
| Agente Suporte | Busca tickets, abre chamado | Zendesk API, Notion |
| Agente Técnico | Consulta docs, gera solução | Vector Store (RAG), GitHub |
| Consolidador | Formata resposta final para canal | Sem ferramentas — apenas formatação |

**Fluxo completo:**

```
1. Webhook recebe mensagem do usuário (WhatsApp/Slack/Chat)
2. Roteador analisa com GPT-4o → retorna { categoria, resumo }
3. Switch roteia para o agente correto
4. Agente especializado executa e retorna { output, status }
5. Consolidador recebe output e formata para o canal de origem
6. Resposta enviada de volta ao usuário
```

---

### 5. Loop de Feedback (Avaliação de Qualidade)

Para respostas críticas, adicione um **agente avaliador** que verifica se a resposta atende aos critérios antes de entregar ao usuário.

**Fluxo com loop de feedback:**

```
[Sub-Agente] → [Avaliador] → { aprovado: true } → [Entrega]
                           ↘ { aprovado: false, motivo } → [Sub-Agente novamente]
```

**Regras obrigatórias do loop:**
- Contador de tentativas via `$executionData` ou campo no payload
- **Máximo de 3 tentativas** — nunca loop infinito
- Condição de parada: `{{ $json.tentativa >= 3 || $json.aprovado === true }}`
- Se esgotar tentativas: retornar resposta de fallback ao usuário

**System prompt do avaliador:**

```
Avalie a resposta abaixo com base nos critérios:
1. Responde diretamente à pergunta? (sim/não)
2. Tem no máximo 3 parágrafos? (sim/não)
3. Contém links ou referências concretas? (sim/não)

Responda APENAS: { "aprovado": true/false, "motivo": "string" }
```

---

### 6. Paralelismo de Sub-Agentes

Quando a tarefa pode ser dividida em partes independentes, execute múltiplos sub-agentes **simultaneamente**.

**Como implementar no N8N:**
1. Após o roteador, adicione múltiplos **HTTP Request Nodes** em paralelo
2. Use o nó **Merge** (modo: "Wait for All") para consolidar
3. O consolidador recebe um array com todas as respostas

**Cuidados com paralelismo:**
- Garanta que os sub-agentes são **stateless** (sem efeitos colaterais interdependentes)
- Defina timeout individual em cada chamada HTTP (`15000 ms`)
- No Merge, verifique se todas as respostas chegaram com `status: "sucesso"`
- Trate falhas parciais: se um sub-agente falhar, os demais continuam

**Exemplo de uso:**
- Roteador recebe: "Qual o melhor plano para minha empresa com 50 usuários?"
- Executa em paralelo: Agente Vendas (preços) + Agente Técnico (limites técnicos)
- Consolidador mescla as respostas em uma recomendação unificada

---

### 7. Anti-Padrões a Evitar

| Anti-Padrão | Problema | Solução |
|---|---|---|
| Agente único com 15+ ferramentas | Context bloat, alucinações, custo alto | Dividir em sub-agentes por domínio |
| Contexto compartilhado sem isolamento | Vazamento de dados entre sessões | Usar `session_id` + memória isolada por agente |
| Loop sem condição de saída | Execução infinita, custo ilimitado | Sempre adicionar contador + `max_tentativas` |
| Sub-agentes com ferramentas desnecessárias | Risco de uso indevido, custo extra | Princípio do menor privilégio nas ferramentas |
| Orquestrador que escreve/modifica dados | Viola separação de responsabilidades | Orquestrador só roteia e consolida |
| Chamadas síncronas sem timeout | Workflow travado indefinidamente | Timeout obrigatório em toda chamada HTTP |

---

## Exemplos de Uso

### Exemplo 1: Triagem de E-mails Corporativos

**Cenário:** E-mails chegam via Gmail Trigger. O orquestrador classifica em: Comercial, RH, Jurídico ou Spam.

```
[Gmail Trigger]
→ [Orquestrador: classifica e-mail com LLM]
→ [Switch por categoria]
  → Comercial: [Agente Comercial] → resposta automática + CRM
  → RH: [Agente RH] → notifica equipe no Slack
  → Jurídico: [Agente Jurídico] → cria ticket no Notion
  → Spam: [Mover para Spam]
```

---

### Exemplo 2: Pipeline de Geração de Conteúdo

**Cenário:** Usuário solicita artigo sobre um tema. Múltiplos agentes colaboram.

```
[Input: tema + público-alvo]
→ [Orquestrador]
→ Paralelo:
  → [Agente Pesquisa] → bullet points de referências
  → [Agente SEO] → keywords e estrutura de headings
→ [Merge]
→ [Agente Redator] → draft completo do artigo
→ [Agente Revisor] → revisão gramatical e de tom
→ [Output: artigo finalizado]
```

---

### Exemplo 3: Suporte Técnico com Escalamento

**Cenário:** Bot de suporte que tenta resolver automaticamente e escala para humano se necessário.

```
[Webhook: mensagem do usuário]
→ [Agente L1: solução automática via RAG]
→ [Avaliador: solução foi completa?]
  → Sim: [Resposta ao usuário]
  → Não: [Agente L2: busca engenheiro + abre ticket]
         → [Notifica Slack com contexto completo]
         → [Resposta ao usuário: "Um especialista vai te contatar"]
```

---

## Checklist de Qualidade

Antes de publicar um sistema multi-agente em produção, valide:

- [ ] Cada sub-agente tem responsabilidade única e bem definida
- [ ] Payload de entrada e saída são padronizados e documentados
- [ ] Todos os HTTP Requests têm timeout configurado
- [ ] Loops têm contador e condição de saída obrigatória
- [ ] Sub-agentes usam somente ferramentas necessárias ao seu domínio
- [ ] Orquestrador não realiza escrita ou modificação de dados
- [ ] `session_id` é propagado em todas as chamadas para rastreabilidade
- [ ] Há tratamento de erro em caso de sub-agente indisponível
- [ ] Logs estruturados em cada agente para auditoria
- [ ] Testado com cenários de falha parcial (um sub-agente offline)
- [ ] Custo de tokens estimado por chamada completa documentado
- [ ] Documentação do fluxo atualizada em `.agents/docs/`
