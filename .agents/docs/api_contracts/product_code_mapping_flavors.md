# Contrato de API: Produtos, SKUs e Consulta ERP Atrio (`product_code_mapping_flavors`)

Este documento define os contratos de integração REST do `fitoherb-backend-v2` (Spring Boot 4.0.5 / Java 21) para o cadastro Multi-SKU com obrigatoriedade de código `Id_Pro` (`erpCode`), segregação Vitrine × Admin, busca/importação em lote direta do ERP Atrio (via `ErpCatalogGateway` somente-leitura + cache RAM, sem manter tabela espelho ERP no PostgreSQL conforme `A1`) e atualização sob demanda do cache ERP.

---

## 1. Visão Geral

- **Serviço:** `fitoherb-backend-v2` (Controllers: `ProductController` em `@RequestMapping("/products")` e novo `ErpProductController` em `@RequestMapping("/erp-products")`).
- **Base URL:**
  - Local: `http://localhost:8080` (sem prefixo `/api`, conforme `environment.development.ts`)
  - Produção: `https://fitoherb-backend-nkrtrtj5hq-uc.a.run.app` (`environment.ts`)
- **Padrão de Nomenclatura JSON:** `camelCase` estrito em todos os payloads e query params (exceção apenas para os nomes de campo quando mapeados em `errors` de Bean Validation).
- **Segurança & Autenticação (`SecurityConfigurations` + `SecurityFilter`):**
  - Autenticação stateless via **Cookie `fitoherb_jwt` (`HttpOnly`, `Path=/`)** enviado automaticamente pelo `authInterceptor` (`withCredentials: true`), com suporte complementar ao header `Authorization: Bearer <jwt>`.
  - `GET /products/gallery`: **Público** (sem `@PreAuthorize`).
  - Demais endpoints em `/products/**` e leitura/sugestão em `/erp-products/**`: protegidos por `@PreAuthorize("@authorizationService.isAdminOrUser()")` (`ROLE_ADMIN` ou `ROLE_USER`; `ROLE_SELLER` e anônimos recebem `403`/`401`).
  - `POST /erp-products/sync`: restrito estritamente a `@PreAuthorize("@authorizationService.isAdmin()")` (`ROLE_ADMIN`).
  - **Adendo Onda 4 (`US-P7` / `US-P8` — Proteção Dupla `SecurityConfigurations` + `@PreAuthorize`):**
    - `POST /erp-products/sync/daily`: `hasAnyRole("ADMIN", "SYNC_SCHEDULER")` via header `X-Sync-Scheduler-Token` (comparado em tempo constante via `MessageDigest.isEqual` contra `SYNC_SCHEDULER_TOKEN` em Secret Manager, fail-closed, sem conflitar com `SecurityFilter` Auth0 JWT) **ou** JWT `ROLE_ADMIN`.
    - `GET /erp-products/curation-pending` e `POST /erp-products/curation-pending/{slug}/ignore`: `hasAnyRole("ADMIN", "USER")` (`@PreAuthorize("@authorizationService.isAdminOrUser()")`; bloqueia `ROLE_SELLER` com `403` e anônimo com `401`).
    - Webhook `fitoherb-backend-v2 -> fitoherb-ai`: `POST {FITOHERB_AI_URL}/api/v1/chat/catalog/refresh` autenticado via `X-Internal-Refresh-Token` (`hmac.compare_digest`).
  - **`GET /products/gallery` (`ProductRes` público) & `ProductAdminRes` / `PUT /products/{slug}`:**
    - `GET /products/gallery` filtra `products.active = true`, projeta em `flavours`/`presentation` apenas variações com `erpInactive = false`, permite `imageUrl = null` (vitrine exibe fallback institucional) e **nunca** expõe `active`, `curationStatus`, `erpCode`, `skus` ou `Estoque`.
    - `ProductAdminRes` adiciona `"active": boolean` e `"curationStatus": "PENDING_IMAGE" | "COMPLETED" | "IGNORED"`; `GET /products` aceita filtros opcionais `active` e `curationStatus`.
    - `POST /products` mantém imagem obrigatória manual (`400 Bad Request` se ausente, `IMG-001`) com `curationStatus = COMPLETED`; `PUT /products/{slug}` transita `PENDING_IMAGE -> COMPLETED` quando imagem válida é salva (mantendo `PENDING_IMAGE` se salvo sem foto).
- **Estratégia de Envelope:**
  - Todos os novos endpoints (`/erp-products/**`) seguem estritamente o envelope canônico `{"data": ..., "meta": {...}}` (`ApiEnvelope<T>`).
  - Endpoints existentes em `ProductController` preservam o formato Spring Data `Page<T>` / `201 Location` / `200 Void` (`CRUD-004`, `CRUD-005`) para retrocompatibilidade com `GalleryComponent` e `AdminComponent`, conforme ADR-005.

---

## 2. Endpoints

### 2.1. `GET /products/gallery` (Vitrine Pública — Sem Dados ERP)
**Objetivo:** Listagem paginada otimizada para a vitrine pública (`/produtos` — `GalleryComponent`, `ItemCardGalleryComponent`, `ModalGalleryComponent`) e consulta auxiliar de cascata. **Nunca expõe** `erpCode`, `skus`, `erpStatus`, `inativoPro` ou `Estoque` (`P-408`, `P-302`).

**Requisição (Request):**
- **Autenticação:** Pública (não requer JWT).
- **Query Params:**
  - `search` (string, opcional): busca em `name`, `category.name`, `supplier.name`, `description`, `flavours` e `presentation`. (Ignora `erpCode` propositalmente na rota pública.)
  - `category` (`string[]`, opcional): slugs de categorias (ex.: `?category=suplementos&category=chas`).
  - `supplier` (`string[]`, opcional): slugs de fornecedores.
  - `page` (int, padrão `0`): página 0-indexada.
  - `size` (int, padrão `15`, máx. recomendado `100`): itens por página.
  - `direction` (string, padrão `ASC`): `ASC` | `DESC`.

**Resposta de Sucesso (`200 OK` — `Page<ProductRes>`):**
```json
{
  "content": [
    {
      "name": "B.O.P.E",
      "imageUrl": "https://storage.googleapis.com/fitoherb-images-bucket/products/bope.webp",
      "description": "Pré-treino formulado para energia e foco.",
      "flavours": ["Fruit Punch", "Limão", "Melancia"],
      "presentation": ["150g", "300g"],
      "slug": "bope-black-skull",
      "category": {
        "name": "Pré-Treinos",
        "slug": "pre-treinos",
        "createdAt": "12-04-2026 14:30:00",
        "imageUrl": "https://storage.googleapis.com/fitoherb-images-bucket/categories/pre.webp",
        "count": 18
      },
      "supplier": {
        "name": "Black Skull",
        "slug": "black-skull",
        "createdAt": "12-04-2026 10:15:30",
        "imageUrl": "https://storage.googleapis.com/fitoherb-images-bucket/suppliers/black-skull.webp",
        "isHighlighted": true,
        "count": 42
      },
      "createdAt": "12-04-2026 15:00:00"
    }
  ],
  "totalPages": 69,
  "totalElements": 1040,
  "size": 15,
  "number": 0,
  "first": true,
  "last": false,
  "empty": false
}
```
> **Invariante `P-401` + `P-408`:** `flavours` e `presentation` contêm apenas strings atômicas limpas e **sem duplicatas**; nenhum atributo `skus`, `erpCode`, `erpStatus`, `inativoPro` ou `Estoque` existe em `ProductRes`.

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** Parâmetros de página ou tipo inválidos (`RestErrorMessage`).
- **404 Not Found:** Categoria ou fornecedor explicitamente inexistente quando aplicável (`RestErrorMessage`).

---

### 2.2. `GET /products` (Listagem Administrativa com Busca por `erpCode` e Filtro `erpStatus`)
**Objetivo:** Listagem paginada para a tabela `Produtos` do `/admin` (`AdminComponent`), com exibição resumida/detalhada dos vínculos ERP, pesquisa global incluindo `erpCode` e filtragem por status de governança ERP (`P-408`).

**Requisição (Request):**
- **Autenticação:** Cookie `fitoherb_jwt` ou `Authorization: Bearer <token>` — `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Query Params:**
  - `search` (string, opcional): busca em `name`, `description`, `flavours`, `presentation` **e** `product_skus.erp_code` (ex.: `search=131477` encontra `100% Pure Whey 900g`).
  - `category` (`string[]`, opcional): slugs de categorias.
  - `supplier` (`string[]`, opcional): slugs de fornecedores.
  - `erpStatus` (`string[]`, opcional): filtro por status ERP (`UNMAPPED`, `COMPLETE`, `INACTIVE_ALERT`).
  - `page` (int, padrão `0`): página 0-indexada.
  - `size` (int, padrão `10`, máx. `50`): tamanho de página administrativo.
  - `sortField` (string, padrão `name`): `name` | `createdAt` | `category.name` | `supplier.name`.
  - `direction` (string, padrão `ASC`): `ASC` | `DESC`.

**Resposta de Sucesso (`200 OK` — `Page<ProductAdminRes>`):**
```json
{
  "content": [
    {
      "name": "100% Pure Whey 900g",
      "imageUrl": "/uploads/products/whey-900g.webp",
      "description": "Proteína concentrada do soro do leite.",
      "flavours": ["Baunilha", "Chocolate", "Morango"],
      "presentation": [],
      "slug": "100-pure-whey-900g-probiotica",
      "category": {
        "name": "Proteínas",
        "slug": "proteinas",
        "createdAt": "12-04-2026 14:30:00",
        "imageUrl": "/uploads/categories/proteinas.webp",
        "count": 35
      },
      "supplier": {
        "name": "Probiótica",
        "slug": "probiotica",
        "createdAt": "12-04-2026 10:15:30",
        "imageUrl": "/uploads/suppliers/probiotica.webp",
        "isHighlighted": false,
        "count": 28
      },
      "createdAt": "12-04-2026 15:00:00",
      "topology": "FLAVOUR_ONLY",
      "erpStatus": "COMPLETE",
      "skuCount": 3,
      "primaryErpCode": 131476,
      "skus": [
        {
          "id": "a1111111-1111-1111-1111-111111111111",
          "flavour": "Baunilha",
          "presentation": null,
          "erpCode": 131476,
          "erpInactive": false,
          "erpInactiveConfirmed": false,
          "erpDescription": "WHEY 100% PURE 900G BAUNILHA PROBIOTICA"
        },
        {
          "id": "a2222222-2222-2222-2222-222222222222",
          "flavour": "Chocolate",
          "presentation": null,
          "erpCode": 131477,
          "erpInactive": false,
          "erpInactiveConfirmed": false,
          "erpDescription": "WHEY 100% PURE 900G CHOCOLATE PROBIOTICA"
        },
        {
          "id": "a3333333-3333-3333-3333-333333333333",
          "flavour": "Morango",
          "presentation": null,
          "erpCode": 131478,
          "erpInactive": false,
          "erpInactiveConfirmed": false,
          "erpDescription": "WHEY 100% PURE 900G MORANGO PROBIOTICA"
        }
      ]
    }
  ],
  "totalPages": 104,
  "totalElements": 1040,
  "size": 10,
  "number": 0,
  "first": true,
  "last": false,
  "empty": false
}
```

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** `sortField` inválido ou `erpStatus` desconhecido.
- **401 Unauthorized:** Token JWT ausente, inválido ou expirado.
- **403 Forbidden:** Perfil `ROLE_SELLER` tentando acessar listagem administrativa.

---

### 2.3. `GET /products/{slug}` (Detalhes Administrativos por Slug)
**Objetivo:** Recupera os detalhes completos de um produto, incluindo sua lista ordenada de `skus[]`, para carregamento no `ModalEntityComponent` em modo edição (`P-405`, `P-408`).

**Requisição (Request):**
- **Autenticação:** Cookie `fitoherb_jwt` ou `Authorization: Bearer <token>` — `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Path Param:** `slug` (string, regex `^[a-z0-9-]+$`).

**Resposta de Sucesso (`200 OK`):**
Retorna objeto `ProductAdminRes` idêntico aos itens de `content[]` descritos em `2.2`.

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** `slug` fora do padrão `SLUG_REGEX` (`RestValidationErrorMessage`).
- **401 Unauthorized / 403 Forbidden:** Sem permissão administrativa.
- **404 Not Found:** Produto não encontrado (`RestErrorMessage`).

---

### 2.4. `POST /products` (Cadastro de Produto com Validação ERP Multi-SKU)
**Objetivo:** Cadastra um novo produto (Simples, Somente Sabor, Somente Apresentação ou Matriz Sabor × Apresentação) com imagem obrigatória, exigindo `erpCode` válido no catálogo do ERP Atrio e único em todo o site (`P-401` a `P-406`).

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Content-Type:** `multipart/form-data`
- **Parts:**
  - `product` (`application/json` — DTO `ProductReq`):
    ```json
    {
      "name": "B.O.P.E",
      "description": "Pré-treino de alta performance.",
      "categorySlug": "pre-treinos",
      "supplierSlug": "black-skull",
      "allowInactiveErp": false,
      "skus": [
        { "erpCode": 90101, "flavour": "Fruit Punch", "presentation": "150g" },
        { "erpCode": 90102, "flavour": "Limão", "presentation": "150g" },
        { "erpCode": 90103, "flavour": "Melancia", "presentation": "150g" },
        { "erpCode": 90201, "flavour": "Fruit Punch", "presentation": "300g" },
        { "erpCode": 90202, "flavour": "Limão", "presentation": "300g" }
      ]
    }
    ```
    *Exemplo Produto Simples (`SIMPLE`):*
    ```json
    {
      "name": "Mel Silvestre 500g",
      "description": "Mel puro de florada silvestre.",
      "categorySlug": "naturais",
      "supplierSlug": "apisnutri",
      "allowInactiveErp": false,
      "skus": [
        { "erpCode": 41025, "flavour": null, "presentation": null }
      ]
    }
    ```
  - `image` (`file`, obrigatório): imagem do produto (máx. `10MB`).

**Regras de Validação no Servidor:**
1. `skus` deve conter entre `1` e `100` itens (`MAX_SKUS_PER_PRODUCT = 100`).
2. Cada item de `skus` exige `erpCode` inteiro positivo (`@NotNull`, `@Positive`, compatível com `bigint`).
3. `flavour` e `presentation` passam pelo `ProductVariantSanitizer` (`trim`, remoção de ponto final residual `.`, rejeição de variação explícita com valor apenas de pontuação/espaços -> `400`).
4. Todos os SKUs devem obedecer exatamente uma única topologia (`SIMPLE`, `FLAVOUR_ONLY`, `PRESENTATION_ONLY`, `MATRIX`) -> erro `422 PRODUCT_TOPOLOGY_INVALID`.
5. Catálogo ERP em memória/SQL Server (`ErpCatalogGateway`) deve estar acessível/carregado -> erro `503 ERP_CATALOG_UNAVAILABLE`.
6. Todos os `erpCode`s devem existir no catálogo do ERP Atrio -> erro `422 ERP_CODE_NOT_FOUND`.
7. Se algum `erpCode` tiver `inativo_pro = true` e `allowInactiveErp != true` -> erro `422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED` com lista `details.inactiveErpCodes`.
8. Sem `erpCode` repetido ou combinação normalizada `(flavour, presentation)` repetida no mesmo payload -> erro `422 DUPLICATE_ERP_CODE_IN_PAYLOAD` / `DUPLICATE_VARIANT_COMBINATION`.
9. Sem colisão com `erpCode` já vinculado a outro produto no banco -> erro `409 Conflict` informando o nome do produto detentor (`P-404`).

**Resposta de Sucesso (`201 Created`):**
- Header `Location: /products/{id}`
- Body vazio (mantendo compatibilidade com `CRUD-004` e `ProductsService.create(): Observable<void>`).

**Respostas de Erro Mapeadas:** `400`, `401`, `403`, `404`, `409`, `422`, `503` (ver seção `2.10`).

---

### 2.5. `PUT /products/{slug}` (Edição com Reconciliação Atômica de SKUs)
**Objetivo:** Atualiza metadados, imagem opcional e a lista de SKUs de um produto existente, permitindo troca de códigos entre variações do mesmo produto e liberação de códigos removidos sem falso conflito `409` (`P-404`, `C-05`, `C-16`).

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Path Param:** `slug` (regex `^[a-z0-9-]+$`).
- **Content-Type:** `multipart/form-data`
- **Parts:**
  - `product` (`application/json` — DTO `ProductReq`, mesma estrutura de `2.4`).
  - `image` (`file`, opcional): se omitido, preserva imagem atual (`P-011`).

**Comportamento Crítico de Integridade (`P-404`):**
- A checagem de conflito global verifica `product_skus` onde `erp_code IN (:erpCodes) AND product_id <> :currentProductId`.
- SKUs anteriores do próprio produto são reconciliados atomicamente com `flush()` intermediário antes da gravação de códigos permutados entre sabores do mesmo produto (`C-05`).
- `ProductService.updateProductBySlug` **NÃO** envolve exceções de negócio/integridade em `DatabaseOperationException` (HTTP `500`); `409`, `422`, `404` e `503` propagam intactos ao `RestExceptionHandler` (`C-16`).

**Resposta de Sucesso (`200 OK`):**
- Body vazio (`CRUD-005`).

**Respostas de Erro Mapeadas:** `400`, `401`, `403`, `404`, `409`, `422`, `503`.

---

### 2.6. `GET /erp-products/search` (Busca no Catálogo do ERP Atrio via Cache RAM / SQL Server)
**Objetivo:** Pesquisa paginada sobre o snapshot em memória RAM do ERP Atrio (`FITOHERB`, atualizado por `ErpCatalogGateway` em modo somente-leitura, sem manter tabela espelho ERP permanente no PostgreSQL — `A1`) para o modal de seleção/importação em lote (`P-407`). Busca por `Id_Pro`, `codbarra_pro` (`EAN`), `descricao_pro`, marca ou tipo de produto ERP, **sem restringir** pela marca selecionada no formulário do site (usando `supplierSlug` opcional apenas para priorizar ordenação via aliases versionados, garantindo `C-10` `Arrebite` ↔ `GUARANAPIS`).

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Query Params:**
  - `q` (string, obrigatório): termo de busca. Aceita `>= 1` dígito quando puramente numérico (busca exata/prefixo em `id_pro` ou `codbarra_pro`) ou `>= 2` caracteres para busca textual. Termo vazio ou com apenas 1 letra não numérica retorna `400 Bad Request` para impedir carga total dos 6.946 registros (`P-407`).
  - `supplierSlug` (string, opcional): slug do fornecedor selecionado no formulário do site; usado **exclusivamente para ordenação de relevância (boost)** via `supplier_brand_aliases`, **nunca** como filtro `WHERE` excludente.
  - `includeInactive` (boolean, padrão `true`): quando `true`, inclui registros com `inativo_pro = true` exibindo flag de alerta; quando `false`, retorna apenas `inativo_pro = false`.
  - `excludeProductSlug` (string, opcional): slug do produto atualmente em edição para não marcar os SKUs do **próprio** produto como bloqueados (`alreadyMapped`).
  - `page` (int, padrão `0`): página 0-indexada.
  - `size` (int, padrão `20`, máx. `50`): tamanho da página.

**Resposta de Sucesso (`200 OK` — Envelope `ApiEnvelope<List<ErpCatalogItemRes>>`):**
```json
{
  "data": [
    {
      "erpCode": 131476,
      "erpDescription": "WHEY 100% PURE 900G BAUNILHA PROBIOTICA",
      "ean": "7896438201234",
      "erpBrand": "PROBIOTICA",
      "erpSupplier": "PROBIOTICA LABS",
      "inativoPro": false,
      "inExterno01": true,
      "alreadyMapped": true,
      "mappedProductSlug": "100-pure-whey-900g-probiotica",
      "mappedProductName": "100% Pure Whey 900g",
      "mappedFlavour": "Baunilha",
      "mappedPresentation": null
    },
    {
      "erpCode": 131479,
      "erpDescription": "WHEY 100% PURE 900G COOKIES PROBIOTICA",
      "ean": "7896438201296",
      "erpBrand": "PROBIOTICA",
      "erpSupplier": "PROBIOTICA LABS",
      "inativoPro": true,
      "inExterno01": true,
      "alreadyMapped": false,
      "mappedProductSlug": null,
      "mappedProductName": null,
      "mappedFlavour": null,
      "mappedPresentation": null
    }
  ],
  "meta": {
    "timestamp": "2026-11-17T18:10:00-03:00",
    "page": 0,
    "size": 20,
    "totalElements": 2,
    "totalPages": 1,
    "lastSyncedAt": "2026-11-17T06:00:00-03:00"
  }
}
```
> **Minimização LGPD & Sigilo (`P-302`, `P-408`):** `Estoque` e valores monetários nunca fazem parte do schema `ErpCatalogItemRes`.

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** `q` ausente, vazio ou `< 2` caracteres não numéricos; `size > 50`.
- **401 Unauthorized / 403 Forbidden:** Usuário sem `ROLE_ADMIN` ou `ROLE_USER`.
- **503 Service Unavailable:** Catálogo do ERP Atrio inacessível / cache RAM ainda vazio (`ERP_CATALOG_UNAVAILABLE`).

---

### 2.7. `GET /erp-products/{erpCode}` (Consulta Unitária por `Id_Pro`)
**Objetivo:** Consulta direta de um único SKU do catálogo ERP (`ErpCatalogGateway` cache RAM + lookup pontual SQL Server) pelo seu `Id_Pro` (ex.: validação instantânea ao digitar código manual no formulário).

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Path Param:** `erpCode` (long `> 0`).
- **Query Param:** `excludeProductSlug` (string, opcional).

**Resposta de Sucesso (`200 OK` — Envelope `ApiEnvelope<ErpCatalogItemRes>`):**
```json
{
  "data": {
    "erpCode": 580000,
    "erpDescription": "STEVITA LIQUIDO 25ML",
    "ean": "7896005800001",
    "erpBrand": "STEVITA",
    "erpSupplier": "STEVITA",
    "inativoPro": false,
    "inExterno01": true,
    "alreadyMapped": false,
    "mappedProductSlug": null,
    "mappedProductName": null,
    "mappedFlavour": null,
    "mappedPresentation": null
  },
  "meta": {
    "timestamp": "2026-11-17T18:12:00-03:00",
    "lastSyncedAt": "2026-11-17T06:00:00-03:00"
  }
}
```

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** `erpCode` não numérico ou `<= 0`.
- **401 / 403:** Sem permissão administrativa.
- **404 Not Found:** Código `erpCode` não encontrado no catálogo do ERP Atrio (`Empresa_Pro = 1`).
- **503 Service Unavailable:** ERP Atrio inacessível no momento (`ERP_CATALOG_UNAVAILABLE`).

---

### 2.8. `POST /erp-products/suggest-variants` (Importação em Lote & Expansão de Abreviações `P-407`)
**Objetivo:** Recebe um conjunto de códigos `erpCode` selecionados em lote no modal administrativo, verifica disponibilidade/conflito, expande abreviações conhecidas do ERP Atrio (`CHOCO` → `Chocolate`, `CAPSGEL` → `Cápsulas`, `DISP.` → `Display`, `STAND UP` → `Stand Up / Refil`, extração de gramaturas/volumes `900g`, `150g`, `300g`, `25ml`, `60ml`), sugere `suggestedTopology`, `suggestedFlavour`, `suggestedPresentation` e alerta divergências de embalagem (`DISP.` / `CX` vs `UN`) e `inativoPro` para revisão humana antes de salvar. **Opera deterministicamente com 0 tokens de LLM.**

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")`.
- **Headers:** `Content-Type: application/json`
- **Body (`SuggestVariantsReq`):**
  ```json
  {
    "erpCodes": [131476, 131477, 131478],
    "excludeProductSlug": "100-pure-whey-900g-probiotica"
  }
  ```
  *Validações:* `erpCodes` obrigatório, `@NotEmpty`, tamanho `1..100`, cada item `@Positive`.

**Resposta de Sucesso (`200 OK` — Envelope `ApiEnvelope<SuggestVariantsRes>`):**
```json
{
  "data": {
    "suggestedTopology": "FLAVOUR_ONLY",
    "hasInactiveItems": false,
    "hasConflictingItems": false,
    "items": [
      {
        "erpCode": 131476,
        "erpDescription": "WHEY 100% PURE 900G BAUN PROBIOTICA",
        "suggestedFlavour": "Baunilha",
        "suggestedPresentation": null,
        "inativoPro": false,
        "inExterno01": true,
        "alreadyMappedElsewhere": false,
        "conflictingProductName": null,
        "packageWarning": null
      },
      {
        "erpCode": 131477,
        "erpDescription": "WHEY 100% PURE 900G CHOCO PROBIOTICA",
        "suggestedFlavour": "Chocolate",
        "suggestedPresentation": null,
        "inativoPro": false,
        "inExterno01": true,
        "alreadyMappedElsewhere": false,
        "conflictingProductName": null,
        "packageWarning": null
      },
      {
        "erpCode": 131478,
        "erpDescription": "WHEY 100% PURE 900G MOR PROBIOTICA",
        "suggestedFlavour": "Morango",
        "suggestedPresentation": null,
        "inativoPro": false,
        "inExterno01": true,
        "alreadyMappedElsewhere": false,
        "conflictingProductName": null,
        "packageWarning": null
      }
    ]
  },
  "meta": {
    "timestamp": "2026-11-17T18:15:00-03:00",
    "count": 3
  }
}
```
*Nota de comportamento para `Q-06`:* Se `erpDescription` contiver marcadores de embalagem fechada (`DISP.`, `DISPLAY`, `CX`, `CAIXA`), `packageWarning` retorna `"Embalagem coletiva detectada no ERP (Display/Caixa). Confirme se o produto do site refere-se à unidade ou ao display."`.

**Respostas de Erro Mapeadas:**
- **400 Bad Request:** Lista vazia, > 100 códigos ou item `<= 0`.
- **401 / 403:** Sem permissão administrativa.
- **422 Unprocessable Entity:** Algum `erpCode` informado não existe no catálogo espelhado (`ERP_CODE_NOT_FOUND`).
- **503 Service Unavailable:** Base espelho indisponível (`ERP_CATALOG_UNAVAILABLE`).

---

### 2.9. `POST /erp-products/sync` (Refresh do Snapshot ERP em Memória & Reconciliação de Flags `A1`/`P-406`)
**Objetivo:** Endpoint restrito exclusivamente a `ROLE_ADMIN` para recarregar imediatamente o cache snapshot em memória RAM diretamente do SQL Server `FITOHERB` (`WITH (NOLOCK)`, somente leitura) — **sem persistir tabela de catálogo ERP no PostgreSQL do site (`A1`)** — e sincronizar `erp_inactive` / `erp_last_verified_at` nos `product_skus` existentes mantendo os produtos visíveis (`P-406`).

**Requisição (Request):**
- **Autenticação:** `@PreAuthorize("@authorizationService.isAdmin()")` (`ROLE_ADMIN` obrigatório; `ROLE_USER` recebe `403 Forbidden`).
- **Headers:** `Content-Type: application/json` *(body opcional `{}`)*

**Resposta de Sucesso (`200 OK` — Envelope `ApiEnvelope<SyncErpCatalogRes>`):**
```json
{
  "data": {
    "processedCatalogItems": 6946,
    "activeCatalogItems": 1652,
    "inactiveCatalogItems": 5294,
    "checkedSiteSkus": 1040,
    "newlyInactivatedMappedProducts": 2
  },
  "meta": {
    "timestamp": "2026-11-18T08:45:00-03:00",
    "syncedAt": "2026-11-18T08:45:00-03:00"
  }
}
```

**Respostas de Erro Mapeadas:**
- **401 Unauthorized / 403 Forbidden:** Qualquer usuário que não possua `ROLE_ADMIN`.
- **503 Service Unavailable:** SQL Server `FITOHERB` inacessível (`ERP_CATALOG_UNAVAILABLE`).

---

### 2.10. Envelope Padronizado de Erros (`RestErrorMessage` & `RestValidationErrorMessage`)

Todos os erros retornam JSON compatível com `RestExceptionHandler`:

1. **400 Bad Request — Validação de Campos (`RestValidationErrorMessage`):**
   ```json
   {
     "status": "BAD_REQUEST",
     "message": "Falha na validação de um ou mais campos",
     "errors": {
       "skus[0].erpCode": "O código do produto no ERP (Id_Pro) é obrigatório e deve ser um número inteiro positivo.",
       "skus[1].flavour": "O nome do sabor ou apresentação não pode ser vazio ou conter apenas pontuação."
     }
   }
   ```
2. **409 Conflict — `Id_Pro` já vinculado a outro produto (`RestErrorMessage`, `P-404`):**
   ```json
   {
     "status": "CONFLICT",
     "message": "O código ERP '131476' já está vinculado ao produto '100% Pure Whey 900g'.",
     "code": "ERP_CODE_ALREADY_MAPPED",
     "details": {
       "erpCode": 131476,
       "conflictingProductName": "100% Pure Whey 900g",
       "conflictingProductSlug": "100-pure-whey-900g-probiotica"
     }
   }
   ```
3. **422 Unprocessable Entity — Confirmação Obrigatória de SKU Inativo (`RestErrorMessage`, `P-406`):**
   ```json
   {
     "status": "UNPROCESSABLE_ENTITY",
     "message": "O código ERP '131479' está marcado como inativo no ERP Atrio (inativo_pro = 1). Confirme se deseja vinculá-lo mesmo assim.",
     "code": "ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED",
     "details": {
       "inactiveErpCodes": [131479]
     }
   }
   ```
4. **422 Unprocessable Entity — Demais Regras de Domínio (`RestErrorMessage`):**
   - `code: "ERP_CODE_NOT_FOUND"` (`P-403`): `"Código ERP '9999999' não encontrado no catálogo do ERP Atrio."`
   - `code: "PRODUCT_TOPOLOGY_INVALID"` (`P-405`): `"Estrutura de variações inconsistente: todas as variações do produto devem seguir o mesmo padrão (Simples, Sabores, Apresentações ou Matriz Sabor × Apresentação)."`
   - `code: "DUPLICATE_ERP_CODE_IN_PAYLOAD"` (`P-404`): `"O código ERP '131476' foi informado mais de uma vez neste produto."`
   - `code: "DUPLICATE_VARIANT_COMBINATION"` (`P-404`): `"A variação 'Morango / 300g' está duplicada neste produto."`
5. **503 Service Unavailable — Catálogo Espelho Indisponível (`RestErrorMessage`, `P-403`):**
   ```json
   {
     "status": "SERVICE_UNAVAILABLE",
     "message": "Base de referência do ERP Atrio indisponível no momento para validar os códigos informados.",
     "code": "ERP_CATALOG_UNAVAILABLE"
   }
   ```
6. **409 Conflict — Lock de Sincronização Diária Concorrente (`P-410`):**
   ```json
   {
     "status": "CONFLICT",
     "message": "Já existe uma sincronização diária do ERP Atrio em andamento.",
     "code": "ERP_SYNC_ALREADY_RUNNING",
     "details": {
       "activeRunId": "d9a01122-0000-4000-8000-111122223333",
       "lockExpiresAt": "2026-11-18T05:15:00-03:00"
     }
   }
   ```
7. **401 Unauthorized — Token Scheduler Inválido ou Ausente:**
   `{"status": "UNAUTHORIZED", "message": "Credencial de agendamento inválida ou ausente.", "code": "SYNC_SCHEDULER_UNAUTHORIZED"}`

---

### 2.11. `POST /erp-products/sync/daily` (Sincronização Diária Idempotente ERP → Site às `08:00 BRT` `P-410`, `P-411`, `P-412`)
**Objetivo:** Executa o ciclo diário idempotente (agendado às **08:00 BRT**, `app.erp.sync.cron=${ERP_SYNC_CRON:0 0 8 * * *}`, `zone = "America/Sao_Paulo"`) entre `FITOHERB` (`ErpCatalogGateway`, somente leitura) e o PostgreSQL (`products`, `product_skus`), ocultando produtos com 100% dos SKUs inativos (`active = false`), recalculando variações ativas em Multi-SKU parcial, reativando e publicando imediatamente produtos ativos mesmo com `image_path = NULL` (`curationStatus = PENDING_IMAGE`), respeitando baseline (`erp_sync_state`) e `erp_ignored_catalog_codes`, disparando recarga em `fitoherb-ai` e enviando relatório *best-effort* por e-mail via `MailService.sendEmail(MailReq)` para `${app.erp.sync.report-email:}` (`ERP_SYNC_REPORT_EMAIL`, jamais hardcoded ou exposto na resposta HTTP).

- **Autenticação:** Header `X-Sync-Scheduler-Token` validado em tempo constante **OU** JWT `ROLE_ADMIN`. (`ROLE_USER`, `ROLE_SELLER` e anônimos: `403`/`401`.)
- **Query Params:** `ifRunning` (`"FAIL"` padrão -> `409`; `"ACCEPT"` -> `202 Accepted` com `status = "ALREADY_RUNNING"`).
- **Body (`DailySyncReq`, opcional `{}`):** `{"mode": "INCREMENTAL" | "STATUS_ONLY" | "INITIAL_BASELINE_SEED", "dryRun": false}` (`INITIAL_BASELINE_SEED` exclusivo `ROLE_ADMIN`).
- **Sucesso (`200 OK` — `ApiEnvelope<DailySyncRes>`):**
  ```json
  {
    "data": {
      "runId": "f3c2b1a0-4e21-4d77-9b21-98a1c02b1111",
      "mode": "INCREMENTAL",
      "status": "COMPLETED",
      "dryRun": false,
      "baselineCutoffAt": "2026-11-18T05:00:00-03:00",
      "checkedMappedSkus": 1040,
      "deactivatedProducts": 3,
      "partiallyDeactivatedProducts": 1,
      "reactivatedProducts": 2,
      "createdPendingProducts": 4,
      "ignoredCodesSkipped": 1,
      "aiCatalogRefreshed": true
    },
    "meta": { "timestamp": "2026-11-18T05:00:14-03:00", "durationMs": 1420, "triggerSource": "CLOUD_SCHEDULER" }
  }
  ```
- **Erros:** `400`, `401`, `403`, `409 (ERP_SYNC_ALREADY_RUNNING)`, `503 (ERP_CATALOG_UNAVAILABLE — preserva estado active atual)`.

---

### 2.12. `GET /erp-products/curation-pending` (Central de Curadoria Rápida `P-413`)
**Objetivo:** Lista paginada dos produtos ativos aguardando imagem (`curationStatus = PENDING_IMAGE`) para exibição automática ao entrar no `/admin` (`ROLE_ADMIN` e `ROLE_USER` apenas).

- **Autenticação:** Cookie `fitoherb_jwt` ou Bearer (`isAdminOrUser()`; `401` anônimo, `403` `ROLE_SELLER`).
- **Query Params:** `page` (default `0`), `size` (default `20`, máx. `50`), `onlyFallback` (`boolean`), `search` (`string` por nome ou `erpCode`).
- **Sucesso (`200 OK` — `ApiEnvelope<List<QuickCurationPendingItemRes>>`):**
  Cada item contém `slug`, `name`, `description`, `categorySlug`, `categoryName`, `supplierSlug`, `supplierName`, `active`, `curationStatus`, `fallbackCategoryWarning`, `fallbackSupplierWarning`, `imageUrl` (`null`), `topology`, `createdAt`, `skus[]` (`id`, `flavour`, `presentation`, `erpCode`, `erpInactive`, `erpInactiveConfirmed`, `erpDescription`), e `meta` inclui `pendingCount`, `fallbackItemsCount`, `totalElements`, `totalPages`. **Sem `createdBy`/`updatedBy`/`users` (`P-408`).**

---

### 2.13. `POST /erp-products/curation-pending/{slug}/ignore` (Descarte Auditável *"Ignorar / Não exibir no site"* `P-413`)
**Objetivo:** Oculta imediatamente o produto da vitrine (`active = false`) e do `CatalogIndex`, grava `curationStatus = IGNORED` e registra seus `erpCode`s em `erp_ignored_catalog_codes` (`source = 'ADMIN_IGNORED'`), impedindo ressincronização automática futura (`P-410`).

- **Autenticação:** `@PreAuthorize("@authorizationService.isAdminOrUser()")` (`401`/`403` para anônimo/`ROLE_SELLER`).
- **Path Param:** `slug` (`^[a-z0-9-]+$`). Body opcional: `{"reason": "..."}` (`@Size(max = 255)`).
- **Sucesso (`200 OK` — `ApiEnvelope<IgnoreCurationProductRes>`):** `{"data": {"slug": "...", "active": false, "curationStatus": "IGNORED", "ignoredErpCodes": [991045]}, "meta": {"timestamp": "...", "aiCatalogRefreshed": true}}`.
- **Erros:** `400`, `401`, `403`, `404`.

---

### 2.14. Referência Cruzada: `POST /api/v1/chat/catalog/refresh` (`fitoherb-backend-v2` → `fitoherb-ai`)
Especificação completa em [chatbot_assistant.md](./chatbot_assistant.md) (header `X-Internal-Refresh-Token` com `hmac.compare_digest`, 0 tokens LLM, Scale-to-Zero safe, TTL fallback passivo `3600s`).

---

## 3. Implementação no Frontend (Angular 18+ Standalone & Signals)

### 3.1. Serviços e Integração HTTP
- **`ProductsService` (`src/app/services/products/products.service.ts`):**
  - Atualizar `adminProducts` para `signal<PageResponse<ProductAdminRes> | null>(null)`.
  - Atualizar `getPaginated(...)` adicionando parâmetro opcional `erpStatuses: ErpMappingStatus[] = []`, anexando `?erpStatus=...` ao `HttpParams`.
  - `getBySlug(slug: string): Observable<ProductAdminRes>` para carregar os `skus[]` completos ao abrir edição se a linha da tabela precisar de refresh, mantendo `getGallery(...)` e `getProductsBySupplier(...)` inalterados com `ProductRes` (público).
  - `create(productReq: ProductReq, image: File)` e `update(slug: string, productReq: ProductReq, image: File | null)` serializando o part `product` com `skus[]` e `allowInactiveErp`.
- **`ErpProductsService` (`src/app/services/erp-products/erp-products.service.ts` — Novo):**
  - `search(params: { q: string; supplierSlug?: string; includeInactive?: boolean; excludeProductSlug?: string; page?: number; size?: number }): Observable<ApiEnvelope<ErpCatalogItemRes[]>>`
  - `getByErpCode(erpCode: number, excludeProductSlug?: string): Observable<ApiEnvelope<ErpCatalogItemRes>>`
  - `suggestVariants(req: SuggestVariantsReq): Observable<ApiEnvelope<SuggestVariantsRes>>`
  - Todas as chamadas usam `HttpClient` padrão (coberto automaticamente por `authInterceptor` com `withCredentials: true`).

### 3.2. Tratamento de Estado & Erros na UI (`AdminComponent` & `ModalEntityComponent`)
- **Estados Reativos (Signals):**
  - `erpSearchResults`, `isErpSearching`, `erpSearchError`, `selectedErpQueue`, `isSuggestingVariants`, `pendingInactiveConfirmation` (para fluxo `422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED`).
  - Na busca ERP dentro do `ModalEntityComponent`, usar `debounceTime(350)` + `distinctUntilChanged()` e só disparar HTTP quando `q.trim().length >= 2` ou `/^\d+$/.test(q.trim())` (evitando `400 Bad Request` no backend).
- **Correção Obrigatória em `AdminComponent.handleSave`:**
  - **Remover** a sobrescrita fixa `else if (status === 409 && type === 'Produtos') { this.showFeedback(409, 'Já existe um produto com este nome...'); }`.
  - Sempre priorizar `err.error?.message` para `409 Conflict` (exibindo tanto conflitos de slug quanto conflitos específicos de código ERP `"O código ERP '...' já está vinculado ao produto '...'."`).
  - Para `400 Bad Request` com `err.error?.errors`, mapear mensagens por campo/índice `skus[i]` dentro do próprio `ModalEntityComponent` sem fechar o modal nem perder os dados digitados!
  - Para `422 Unprocessable Entity`:
    - Se `err.error?.code === 'ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED'`: abrir confirmação explícita exibindo os códigos `details.inactiveErpCodes` (`inativo_pro = 1`); se operador confirmar, reenviar exatamente a mesma requisição com `allowInactiveErp: true`.
    - Caso contrário (`ERP_CODE_NOT_FOUND`, `PRODUCT_TOPOLOGY_INVALID`, duplicidade interna): exibir `err.error?.message` em alerta inline no modal mantendo o formulário editável.
  - Para `503 Service Unavailable`: exibir feedback claro informando indisponibilidade da base espelho ERP sem limpar o formulário.

### 3.3. Tipagem TypeScript (`src/app/types/products/`)

```typescript
export type ProductTopology = 'SIMPLE' | 'FLAVOUR_ONLY' | 'PRESENTATION_ONLY' | 'MATRIX';
export type ErpMappingStatus = 'UNMAPPED' | 'COMPLETE' | 'INACTIVE_ALERT';

export interface ProductSkuReq {
  erpCode: number;
  flavour: string | null;
  presentation: string | null;
}

export interface ProductReq {
  name: string;
  description?: string;
  categorySlug: string;
  supplierSlug: string;
  allowInactiveErp?: boolean;
  skus: ProductSkuReq[];
}

export interface ProductSkuRes {
  id: string;
  flavour: string | null;
  presentation: string | null;
  erpCode: number | null;
  erpInactive: boolean;
  erpInactiveConfirmed: boolean;
  erpDescription?: string | null;
}

/** DTO público da vitrine (/products/gallery) — estritamente sem dados ERP */
export interface ProductRes {
  name: string;
  imageUrl: string;
  description?: string;
  flavours: string[];
  presentation?: string[];
  slug: string;
  category: ProductCategoryRes;
  supplier: SupplierRes;
  createdAt: string;
}

/** DTO administrativo (/products e /products/{slug}) */
export interface ProductAdminRes extends ProductRes {
  topology: ProductTopology;
  erpStatus: ErpMappingStatus;
  skuCount: number;
  primaryErpCode: number | null;
  skus: ProductSkuRes[];
}

export interface ErpCatalogItemRes {
  erpCode: number;
  erpDescription: string;
  ean: string | null;
  erpBrand: string | null;
  erpSupplier: string | null;
  inativoPro: boolean;
  inExterno01: boolean;
  alreadyMapped: boolean;
  mappedProductSlug: string | null;
  mappedProductName: string | null;
  mappedFlavour: string | null;
  mappedPresentation: string | null;
}

export interface SuggestVariantsReq {
  erpCodes: number[];
  excludeProductSlug?: string;
}

export interface SuggestedVariantItem {
  erpCode: number;
  erpDescription: string;
  suggestedFlavour: string | null;
  suggestedPresentation: string | null;
  inativoPro: boolean;
  inExterno01: boolean;
  alreadyMappedElsewhere: boolean;
  conflictingProductName: string | null;
  packageWarning: string | null;
}

export interface SuggestVariantsRes {
  suggestedTopology: ProductTopology;
  hasInactiveItems: boolean;
  hasConflictingItems: boolean;
  items: SuggestedVariantItem[];
}

export interface ApiEnvelope<T> {
  data: T;
  meta: {
    timestamp: string;
    page?: number;
    size?: number;
    totalElements?: number;
    totalPages?: number;
    lastSyncedAt?: string;
    count?: number;
  };
}

export interface ApiErrorRes {
  status: string;
  message: string;
  code?: string;
  details?: {
    inactiveErpCodes?: number[];
    erpCode?: number;
    conflictingProductName?: string;
    conflictingProductSlug?: string;
    activeRunId?: string;
    lockExpiresAt?: string;
  };
  errors?: Record<string, string>;
}

// === Adendo Onda 4 (US-P7 / US-P8) ===
export type ProductCurationStatus = 'PENDING_IMAGE' | 'COMPLETED' | 'IGNORED';
export type DailySyncMode = 'INCREMENTAL' | 'STATUS_ONLY' | 'INITIAL_BASELINE_SEED';

export interface ProductAdminResWave4Extension {
  active: boolean;
  curationStatus: ProductCurationStatus;
}

export interface QuickCurationPendingItemRes {
  slug: string;
  name: string;
  description: string | null;
  categorySlug: string;
  categoryName: string;
  supplierSlug: string;
  supplierName: string;
  active: boolean;
  curationStatus: ProductCurationStatus;
  fallbackCategoryWarning: boolean;
  fallbackSupplierWarning: boolean;
  imageUrl: string | null;
  topology: ProductTopology;
  createdAt: string;
  skus: ProductSkuRes[];
}

export interface IgnoreCurationProductRes {
  slug: string;
  active: boolean;
  curationStatus: ProductCurationStatus;
  ignoredErpCodes: number[];
}

export interface DailySyncRes {
  runId: string;
  mode: DailySyncMode;
  status: 'COMPLETED' | 'ALREADY_RUNNING';
  dryRun: boolean;
  baselineCutoffAt: string | null;
  checkedMappedSkus: number;
  deactivatedProducts: number;
  partiallyDeactivatedProducts: number;
  reactivatedProducts: number;
  createdPendingProducts: number;
  ignoredCodesSkipped: number;
  aiCatalogRefreshed: boolean;
}
```
> **Serviços Angular (`US-P7`/`US-P8`):** `ErpProductsService` inclui `getCurationPending`, `ignoreCurationPending` e `triggerDailySync` (`ROLE_ADMIN` apenas); `ProductsService.getPaginated` suporta `active` e `curationStatuses`; `AdminComponent` nunca dispara `getCurationPending` quando `currentUserRole() === 'SELLER'`; `ProductRes.imageUrl` aceita `string | null` com fallback `'assets/images/fitoherb-leaf-icon.png'`.
