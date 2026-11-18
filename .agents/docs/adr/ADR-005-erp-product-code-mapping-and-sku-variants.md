# ADR-005: Integração Espelhada com ERP Atrio, Modelagem Multi-SKU (`ProductSku`), Segregação Admin/Vitrine e Rollout Seguro

> **Status:** Aprovado no Checkpoint com Diretriz `A1`–`A4` (Refatorado após prova empírica Java 21 × SQL Server 2008 R2)  
> **Data:** 2026-11-18  
> **Autor:** Arquiteto (`architect.md`)  
> **Localização Mandatória:** `.agents/docs/adr/ADR-005-erp-product-code-mapping-and-sku-variants.md`

---

## 1. Contexto do Problema

O catálogo do ecossistema Fitoherb (`fitoherb-backend-v2`, `fitoherb-frontend-v2` e `fitoherb-ai`) possui atualmente **1.040 produtos** armazenados em PostgreSQL (`products` com arrays `TEXT[]` em `flavours` e `presentation`), sem vínculo com o identificador oficial **`Id_Pro`** do **ERP Atrio** (SQL Server 2008 R2, base `FITOHERB`, tabelas `[dbo].[Produtos]` com 6.946 registros e view `[Externo01].[Produto]` com 2.194 registros para `Empresa_Pro = 1`).

Levantamentos técnicos e de negócio (`P-400` a `P-409`) evidenciaram cinco desafios arquiteturais críticos:

1. **Conectividade Cloud Run × SQL Server 2008 R2 Legado:** `fitoherb-backend-v2` executa em Google Cloud Run (Java 21 `eclipse-temurin:21-jre-alpine`, Spring Boot `4.0.5`, HikariCP limitado a `maximum-pool-size=3` no Supabase em `application-prod.properties`), enquanto o ERP Atrio roda on-premise atrás de DDNS sobre SQL Server 2008 R2 (que tipicamente negocia TLS 1.0/1.1 legado, desabilitado por padrão no Java 21).
2. **Granularidade 1:1 de SKUs e Listas Legadas Concatenadas:** No ERP Atrio, cada combinação física de produto, sabor e/ou apresentação possui seu próprio `Id_Pro` (`100% Pure Whey 900g` = 3 SKUs; `B.O.P.E` = matriz `150g`/`300g` × 3 sabores; `Stevita Líquido` = `25ml`/`60ml`; 865 produtos simples). Entretanto, 90 produtos possuem `flavours` e 87 possuem `presentation` concatenados em texto livre (ex.: `{"Baunilha","Chocolate e Morango."}`, `{"25ml e 60ml."}`).
3. **Preservação de Leitores Públicos e do `CatalogIndex` (`fitoherb-ai`):** A vitrine pública (`GET /products/gallery`, `ItemCardGalleryComponent`, `ModalGalleryComponent`) e `CatalogIndex` (`fitoherb-ai/app/domains/chat/infrastructure/catalog_index.py`, via SQL direto em `products`) dependem de `products.flavours` e `products.presentation` limpos e deduplicados, e NÃO podem receber `Id_Pro`, `inativo_pro` ou `Estoque` (`P-302`, `P-408`).
4. **Falhas de Semântica HTTP e Mascaramento de Erros:** `ProductService.updateProductBySlug` captura `Exception` genérica convertendo violações de integridade/conflito em `DatabaseOperationException` (HTTP `500`), e `AdminComponent.handleSave` substitui qualquer HTTP `409` por mensagem fixa de conflito de nome/fornecedor.
5. **Risco de Rollout em Produção e Curadoria Sem Suposições:** `698` itens de `[Externo01].[Produto]` têm `inativo_pro = 1` em `[dbo].[Produtos]`, marcas diferem nominalmente (ex.: `Arrebite` no site vs `GUARANAPIS` no ERP) e ativar `NOT NULL` em produção antes da curadoria local dos 1.040 produtos paralisaria operações do `/admin`.

---

## 2. Decisões Arquiteturais

### 2.1. Decisão 1 — Espelho Temporário Apenas no Clone/Sync (`A1`) + Consulta Somente-Leitura em Runtime ao SQL Server via jTDS (`ssl=off`) + Cache em Memória RAM

Em estrito cumprimento à diretriz do Usuário no Checkpoint (`A1`: usar espelho apenas para clonar/sincronizar na curadoria e **remover qualquer tabela de catálogo ERP do PostgreSQL do site depois**):

- **Separação de Ciclo de Vida (Curadoria Temporária vs. Runtime Definitivo):**
  1. **Janela Local de Clonagem e Curadoria (`US-P1`):** As tabelas de apoio (`erp_catalog_items_staging`, `human_review_queue_staging`, `erp_mapping_audit_staging`, `supplier_brand_aliases_staging`) são criadas **exclusivamente no PostgreSQL local (`fitoherb-v2`)** durante a execução da curadoria zero-chutes e **removidas explicitamente (`DROP TABLE`) ao término do mapeamento**. Nenhuma tabela espelho do catálogo ERP permanece no PostgreSQL local após a curadoria nem é criada no Supabase de produção.
  2. **Runtime Definitivo (`fitoherb-backend-v2` — Local, QA e Cloud Run):** Sem espelho persistido no PostgreSQL do site, o backend consulta o **SQL Server 2008 R2 (`FITOHERB`) diretamente em modo somente leitura (`WITH (NOLOCK)`, `PreparedStatement`, projeção restrita à Allowlist)** por meio da interface `ErpCatalogGateway`, alimentando um **cache snapshot em memória RAM com TTL curto** (`AtomicReference<ErpCatalogSnapshot>`, ~2 MB para 6.946 itens, TTL padrão `15 min`) e lookup pontual complementar (`WHERE p.Id_Pro = ?`) em caso de miss no cache quente.
  3. **Aliases de Marca e Flags de Inatividade:** Aliases de fabricante (ex.: `Arrebite` ↔ `GUARANAPIS`) passam a residir em configuração versionada (`BrandAliasRegistry` / YAML), e cada vínculo em `product_skus` persiste seu próprio estado mínimo (`erp_code`, `erp_inactive`, `erp_inactive_confirmed`, `erp_last_verified_at`), eliminando dependência de joins com tabelas ERP no PostgreSQL.
  4. **Falha Segura (`Fail-Closed`):** Se `FITOHERB` estiver inacessível quando o cache RAM ainda estiver frio (vazio), operações que exigem validação ERP lançam `ServiceUnavailableException` (**HTTP `503 Service Unavailable`**, `P-403`). `POST /erp-products/sync` (`ROLE_ADMIN`) força o reload do snapshot em RAM e revalida flags `erp_inactive` nos `product_skus` existentes.

**Descoberta Empírica e Justificativa Técnica / FinOps / SecOps (Java 21 × SQL Server 2008 R2):**
- **Por que `net.sourceforge.jtds:jtds:1.3.1` (`ssl=off`) em vez de `mssql-jdbc`:** Provas empíricas em Java 21 (Temurin 21) contra `FITOHERB` (`10.50.1600`) comprovaram que o servidor negocia Prelogin TDS `ENCRYPT_OFF (Login Only)` selecionando `TLS 1.0`, o que leva `mssql-jdbc:12.8.1` (inclusive com `encrypt=false`) a falhar com `TLS10 is not accepted by client preferences [TLS13, TLS12]`. Já `jtds:1.3.1` com `ssl=off` conecta com sucesso em Java 21, executa `PreparedStatement` parametrizado e decodifica acentuação PT-BR (`Ã`, `Ç`, `Ú`) **sem alterar `jdk.tls.disabledAlgorithms` da JVM** (mantendo TLS 1.2/1.3 rígido para GCS, SMTP, Supabase e `fitoherb-ai`).
- **Mitigação de Risco do Driver Legado / DDNS (`ssl=off`):** Como `jtds` em `ssl=off` não cifra o pacote Login7 em trânsito, o `ErpCatalogGateway` **DEVE** autenticar-se com uma credencial SQL Server **dedicada exclusivamente `SELECT`** apenas nas tabelas/colunas da Allowlist (`dbo.Produtos`, `dbo.Marca`, `dbo.TipoProd`, `Externo01.Produto`), nunca utilizando usuário administrativo (`sa`) nem tendo permissão em `Clientes`, `dbo.Fornecedor`, `Estoque` ou tabelas financeiras (`P-302`, `P-408`), isolada atrás da interface para futura troca direta para `mssql-jdbc` quando o SQL Server ou túnel VPN for modernizado.
- **FinOps & Pool Supabase:** Evita bloat de 6.946+ linhas e índices trigram GIN no Supabase free-tier, evita segundo pool HikariCP no PostgreSQL (preservando `maximum-pool-size=3`) e usa conexões curtas sob demanda apenas na renovação do snapshot RAM.

---

### 2.2. Decisão 2 — Modelagem Normalizada `Product` (1) ↔ `ProductSku` (N) com Projeção Saneada e Deduplicada em `products`

Evoluir o domínio de catálogo mantendo `products.flavours` e `products.presentation` (`TEXT[]`) como projeção sincronizada a partir da nova entidade normalizada `ProductSku` (`product_skus`):

- **Entidade `ProductSku` (`@Table(name = "product_skus")`):**
  - `id` (`String` UUID, `GenerationType.UUID`, padrão do projeto).
  - `product` (`@ManyToOne(fetch = FetchType.LAZY)`, FK `product_id` → `products.id`).
  - `erpCode` (`Long`, coluna `erp_code BIGINT`, constraint global única `uk_product_skus_erp_code` — `NOT NULL` ativado na Fase 4 pós-backfill).
  - `flavour` (`String`, `VARCHAR(120)`, nullable — texto atômico saneado para exibição).
  - `flavourNormalized` (`String`, `VARCHAR(120)`, nullable — lowercase sem acentos/espaços para chave de unicidade interna).
  - `presentation` (`String`, `VARCHAR(120)`, nullable — texto atômico saneado para exibição).
  - `presentationNormalized` (`String`, `VARCHAR(120)`, nullable — lowercase sem acentos/espaços para chave de unicidade interna).
  - `ean` (`String`, `VARCHAR(20)`, nullable — código de barras técnico do ERP).
  - `sortOrder` (`Integer`, `NOT NULL`, preserva ordem de exibição/cadastro).
  - `erpInactive` (`Boolean`, `NOT NULL DEFAULT false`, espelha `inativo_pro` verificado na última consulta ERP).
  - `erpInactiveConfirmed` (`Boolean`, `NOT NULL DEFAULT false`, registra aceite explícito de `inativo_pro = 1` conforme `P-406`).
  - `erpLastVerifiedAt` (`LocalDateTime`, timestamp da última verificação direta contra o catálogo ERP em RAM/SQL Server).
  - Auditoria padrão via `AuditingEntityListener` (`created_at`, `updated_at`, `created_by`, `updated_by`).
  - Índice único funcional interno por produto em `(product_id, COALESCE(flavour_normalized, ''), COALESCE(presentation_normalized, ''))` (`P-404`).

- **Validação Estrutural das 4 Topologias (`ProductTopology`, `P-405`):**
  Um `Product` DEVE possuir `>= 1` `ProductSku` e enquadrar-se estritamente em uma única topologia:
  1. `SIMPLE`: exatamente `1` SKU com `flavour = null` e `presentation = null`.
  2. `FLAVOUR_ONLY`: `>= 1` SKUs onde todos têm `flavour != null` e `presentation = null`.
  3. `PRESENTATION_ONLY`: `>= 1` SKUs onde todos têm `flavour = null` e `presentation != null`.
  4. `MATRIX`: `>= 1` SKUs onde todos têm `flavour != null` e `presentation != null` (admitindo matriz esparsa).
  Misturas entre topologias ou lista vazia são rejeitadas com **HTTP `422 Unprocessable Entity`** (`code: "PRODUCT_TOPOLOGY_INVALID"`).

- **Saneamento Atômico (`ProductVariantSanitizer`) e Projeção Deduplicada (`P-401`):**
  - Todo `flavour` e `presentation` passa por normalização (`trim`, colapso de espaços múltiplos, remoção de ponto final residual `.` e rejeição de itens vazios/apenas pontuação com **HTTP `400 Bad Request`**).
  - Na persistência (`POST` / `PUT`) e no script de saneamento legado (`US-P1`), `products.flavours` e `products.presentation` são recalculados atomicamente a partir dos SKUs ordenados por `sortOrder` usando `LinkedHashSet` (garantindo ausência de duplicatas na matriz `B.O.P.E` `150g`/`300g` × 3 sabores e preservando 100% de compatibilidade com `ItemCardGalleryComponent`, `ModalGalleryComponent` e `CatalogIndex`).

- **Reconciliação Atômica no `PUT /products/{slug}` (`P-404`, `C-05`):**
  - Como `product_skus.erp_code` possui `UNIQUE` global, a troca de códigos entre dois sabores do mesmo produto (ex.: `Baunilha 131476 ↔ Chocolate 131477`) dentro de um único `PUT` falharia em Hibernate se novos `INSERT`s ocorressem antes dos `DELETE`s no flush da sessão JPA.
  - Portanto, `ProductService.updateProductBySlug` executará **reconciliação atômica em duas fases** dentro da `@Transactional`: (1) validar globalmente que nenhum `erpCode` pertence a **outro** `product_id != currentProduct.id` (`409 Conflict` antes de mutar); (2) remover SKUs órfãos/substituídos e invocar `entityManager.flush()` antes de gravar/reassociar os novos `erpCode`s (ou atualizar em memória via *in-place update* quando a chave normalizada coincidir, usando troca temporária segura quando houver permuta cruzada).

---

### 2.3. Decisão 3 — Segregação Vitrine × Admin (`ProductRes` vs `ProductAdminRes`), Contratos `/products` vs `/erp-products/**` e Correção de Exceções

1. **Segregação Estrita de DTOs de Resposta (`P-408`):**
   - **`ProductRes` (Público):** Mantido intacto (`name`, `imageUrl`, `description`, `flavours`, `presentation`, `slug`, `category`, `supplier`, `createdAt`). Retornado exclusivamente por `GET /products/gallery` (rota pública, sem `@PreAuthorize`), utilizando `ProductMapper.entityToPublicRes(Product)` sem tocar em `product_skus` (zero overfetching, zero N+1 e impossibilidade estrutural de vazar `erpCode`, `inativo_pro`, `createdBy` ou `Estoque`).
   - **`ProductAdminRes` (Administrativo):** Novo DTO exclusivo para `GET /products` e `GET /products/{slug}` (ambos sob `@PreAuthorize("@authorizationService.isAdminOrUser()")`). Estende/espelha os dados de `ProductRes` acrescidos de `topology`, `erpStatus` (`UNMAPPED` | `COMPLETE` | `INACTIVE_ALERT`), `skuCount`, `primaryErpCode` e `skus: List<ProductSkuRes>`.
   - **`CatalogIndex` (`fitoherb-ai`):** Continua consultando apenas `products`, `product_categories` e `suppliers` (jamais `product_skus` ou `erp_catalog_items`), com melhoria opcional em `CatalogIndex.search()` para dar peso explícito também a tokens de `presentation` (`P-304`, `P-305`, `P-408`).

2. **Padronização de Contratos e Envelope `data` / `meta`:**
   - **Novos endpoints (`ErpProductController` em `/erp-products/**`):** Adotam estritamente o envelope canônico `{"data": ..., "meta": ...}` (`ApiEnvelope<T>`) exigido por `.agents/rules/backend-api-contract-rules.md` e `api-contract-expert`. Protegidos por `@PreAuthorize("@authorizationService.isAdminOrUser()")` (`search`, `/{erpCode}`, `suggest-variants`) e `@PreAuthorize("@authorizationService.isAdmin()")` (`sync`).
   - **Endpoints existentes em `ProductController` (`/products`, `/products/gallery`, `/products/{slug}`):** Mantêm retrocompatibilidade estrutural de envelope com o ecossistema existente (`Page<ProductRes>` em `/products/gallery`, `Page<ProductAdminRes>` em `/products`, `201 Created` + `Location` em `POST /products`, `200 OK` vazio em `PUT`/`DELETE`, conforme `CRUD-004`/`CRUD-005` e `GalleryComponent`/`AdminComponent`), evitando regressão nos contratos públicos e testes existentes.
   - **Busca Admin por `erpCode` e Filtro `erpStatus`:** `GET /products` ganha filtro opcional `erpStatus` (`List<ErpMappingStatus>`) e amplia `search` (exclusivamente no fluxo admin, via `Specification` com `EXISTS` em `product_skus`) para localizar produtos por `erpCode` sem duplicar linhas paginadas.

3. **Correção do Fluxo de Exceções (`P-403`, `P-404`, `P-406`):**
   - **Remoção do `try { ... } catch (Exception e)` genérico em `ProductService.updateProductBySlug`:** Exceções de domínio (`ResourceAlreadyExistsException`, `ResourceNotFoundException`, `UnprocessableEntityException`, `ServiceUnavailableException`) e `DataIntegrityViolationException` devem propagar diretamente até `RestExceptionHandler`, eliminando o mascaramento de `409 Conflict` como HTTP `500` (`C-16`).
   - **Evolução Retrocompatível de `RestErrorMessage`:** Inclusão dos campos opcionais `@JsonInclude(NON_NULL)` `code` (`String`) e `details` (`Map<String, Object>`), preservando o construtor atual `(HttpStatus, String)`.
   - **Novos Handlers no `RestExceptionHandler`:**
     - `UnprocessableEntityException` → HTTP `422 Unprocessable Entity` (cobrindo `ERP_CODE_NOT_FOUND`, `ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED`, `PRODUCT_TOPOLOGY_INVALID`, `DUPLICATE_ERP_CODE_IN_PAYLOAD`, `DUPLICATE_VARIANT_COMBINATION`).
     - `ServiceUnavailableException` → HTTP `503 Service Unavailable` (`ERP_CATALOG_UNAVAILABLE`).
     - `DataIntegrityViolationException` → HTTP `409 Conflict` com inspeção de constraint (`uk_product_skus_erp_code`, `uk_products_slug`) para fallback legível em condição de corrida.
   - **Frontend (`AdminComponent.handleSave`):** Remover sobrescrita fixa de HTTP `409`; renderizar `err.error?.message` e tratar `err.status === 422 && err.error?.code === 'ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED'` exibindo diálogo explícito para reenvio com `allowInactiveErp = true`.

---

### 2.4. Decisão 4 — Estratégia de Rollout em Fases (Prod → Local → Curadoria Zero-Chutes → Prod)

Executar o rollout em **4 fases controladas** para garantir zero perda de dados, zero suposições e nenhuma interrupção operacional:

1. **Fase 1 — Clonagem Segura Prod → Local (`P-400`):**
   - Executar `.github/workflows/backup.yml` (`pg_dump --clean --if-exists --inserts`) para gerar `fitoherb_backup.sql`.
   - Antes de restaurar no PostgreSQL local `fitoherb-v2`, gerar snapshot local prévio e validar trava de host (`localhost` / `127.0.0.1` apenas), preservando os **1.040 produtos, 6 categorias e 44 fornecedores**.
2. **Fase 2 — Espelhamento Temporário ERP + Saneamento + Curadoria Zero-Chutes Local + Limpeza (`P-401`, `P-409`, `A1`, `A2`):**
   - Criar tabelas temporárias de staging exclusivamente no PostgreSQL local (`erp_catalog_items_staging`, `supplier_brand_aliases_staging`, `human_review_queue_staging`, `erp_mapping_audit_staging`) com snapshot de `[dbo].[Produtos]` + `[Externo01].[Produto]` (`Empresa_Pro = 1`).
   - Executar pipeline Python determinístico de saneamento (`flavours`/`presentation`) e matching em 3 níveis:
     - *Nível 1 (`AUTO_EXACT`):* Match determinístico inequívoco com aliases de marca (`Arrebite` ↔ `GUARANAPIS`) e dicionário controlado de abreviações (`CHOCO`, `CAPSGEL`, `DISP.`, `STAND UP`, gramaturas/volumes) **somente quando o candidato no ERP estiver ativo (`inativo_pro = 0`)**.
     - *Nível 2 (`WEB_VERIFIED`):* Pesquisa externa em catálogos oficiais / EAN para desambiguação documental auditável.
     - *Nível 3 (`HUMAN_REVIEW_QUEUE` + `INACTIVE_MATCH_ALERTS`, `A2`, `A4`):* Qualquer item sem match, com múltiplos candidatos, conflito de embalagem (`UN` vs `DISP.` / `CX`) ou cujo vínculo provável seja um item inativo (`inativo_pro = 1`) **não** é vinculado silenciosamente; é separado em lista/fila explícita para decisão do Usuário. **Zero chutes.**
   - Após gravação e validação dos `product_skus` locais curados, executar **`DROP TABLE`** das tabelas temporárias ERP/staging no `fitoherb-v2` local (`A1`), mantendo em PostgreSQL exclusivamente as tabelas de catálogo do site (`products` + `product_skus`).
3. **Fase 3 — Pacote Idempotente de Promoção para Produção (`US-P6`):**
   - Exportar apenas a DDL limpa de `product_skus` + backfill curado (`products` saneado e `product_skus`) em script SQL 100% **idempotente** (`ON CONFLICT DO NOTHING` / checagem prévia de vínculos já existentes), sem criar tabelas de catálogo ERP no Supabase de produção.
4. **Fase 4 — Ativação Gradual de Travas Rígidas:**
   - Criar `product_skus` inicialmente permitindo `erp_code` nullable durante o backfill em produção (`app.erp.strict-sku-required=true|false`).
   - Somente após validação `SELECT COUNT(*) FROM product_skus WHERE erp_code IS NULL` = `0` e `0` produtos sem SKU no banco alvo (`A3`), aplicar `ALTER TABLE product_skus ALTER COLUMN erp_code SET NOT NULL`.

---

### 2.5. Governança de Documentação OpenAPI 3 / Swagger e Padrão de Comentários em Código

- **Swagger / OpenAPI 3 (`springboot-swagger`):**
  - Novos controllers (`ErpProductController`) e alterações em `ProductController` DEVEM conter `@Tag`, `@Operation(summary, description)` e `@ApiResponses` completos (`200`/`201`, `400`, `401`, `403`, `404`, `409`, `422`, `503`) com `@ExampleObject` aderente ao envelope real.
  - Todos os DTOs (`ProductReq`, `ProductSkuReq`, `ProductAdminRes`, `ProductSkuRes`, `ErpCatalogItemRes`, `SuggestVariantsReq`, `SuggestVariantsRes`, `SyncErpCatalogReq`, `ApiEnvelope`) DEVEM declarar `@Schema(description, example, requiredMode)`.
- **Padrão de Comentários / Docstrings:**
  - **Java:** Javadoc conciso em classes públicas, serviços e métodos de reconciliação/validação, explicando o *porquê* de invariantes (ex.: flush intermediário antes da re-inserção de SKUs em permutas no `PUT`, referência a `P-40X`).
  - **Python (`fitoherb-ai` e scripts de dados):** Type hints PEP 484 obrigatórios e docstrings padrão Google em funções/classes públicas.
  - **TypeScript (`fitoherb-frontend-v2`):** JSDoc nas interfaces exportadas, serviços (`ErpProductsService`, `ProductsService`) e métodos de estado reativo (Signals).

---

### 2.6. Decisões Consolidadas no Checkpoint (`A1`–`A4`)

| Dúvida | Decisão Homologada pelo Usuário (`A1`–`A4`) | Implementação Resultante |
| :--- | :--- | :--- |
| **Q-01 (`A1`)** | Espelho PostgreSQL **apenas temporário** para clonar/sincronizar na curadoria, sendo **removido do PostgreSQL depois**. | Tabelas de staging ERP usadas só localmente em `US-P1` e removidas (`DROP TABLE`) ao final; runtime consulta SQL Server via `ErpSqlServerGateway` (`jtds:1.3.1` `ssl=off`) + cache em RAM (~2 MB, TTL 15 min) + `POST /erp-products/sync` para refresh em memória. |
| **Q-02 (`A2`)** | Na curadoria, separar lista explícita e avisar caso algum produto vá se vincular a `inativo_pro = 1`. | Na curadoria `US-P1`: nenhum match apenas-inativo é gravado sem aval (`INACTIVE_MATCH_ALERTS`). Em runtime: `422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED` -> confirmação explícita com `allowInactiveErp = true`. |
| **Q-03 / Q-04 (`A3`)** | Todos os produtos do site em teoria estão ativos; concluir curadoria e avisar pendências antes de ativar trava estrita. | Rollout progressivo com lista explícita de não-mapeados/inativos ao usuário antes de `ALTER TABLE product_skus ALTER COLUMN erp_code SET NOT NULL`. |
| **Q-05 / Q-06 (`A4`)** | Código direto em simples / badge `N SKUs · código` + popover Multi-SKU; `UN` vs `DISP.`/`CX` sem chutes na fila humana. | Popover `position: fixed` na tabela `/admin` (`DynamicTableComponent`) + `packageWarning` na importação em lote + `HUMAN_REVIEW_QUEUE`. |

---

## 3. Alternativas Consideradas

1. **Manter tabela espelho `erp_catalog_items` permanentemente no PostgreSQL de Produção (Decisão 1 — Rejeitada em `A1`):**
   - *Motivo de descarte:* O Usuário solicitou explicitamente remover o espelho ERP do banco PostgreSQL do site após a clonagem e sincronização inicial (`A1`), evitando acúmulo de tabelas e espaço no Supabase.
2. **Driver `mssql-jdbc` direto no Java 21 (Decisão 1 — Inviável sem rebaixar TLS da JVM):**
   - *Motivo de descarte:* Empiricamente comprovado em Java 21 que o SQL Server 2008 R2 (`FITOHERB`) negocia `TLSv1.0` no Login7 e `mssql-jdbc:12.8.1` aborta o handshake. Adotou-se `jtds:1.3.1` (`ssl=off`) isolado atrás de `ErpCatalogGateway` com credencial `SELECT`-only.
3. **Armazenar SKUs e `erpCode` em coluna `JSONB` dentro de `products` sem tabela `product_skus` (Decisão 2):**
   - *Motivo de descarte:* Impede `UNIQUE CONSTRAINT` nativa simples de `erp_code` em nível relacional (`P-404`), dificulta queries/filtros performáticos por `erp_code` e `INACTIVE_ALERT` (`P-408`) e viola normalização de banco para integridade 1:1 com ERP.
4. **Unificar `ProductRes` com campos opcionais ERP para Vitrine e Admin (Decisão 3):**
   - *Motivo de descarte:* Cria risco permanente de vazamento acidental de `erpCode`/`inativoPro` na rota pública `GET /products/gallery` (`P-408`) e força joins desnecessários com `product_skus` na vitrine pública.
5. **Alterar imediatamente `GET /products/gallery` para novo envelope `{data, meta}` sem compatibilidade (Decisão 3):**
   - *Motivo de descarte:* Quebra consumidores existentes de `PageResponse<T>` (`GalleryComponent` e `ProductsService.getProductsBySupplier`); padronizou-se `{data, meta}` obrigatoriamente em todo novo endpoint (`/erp-products/**`) preservando `Page<T>` apenas nos endpoints legados de `ProductController`.
6. **Aplicar `NOT NULL` em `product_skus.erp_code` na primeira migration antes do backfill (Decisão 4):**
   - *Motivo de descarte:* Falharia imediatamente sobre os 1.040 produtos existentes e bloquearia edições legadas antes da curadoria zero-chutes (`P-409`).

---

## 4. Consequências e Trade-offs

- **Pontos Positivos:**
  - **PostgreSQL 100% enxuto (`A1`):** Apenas `products` e `product_skus` no catálogo definitivo; zero tabelas ERP no banco do site em produção.
  - Rastreabilidade 1:1 auditável entre cada variação física no site e o `Id_Pro` no ERP Atrio, com unicidade garantida por constraint de banco e reconciliação atômica em trocas no mesmo produto.
  - Zero regressão na vitrine pública e no `CatalogIndex` (`fitoherb-ai`), mantendo `products.flavours` e `products.presentation` saneados e deduplicados.
  - Desempenho `< 5ms` nas buscas e validações com snapshot em memória RAM (~2 MB), com FinOps preservado (0 tokens de LLM, `maximum-pool-size=3` no Supabase intacto e Scale-to-Zero preservado).
  - Isolamento estrutural de segurança e LGPD (`ProductRes` sem dados ERP ou dados de operador; `Estoque` jamais consultado).
- **Pontos Negativos / Débito Técnico Aceito:**
  - **Dependência de rede Cloud Run ↔ `FITOHERB` na renovação do cache RAM / `fail-closed`:** Se o servidor local/DDNS estiver offline quando o container fizer cold start sem snapshot prévio em RAM, endpoints que validam/buscam ERP retornam `503 ERP_CATALOG_UNAVAILABLE`; enquanto houver snapshot quente em RAM com TTL expirado e falha de rede, métricas/header ou erro controlado garantem consistência. *Mitigação:* Isolamento em `ErpCatalogGateway` e botão/endpoint `POST /erp-products/sync` (`ROLE_ADMIN`) para refresh imediato.
  - **Login7 sem TLS em `jtds` (`ssl=off`):** Obrigatório usar usuário SQL Server restrito estritamente a `SELECT` apenas nos 4 objetos da Allowlist até que o SQL Server on-premise receba suporte a TLS 1.2+ ou túnel VPN.
  - **Coexistência controlada de formatos de paginação:** `/erp-products/**` usa envelope `{"data": ..., "meta": ...}`, enquanto `/products` e `/products/gallery` mantêm `Page<T>` por retrocompatibilidade; unificação futura em `/api/v2/products` permanece mapeada como evolução limpa.
  - **Sincronização dupla `product_skus` ↔ `products.flavours/presentation`:** Exige centralizar toda escrita de variações no `ProductService` (e no pacote SQL idempotente de backfill) para impedir divergência entre a tabela normalizada e os arrays projetados.

---

## 5. Adendo Arquitetural — Onda 4 (Decisões 5 e 6: `US-P7` Sincronização Diária, Visibilidade Automática & `US-P8` Curadoria Rápida)

> **Status:** Proposto para Validação no Checkpoint (Onda 4 — `P-406`, `P-410` a `P-413`)  
> **Data:** 2026-11-18  
> **Autores:** Arquiteto (`architect.md`) + Especialista de IA (`ai_specialist.md`)

### 5.1. Evolução de Domínio: Visibilidade Lógica (`products.active`), Curadoria (`curationStatus`) e Projeção Parcial Multi-SKU (`P-406`, `P-411`)

1. **Novos Atributos em `Product` (`products`):**
   - `active` (`Boolean`, `NOT NULL DEFAULT TRUE`): controla a exposição pública na vitrine (`GET /products/gallery`) e no `CatalogIndex` (`fitoherb-ai`).
   - `curationStatus` (`ProductCurationStatus` enum `VARCHAR(20)`, `NOT NULL DEFAULT 'COMPLETED'`): valores `PENDING_IMAGE`, `COMPLETED`, `IGNORED`. Todos os 1.032 produtos clonados da produção e cadastros manuais iniciam em `COMPLETED`.
   - **`ProductRes` (Público) Intacto:** Nenhuma propriedade interna (`active`, `curationStatus`, `erpCode`, `skus`, `erpInactive`) é adicionada a `ProductRes`. A query pública em `ProductService.getProductGallery` injeta obrigatoriamente `cb.isTrue(root.get("active"))` na `Specification<Product>`.
   - **`ProductAdminRes` (Administrativo):** Passa a expor `active` e `curationStatus` para filtragem e sinalização no `/admin`.

2. **Regra Determinística de Visibilidade e Inativação Parcial Multi-SKU (`P-411`, `C-17`, `C-18`):**
   - **Conciliação `A2` + `P-411`:** O envio de `allowInactiveErp = true` em `POST /products` ou `PUT /products/{slug}` autoriza persistir o vínculo `product_skus` com `erp_inactive = true` e `erp_inactive_confirmed = true` para governança no `/admin`, porém a visibilidade na vitrine é derivada exclusivamente do estado ativo real dos SKUs:
     - Se o produto possui `0` SKUs (`UNMAPPED` durante janela transitória pós-`US-P1`): `active` permanece `true` (`A3`).
     - Se `curationStatus == IGNORED` (`P-413`): `active` permanece obrigatoriamente `false`.
     - Se **100%** dos `product_skus` possuem `erpInactive == true`: `products.active = false` (oculto de `/products/gallery` e `CatalogIndex`, mantendo `image_path` e `product_skus` intactos para reativação instantânea sem `DELETE`).
     - Se **ao menos 1** `ProductSku` possui `erpInactive == false`: `products.active = true`, **e** a projeção `products.flavours` / `products.presentation` (via `LinkedHashSet` ordenado por `sortOrder`) considera **apenas** os SKUs com `erpInactive == false`. Desse modo, sabores ou apresentações inativadas no ERP desaparecem automaticamente da vitrine pública e do `CatalogIndex`, enquanto `ProductAdminRes.skus[]` continua exibindo todos os SKUs com alerta `INACTIVE_ALERT`.
   - **Reativação Imediata (`C-17`):** Quando ao menos um SKU de um produto `active = false` (não `IGNORED`) retorna a `inativo_pro = 0`, `ErpDailySyncService` atualiza `erpInactive = false`, recalcula `flavours`/`presentation` ativos e restaura `products.active = true` no mesmo ciclo — inclusive se `image_path IS NULL` (`curationStatus` assume `PENDING_IMAGE` se ainda sem foto).

### 5.2. Mecanismo Dual de Disparo Diário às `08:00 BRT` (`CloudSchedulerSyncTrigger` + `@Scheduled`), Relatório por E-mail (`ERP_SYNC_REPORT_EMAIL`), Idempotência e Fail-Closed (`P-410`)

1. **Disparo Dual às `08:00 BRT` Compatível com Cloud Run Scale-to-Zero (FinOps):**
   - **Disparo Interno (`@Scheduled`):** `FitoherbBackendV2Application` já possui `@EnableScheduling`. O método agendado em `ErpDailySyncService` / `ErpDailySyncJob` executa às **08:00 AM** com cron configurável `${app.erp.sync.cron:0 0 8 * * *}` (`app.erp.sync.cron=${ERP_SYNC_CRON:0 0 8 * * *}`, `zone = "America/Sao_Paulo"`), habilitado por `${app.erp.sync.internal-scheduler-enabled:true}` para ambientes always-on/locais.
   - **Disparo Externo Serverless (`POST /erp-products/sync/daily`):** Em produção no Cloud Run (`deploy-prod.yml` opera em Scale-to-Zero sem `--min-instances=1`), o **Google Cloud Scheduler** (`0 8 * * *`, `America/Sao_Paulo`) desperta o container via HTTP `POST /erp-products/sync/daily` usando autenticação Machine-to-Machine por header dedicado `X-Sync-Scheduler-Token` (Secret Manager `SYNC_SCHEDULER_TOKEN`).
   - **Relatório Diário por E-mail (*Best-Effort* via `MailService`):** Ao concluir `ErpDailySyncService` (fora da `@Transactional` de banco, após o commit), o serviço verifica a propriedade `app.erp.sync.report-email=${ERP_SYNC_REPORT_EMAIL:}`. Se não estiver em branco, invoca `MailService.sendEmail(MailReq)` com o resumo operacional da execução. O destinatário **JAMAIS** é hardcoded no código ou em arquivos versionados (definido via `.env` gitignored em ambiente local e via secret `ERP_SYNC_REPORT_EMAIL` em produção). Se a propriedade estiver vazia, não envia; se o envio SMTP falhar, captura a exceção e registra apenas `log.warn` sanitizado (sem imprimir o endereço de e-mail nem abortar/reverter a sincronização).
   - **Segurança em Profundidade contra `SecurityFilter` e `.anyRequest().permitAll()`:** `SecurityFilter` valida `Authorization: Bearer` exclusivamente contra JWT HMAC256 de usuários. Por isso, um filtro dedicado valida `X-Sync-Scheduler-Token` com comparação em tempo constante (`MessageDigest.isEqual`, *fail-closed* se variável ausente — zero fallback literal) injetando principal técnico `"CLOUD_SCHEDULER"` (`ROLE_SYNC_SCHEDULER`), além de regras explícitas `requestMatchers` em `SecurityConfigurations.java` para `/erp-products/**` + `@PreAuthorize`.

2. **Controle de Estado, Lock Anti-Concorrência e Idempotência (`ErpSyncState` / `ErpSyncRun` / `ErpIgnoredCatalogCode`):**
   - **`erp_sync_state` (singleton `id = 1`):** Armazena `baseline_cutoff_at`, `auto_sync_enabled` (`false` até finalização de `US-P1`/`US-P6` e aprovação humana), `last_successful_sync_at`, `in_progress`, `lock_acquired_at` (TTL 15 min para *stale-lock recovery* em queda de container) e `active_run_id`.
   - **Lock Atômico:** `UPDATE` condicional em `erp_sync_state` (`in_progress = FALSE OR lock_acquired_at < NOW() - INTERVAL '15 minutes'`). Caso retorne `0` linhas, retorna `409 Conflict` (`ERP_SYNC_ALREADY_RUNNING`) por padrão ou `202 Accepted` (`ALREADY_RUNNING`) se `?ifRunning=ACCEPT`.
   - **`erp_sync_runs`:** Registra histórico sanitizado de cada execução (`trigger_type`, `triggered_by`, `status`, contadores, `error_summary` sem credenciais/PII/stacktrace), com expurgo automático > **90 dias** (LGPD/FinOps).
   - **Política Anti-Flood de Baseline (`P-410`, Q-07):** Ao concluir `US-P1`/`US-P6`, os `Id_Pro` pré-existentes no ERP que deliberadamente não pertencem ao site (~650 itens) são registrados apenas como chaves numéricas mínimas em `erp_ignored_catalog_codes` (`source = 'BASELINE_EXCLUSION'`, `< 50 KB`, em total conformidade com `A1` — zero tabela espelho do catálogo no PostgreSQL). Ciclos diários seguintes só criam automaticamente novos códigos ativos não constantes em `product_skus` nem em `erp_ignored_catalog_codes` (`BASELINE_EXCLUSION` ou `ADMIN_IGNORED`).
   - **Fail-Closed:** Se `ErpCatalogGateway` não conectar ao SQL Server `FITOHERB`, aborta antes de qualquer escrita em `products`/`product_skus`, preserva 100% do catálogo `active` atual e retorna `503` (`ERP_CATALOG_UNAVAILABLE`).

### 5.3. Publicação Imediata Sem Imagem (`image_path = NULL`), Metadados Determinísticos e Fallback Visual (`P-412`, `P-413`)

1. **Exceção Controlada à `IMG-001`:** `POST /products` (cadastro manual) mantém `MultipartFile image` obrigatório (`400 Bad Request` se ausente). `ErpDailySyncService` cria produtos pós-baseline com `image_path = NULL`, `active = true` e `curation_status = PENDING_IMAGE`. Como `ImageUrlBuilder.toProductPublicUrl(null)` retorna `null`, a vitrine pública renderiza `'assets/images/fitoherb-leaf-icon.png'` imediatamente via classe limpa `.placeholder-image` (sem estilização `.fallback-image` acinzentada de erro).
2. **Resolução Determinística de Metadados (0 Tokens LLM):** `name` higienizado via `ErpVariantSuggestionService`, `slug` único via `StringUtils.toSlug()` com desempate incremental (`-2`, `-3`), e `supplier_id`/`category_id` via `BrandAliasRegistry` + dicionário determinístico com fallback configurável (`app.erp.sync.fallback-category-slug`, `app.erp.sync.fallback-supplier-slug`), sinalizado ao operador na Curadoria Rápida (`fallbackCategoryWarning` / `fallbackSupplierWarning`). Granularidade inicial conservadora `1:1` por `Id_Pro` novo (Q-08).
3. **Ciclo na Curadoria Rápida (`P-413`):** `PUT /products/{slug}` transita `PENDING_IMAGE -> COMPLETED` apenas ao receber `image` válida (`isImageValid` em modo edição não bloqueia ajustes parciais de texto sem foto). `POST /erp-products/curation-pending/{slug}/ignore` grava em `erp_ignored_catalog_codes` (`source = 'ADMIN_IGNORED'`), define `active = false` e `curation_status = IGNORED`.

### 5.4. Sincronização Ativa do `CatalogIndex`, Invalidação de Cache L1 e Resiliência Scale-to-Zero (`fitoherb-ai`)

1. **Query Estrita e Isolada (`P-408`, `P-411`, `P-412`):**
   - `CatalogIndex.load_from_db()` filtra `WHERE COALESCE(p.active, TRUE) = TRUE ORDER BY p.name ASC` (e facetas de `product_categories`/`suppliers` com `EXISTS (SELECT 1 FROM products p WHERE ... AND COALESCE(p.active, TRUE) = TRUE)`), lendo apenas `products`, `product_categories` e `suppliers` em sessão read-only (`default_transaction_read_only=on`, fechamento garantido em `finally:`), removendo a senha literal `"Dm120394"` (`catalog_index.py:81`) e convertendo `image_path IS NULL` em `image_url = None`. Proibido consultar `product_skus`, `erp_ignored_catalog_codes`, `erp_sync_runs` ou `users`.
2. **Invalidação e Recarga Pós-Sync (0 Tokens LLM & `--cpu-throttling` Safe):**
   - `fitoherb-backend-v2` invoca `POST {fitoherb.ai.service.url}/api/v1/chat/catalog/refresh` **fora da `@Transactional` imediatamente após o commit** (`RestClient` síncrono com `connectTimeout=3s`, `readTimeout=5s` e fallback best-effort `WARN` sem reverter o PostgreSQL), autenticando via header `X-Internal-Refresh-Token` (`INTERNAL_REFRESH_TOKEN` no Secret Manager, validado em tempo constante via `hmac.compare_digest` — fail-closed `503` se ausente no ambiente).
   - No `fitoherb-ai`, a troca do snapshot ocorre atomicamente sob `threading.RLock`, incrementando `catalog_version`, limpando `ConversationCacheService` e vinculando gravações no cache L1 à `catalog_version` capturada no início da requisição (prevenindo *race condition* onde requisição em voo reintroduza produto recém-inativado). Em falha de PostgreSQL durante refresh, mantém o último snapshot válido em RAM e retorna `503 CATALOG_REFRESH_FAILED`.
   - **Auto-Cura TTL Passivo:** Sem threads de polling em background (preservando Scale-to-Zero `$0`), `CatalogIndex.ensure_fresh()` revalida sob demanda se `monotonic_now - _last_loaded_monotonic >= CATALOG_REFRESH_TTL_SECONDS` (`3600s` padrão). Em múltiplas réplicas Cloud Run, a réplica atingida pelo webhook atualiza de imediato e eventuais réplicas paralelas convergem no máximo em `CATALOG_REFRESH_TTL_SECONDS`.
~~~~,Target:
