# Checklist Operacional de Deploy do N8N em Produção

Use este checklist antes, durante e após publicar ou atualizar uma instância N8N em VPS (Docker Compose + Proxy Reverso) ou Cloud Run.

---

## 1. Pré-Deploy e Segredos
- [ ] Arquivo `.env` criado no host e listado no `.gitignore` (nunca versionar segredos).
- [ ] `N8N_ENCRYPTION_KEY` gerada com alta entropia (mínimo 32 caracteres) e salva em cofre seguro (sem ela, credenciais não podem ser restauradas).
- [ ] Senhas fortes distintas para banco (`POSTGRES_PASSWORD`) e usuário owner do N8N.
- [ ] Registro DNS (`A` ou `CNAME`) apontando para o servidor/load balancer antes de emitir certificado SSL.

## 2. Rede, Proxy Reverso e TLS
- [ ] Porta `5678` vinculada apenas a `127.0.0.1:5678:5678` (nunca exposta diretamente na internet).
- [ ] Proxy reverso (Nginx, Caddy ou Traefik) com HTTPS ativo e redirecionamento automático HTTP → HTTPS.
- [ ] Headers `Upgrade`, `Connection`, `Host`, `X-Forwarded-For` e `X-Forwarded-Proto` configurados (essencial para WebSockets da UI e SSE/MCP).
- [ ] `WEBHOOK_URL=https://<seu-dominio>/` e `N8N_PROXY_HOPS=1` definidos corretamente.
- [ ] Firewall liberando apenas portas `80`, `443` e SSH (`22` restrita por chave/IP).

## 3. Banco de Dados e Retenção
- [ ] PostgreSQL ativo com `healthcheck` e volume persistente (`postgres_data`).
- [ ] Volume persistente do N8N (`n8n_data:/home/node/.n8n`) validado após restart do container.
- [ ] Limpeza automática habilitada (`EXECUTIONS_DATA_PRUNE=true` e `EXECUTIONS_DATA_MAX_AGE`) para evitar crescimento descontrolado do banco.

## 4. Backup, Restore e Atualização
- [ ] Rotina automatizada (cron/systemd) de backup do PostgreSQL (`pg_dump`) e exportação dos workflows (`n8n export:workflow --all`).
- [ ] Backup armazenado fora do servidor (ex: GCS/S3 com ciclo de vida).
- [ ] Teste de restore validado em ambiente de staging antes do go-live.
- [ ] Estratégia de upgrade documentada (`docker compose pull` + `docker compose up -d` após snapshot do banco).

## 5. Observabilidade e Pós-Deploy
- [ ] Error Workflow global configurado para alertar falhas críticas (Slack/Telegram/E-mail).
- [ ] Teste real de webhook externo (`curl -X POST https://<seu-dominio>/webhook/<path>`) retornando `2xx`.
- [ ] Monitoramento de uptime e renovação automática de SSL testada (`certbot renew --dry-run`).
