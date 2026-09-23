---
name: n8n-deploy
description: Deploy do N8N em diferentes ambientes — Cloud n8n.io, VPS com Docker+Nginx+SSL, local com Docker, ngrok para webhooks e Google Cloud Run. Inclui configuracao de dominio, HTTPS e backup de workflows.
pages: 683-704
---

# N8N Deploy — Estrategias de Hospedagem e Configuracao

## Objetivo

Implantar o N8N de forma segura e persistente nos diferentes ambientes disponiveis — desde testes locais com Docker ate producao em VPS ou Google Cloud Run — garantindo HTTPS, dominio personalizado, backup de dados e variaveis de ambiente corretas.

---

## Conceitos Fundamentais

### Mapa de Opcoes de Deploy

| Opcao           | Custo          | Setup    | SSL          | Ideal para                    |
|-----------------|----------------|----------|--------------|-------------------------------|
| n8n.io Cloud    | $24/mes+       | Imediato | Automatico   | Iniciantes sem infra           |
| VPS + Docker    | $5-20/mes      | 30 min   | Manual Nginx | Producao com controle total    |
| Local + Ngrok   | Gratis         | 5 min    | Via ngrok    | Desenvolvimento e testes       |
| Google Cloud Run| Pay-per-use    | 45 min   | Automatico   | Uso pessoal/interno sem licenca|

### Tabela Comparativa Detalhada

| Criterio           | n8n.io Cloud   | VPS + Docker   | Local + Ngrok  | Cloud Run      |
|--------------------|----------------|----------------|----------------|----------------|
| Custo mensal       | $24+           | $5-20          | $0             | Uso real       |
| Setup              | Imediato       | 30 min         | 5 min          | 45 min         |
| SSL/HTTPS          | Automatico     | Manual (Nginx) | Via ngrok      | Automatico     |
| Dominio proprio    | Sim            | Sim            | URL ngrok      | Sim            |
| Licenca comercial  | Inclusa        | Fair Code ok   | Fair Code      | Nao necessaria |
| Persistencia       | Sim            | Sim (volumes)  | Reiniciavel    | Sim (database) |
| Execucoes ilimit.  | Plano pago     | Sim            | Sim            | Sim            |

---

## Padroes e Boas Praticas

### 1. Deploy Local com Docker (Desenvolvimento)

```bash
# Execucao basica — dados nao persistem
docker run -it --rm \
  -p 5678:5678 \
  --name n8n \
  n8nio/n8n

# Execucao com volume para persistencia
docker run -it --rm \
  -p 5678:5678 \
  --name n8n \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_HOST=localhost \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  n8nio/n8n

# Acessar em: http://localhost:5678
```

**Variaveis de Ambiente Essenciais:**

```bash
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=https
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=senha_forte
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
GENERIC_TIMEZONE=America/Sao_Paulo
TZ=America/Sao_Paulo
```

---

### 2. Ngrok — Webhooks em Desenvolvimento Local

O ngrok expoe o N8N local na internet via tunnel HTTPS, essencial para testar webhooks do Telegram, WhatsApp, Stripe etc.

```bash
# Instalar ngrok em https://ngrok.com/download

# Expor a porta 5678 do N8N
ngrok http 5678

# Output exemplo:
# Forwarding  https://abc123.ngrok-free.app -> http://localhost:5678

# Usar a URL ngrok como WEBHOOK_URL no N8N
docker run -it --rm \
  -p 5678:5678 \
  -e WEBHOOK_URL=https://abc123.ngrok-free.app \
  n8nio/n8n
```

> AVISO: URL do ngrok muda a cada restart no plano gratis. Use conta paga para dominio fixo ou substitua por VPS em producao.

---

### 3. VPS com Docker Compose + Nginx + SSL

#### Estrutura de Arquivos no Servidor

```
/opt/n8n/
├── docker-compose.yml
├── .env
└── nginx/
    └── n8n.conf
```

#### docker-compose.yml Padrao Completo

```yaml
version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${DB_USER}
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - TZ=America/Sao_Paulo
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres
    networks:
      - n8n_net

  postgres:
    image: postgres:15-alpine
    container_name: n8n_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n_net

volumes:
  n8n_data:
  postgres_data:

networks:
  n8n_net:
    driver: bridge
```

#### Arquivo .env do Servidor

```bash
N8N_HOST=n8n.meudominio.com
N8N_USER=admin
N8N_PASSWORD=SenhaForteAqui123!
DB_USER=n8nuser
DB_PASSWORD=DbSenhaForte456!
```

#### Configuracao Nginx com SSL

```nginx
server {
    listen 80;
    server_name n8n.meudominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name n8n.meudominio.com;

    ssl_certificate     /etc/letsencrypt/live/n8n.meudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.meudominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

#### Comandos de Deploy Passo a Passo

```bash
# 1. Conectar na VPS
ssh root@IP_DO_SERVIDOR

# 2. Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# 3. Criar estrutura
mkdir -p /opt/n8n/nginx && cd /opt/n8n

# 4. Criar arquivos docker-compose.yml, .env, nginx/n8n.conf

# 5. SSL com Certbot
apt install certbot python3-certbot-nginx -y
certbot --nginx -d n8n.meudominio.com

# 6. Subir os containers
docker compose up -d

# 7. Verificar logs
docker compose logs -f n8n

# 8. Verificar status
docker compose ps
```

---

### 4. Google Cloud Run — Sem Licenca Comercial

Ideal para uso pessoal ou interno sem custo fixo. O Cloud Run fatura apenas pelo tempo de execucao efetivo.

```bash
# Deploy via gcloud CLI
gcloud run deploy n8n \
  --image n8nio/n8n \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5678 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1 \
  --set-env-vars="N8N_HOST=n8n-xxx-uc.a.run.app,N8N_PROTOCOL=https,N8N_PORT=5678"

# Configurar banco externo (Cloud SQL / Supabase) para persistencia
# N8N precisa de DB externo para persistir dados no Cloud Run

# Mapear dominio personalizado
# Cloud Run -> Domain Mappings -> Add Mapping
```

> AVISO: Cloud Run tem cold start (~2-5s). Para webhooks em producao criticos, use --min-instances 1 ou prefira VPS.

---

### 5. Backup de Workflows

```bash
# Exportar todos os workflows via CLI do N8N
docker exec -it n8n n8n export:workflow \
  --all \
  --output=/home/node/.n8n/backups/workflows_$(date +%Y%m%d).json

# Exportar credenciais (criptografadas)
docker exec -it n8n n8n export:credentials \
  --all \
  --output=/home/node/.n8n/backups/credentials_$(date +%Y%m%d).json

# Cron de backup automatico no servidor (crontab -e)
0 2 * * * docker exec n8n n8n export:workflow --all \
  --output=/opt/n8n/backups/wf_$(date +%Y%m%d).json

# Importar workflows em nova instancia
docker exec -it n8n n8n import:workflow \
  --input=/caminho/workflows.json
```

---

## Exemplos de Uso

### Exemplo 1 — Startup rapido para dev com ngrok

```bash
# Terminal 1: subir N8N
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Terminal 2: expor com ngrok
ngrok http 5678

# Copiar URL ngrok e configurar em:
# N8N Settings -> Webhook URL -> colar URL do ngrok
```

### Exemplo 2 — Atualizar versao sem downtime

```bash
cd /opt/n8n

# Puxar nova imagem
docker compose pull n8n

# Recriar container com nova versao
docker compose up -d --no-deps n8n

# Verificar nova versao
docker exec n8n n8n --version
```

### Exemplo 3 — Rollback de workflow

```bash
# Importar versao anterior exportada
docker exec -it n8n n8n import:workflow \
  --input=/opt/n8n/backups/wf_20261001.json

# Verificar workflows importados na UI do N8N
```

---

## Checklist de Qualidade

```
ANTES DO DEPLOY
[ ] .env criado com todas as variaveis necessarias
[ ] .env esta no .gitignore (NUNCA commitar segredos)
[ ] Senha forte para autenticacao (minimo 16 caracteres)
[ ] Banco de dados externo configurado (PostgreSQL, nao SQLite em prod)
[ ] DNS do dominio apontando para IP do servidor

SSL E SEGURANCA
[ ] SSL/HTTPS configurado e funcionando
[ ] HTTP para HTTPS redirect ativo no Nginx
[ ] Firewall: apenas portas 80, 443 e 22 abertas
[ ] N8N nao exposto diretamente (Nginx como proxy reverso)
[ ] Autenticacao basica ou OAuth habilitados

WEBHOOKS E CONECTIVIDADE
[ ] WEBHOOK_URL configurada com HTTPS correto
[ ] Testar webhook externo (curl -X POST https://...) antes de producao
[ ] Ngrok apenas em desenvolvimento, NUNCA em producao

PERSISTENCIA E BACKUP
[ ] Volumes Docker mapeados para diretorio do host
[ ] PostgreSQL como banco (nao SQLite para producao)
[ ] Backup automatico de workflows configurado com cron
[ ] Backup de credenciais criptografado e armazenado com seguranca
[ ] Teste de restore de backup realizado antes de ir para producao

MONITORAMENTO
[ ] Logs do container acessiveis (docker logs n8n)
[ ] Alertas de erro configurados (Error Workflow no N8N)
[ ] Uptime monitoring configurado (UptimeRobot, Checkly)
[ ] Renovacao automatica de SSL testada (certbot renew --dry-run)
```
