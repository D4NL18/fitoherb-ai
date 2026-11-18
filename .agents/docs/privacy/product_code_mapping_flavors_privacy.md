# Parecer Oficial de Privacy by Design & Conformidade LGPD 🛡️📜

**Feature / Módulo:** Mapeamento de Código ERP por SKU, Sabores/Apresentações e Sincronização Prod → Local (`product_code_mapping_flavors`)  
**Regras Auditadas:** `P-400` a `P-413` ([`.agents/docs/business_rules/product_code_mapping_flavors.md`](../business_rules/product_code_mapping_flavors.md)) e `P-302`, `P-304`, `P-305` ([`.agents/docs/business_rules/chatbot_assistant.md`](../business_rules/chatbot_assistant.md))  
**Etapa da Esteira:** Etapa 2 — Revisão de Privacy by Design & Bases Legais  
**Autoridade Responsável:** Encarregado de Proteção de Dados / DPO (`privacy_officer`)  
**Skill Aplicada:** `lgpd-privacy-expert` (Lei nº 13.709/2018 - LGPD & 7 Princípios de Ann Cavoukian)  
**Status do Parecer:** **APROVADO COM CONDICIONANTES OBRIGATÓRIAS** ✅⚠️

---

## 1. Matriz de Classificação Jurídico-Técnica de Dados (LGPD)

Nos termos dos arts. 1º, 5º, 7º, 11 e 12 da Lei nº 13.709/2018 (LGPD), todos os domínios de dados manipulados pela feature nos repositórios `fitoherb-backend-v2`, `fitoherb-frontend-v2` e `fitoherb-ai` foram auditados e classificados:

| Domínio / Fonte de Dados | Campos / Atributos Auditados | Classificação LGPD | Enquadramento Legal e Tratamento Exigido |
| :--- | :--- | :--- | :--- |
| **Catálogo de Produtos e SKUs (`products`, `product_skus`)** | `id`, `name`, `slug`, `description`, `image_path`, `flavours`, `presentation`, `erpCode` (`Id_Pro`), `category_id`, `supplier_id` | **Dado Corporativo / Cadastral de Mercadoria (Não Pessoal)** | **Fora do escopo de dados pessoais (Art. 1º da LGPD).** Contudo, `erpCode` (`Id_Pro`) e status ERP possuem sigilo operacional restrito ao `/admin` (`P-408`). |
| **Espelho ERP Atrio (`erp_catalog_items`)** | `Id_Pro`, `descricao_pro`, `codbarra_pro` (EAN), `inativo_pro`, `Marca.Nome_Marc`, `in_externo_01`, `synced_at` | **Dado Corporativo / Operacional (Não Pessoal)** | **Fora do escopo de dados pessoais**, desde que respeitada rigorosamente a **Allowlist de Extração** (Seção 2.2), vedando ingestão de PII de `Clientes`, vendedores e `dbo.Fornecedor` (PF/MEI). |
| **Origem ERP Restrita (NÃO IMPORTAR): `dbo.Fornecedor`, `Clientes`, Vendedores, `Estoque`, Preços** | Nome civil/CPF de fornecedores PF/MEI (ex.: `MARCO ANTONIO DE BRITO JUNIOR`, `NILZA SANTOS DE ANDRADE`, `DEBORA DA SILVA LEMOS SANTANA`), `CNPJ`, `Clientes.*`, `Estoque`, `Pc.Ultimo Custo`, `Pc.Venda` | **Dado Pessoal (quando PF/MEI/Cliente/Vendedor)** / **Sigilo Comercial (Estoque/Custos/Preços)** | **BLOQUEIO NA ORIGEM (Minimização — Art. 6º, III LGPD).** Proibida a extração, sincronização para `erp_catalog_items`, persistência em logs, exportação em filas de curadoria ou exposição em APIs/Chatbot (`P-302`, `P-408`). |
| **Auditoria Interna JPA (`products`, `suppliers`, `product_categories`, `product_skus`)** | `created_by`, `updated_by` (preenchidos via `AuditorAwareImpl` com `authentication.getName()` = `user.email`), `created_at`, `updated_at` | **Dado Pessoal (Operador Interno / Colaborador)** | **Execução de Contrato (Art. 7º, V)** e **Legítimo Interesse (Art. 7º, IX — LIA na Seção 5.1).** Uso restrito à rastreabilidade interna no banco; jamais exposto em rotas públicas, DTOs públicos ou `CatalogIndex`. |
| **Tabela `users` no Dump Prod → Local (`fitoherb_backup.sql`)** | `id`, `email`, `name`, `password` (hash BCrypt), `role` (`ADMIN`, `USER`, `SELLER`) | **Dado Pessoal e Credencial de Acesso (Operadores Internos)** | **Execução de Contrato (Art. 7º, V) / Segurança (Art. 46).** Proibido expor em logs ou artefatos de curadoria; exige higienização local pós-restore (Seção 3.3). |
| **Vitrine Pública e `CatalogIndex` (`fitoherb-ai`)** | `name`, `slug`, `image_url`, `description`, `flavours`, `presentation`, `category`, `supplier` | **Dado Comercial Público (Não Pessoal)** | **Fora do escopo de dados pessoais.** Deve permanecer 100% isolado de `Id_Pro`, `inativo_pro`, `Estoque` e e-mails de operadores (`P-408`). |

---

## 2. Minimização de Dados e Anti-Overfetching na Integração com o ERP Atrio (`FITOHERB`)

### 2.1. Diagnóstico de Riscos na Base de Origem (SQL Server 2008 R2 `FITOHERB`)
A análise do ecossistema do ERP Atrio revelou dois vetores críticos de risco de privacidade e confidencialidade:
1. **Mistura de Dados Corporativos com Dados Pessoais (PII) em `dbo.Fornecedor`:** Embora muitos fabricantes/distribuidores sejam pessoas jurídicas, existem registros cadastrados como pessoas físicas ou MEIs contendo nome civil completo e CPF (exemplos identificados na base: `MARCO ANTONIO DE BRITO JUNIOR`, `NILZA SANTOS DE ANDRADE`, `DEBORA DA SILVA LEMOS SANTANA`). Além disso, o ERP mantém tabelas integrais de `Clientes` (titulares pessoas físicas/jurídicas) e vendedores.
2. **Dados Comerciais e Financeiros Sensíveis ao Negócio:** As views e tabelas do ERP (`[dbo].[Produtos]` e `[Externo01].[Produto]`) contêm colunas como `Estoque`, `Pc.Ultimo Custo`, `Pc.Venda` e identificadores fiscais (`CNPJ`/`CPF`), cuja exposição violaria as regras `P-302` e `P-408`.

Em estrita observância ao **Princípio da Necessidade / Minimização (Art. 6º, III da LGPD)** e ao **1º e 3º Princípios de Privacy by Design (Proatividade e Privacidade Incorporada à Arquitetura)**, a integração deve operar por **Allowlist Explícita (Projection Pushdown)**.

### 2.2. Matriz Mandatória: Allowlist vs. Blocklist na Sincronização para `erp_catalog_items`

| Tabela / Coluna de Origem no ERP Atrio | Destino em `erp_catalog_items` | Decisão DPO | Justificativa Técnica e Legal |
| :--- | :--- | :--- | :--- |
| `[dbo].[Produtos].Id_Pro` (com `Empresa_Pro = 1`) | **PERMITIDO** (`id_pro` / `erp_code`, PK/Unique) | ✅ **SINCRONIZAR** | Chave autoritativa indispensável para rastreabilidade 1:1 do SKU (`P-402`, `P-403`). |
| `[dbo].[Produtos].descricao_pro` (ou `[Externo01].[Produto].Descricao`) | **PERMITIDO** (`description`) | ✅ **SINCRONIZAR** | Necessário para busca administrativa (`P-407`) e matching determinístico (`P-409`). |
| `[dbo].[Produtos].codbarra_pro` (ou `[Externo01].[Produto].EAN`) | **PERMITIDO** (`ean` / `barcode`) | ✅ **SINCRONIZAR** | Identificador técnico GTIN/EAN da mercadoria para busca e pesquisa web (`P-407`, `P-409`). |
| `[dbo].[Produtos].inativo_pro` | **PERMITIDO** (`is_inactive` / `inativo_pro`) | ✅ **SINCRONIZAR** | Flag operacional (`0`/`1`) necessária para política de alertas administrativos (`P-406`). |
| `Marca.Nome_Marc` (via `Marca_Pro`) | **PERMITIDO** (`brand_name`) | ✅ **SINCRONIZAR (PREFERENCIAL)** | Representa a marca comercial/fabricante (dado não pessoal), evitando ingestão de nome civil/CPF de `dbo.Fornecedor`. |
| `[Externo01].[Produto].Fornecedor` | **PERMITIDO COM FILTRO SANITIZADOR** (`erp_supplier_label`) | ⚠️ **SINCRONIZAR APENAS SE SANITIZADO** | Utilizar somente após descartar padrões de CPF/CNPJ ou nomes civis PF/MEI não comerciais, preferindo sempre `Marca.Nome_Marc`. |
| Presença na view `[Externo01].[Produto]` | **PERMITIDO** (`in_externo_view` boolean) | ✅ **SINCRONIZAR** | Flag booleana necessária para distinguir inativos em `Externo01` (`P-406`). |
| `dbo.Clientes` (toda a tabela) | **PROIBIDO** | 🚫 **VETADO** | Contém PII integral de clientes/consumidores sem nenhuma finalidade no catálogo. |
| Tabelas de Vendedores / Usuários do ERP | **PROIBIDO** | 🚫 **VETADO** | Contém PII de colaboradores/representantes sem finalidade no catálogo. |
| `dbo.Fornecedor` (razão social PF/MEI, nome civil, CPF, CNPJ, telefone, endereço, e-mail) | **PROIBIDO** | 🚫 **VETADO** | Risco direto de coleta e exposição de dados pessoais (ex.: nomes civis e CPFs de MEIs/autônomos). |
| `[Externo01].[Produto].Estoque` / saldos de estoque | **PROIBIDO** | 🚫 **VETADO** | Violação direta de `P-302` e `P-408`; zero necessidade para mapeamento de SKU. |
| `Pc.Ultimo Custo`, `Pc.Venda`, preços, margens, tributos, `CNPJ`/`CPF` | **PROIBIDO** | 🚫 **VETADO** | Sigilo comercial e fiscal; violação de `P-302` e minimização. |

### 2.3. Diretrizes de Extração Segura (SQL Server → Curadoria Temporária & Runtime Cache)
1. **Proibição de `SELECT *`:** Todo script, job ou conector JDBC (`ErpSqlServerGateway` em runtime e script Python na curadoria `US-P1`) no SQL Server 2008 R2 DEVE declarar explicitamente apenas as colunas da **Allowlist** acima (`Id_Pro`, `Empresa_Pro`, `descricao_pro`, `codbarra_pro`, `Marca.Nome_Marc`, `TipoProd.descricao_tppro`, `inativo_pro`, flag `Externo01.Produto`) com filtro `WHERE p.Empresa_Pro = 1` e `WITH (NOLOCK)`.
2. **Substituição de `dbo.Fornecedor` por `Marca.Nome_Marc`:** A query de extração usa exclusivamente `LEFT JOIN` com `dbo.Marca` e `dbo.TipoProd`, eliminando totalmente `dbo.Fornecedor`, `Clientes`, Vendedores, `Estoque` e preços (`P-302`, `P-408`).
3. **Atualização da Dúvida `Q-01` conforme Decisão `A1` + Condicionante SecOps Obrigatória:** O Usuário optou em `A1` por usar espelho ERP em PostgreSQL **exclusivamente durante o clone/sincronização inicial**, removendo-o em seguida (`DROP TABLE`) do banco do site. Em runtime, como a prova técnica em Java 21 comprovou que `mssql-jdbc` falha no handshake TLS 1.0 do SQL Server 2008 R2 e `jtds:1.3.1` (`ssl=off`) trafega Login7 sem TLS, é **CONDICIONANTE BLOQUEANTE DE PRIVACIDADE E SEGURANÇA** utilizar uma conta SQL Server **dedicada exclusivamente `SELECT`** apenas nesses 4 objetos de catálogo (jamais credencial `sa` ou com leitura sobre `Clientes`/`dbo.Fornecedor`), mantida exclusivamente via variáveis de ambiente / Secret Manager.

### 2.4. Restrições de Privacidade na Pesquisa Web de Curadoria (`P-409` — Nível 2)
Durante a execução da pesquisa externa na web para desambiguação de SKUs legados (`P-409`):
- As consultas enviadas a motores de busca externos devem conter **exclusivamente** nome comercial do produto, marca fabricante (`Marca.Nome_Marc` / marca do site), gramatura/apresentação e código EAN.
- É **TERMINANTEMENTE PROIBIDO** incluir nas queries de pesquisa externa nomes de pessoas físicas oriundos de `dbo.Fornecedor`, CPFs, e-mails de operadores da tabela `users`, endereços ou dados comerciais internos (`Estoque`, `Pc.Ultimo Custo`, `Pc.Venda`).

---

## 3. Proteção de Credenciais, Segredos e Isolamento de Ambientes (`P-400`, `P-408`)

### 3.1. Gestão de Credenciais do ERP SQL Server, `backup.yml` e Deploy Cloud Run
- **Credenciais do ERP SQL Server (`FITOHERB`):**
  - Variáveis como host/IP interno, instância, porta, banco (`FITOHERB`), usuário e senha do SQL Server devem residir exclusivamente em arquivo `.env` local (não versionado) ou em cofres gerenciados (**Google Secret Manager** / **GitHub Actions Secrets**).
  - O usuário de banco configurado no ERP para o job de sincronização deve seguir o **Princípio do Menor Privilégio**: permissão exclusivamente `SELECT` apenas nas tabelas/colunas estritamente necessárias (`[dbo].[Produtos]`, `[Externo01].[Produto]`, tabela `Marca`), sem permissão de `SELECT` em `Clientes`, `dbo.Fornecedor` ou tabelas financeiras/fiscais e sem permissão de escrita (`INSERT`/`UPDATE`/`DELETE`).
  - É **terminantemente proibido** expor qualquer variável, string de conexão, host ou código de erro bruto do SQL Server no frontend Angular (`environment.ts` / `environment.prod.ts`), em mensagens HTTP de erro (`RestExceptionHandler`) ou em logs públicos.
- **Secrets de Backup e Produção (`backup.yml`, `deploy-prod.yml`, `deploy-qa.yml`):**
  - Em `fitoherb-backend-v2/.github/workflows/backup.yml`, o acesso ao banco Supabase de produção usa `${{ secrets.PROD_DB_PASSWORD }}` com artefato de retenção mínima (`retention-days: 1`).
  - O arquivo exportado `fitoherb_backup.sql` **nunca** deve ser salvo em diretório compartilhado ou versionado no Git, e deve ser removido do sistema de arquivos local imediatamente após a restauração e validação da base local `fitoherb-v2`.

### 3.2. Achados Críticos Identificados na Auditoria Atual (Ação Obrigatória)
Durante a inspeção dos três repositórios na Etapa 2, foram detectadas **três vulnerabilidades pré-existentes** que impactam diretamente a segurança de credenciais e PII desta feature:

1. **Gap no `.gitignore` de `fitoherb-backend-v2`:**
   - *Evidência:* `fitoherb-backend-v2/.gitignore` ignora `automation_scripts/`, `temp_images/` e `.agents/docs/STATE.md`, porém **não ignora** `.env`, `.env.*`, `*.sql`, `*.dump`, `*.bak` nem `fitoherb_backup.sql`.
   - *Condicionante Obrigatória:* Atualizar `fitoherb-backend-v2/.gitignore` (e revisar `fitoherb-ai/.gitignore`) na Etapa 3 antes de qualquer script/backup local para bloquear explicitamente `.env`, `.env.*` (preservando `.env.example`), `*.sql` (exceto migrations versionadas em `src/main/resources/db/migration/`), `*.dump`, `*.bak` e artefatos locais de fila humana contendo dados de dump.
2. **Senha Fallback Hardcoded em `fitoherb-ai`:**
   - *Evidência:* `fitoherb-ai/app/domains/chat/infrastructure/catalog_index.py` (linha 81) contém credencial literal de fallback: `db_pass = password or os.getenv("PostgresPassword") or os.getenv("POSTGRES_PASSWORD") or "Dm120394"`.
   - *Condicionante Obrigatória:* Remover a senha literal `"Dm120394"` na Etapa 3 (`US-P5`), exigindo leitura estrita de variável de ambiente (`POSTGRES_PASSWORD` / `PostgresPassword`) e falhando de forma segura (sem logar a senha) quando não configurada.
3. **Log de PII (E-mail de Operador) em `SecurityFilter.java`:**
   - *Evidência:* `fitoherb-backend-v2/.../infra/security/SecurityFilter.java` (linha 34) executa `System.out.println("Token validated, email: " + email);`, gravando endereço de e-mail pessoal em texto puro nos logs de stdout/Cloud Logging.
   - *Condicionante Obrigatória:* Toda nova classe/serviço da feature (`ErpCatalogService`, `ProductSkuService`, scripts de curadoria) está proibida de logar e-mails, senhas, tokens JWT ou payloads de `users`; adicionalmente, recomenda-se remover/sanitizar a linha 34 de `SecurityFilter.java` e evitar logs com e-mail em texto puro em `AuthorizationService.java`.

### 3.3. Cláusula de Higienização Prod → Local (`P-400`) e Proteção da Tabela `users`
Ao restaurar `fitoherb_backup.sql` (produção) para o PostgreSQL local `fitoherb-v2`:
1. **Escopo Estrito de Leitura na Curadoria:** Scripts de saneamento, matching e geração de backfill (`US-P1` / `US-P6`) devem acessar **apenas** `products`, `product_categories`, `suppliers`, `product_skus` e `erp_catalog_items`. É **proibido** ler, imprimir, incluir em CSVs/JSONs da `HUMAN_REVIEW_QUEUE` ou copiar para pacotes de promoção quaisquer registros da tabela `users` (`email`, `name`, `password` BCrypt, `role`) ou colunas de auditoria pessoal (`created_by`, `updated_by`).
2. **Higienização Obrigatória Pós-Restore na Base Local (`users` e Auditoria):**
   - Imediatamente após restaurar o dump no PostgreSQL local, deve ser executado script de sanitização local para:
     - Substituir/mascarar os e-mails reais e hashes de senha na tabela `users` local (preservando apenas usuários sintéticos de desenvolvimento local, como `admin@local.fitoherb`), impedindo o uso acidental de dados reais de colaboradores ou disparo acidental de e-mails reais pelo `MailService` em ambiente local.
     - Opcionalmente higienizar `created_by` e `updated_by` no clone local para `"MIGRATION_LOCAL"` / `"SYSTEM"` quando não forem necessários para testes locais.
3. **Trava de Segurança Anti-Escrita em Produção (`P-400`):**
   - Qualquer script de restauração, saneamento (`P-401`) ou curadoria local (`P-409`) deve validar programaticamente que o hostname de destino é exclusivamente local (`localhost` ou `127.0.0.1`) antes de executar `DROP`, `TRUNCATE`, `RESTORE` ou `UPDATE`, abortando imediatamente caso detecte host remoto/produção (ex.: `*.supabase.com`).
4. **Higiene do Pacote Idempotente de Rollout (`US-P6`):**
   - A migração/backfill promovida posteriormente para QA/Produção deve conter exclusivamente `INSERT`/`UPDATE` sobre `products` (`flavours`, `presentation`) e `product_skus` (`erpCode` / `Id_Pro`), sem tocar na tabela `users` e sem gravar e-mails pessoais fixos em `created_by`/`updated_by` (usando identificador técnico de sistema, ex.: `"SYSTEM_BACKFILL"`).

---

## 4. Segregação Vitrine Pública vs. Painel Admin e RBAC (`ROLE_ADMIN`/`ROLE_USER` vs `ROLE_SELLER` vs Público)

### 4.1. Auditoria de `SecurityConfigurations.java` e Matriz RBAC
A análise de `SecurityConfigurations.java`, `SecurityFilter.java`, `User.java`, `UserRole.java`, `AuthorizationService.java` e `AdminComponent` / `AdminNavComponent` constatou que:
- O sistema adota autenticação Stateless JWT (via cookie `HttpOnly` `fitoherb_jwt` ou header `Authorization: Bearer`) e `@EnableMethodSecurity`.
- `User.getAuthorities()` concede:
  - `UserRole.ADMIN` → `ROLE_ADMIN`, `ROLE_USER`, `ROLE_SELLER` (`isAdminOrUser() = true`)
  - `UserRole.USER` → `ROLE_USER` (`isAdminOrUser() = true`)
  - `UserRole.SELLER` → `ROLE_SELLER` (`isAdminOrUser() = false`)
- **⚠️ ALERTA ARQUITETURAL CRÍTICO EM `SecurityConfigurations.java` (Linha 41):**
  O método `securityFilterChain` possui `.anyRequest().permitAll()` na configuração HTTP global, delegando o bloqueio 100% às anotações `@PreAuthorize` nos métodos dos controllers. Sob a ótica de **Privacy by Design (Fail-Safe Defaults / Deny by Default)**, qualquer novo endpoint criado sem `@PreAuthorize` ficará automaticamente exposto à internet sem autenticação!

#### Matriz Obrigatória de Controle de Acesso (RBAC) para a Feature

| Fluxo / Recurso | Público (Anônimo) | `ROLE_SELLER` (Vendedor) | `ROLE_USER` (Operador Catálogo) | `ROLE_ADMIN` (Administrador) | Regra de Proteção Backend Obrigatória |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Vitrine Pública (`GET /products/gallery`)** | ✅ Permitido | ✅ Permitido | ✅ Permitido | ✅ Permitido | Sem dados ERP (`Id_Pro`, `inativo_pro`, `Estoque`) e sem PII (`P-408`). |
| **Chatbot (`POST /api/v1/chat/messages`) & `CatalogIndex`** | ✅ Permitido | ✅ Permitido | ✅ Permitido | ✅ Permitido | Lê apenas campos públicos saneados (`flavours`, `presentation`, `P-302`, `P-408`). |
| **Listagem/Detalhe Admin (`GET /products`, `GET /products/{slug}`)** | ❌ `401`/`403` | ❌ `403` | ✅ Permitido | ✅ Permitido | `@PreAuthorize("@authorizationService.isAdminOrUser()")` |
| **CRUD Produtos (`POST`, `PUT`, `DELETE /products/**`)** | ❌ `401`/`403` | ❌ `403` | ✅ Permitido | ✅ Permitido | `@PreAuthorize("@authorizationService.isAdminOrUser()")` |
| **Busca/Leitura Catálogo Espelhado ERP (`GET /erp/products/**`)** | ❌ `401`/`403` | ❌ `403` | ✅ Permitido | ✅ Permitido | `@PreAuthorize("@authorizationService.isAdminOrUser()")` + proteção `requestMatchers` em `SecurityConfigurations`. |
| **Refresh / Sync / Governança Backfill ERP (se exposto via HTTP)** | ❌ `401`/`403` | ❌ `403` | ❌ `403` | ✅ Permitido | `@PreAuthorize("@authorizationService.isAdmin()")` (somente `ADMIN`). |

**Condicionantes Técnicas de Segurança & RBAC:**
1. **Defesa em Profundidade em `SecurityConfigurations.java`:** Além de exigir `@PreAuthorize("@authorizationService.isAdminOrUser()")` (ou `isAdmin()`) em todos os novos controllers/métodos ERP e de SKUs, recomenda-se restringir explicitamente as rotas administrativas novas no `authorizeHttpRequests` (ex.: `.requestMatchers("/erp/**").hasAnyRole("ADMIN", "USER")`), mitigando o risco do `.anyRequest().permitAll()`.
2. **Isolamento de `ROLE_SELLER`:** Conforme `admin-nav.component.ts`, `ROLE_SELLER` acessa apenas *Rotas* e *Alterar Senha*. O backend DEVE rejeitar com HTTP `403 Forbidden` qualquer tentativa de token `ROLE_SELLER` acessar a busca do ERP Atrio, listagem administrativa de produtos ou importação em lote (`P-407`, `P-408`).
3. **Observação Pré-existente (Não Replicar):** Foi identificado que `UserController.getUserByEmail` e `updatePasswordByEmail` usam `@PreAuthorize("@authorizationService.isAuthenticated()")` sem validar ownership (`authentication.getName().equals(email)` ou `isAdmin()`), e que `TokenService` no frontend espelha JWT em `document.cookie` não-HttpOnly. Embora pré-existentes fora do escopo de catálogo, novos endpoints desta feature NÃO devem replicar leitura/escrita por e-mail de terceiros sem validação de role/ownership, e recomenda-se plano posterior de remediação no módulo de usuários/auth.

### 4.2. Segregação de Contratos e DTOs (`GET /products/gallery` vs. Admin)
Na inspeção de `ProductController.java` (linhas 75 e 109) e `ProductService.java` (linhas 77 e 86), observou-se que a listagem administrativa (`GET /products`) e a vitrine pública (`GET /products/gallery`) retornam atualmente o **mesmo DTO (`ProductRes`)** via `productMapper::entityToRes`.

- **Condicionante Arquitetural Bloqueante (`P-408`):**
  Para prevenir vazamento acidental (*Overfetching / Excessive Data Exposure*) na vitrine pública:
  1. `GET /products/gallery` **NÃO PODE** receber campos internos de ERP (`erpCode` / `Id_Pro`, lista `skus` com `erpCode`, `inativo_pro`, `erpMappingStatus`, `codbarra_pro`/EAN interno, `Estoque`, `createdBy`, `updatedBy`).
  2. O Arquiteto DEVE segregar os contratos de resposta na Etapa 2: manter `ProductRes` (ou `ProductGalleryRes`) estritamente público para `GET /products/gallery` e criar um DTO administrativo dedicado (ex.: `ProductAdminRes`) para `GET /products` e `GET /products/{slug}`, ou aplicar Mapper específico (`toPublicGalleryRes` vs `toAdminRes`) com testes de contrato automatizados garantindo que nenhuma chave de ERP apareça no JSON de `/products/gallery`.
  3. As listas `flavours` e `presentation` no DTO público devem ser exclusivamente a projeção atômica, higienizada e deduplicada (`P-401`), garantindo compatibilidade com `ItemCardGalleryComponent` e `ModalGalleryComponent`.

### 4.3. Proteção do `CatalogIndex` e Respostas do Chatbot (`fitoherb-ai`)
Na inspeção de `fitoherb-ai/app/domains/chat/infrastructure/catalog_index.py` e `chat_dto.py`:
- `CatalogIndex.load_from_db()` consulta apenas `products`, `product_categories` e `suppliers` (`id`, `name`, `slug`, `image_path`, `description`, `flavours`, `presentation`).
- `ProductSnippetDto` expõe apenas `name`, `slug`, `image_url`, `category`, `supplier`.
- **Condicionantes Obrigatórias para `fitoherb-ai` (`US-P5`, `P-408`, `P-302`, `P-304`):**
  1. `CatalogIndex` NÃO DEVE consultar `erp_catalog_items`, `product_skus` (para extrair `Id_Pro` ou `inativo_pro`) nem qualquer tabela `users` ou de auditoria.
  2. Nenhum prompt enviado ao Gemini (`ChatOrchestrator`), snippet JSON (`ProductSnippetDto`) ou resposta textual pode conter `Id_Pro`, status de inatividade no ERP, `Estoque` ou dados de fornecedores PF/MEI do ERP.
  3. Caso `CatalogIndex` seja atualizado para enriquecer busca por apresentações/sabores após saneamento `P-401`, deve manter neutralidade absoluta entre fornecedores (`P-304`) e redirecionamento seguro (`P-305`).

---

## 5. Parecer Formal de Enquadramento LGPD e Necessidade de RIPD/DPIA

### 5.1. Bases Legais Aplicadas e Teste de Balanceamento (LIA — Legitimate Interest Assessment)
Para os únicos dados pessoais tangencialmente tocados na operação (dados de operadores administrativos em `users` e campos `created_by`/`updated_by` no PostgreSQL):

1. **Execução de Contrato / Procedimentos Preliminares (Art. 7º, V da LGPD):** Gestão de credenciais e permissões (`ROLE_ADMIN`, `ROLE_USER`) necessárias para que colaboradores autorizados operem o catálogo corporativo.
2. **Legítimo Interesse do Controlador (Art. 7º, IX da LGPD) — Teste de Ponderação (LIA):**
   - **Teste de Finalidade:** Registrar `created_by` e `updated_by` em entidades administrativas (`Product`, `ProductSku`) atende ao interesse legítimo, concreto e transparente da Fitoherb de manter trilha de auditoria contra alterações indevidas ou erros de vínculo SKU × ERP no catálogo.
   - **Teste de Necessidade:** Utiliza exclusivamente o identificador mínimo já presente na sessão autenticada (`AuditorAwareImpl`), sem coleta de dados pessoais adicionais, sem rastreamento comportamental e sem exposição em APIs públicas, `CatalogIndex` ou listas de curadoria.
   - **Teste de Balanceamento e Salvaguardas:** O tratamento ocorre dentro da expectativa razoável do operador administrativo no exercício da sua função; os riscos são mitigados por criptografia em trânsito (TLS), controle de acesso RBAC, proibição de log em texto puro (remediação do `SecurityFilter`) e higienização da tabela `users` ao clonar produção para ambiente local (`P-400`).

### 5.2. Avaliação Formal de Gatilho de RIPD / DPIA (Art. 11 e Art. 20 da LGPD)

| Critério de Gatilho Regulatório (LGPD & Skill `lgpd-privacy-expert`) | Análise Técnica e Jurídica na Feature `product_code_mapping_flavors` | Incidência |
| :--- | :--- | :---: |
| **Tratamento de Dados Pessoais Sensíveis (Art. 5º, II e Art. 11)?** | **Não.** A feature trata exclusivamente metadados de mercadorias/SKUs (códigos `Id_Pro`, EAN, sabores, apresentações, marca). Não há coleta de dados de saúde, biometria, origem racial ou convicções de pessoas naturais. *(O guardrail médico `P-303` no chatbot permanece ativo de forma independente.)* | ❌ **Não incide** |
| **Decisões Automatizadas sobre Titulares Humanos (Art. 20)?** | **Não.** A esteira assistida de matching (`P-409`) e a importação em lote (`P-407`) operam sobre **produtos/SKUs comerciais**, nunca avaliando perfil, crédito ou desempenho de titulares humanos; ademais, qualquer ambiguidade segue para a Fila de Decisão Humana (`HUMAN_REVIEW_QUEUE`). | ❌ **Não incide** |
| **Tratamento de PII em Larga Escala / Alto Risco de Clientes?** | **Não.** A extração da tabela `Clientes`, vendedores e campos pessoais/CPF de `dbo.Fornecedor` do ERP Atrio é expressamente **proibida** na arquitetura (Blocklist na Seção 2.2). | ❌ **Não incide** |

### 5.3. Conclusão Formal sobre RIPD/DPIA e Status do Parecer
- **Decisão quanto ao RIPD/DPIA:** Um **RIPD/DPIA completo de alto risco é DISPENSÁVEL** para esta feature, uma vez que o escopo se limita à governança de catálogo comercial (SKUs × `Id_Pro`) com **eliminação na borda** de qualquer PII existente no ERP (`Clientes`, vendedores e PF/MEI em `dbo.Fornecedor`), ausência de dados sensíveis (Art. 11) e ausência de decisões automatizadas sobre pessoas naturais (Art. 20). Este parecer formal, somado ao LIA resumido e às condicionantes abaixo, supre integralmente o requisito de conformidade da Etapa 2.
- **Cláusula de Reavaliação:** Caso futuras evoluções venham a sincronizar tabelas de `Clientes`, vendedores, notas fiscais de pessoas físicas ou dados pessoais de `dbo.Fornecedor`, a esteira deverá ser bloqueada até a elaboração prévia de um RIPD completo.
- **Status Final do Parecer:** **APROVADO COM CONDICIONANTES OBRIGATÓRIAS** ✅⚠️ — Liberado para conclusão da Etapa 2 (Contratos, DB Schema, Design Plan) e avanço à Etapa 3 **mediante incorporação obrigatória das condicionantes listadas na Seção 6**.

---

## 6. Checklist Obrigatório para as Etapas 2, 3 e 4 (Quality Gate 360)

O Arquiteto, DBA, AI Specialist, Desenvolvedor, Tester, Reviewer e Privacy Officer (na auditoria de código da Etapa 4) deverão comprovar o cumprimento integral dos itens abaixo:

- [ ] **Allowlist Estrita no Conector/Sync ERP (`US-P1`, `Etapa 2/3`):** Queries de extração no SQL Server 2008 R2 (`FITOHERB`) utilizam `SELECT` explícito contendo **apenas** `Id_Pro`, `descricao_pro`, `codbarra_pro`, `inativo_pro`, `Marca.Nome_Marc` (ou `Externo01.Produto.Fornecedor` sanitizado contra CPF/PII) e flag de presença em `Externo01`, com filtro `Empresa_Pro = 1`. Zero `SELECT *`; zero leitura de `Clientes`, vendedores, `dbo.Fornecedor` (CPF/CNPJ/nome civil PF/MEI), `Estoque`, `Pc.Ultimo Custo` ou `Pc.Venda`.
- [ ] **Segregação de DTOs e Proteção da Vitrine Pública (`P-408`):** `GET /products/gallery` retorna DTO estritamente público sem `Id_Pro`/`erpCode`, `skus` internos, `inativo_pro`, `erpMappingStatus`, `EAN` interno, `Estoque`, `createdBy` ou `updatedBy`. Teste de contrato automatizado valida ausência desses campos na resposta da galeria.
- [ ] **Proteção do `CatalogIndex` e Chatbot (`US-P5`, `P-408`):** `CatalogIndex` (`fitoherb-ai`) lê somente campos públicos de `products`, `product_categories` e `suppliers` (`flavours` e `presentation` saneados), sem `JOIN` em `erp_catalog_items`, `product_skus` (para extrair `Id_Pro`) ou `users`.
- [ ] **Remoção de Credencial Hardcoded em `fitoherb-ai`:** Remover a senha literal fallback `"Dm120394"` em `app/domains/chat/infrastructure/catalog_index.py` (linha 81), exigindo configuração via variável de ambiente.
- [ ] **Blindagem de `.gitignore` (`fitoherb-backend-v2`):** Adicionar `.env`, `.env.*` (exceto `.env.example`), `*.sql` (exceto migrations versionadas), `*.dump`, `*.bak` e `fitoherb_backup.sql` ao `.gitignore` antes de qualquer extração/restore local.
- [ ] **Isolamento Prod → Local e Higienização de `users` (`P-400`):** Scripts de curadoria validam explicitamente host `localhost`/`127.0.0.1` antes de escrita; tabela `users` é higienizada pós-restore local e **nunca** é exportada em logs ou arquivos da `HUMAN_REVIEW_QUEUE`; `fitoherb_backup.sql` é removido localmente após restauração e nunca commitado.
- [ ] **RBAC Fail-Safe nos Novos Endpoints (`P-407`, `P-408`):** Todos os novos endpoints administrativos/ERP possuem `@PreAuthorize("@authorizationService.isAdminOrUser()")` (ou `isAdmin()` para sync/backfill) **e** proteção correspondente em `SecurityConfigurations.java`, com testes garantindo `401` para anônimo e `403` para `ROLE_SELLER`.
- [ ] **Zero PII em Logs e Tratamento de Exceções Sanitizado (`Etapa 3/4`):** Nenhum novo controller, service, script ou interceptor loga e-mails (`users`, `created_by`), tokens JWT, credenciais SQL Server ou stacktraces em produção; remover/sanitizar `System.out.println("Token validated, email: " + email)` em `SecurityFilter.java:34`.
- [ ] **Pesquisa Web Livre de PII (`P-409`):** Rotina de pesquisa web na curadoria utiliza apenas termos de produto/marca/EAN, nunca enviando nomes civis/CPFs de `dbo.Fornecedor` ou dados de operadores.

---

## 7. Adendo Etapa 2 — Auditoria Privacy by Design & SecOps (Onda 4: `US-P7` e `US-P8` · `P-406`, `P-410` a `P-413`)

**Escopo Incremental Auditado:** Sincronização diária agendada ERP ↔ Site (`P-410`), governança automática de visibilidade e inativação parcial Multi-SKU (`P-406`, `P-411`), publicação imediata sem foto com fallback visual (`P-412`) e Central de Curadoria Rápida com descarte auditável (`P-413`).  
**Status do Adendo:** **APROVADO COM CONDICIONANTES OBRIGATÓRIAS** ✅⚠️

### 7.1. Minimização Contínua (`A1`) e Allowlist Estrita na Sincronização Diária (`US-P7` / `P-410`–`P-412`)

1. **Allowlist Imutável no SQL Server 2008 R2 (`FITOHERB`):** Toda consulta diária executada por `@Scheduled` ou `POST /erp-products/sync/daily` DEVE reutilizar a Allowlist estrita via `ErpCatalogGateway` em modo somente-leitura (`Empresa_Pro = 1`), vetando `SELECT *`, `Clientes`, vendedores, `dbo.Fornecedor`, `Estoque`, custos e preços, com credencial SQL Server dedicada restrita a `SELECT`.
2. **Zero Espelho Permanente no PostgreSQL (`A1`):** Nenhuma tabela espelho de descrições do catálogo ERP permanece no PostgreSQL. Ficam apenas os atributos de governança (`products.active`, `products.curation_status`, `product_skus.erp_inactive`, `product_skus.erp_last_verified_at`) e as tabelas operacionais enxutas `erp_sync_state`, `erp_sync_runs` e `erp_ignored_catalog_codes`.
3. **Processamento Determinístico (0 Tokens LLM):** Higienização e mapeamento categoria/fornecedor operam 100% deterministicamente, sem enviar dados brutos do ERP a serviços de IA externos.

### 7.2. Autenticação Segura M2M: `CloudSchedulerSyncTrigger` e Webhook `fitoherb-ai`

> [!CAUTION]
> Ambos os serviços (`fitoherb-backend-v2` e `fitoherb-ai`) fazem deploy com `--allow-unauthenticated` no Cloud Run e `SecurityConfigurations.java` usa `.anyRequest().permitAll()`, enquanto `fitoherb-ai` aceita `"*"` em `BACKEND_CORS_ORIGINS`.

| Fluxo / Endpoint M2M | Mecanismo Obrigatório (Secret Manager + Header) | Comparação Constant-Time | Fail-Closed & Hardening |
| :--- | :--- | :--- | :--- |
| **`POST /erp-products/sync/daily`** (`fitoherb-backend-v2`) | Header `X-Sync-Scheduler-Token` (`SYNC_SCHEDULER_TOKEN` em Secret Manager) validado por filtro dedicado antes da autorização HTTP (sem conflitar com `SecurityFilter` de JWT Auth0) **ou** sessão JWT com `ROLE_ADMIN`. | `java.security.MessageDigest.isEqual(...)` (UTF-8), checando null/blank antes. | **Fail-Closed:** Se `SYNC_SCHEDULER_TOKEN` ausente/vazio, rejeitar toda requisição M2M (`401`/`503`); proibido default literal. |
| **`POST /api/v1/chat/catalog/refresh`** (`fitoherb-ai`) | Header `X-Internal-Refresh-Token` (`INTERNAL_REFRESH_TOKEN` em Secret Manager). | `hmac.compare_digest(...)` (Python `hmac`). | **Fail-Closed:** Se `INTERNAL_REFRESH_TOKEN` ausente/vazio, rejeitar (`503 REFRESH_TOKEN_NOT_CONFIGURED`); não vazar `str(exc)` de DB. |

- **Veto Absoluto a Tokens em Query String (`?token=...`)** e **Independência de CORS** (validação 100% server-side).
- **Defesa em Profundidade no `SecurityConfigurations.java`:** Regras `requestMatchers` explícitas para `/erp-products/**`, `/erp-products/curation-pending/**` (`hasAnyRole("ADMIN", "USER")`), `/erp-products/sync` (`hasRole("ADMIN")`) e `/erp-products/sync/daily` (`hasAnyRole("ADMIN", "SYNC_SCHEDULER")`).

### 7.3. Auditoria de PII, Bases Legais, Logs, Relatório por E-mail (`ERP_SYNC_REPORT_EMAIL`) e Retenção (`erp_sync_runs.triggered_by` e `erp_ignored_catalog_codes.ignored_by`)

| Campo / Coluna | Classificação LGPD | Base Legal (Art. 7º) | Finalidade & Retenção |
| :--- | :--- | :--- | :--- |
| `erp_sync_runs.triggered_by` | Identificador Técnico (`"SYSTEM_SCHEDULED"`/`"CLOUD_SCHEDULER"`) ou Operador (`ROLE_ADMIN`) | **Art. 7º, V e IX** (LIA) | Auditabilidade de disparos manuais/agendados. **Retenção máxima de 90 dias** (expurgo/anonimização mantendo sempre o último `'SUCCESS'`). |
| `erp_ignored_catalog_codes.ignored_by` | Operador Interno (`ROLE_USER`/`ROLE_ADMIN`) ou `"SYSTEM_BASELINE"` | **Art. 7º, V e IX** (LIA) | Autoria do descarte (*"Ignorar / Não exibir no site"*). Anonimizar referência pessoal no desligamento/após 12 meses mantendo o bloqueio do `erp_code`. |
| `app.erp.sync.report-email` (`ERP_SYNC_REPORT_EMAIL`) | Dado Pessoal de Destinatário Operacional (E-mail Corporativo/Operador) | **Art. 7º, V e IX** (Execução de Contrato / Legítimo Interesse) | Envio *best-effort* do relatório diário pós-sync (08:00 BRT) via `MailService`. **Proibido hardcode** em código ou docs versionados (apenas `.env` local gitignored e secret `ERP_SYNC_REPORT_EMAIL` em prod); proibido logar o endereço de e-mail em caso de sucesso ou falha SMTP. |
| `erp_sync_runs.error_summary` | Telemetria Técnica Sanitizada (`VARCHAR(500)`) | Não aplicável | Proibido gravar stacktrace, strings JDBC, senhas ou PII. |

- **Proibição em Logs, Código Versionado e DTOs Públicos:** `triggered_by`, `ignored_by` e `ERP_SYNC_REPORT_EMAIL` nunca aparecem em `ProductRes`, `CatalogIndex`, respostas HTTP públicas, documentos versionados nem logs em texto puro (`SecurityFilter.java:34` deve ser corrigido). O conteúdo do e-mail de relatório contém exclusivamente contadores e metadados comerciais de produtos (`Id_Pro`, nome, pendência de foto), sem PII de titulares. Scripts locais de sanitização Pós-Restore também sobrescrevem `triggered_by`/`ignored_by` com `"LOCAL_SANITIZED"`.

### 7.4. RBAC & Veredicto RIPD/DPIA Atualizado

| Recurso Novo (`US-P7` / `US-P8`) | Anônimo | `ROLE_SELLER` | `ROLE_USER` | `ROLE_ADMIN` | M2M Secret |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Vitrine Pública (`GET /products/gallery`, `active=true`) & `CatalogIndex` | ✅ | ✅ | ✅ | ✅ | N/A |
| Curadoria Rápida (`GET /erp-products/curation-pending` & `ignore`) | ❌ `401` | ❌ `403` | ✅ | ✅ | N/A |
| Sync Diário (`POST /erp-products/sync/daily`) | ❌ `401` | ❌ `403` | ❌ `403` | ✅ | ✅ `X-Sync-Scheduler-Token` |
| Refresh `fitoherb-ai` (`POST /api/v1/chat/catalog/refresh`) | ❌ `401` | ❌ `401`/`403` | ❌ `401`/`403` | ❌ | ✅ `X-Internal-Refresh-Token` |

- **Veredicto RIPD/DPIA:** Permanece **DISPENSÁVEL** (nenhum dado sensível Art. 11, nenhuma decisão automatizada sobre titular humano Art. 20, veto completo na origem a `Clientes`/vendedores/`dbo.Fornecedor`). **Status Onda 4: APROVADO COM CONDICIONANTES OBRIGATÓRIAS.**

### 7.5. Checklist Incremental Obrigatório — Quality Gate 360 (`US-P7` e `US-P8`)
- [ ] (`A1`, `P-410`) Allowlist contínua no SQL Server e zero espelho permanente do catálogo ERP no PostgreSQL.
- [ ] (`P-410`, SecOps) `POST /erp-products/sync/daily` e `POST /api/v1/chat/catalog/refresh` protegidos por headers dedicados (`X-Sync-Scheduler-Token` / `X-Internal-Refresh-Token`), `MessageDigest.isEqual` / `hmac.compare_digest` e comportamento *fail-closed*; zero tokens em query string ou defaults literais.
- [ ] (`P-410`, `P-413`) Zero PII/e-mail de operador em logs de aplicação; retenção de **90 dias** em `erp_sync_runs`; `triggered_by`/`ignored_by` ausentes da vitrine e do `CatalogIndex`.
- [ ] (`P-408`, `P-411`, `P-413`) Vitrine pública e `CatalogIndex` filtram `active = true`; endpoints de Curadoria Rápida e descarte auditável retornam `401` para anônimo e `403` para `ROLE_SELLER`, reforçados via `SecurityConfigurations.java`.
- [ ] (`Saneamento`) Remoção de `"Dm120394"` (`catalog_index.py:81`), remoção do `System.out.println` em `SecurityFilter.java:34` e não exposição de `str(exc)` em `chat_router.py:34`.
