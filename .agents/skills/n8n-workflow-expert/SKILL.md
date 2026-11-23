---
name: n8n-workflow-expert
description: "Use quando a tarefa envolver: Automacao completa com N8N — conceitos fundamentais, nodes, triggers, webhooks, tratamento de erros, deploy (Docker, VPS, Cloud, SSL) e integracoes com Google Workspace, Slack, Telegram e Supabase."
---

# Habilidade: N8N Workflow & Integration Expert ⚡🔄

## Propósito
Desenvolver, configurar, implantar e manter fluxos de trabalho e automações robustas na plataforma **N8N** (low-code / pro-code), cobrindo a arquitetura de nós, webhooks seguros, deploy autônomo com Docker/SSL e integrações empresariais nativas.

---

## 1. Fundamentos & Boas Práticas em N8N
- **Estrutura de Execução:** Trigger $\to$ Transformação de Dados $\to$ Condicionais (If / Switch) $\to$ Ações Externas $\to$ Resposta.
- **Estrutura de Dados:** Compreensão rigorosa do array de objetos JSON `[{ "json": { ... } }]`. Uso de expressões JavaScript em `{{ $json.campo }}` e métodos utilitários (`$now`, `$jmespath`).
- **Resiliência & Error Triggers:** Configuração obrigatória de *Error Trigger Node* em fluxos produtivos com envio de alertas para Telegram/Slack e gravação de logs de falha com payload original.
- **Políticas de Retry:** Configuração de retentativas automáticas nos nós HTTP Request para mitigar falhas transitórias.

---

## 2. Deploy & Infraestrutura do N8N
- **Deploy via Docker Compose:**
  - Instância N8N isolada com persistência em volume (`n8n_data`).
  - Banco de metadados robusto em PostgreSQL (`n8n_db`).
  - Proxy reverso com Nginx e certificados SSL automáticos via Certbot / Let's Encrypt.
- **Variáveis de Ambiente Críticas:**
  - `N8N_ENCRYPTION_KEY`: Chave mestra imutável para proteção de credenciais.
  - `WEBHOOK_URL`: Domínio público canônico HTTPS para callbacks externos.
  - `EXECUTIONS_DATA_PRUNE`: Política de limpeza automática de histórico de execuções para evitar esgotamento de disco.

---

## 3. Integrações Corporativas Nativas
- **Google Workspace:** Triggers e ações de Google Sheets (leitura/escrita em batch), Google Drive (upload/download de assets) e Gmail.
- **Telegram & Slack:** Bots conversacionais, envio de mensagens ricas (Markdown/HTML), botões interativos e escuta de webhooks de mensagens.
- **Supabase / PostgreSQL:** Execução de queries tipadas, inserções, atualizações seguras e escuta de webhooks de banco (Database Webhooks) disparados por mutações de tabelas.
