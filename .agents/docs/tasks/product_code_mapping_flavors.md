# Entidade / Feature: Mapeamento de Código ERP por SKU, Sabores/Apresentações e Sincronização Prod → Local (`product_code_mapping_flavors`)

Este documento centraliza todo o planejamento, as especificações funcionais por User Story (`US-P1` a `US-P8`) e as etapas de execução para governança de códigos ERP por SKU, sincronização diária ativo/inativo e curadoria rápida no ecossistema Fitoherb (`fitoherb-backend-v2`, `fitoherb-frontend-v2`, `fitoherb-ai`).

---

## 1. Dúvidas Resolvidas e Dúvidas em Aberto (Especificação)

### 1.1 Premissas e Decisões Recomendadas Assumidas (Base para Etapa 2)
- **Decisão D-01 (Granularidade 1:1 com ERP Atrio):**
  - *Contexto:* No ERP Atrio (`[dbo].[Produtos]` e `[Externo01].[Produto]`), cada combinação física de sabor e/ou apresentação possui seu próprio `Id_Pro` (ex.: `100% Pure Whey 900g` possui 3 códigos distintos; `B.O.P.E` possui 6 códigos para `150g`/`300g` × 3 sabores; `Stevita Líquido` possui `580000` e `580001`).
  - *Decisão:* Um código `Id_Pro` vincula-se exclusivamente a **um único SKU** em todo o catálogo do site (`P-404`), e um produto no site pode conter 1 SKU simples ou N SKUs de variação (`P-405`).
- **Decisão D-02 (Preservação de `products.flavours` e `products.presentation` como Projeção Saneada):**
  - *Contexto:* A vitrine pública (`ItemCardGalleryComponent`, `ModalGalleryComponent`), a busca administrativa/galeria em `ProductService` e o serviço `CatalogIndex` do `fitoherb-ai` leem diretamente as listas `flavours` e `presentation` da tabela `products`.
  - *Decisão:* As colunas `flavours` e `presentation` de `products` e o contrato público de `ProductRes` permanecem preservados como listas atômicas saneadas e **deduplicadas** (`P-401`, `P-408`), sincronizadas automaticamente a partir dos SKUs do produto.
- **Decisão D-03 (Segurança Prod → Local na Curadoria):**
  - *Contexto:* O workflow `.github/workflows/backup.yml` exporta o banco de produção via `pg_dump --clean --if-exists --inserts`.
  - *Decisão:* O clone para `fitoherb-v2` local e toda a curadoria (`US-P1`) nunca tocam produção diretamente; produção receberá somente pacote idempotente validado após aceite (`P-400`, `P-409`).
- **Decisão D-04 (Protocolo Zero Chutes + Aliases de Marca):**
  - *Contexto:* Existem divergências nominais (ex.: `Arrebite` no site vs `GUARANAPIS` no ERP) e abreviações (`CHOCO`, `CAPSGEL`, `DISP.`, `STAND UP`).
  - *Decisão:* Nenhum código ERP é assumido por palpite; matches ambíguos passam por pesquisa externa na web e, persistindo dúvida, seguem para Fila de Decisão Humana (`P-409`). A busca ERP no admin não bloqueia por nome exato de marca (`P-407`).
- **Decisão D-05 (Segregação Vitrine × Admin):**
  - *Contexto:* O site é um catálogo institucional B2B/B2C sem exposição de preço/estoque (`P-302`).
  - *Decisão:* `Id_Pro`, `inativo_pro`, alertas ERP e `Estoque` nunca são expostos na vitrine pública nem no Chatbot (`P-408`).
- **Decisão D-06 (Tratamento de Erros sem Mascaramento no Backend e UI):**
  - *Contexto:* Observou-se que `ProductService.updateProductBySlug` captura exceções genéricas convertendo em HTTP `500` e `AdminComponent.handleSave` converte qualquer HTTP `409` em mensagem fixa de conflito de nome/fornecedor.
  - *Decisão:* Ambas as camadas devem preservar e exibir a mensagem específica de conflito de código ERP (`P-404`) e validações `400`/`422`.

### 1.2 Decisões Homologadas no Checkpoint (Etapa 2 — `A1` a `A4`)
- **Decisão Q-01 / `A1` (Espelho Postgres Apenas Temporário + Runtime Direto SQL Server com Cache RAM):**
  - *Resolução do Usuário:* `"faça o 1 mas quero isso apenas pra clonar e sincronizar, depois quero que vc tire ele do banco postgres do site"`.
  - *Implementação Arquitetural:* As tabelas de espelho/curadoria (`erp_catalog_items`, `supplier_brand_aliases`, `human_review_queue`, `erp_mapping_audit`) são criadas **exclusivamente em ambiente local** durante `US-P1` e **removidas (`DROP TABLE`) do banco PostgreSQL `fitoherb-v2` ao término do sync/mapeamento**. Em runtime, `fitoherb-backend-v2` consulta o SQL Server 2008 R2 (`FITOHERB`) via `ErpCatalogGateway` (`net.sourceforge.jtds:jtds:1.3.1` com `ssl=off` + `PreparedStatement` + credencial `SELECT`-only) alimentando cache snapshot em memória RAM (~2 MB, TTL 15 min) e mantendo apenas `products` + `product_skus` no PostgreSQL.
- **Decisão Q-02 / `A2` (Política para SKUs Inativos no ERP `inativo_pro = 1`):**
  - *Resolução do Usuário:* `"caso ache que um produto do site será vinculado a um item inativo, separe uma lista e me avise"`.
  - *Implementação:* Durante `US-P1`, matches com `inativo_pro = 1` **não** são gravados automaticamente — ficam em lista separada (`INACTIVE_MATCH_ALERTS`) para revisão explícita do usuário. Em runtime (`POST`/`PUT`), exige confirmação explícita (`422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED` → diálogo → `allowInactiveErp = true`).
- **Decisão Q-03 & Q-04 / `A3` (Rollout e Status do Catálogo):**
  - *Resolução do Usuário:* `"todos os produtos do site em teoria estão ativos"`. Concluir 100% da curadoria local e notificar pendências/inativos ao usuário antes de ativar trava rígida `NOT NULL` em produção (`app.erp.strict-sku-required`).
- **Decisão Q-05 & Q-06 / `A4` (UI da Tabela Admin & Embalagens `UN` vs `DISP.`/`CX`):**
  - *Resolução do Usuário:* Adotada a Opção A em ambas — código direto em simples / badge `"N SKUs · código"` + popover `position: fixed` em Multi-SKU; divergências `UN` vs `DISP.`/`CX` vão para `HUMAN_REVIEW_QUEUE` na curadoria e emitem `packageWarning` na importação em lote.

### 1.3 Premissas e Dúvidas em Aberto — Onda 4 (`US-P7` e `US-P8`: `P-406`, `P-410` a `P-413`)
- **Premissa D-07 (Conciliação `A2` + Vitrine Automática `P-411`):**
  - *Contexto:* `A2` definiu alerta/confirmação para `inativo_pro = 1` sem ocultação automática; a nova demanda (`US-P7`) exige sincronização diária automática para ocultar produtos inativados da vitrine/Chatbot e publicar produtos ativos imediatamente.
  - *Resolução Funcional:* Vínculos manuais em `POST`/`PUT` preservam a confirmação explícita (`allowInactiveErp = true`), enquanto a sincronização diária passa a controlar `products.active` (`true`/`false`) e a projeção ativa de sabores/apresentações em Multi-SKU parcial, sem jamais deletar fotos ou `product_skus`.
- **Premissa D-08 (Publicação Imediata Sem Imagem e Fallback Existente `P-412`):**
  - *Contexto:* `Product.imagePath` já é nullable na entidade e `ItemCardGalleryComponent`/`ModalGalleryComponent` + `CatalogIndex` já toleram `imageUrl = null` com fallback `'assets/images/fitoherb-leaf-icon.png'`.
  - *Resolução Funcional:* Criação automática via sync pode publicar com `image_path = NULL`, mantendo upload obrigatório (`IMG-001`) apenas para cadastros manuais e gerando `QuickCurationPendingItem` (`PENDING_IMAGE`).
- **Dúvidas Residuais Pendentes de Resposta Humana (Antes da Etapa 2/3 de `US-P7` e `US-P8`):**
  - **Dúvida Q-07 (Baseline dos ~650 itens históricos ativos do ERP):** Na virada pós-`US-P1`, adotar corte de baseline (não importar automaticamente o passivo pré-existente fora do site, sincronizando apenas catálogo mapeado + novos itens pós-corte)? Exigir apenas `Empresa_Pro = 1` + `inativo_pro = 0` em `[dbo].[Produtos]` ou também presença em `[Externo01].[Produto]`?
  - **Dúvida Q-08 (Granularidade de Produtos Inéditos Multi-SKU no Sync):** Novo produto com múltiplos `Id_Pro` deve nascer inicialmente 1:1 (Produto Simples por código) para ajuste no modal (zero chutes) ou tentar agrupamento determinístico por nome-base + marca?
  - **Dúvida Q-09 (Precedência de `allowInactiveErp = true` vs. `P-411`):** Confirmado que produto manualmente vinculado a SKU inativo permanece oculto na vitrine (`active = false`) até ser reativado no ERP?
  - **Dúvida Q-10 (Janela Horária, Fallbacks e Edição Parcial sem Foto):** Confirmar horário diário (ex.: `05:00` BRT), uso de categoria/fornecedor fallback configuráveis quando sem match exato, e permanência na fila de pendências até envio da foto ou descarte auditável.

---

## 2. Tarefas e Etapas de Desenvolvimento

### Tarefa 1 (`US-P1` `[PARALLEL]`): Clonagem Prod → Local, Saneamento de Variações Legadas e Mapeamento Assistido Site × ERP (Zero Chutes)

**Descritivo Detalhado:**
Clonar o dump do banco PostgreSQL de produção (obtido via workflow `.github/workflows/backup.yml`) para a base local `fitoherb-v2` com isolamento total de produção (`P-400`), aplicar rotina determinística de saneamento nos 1.040 produtos para decompor strings concatenadas em `flavours` (90 produtos) e `presentation` (87 produtos, incluindo os 2 com ambos: `B.O.P.E` e `Dado de Creatina`) em valores atômicos limpos (`P-401`), e executar pipeline de matching assistido contra `[dbo].[Produtos]` (6.946 registros) e `[Externo01].[Produto]` (2.194 registros) do ERP Atrio. O matching deve aplicar tabela de aliases de marca (ex.: `Arrebite` ↔ `GUARANAPIS`), expansão controlada de abreviações (`CHOCO`, `CAPSGEL`, `DISP.`, `STAND UP`), pesquisa externa na web para casos duvidosos e separação rigorosa de qualquer ambiguidade para a Fila de Decisão Humana (`P-409`).

**Critérios de Aceite:**
- [ ] (`P-400`) Dump de produção restaurado exclusivamente no banco local `fitoherb-v2` (com snapshot de segurança local prévio), preservando os 1.040 produtos, 6 categorias e 44 fornecedores sem nenhuma escrita em produção.
- [ ] (`P-401`) Todos os valores legados com `" e "`, `"/"` ou ponto final residual (ex.: `{"Baunilha","Chocolate e Morango."}`, `{"25ml e 60ml."}`) são desmembrados em variações atômicas distintas, higienizadas e sem duplicatas.
- [ ] (`P-409`) Produtos com correspondência exata inequívoca recebem proposta/pré-vínculo auditável (`AUTO_EXACT`); casos ambíguos são investigados via pesquisa web (`WEB_VERIFIED`) e quaisquer itens ainda com dúvida, múltiplos candidatos, ausência no ERP ou incerteza de embalagem (`UN` vs `DISP.`) entram na **Fila de Decisão Humana** sem nenhum código chutado.
- [ ] (`P-404`, `P-405`) O resultado da curadoria respeita unicidade 1:1 de `Id_Pro` por SKU e cobre as 4 topologias (865 simples, apenas sabor, apenas apresentação e matriz sabor × apresentação).

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Dados / Script Python]:**
  - [ ] (`P-400`) Criar script seguro de restauração local (`pg_restore`/`psql`) sobre `fitoherb_backup.sql` (gerado por `.github/workflows/backup.yml`) com snapshot de segurança local prévio e trava obrigatória de host (`localhost`/`127.0.0.1` apenas), abortando qualquer operação caso detecte host remoto ou violação de integridade.
  - [ ] (`P-400`) Validar restauração local dos 1.040 produtos, 6 categorias e 44 fornecedores em `fitoherb-v2` sem interferir em schemas externos.
  - [ ] (`P-403`, `P-408`) Implementar extrator somente-leitura (`WITH (NOLOCK)`) em SQL Server 2008 R2 (`FITOHERB`: `[dbo].[Produtos]` + `[Externo01].[Produto]` com `Empresa_Pro = 1`), excluindo estritamente `Estoque` e valores monetários, para popular `erp_catalog_items` e seed de `supplier_brand_aliases` (ex.: `Arrebite` ↔ `GUARANAPIS`).
  - [ ] (`P-401`) Implementar rotina determinística de saneamento em `flavours` (90 produtos) e `presentation` (87 produtos), quebrando conectivos (`" e "`, `" / "`, vírgulas), removendo ponto final residual (`.`), espaços extras e duplicatas, gerando relatório de validação (0 concatenações residuais).
  - [ ] (`P-409`) Implementar pipeline de curadoria em 3 níveis sem suposições: Nível 1 (`AUTO_EXACT` via staging aliases + dicionário `CHOCO`, `CAPSGEL`, `DISP.`, `STAND UP`, gramaturas/volumes **apenas para `inativo_pro = 0`**), Nível 2 (`WEB_VERIFIED` com evidência documental de catálogo/EAN) e Nível 3 (`HUMAN_REVIEW_QUEUE` + **lista separada `INACTIVE_MATCH_ALERTS`** para 0 candidatos, múltiplos candidatos, divergência `UN` vs `DISP.`/`CX` ou qualquer match `inativo_pro = 1`, sem chutes).
  - [ ] (`P-404`, `P-405`) Validar que o mapeamento consolidado respeita unicidade global 1:1 de `Id_Pro` por `ProductSku` e cobre exatamente as 4 topologias (`SIMPLE`, `FLAVOUR_ONLY`, `PRESENTATION_ONLY`, `MATRIX`).
  - [ ] (`A1`) **Limpeza Pós-Sync Obrigatória:** Após gravar e validar `product_skus` e arrays saneados em `products`, executar `DROP TABLE` das tabelas temporárias de curadoria (`erp_catalog_items`, `supplier_brand_aliases`, `human_review_queue`, `erp_mapping_audit`) no PostgreSQL `fitoherb-v2` local, mantendo apenas as tabelas do site.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4, validando integridade dos 1.040 produtos locais, ausência de concatenados residuais e zero duplicidade de `Id_Pro`.)*

---

### Tarefa 2 (`US-P2` `[PARALLEL]`): Obrigatoriedade, Validação contra o ERP Atrio e Exibição Admin do Código ERP — Produto Simples (MVP Core)

**Descritivo Detalhado:**
Implementar a base de domínio, contratos de API, persistência e interface administrativa para que todo cadastro (`POST /products`) e edição (`PUT /products/{slug}`) de **produto simples** exija um código `Id_Pro` válido, existente no catálogo de referência do ERP Atrio e único em todo o catálogo do site (`P-402`, `P-403`, `P-404`). No painel `/admin`, a tabela `Produtos` (`AdminComponent` / `DynamicTableComponent`) deve exibir o código ERP e permitir pesquisar produtos pelo `Id_Pro` (`P-408`), garantindo tratamento correto de exceções no backend (`updateProductBySlug`) e mensagens reais de conflito 409/422 no frontend.

**Critérios de Aceite:**
- [ ] (`P-402`) Tentativa de criar ou atualizar produto simples sem `Id_Pro`, com formato não numérico ou `<= 0` é bloqueada com HTTP `400 Bad Request` (`RestValidationErrorMessage`) e destaque visual do campo no `ModalEntityComponent`.
- [ ] (`P-403`) Tentativa de salvar `Id_Pro` inexistente no catálogo espelhado do ERP Atrio é rejeitada com erro claro (`422` / `404`) informando que o código não existe no ERP.
- [ ] (`P-404`) Tentativa de usar `Id_Pro` já vinculado a outro produto retorna HTTP `409 Conflict` indicando o nome do produto conflitante; `updateProductBySlug` não mascara esse `409` como erro `500` e `AdminComponent` exibe a mensagem específica retornada pela API.
- [ ] (`P-408`) A listagem administrativa (`GET /api/products` e tabela `Produtos`) exibe a coluna de código ERP e permite localizar o produto digitando o `Id_Pro` na barra de busca global, mantendo `Id_Pro` omitido na vitrine pública (`GET /api/products/gallery`).

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-403`, `P-405`, `A1`) Criar entidade JPA `ProductSku` (`product_skus` com `erp_inactive`, `erp_inactive_confirmed`, `erp_last_verified_at`), DTOs internos ERP em memória (`ErpCatalogItemSnapshot`), registro de aliases versionado em configuração (`BrandAliasProperties`), enums `ProductTopology` e `ErpMappingStatus` em `enums/`, e associação `@OneToMany` em `Product.java` (**zero entidades/tabelas ERP persistidas em PostgreSQL em runtime**).
  - [ ] Criar `ProductSkuRepository` com consultas de colisão por `erpCode` (`product_id <> :currentProductId`).
  - [ ] (`P-403`, `P-404`, `P-406`) Criar `UnprocessableEntityException` e `ServiceUnavailableException` em `exceptions/`; evoluir `RestErrorMessage.java` com campos `@JsonInclude(NON_NULL)` `code` e `details` (mantendo construtor `(HttpStatus, String)`); adicionar handlers `422`, `503` e inspeção de constraint `uk_product_skus_erp_code` em `DataIntegrityViolationException` no `RestExceptionHandler.java`.
  - [ ] (`P-402`, `P-408`) Atualizar `ValidationConstants.java` (`MAX_SKUS_PER_PRODUCT = 100`, `MAX_VARIANT_LENGTH = 120`); criar `ProductSkuReq.java`, `ProductSkuRes.java` e `ProductAdminRes.java` anotados com `@Schema`; atualizar `ProductReq.java` (`skus`, `allowInactiveErp`), mantendo `ProductRes.java` estritamente público.
  - [ ] (`P-401`, `P-402`, `P-403`, `P-404`, `A1`) Criar `ProductVariantSanitizer`, interface `ErpCatalogGateway`, implementação `ErpSqlServerGateway` (`net.sourceforge.jtds:jtds:1.3.1` com `ssl=off`, `PreparedStatement`, `WITH (NOLOCK)`, credencial `SELECT`-only) + `ErpCatalogCacheService` (snapshot em RAM com TTL configurável e fallback por lookup pontual `Id_Pro`) + `ErpCatalogValidationService` (`503` se ERP indisponível com cache frio, `422` se inexistente/inativo sem confirmação, `409` se vinculado a outro produto).
  - [ ] (`P-404`, `P-408`) Atualizar `ProductMapper.java` (`entityToPublicRes` vs `entityToAdminRes`) e `ProductService.java` (`createProduct`, `updateProductBySlug`, `getAllProductsPaginated`, `getProductBySlug`), ampliando `buildProductSpecification` (apenas no fluxo admin) para buscar por `erpCode` via `EXISTS` sem duplicar linhas na paginação, e **removendo o `try/catch (Exception)` genérico de `updateProductBySlug`** para não mascarar `409`/`422` como `500`.
  - [ ] Atualizar `ProductController.java` (`@RequestMapping("/products")`) para retornar `Page<ProductAdminRes>` em `GET /products` e `ProductAdminRes` em `GET /products/{slug}`, com anotações OpenAPI 3 (`@Operation`, `@ApiResponses` `400`/`409`/`422`/`503`).
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] Atualizar tipagens em `src/app/types/products/` (`ProductSkuReq`, `ProductReq`, `ProductSkuRes`, `ProductAdminRes`, `ApiErrorRes`).
  - [ ] Atualizar `ProductsService` (`src/app/services/products/products.service.ts`) para `adminProducts` e `getBySlug` consumirem `ProductAdminRes`.
  - [ ] (`P-402`) Atualizar `ModalEntityComponent` (`src/app/views/admin/components/modal-entity/`) para exigir campo numérico `erpCode` (`> 0`) em Produto Simples com feedback de erro por campo (`400`/`422`).
  - [ ] (`P-404`, `P-408`) Atualizar `AdminComponent` (`src/app/views/admin/admin.component.ts`) exibindo coluna de código ERP na tabela `Produtos` e corrigindo `handleSave` para renderizar `err.error?.message` em respostas `409` sem sobrescrever com mensagem genérica de slug.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 com casos Happy Path e Edge Cases para Produto Simples.)*

---

### Tarefa 3 (`US-P3`): Gestão de Códigos ERP por Sabor e Apresentação — Matriz SKU × Variações

**Descritivo Detalhado:**
Evoluir o modelo de produto, DTOs de requisição/resposta e o formulário administrativo (`ModalEntityComponent`) do modelo atual baseado em strings separadas por vírgula para uma gestão estruturada de **SKUs de Produto**, suportando integralmente todas as 4 topologias (`P-405`): Produto Simples (1 SKU), Somente Sabor (`100% Pure Whey 900g`), Somente Apresentação (`Stevita Líquido`) e Matriz Sabor × Apresentação esparsa ou completa (`B.O.P.E`, `Dado de Creatina`). Cada SKU ativo possui validação individual de obrigatoriedade, existência no ERP e unicidade global (`P-402`, `P-403`, `P-404`), com reconciliação atômica em edições (incluindo troca de códigos entre variações do mesmo produto) e projeção deduplicada em `flavours` e `presentation` (`P-401`).

**Critérios de Aceite:**
- [ ] (`P-405`) O formulário e a API aceitam e validam os 4 modos estruturais (Simples, Sabor, Apresentação, Matriz Sabor × Apresentação inclusive matriz esparsa), bloqueando misturas inconsistentes ou produto com zero SKUs (`422`).
- [ ] (`P-402`, `P-403`) Cada linha/variação ativa exige `Id_Pro` válido no ERP Atrio, retornando erro apontando qual variação está incompleta ou inválida.
- [ ] (`P-404`) O sistema impede duplicidade de `Id_Pro` no mesmo produto, impede duplicidade de combinação normalizada `(sabor, apresentação)` no mesmo produto e impede colisão com outro produto (`409`), mas permite trocar códigos entre dois sabores do mesmo produto dentro de um único `PUT /products/{slug}`.
- [ ] (`P-401`) Ao salvar produto Multi-SKU (ex.: 2 apresentações × 3 sabores), os eixos `flavours` e `presentation` armazenados/retornados para consumo público são sanitizados e **sem duplicatas** (3 sabores distintos, 2 apresentações distintas).

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-405`) Implementar `ProductTopologyValidator` garantindo que todo produto possua `>= 1` SKU e obedeça estritamente uma única topologia (`SIMPLE`, `FLAVOUR_ONLY`, `PRESENTATION_ONLY`, `MATRIX` esparsa), rejeitando inconsistências com `422 PRODUCT_TOPOLOGY_INVALID`.
  - [ ] (`P-404`) Validar unicidade interna no payload (`erpCode` repetido -> `422 DUPLICATE_ERP_CODE_IN_PAYLOAD`; combinação normalizada `(flavour_normalized, presentation_normalized)` repetida -> `422 DUPLICATE_VARIANT_COMBINATION`).
  - [ ] (`P-404`, `C-05`) Implementar reconciliação atômica em `ProductService.updateProductBySlug` dentro de `@Transactional`: validar conflito apenas contra `product_id <> currentProduct.id`, remover/atualizar SKUs substituídos e executar `entityManager.flush()` antes de gravar novos/permutados `erpCode`s, permitindo troca de códigos entre variações do mesmo produto sem falso `409`.
  - [ ] (`P-401`) Implementar sincronização automática da projeção `Product.flavours` e `Product.presentation` (usando `LinkedHashSet` sobre SKUs ordenados por `sortOrder`) garantindo arrays atômicos higienizados e sem duplicatas para matrizes sabor × apresentação.
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] (`P-405`) Evoluir `ModalEntityComponent` para suportar seleção das 4 topologias (`Simples`, `Somente Sabor`, `Somente Apresentação`, `Matriz Sabor × Apresentação`) e grade reativa de SKUs (`flavour`, `presentation`, `erpCode`), permitindo adicionar/remover combinações (matriz esparsa) e validar cada linha.
  - [ ] (`P-405`) Atualizar `AdminComponent.handleSave` removendo o `split(',')` legado de strings e montando `ProductReq.skus[]` diretamente do formulário estruturado.
  - [ ] (`P-408`) Atualizar renderização da coluna ERP em `DynamicTableComponent` / `AdminComponent` para exibir código direto em simples e badge resumido (`N SKUs · <primaryErpCode>`) com tooltip/expansão dos pares Variação → Código em Multi-SKU.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 cobrindo os 4 tipos estruturais e edge cases de edição/troca de código.)*

---

### Tarefa 4 (`US-P4`): Busca Direta e Importação em Lote de Variações do ERP Atrio no Painel Administrativo

**Descritivo Detalhado:**
Integrar ao modal de criação/edição de produtos no painel `/admin` (`ModalEntityComponent`) um buscador e importador em lote conectado ao catálogo espelhado do ERP Atrio (`P-407`). O operador administrativo poderá pesquisar por `Id_Pro`, `EAN`, descrição ou marca/fornecedor (sem restrição rígida pelo nome da marca no site, suportando aliases como `Arrebite` ↔ `GUARANAPIS`), visualizar status ativo/inativo (`P-406`) e eventual vínculo prévio em outro produto, selecionar múltiplos SKUs e importá-los em lote com sugestão automática de sabores e apresentações (expandindo abreviações conhecidas do ERP) para revisão antes de salvar.

**Critérios de Aceite:**
- [ ] (`P-407`) Endpoints e UI de busca ERP permitem filtrar por código `Id_Pro`, `EAN`, descrição ou marca/fornecedor ERP sem ocultar resultados por divergência nominal de marca (ex.: `Arrebite` vs `GUARANAPIS`).
- [ ] (`P-407`, `P-404`) A lista de resultados da busca ERP exibe `Id_Pro`, descrição, EAN, marca/fornecedor, badge de status (`Ativo`/`Inativo no ERP`) e indicador bloqueante quando o código já pertence a outro produto do site (`alreadyMapped`).
- [ ] (`P-407`, `P-401`) A importação em lote popula automaticamente os SKUs selecionados na grade do formulário com `Id_Pro`, sabor e apresentação sugeridos e saneados (ex.: `CHOCO` → `Chocolate`), permitindo edição/remoção pelo operador antes do envio.
- [ ] (`P-406`) Itens com `inativo_pro = 1` exibem alerta visual claro durante a busca e na grade antes da confirmação de salvamento.
- [ ] (`P-408`) Rotas de busca ERP exigem autenticação administrativa (`ROLE_ADMIN`/`ROLE_USER`), retornando `401`/`403` para não autenticados ou `ROLE_SELLER`.

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] Criar wrapper `ApiEnvelope<T>` (`data`, `meta`) em `dtos/responses/` conforme padrão `backend-api-contract-rules.md`.
  - [ ] Criar DTOs `ErpCatalogItemRes`, `SuggestVariantsReq`, `SuggestVariantsRes`, `SuggestedVariantItemRes` em `dtos/` com anotações `@Schema`.
  - [ ] (`P-407`) Implementar `ErpVariantSuggestionService` determinístico (0 tokens de LLM) para expandir abreviações do ERP (`CHOCO`, `MOR`, `BAUN`, `CAPSGEL`, `DISP.`, `STAND UP`), extrair gramaturas/volumes (`900g`, `150g`, `300g`, `25ml`, `60ml`), inferir `suggestedTopology` e emitir `packageWarning` em embalagens coletivas (`DISP.`/`CX`).
  - [ ] (`P-407`, `P-408`) Criar `ErpProductService` e `ErpProductController` (`@RequestMapping("/erp-products")`) implementando `GET /erp-products/search` (validação `q >= 2` chars ou dígito numérico, boost não-restritivo via `supplier_brand_aliases`, `includeInactive`, `excludeProductSlug`, `page`, `size`), `GET /erp-products/{erpCode}` e `POST /erp-products/suggest-variants`, todos protegidos por `@PreAuthorize("@authorizationService.isAdminOrUser()")` e documentados no Swagger.
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] Criar `ErpProductsService` (`src/app/services/erp-products/erp-products.service.ts`) e tipagens `ErpCatalogItemRes`, `SuggestVariantsReq`, `SuggestVariantsRes`, `ApiEnvelope<T>`.
  - [ ] (`P-407`) Integrar painel/buscador e importador em lote ERP dentro do `ModalEntityComponent` (aderente ao Design Plan da Etapa 2): busca com debounce `350ms`, indicador `Ativo`/`Inativo no ERP`, trava visual `"Já vinculado ao produto X"` (`alreadyMapped`), seleção múltipla e acionamento de `POST /erp-products/suggest-variants`.
  - [ ] (`P-407`, `P-406`) Preencher automaticamente a grade de `ProductSku` com as sugestões retornadas mantendo edição livre pelo operador e exibindo alertas de `packageWarning` e `inativoPro` antes do salvamento.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 validando busca cross-brand, bloqueio de já mapeados e fluxo de importação em lote.)*

---

### Tarefa 5 (`US-P5` `[PARALLEL]`): Compatibilidade e Saneamento na Vitrine Pública e no `CatalogIndex` (`fitoherb-ai`)

**Descritivo Detalhado:**
Garantir que a evolução do catálogo para Multi-SKU com códigos ERP preserve 100% da experiência e integridade da vitrine pública (`ItemCardGalleryComponent`, `ModalGalleryComponent`) e do Assistente Virtual Gemini (`fitoherb-ai` / `CatalogIndex`). Confirmar que o endpoint público `GET /api/products/gallery` nunca exponha dados internos do ERP (`P-408`), que a busca textual da galeria continue funcionando sobre sabores/nomes higienizados e que o `CatalogIndex` carregue e ranqueie sabores e apresentações saneadas mantendo estrita conformidade com as regras `P-302`, `P-304` e `P-305`.

**Critérios de Aceite:**
- [ ] (`P-408`) Resposta JSON de `GET /api/products/gallery` (e snippets do `fitoherb-ai`) não expõe `Id_Pro`, status `inativo_pro`, alertas ERP ou `Estoque`.
- [ ] (`P-401`, `P-408`) `ItemCardGalleryComponent` e `ModalGalleryComponent` exibem chips de sabores e apresentações limpos, atômicos e sem duplicatas (mesmo em produtos com matriz 2×3 como `B.O.P.E`).
- [ ] (`P-401`, `P-302`, `P-304`, `P-305`) O `CatalogIndex` (`fitoherb-ai`) carrega `flavours` e `presentation` saneados do PostgreSQL, encontra produtos ao buscar por sabor (ex.: `"whey morango"`) ou apresentação (ex.: `"25ml"`) sem viés de marca e sem vazar informações comerciais restritas.

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-408`) Garantir que `ProductController.getProductGallery` (`GET /products/gallery`) retorne exclusivamente `Page<ProductRes>` via `ProductMapper::entityToPublicRes` e que `buildProductSpecification` no modo público pesquise em `flavours` e `presentation` sem jamais consultar ou expor `product_skus` / `erpCode` / `Estoque`.
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] (`P-401`, `P-408`) Validar `ItemCardGalleryComponent` e `ModalGalleryComponent` garantindo exibição de chips de `flavours` e `presentation` atômicos e deduplicados (ex.: `B.O.P.E` sem repetição de sabores/pesos) e zero referência a dados ERP.
- **[Trilha `fitoherb-ai` (Python / FastAPI)]:**
  - [ ] (`P-408`) Auditar `CatalogIndex.load_from_db()` (`app/domains/chat/infrastructure/catalog_index.py`) assegurando leitura restrita a `products`, `product_categories` e `suppliers` (proibido consultar `product_skus` ou `erp_catalog_items`) e confirmar que `ProductSnippetDto` (`app/domains/chat/schemas/chat_dto.py`) não contém campos ERP.
  - [ ] (`P-401`, `P-304`, `P-305`) Aprimorar `CatalogIndex.search()` para atribuir score estruturado consistente também a tokens em `presentation` (ex.: `"25ml"`, `"900g"`) preservando isonomia de fornecedores (`P-304`) e geração de filtros `NAVIGATE_CATALOG` (`P-305`).
  - [ ] Cobrir `CatalogIndex` com testes unitários `pytest` para variações saneadas e matrizes sem duplicatas.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 validando testes pytest do `CatalogIndex` e contrato público da galeria.)*

---

### Tarefa 6 (`US-P6` `[PARALLEL]`): Filtro Admin de Pendências ERP, Política de Inativos e Governança de Rollout Seguro para Produção

**Descritivo Detalhado:**
Disponibilizar na tela administrativa de Produtos ferramentas de governança contínua (filtro e badges de status ERP: *Sem Código*, *Completo* e *Com Alerta Inativo no ERP*, além de suporte à política de `inativo_pro = 1` definida em `P-406`) e consolidar o pacote de rollout idempotente pós-curadoria (`US-P1`) para promover o mapeamento e as restrições ao ambiente de produção sem perda de dados nem bloqueio operacional indevido (`P-400`, `P-409`).

**Critérios de Aceite:**
- [ ] (`P-408`) A listagem administrativa (`GET /api/products` e tabela `Produtos` no `/admin`) permite filtrar produtos por status ERP (`UNMAPPED`, `COMPLETE`, `INACTIVE_ALERT`) e exibe badges visuais distintos por estado.
- [ ] (`P-406`) Fluxo administrativo aplica exatamente a política homologada para `inativo_pro = 1` (alerta explícito / confirmação requerida na criação e sinalização `INACTIVE_ALERT` em itens já mapeados que inativarem no ERP).
- [ ] (`P-400`, `P-409`) O pacote de migração/backfill gerado pós-curadoria é 100% idempotente, respeita FKs e slugs existentes, não sobrescreve vínculos manuais confirmados e só ativa travas rígidas (`NOT NULL`) após verificação de conformidade na base alvo.

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Dados / Script Python]:**
  - [ ] (`P-400`, `P-409`, `A1`) Após validar e confirmar com o usuário a lista de pendências/inativos (`A2`, `A3`), remover todas as tabelas de staging ERP do banco PostgreSQL `fitoherb-v2` local (`DROP TABLE erp_catalog_items, supplier_brand_aliases, human_review_queue, erp_mapping_audit`) e gerar pacote SQL de promoção 100% idempotente contendo **apenas** `products` saneado (`P-401`) e `product_skus` (`ON CONFLICT DO NOTHING`, preservando vínculos manuais em produção).
  - [ ] (`P-409`, `A3`) Criar script de pré-validação pós-backfill em produção que bloqueia a ativação da constraint `NOT NULL` em `product_skus.erp_code` caso exista qualquer produto sem SKU ou `erp_code` nulo.
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-406`, `P-408`, `A1`) Implementar `POST /erp-products/sync` em `ErpProductController` restrito a `@PreAuthorize("@authorizationService.isAdmin()")` para recarregar o snapshot em memória RAM diretamente do SQL Server `FITOHERB` e atualizar `erp_inactive` / `erp_last_verified_at` em `product_skus` mantendo produtos publicados na vitrine (`INACTIVE_ALERT`).
  - [ ] (`P-408`) Implementar cálculo de `erpStatus` (`UNMAPPED`, `COMPLETE`, `INACTIVE_ALERT`) em `ProductMapper` e filtro `erpStatus` em `ProductService.getAllProductsPaginated` (`Specification<Product>`).
  - [ ] (`P-406`) Implementar tratamento de confirmação explícita para `inativo_pro = 1` (`422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED` quando `allowInactiveErp != true`), com propriedades `app.erp.inactive-policy` e `app.erp.strict-sku-required` alinhadas às definições do Checkpoint.
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] (`P-408`) Adicionar filtro por `erpStatus` (*Sem Código*, *Completo*, *Inativo no ERP*) na tabela `Produtos` (`AdminComponent`) com badges visuais distintos por estado.
  - [ ] (`P-406`) Implementar fluxo de diálogo/confirmação explícita no `AdminComponent` / `ModalEntityComponent` ao receber `422 ERP_SKU_INACTIVE_CONFIRMATION_REQUIRED`, permitindo confirmar os códigos listados e reenviar com `allowInactiveErp: true`.

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 validando idempotência do backfill, filtros administrativos e política de inativos.)*

---

### Tarefa 7 (`US-P7` `[PARALLEL]`): Sincronização Diária Agendada ERP ↔ Site, Ocultação/Reativação Automática e Publicação Sem Foto

**Descritivo Detalhado:**
Implementar a rotina diária automatizada e idempotente de sincronização ativo/inativo entre o ERP Atrio (`FITOHERB` via `ErpCatalogGateway` somente-leitura, respeitando `A1` e Allowlist LGPD) e o catálogo do site (`products`, `product_skus` e `CatalogIndex`). A rotina deve suportar execução interna agendada (`@Scheduled`) e gatilho HTTP autenticado compatível com Cloud Run *Scale-to-Zero* (`CloudSchedulerSyncTrigger`), respeitar a política de baseline pós-curadoria (`P-410`), controlar `products.active` e a projeção ativa de variações Multi-SKU parciais na vitrine e no `CatalogIndex` (`P-411`), e publicar imediatamente produtos ativados mesmo sem foto (`image_path = NULL`) registrando-os para curadoria rápida (`P-412`).

**Critérios de Aceite:**
- [ ] (`P-410`) Sincronização diária executa via `@Scheduled` configurável e via gatilho HTTP autenticado idempotente (`Scale-to-Zero`), com lock de concorrência, registro `ErpSyncState`/`ErpSyncRun`, política de baseline pós-curadoria (sem flood dos ~650 itens históricos) e falha segura (`503` sem alterar `active` atual se ERP offline).
- [ ] (`P-406`, `P-411`) Quando 100% dos SKUs vinculados ficarem `inativo_pro = 1`, `products.active` muda para `false` e o produto some de `GET /products/gallery` e do `CatalogIndex`, preservando foto e `product_skus`. Em Multi-SKU parcial, `products.active` permanece `true` e apenas os sabores/apresentações ativos são projetados na vitrine e no Chatbot. Ao reativar no ERP, `products.active` retorna imediatamente a `true`.
- [ ] (`P-412`) Produtos criados automaticamente ou reativados com `image_path = NULL` são publicados imediatamente com `active = true`, `category_id`, `supplier_id` e `slug` íntegros (via match determinístico ou fallback configurável), exibem `'assets/images/fitoherb-leaf-icon.png'` na vitrine pública, são indexados no `CatalogIndex` e recebem `curationStatus = PENDING_IMAGE`.
- [ ] (`P-408`) Dados internos ERP (`Id_Pro`, `inativo_pro`, `Estoque`, `created_by`/`ignored_by`) jamais vazam na vitrine pública nem no `CatalogIndex`; exclusão física nunca ocorre por inatividade.

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-411`, `P-412`) Evoluir `Product.java` com `active` (`BOOLEAN NOT NULL DEFAULT TRUE`) e `curationStatus` (`ProductCurationStatus` enum `VARCHAR(20) NOT NULL DEFAULT 'COMPLETED'`: `PENDING_IMAGE`, `COMPLETED`, `IGNORED`), criando entidades `ErpSyncState`, `ErpSyncRun`, `ErpIgnoredCatalogCode` e seus `JpaRepository`s (zero espelho de catálogo ERP no PostgreSQL — `A1`).
  - [ ] (`P-411`, `P-408`) Filtrar `cb.isTrue(root.get("active"))` em `ProductService.getProductGallery`; atualizar `ProductMapper` (`ProductRes` público inalterado com `imageUrl` nullable; `ProductAdminRes` expondo `active` e `curationStatus`) e `ProductService.getAllProductsPaginated` com filtros `active` e `curationStatus`.
  - [ ] (`P-411`, `P-406`) Implementar `ProductVisibilityCalculator`: `0` SKUs (`UNMAPPED`) preserva `active = true` (`A3`); `IGNORED` fixa `active = false`; 100% dos SKUs `erpInactive = true` define `active = false` (sem deletar foto/`product_skus`); Multi-SKU parcial preserva `active = true` e projeta `products.flavours`/`presentation` apenas dos SKUs `erpInactive = false`.
  - [ ] (`P-410`, `P-412`) Implementar `ErpAutoCatalogBuilder` (0 tokens LLM, criação `1:1` pós-baseline com `image_path = NULL`, `active = true`, `curationStatus = PENDING_IMAGE`, slug único sem colisão e fallback configurável categoria/fornecedor).
  - [ ] (`P-410`) Implementar `ErpDailySyncService` com lock atômico singleton em `erp_sync_state` (TTL 15 min), corte de baseline / `erp_ignored_catalog_codes`, expurgo > 90 dias em `erp_sync_runs`, idempotência no mesmo dia, *fail-closed* `503` se SQL Server offline e envio *best-effort* de relatório pós-sync via `MailService.sendEmail(MailReq)` para `app.erp.sync.report-email=${ERP_SYNC_REPORT_EMAIL:}` (sem hardcode, ignorando se vazio e logando `WARN` sanitizado sem abortar em falha SMTP).
  - [ ] (`P-410`) Implementar agendamento diário às **08:00 BRT** (`@Scheduled(cron = "${app.erp.sync.cron:0 0 8 * * *}", zone = "America/Sao_Paulo")`) + endpoint `POST /erp-products/sync/daily` em `ErpProductController` com `ifRunning=FAIL|ACCEPT` (`409`/`202`).
  - [ ] (`P-410`, `SecOps`) Implementar filtro `X-Sync-Scheduler-Token` com comparação constant-time `MessageDigest.isEqual` (`fail-closed` sem default literal), reforçar `SecurityConfigurations.java` (`requestMatchers` explícitos para `/erp-products/**`) e remover `System.out.println` de e-mail em `SecurityFilter.java:34`.
  - [ ] (`P-410`, `P-411`) Implementar `AiCatalogRefreshClient` (`RestClient` `connectTimeout=3s`/`readTimeout=5s` + header `X-Internal-Refresh-Token`) chamado fora da `@Transactional` pós-commit com fallback `WARN` compatível com `--cpu-throttling` do Cloud Run.
- **[Trilha `fitoherb-ai` (Python / FastAPI)]:**
  - [ ] (`P-411`, `P-408`) Filtrar `WHERE COALESCE(p.active, TRUE) = TRUE` em `CatalogIndex.load_from_db()` (e `EXISTS` em facetas), lendo apenas `products`, `product_categories`, `suppliers` em sessão read-only (`finally:` garantindo close) e removendo `"Dm120394"` em `catalog_index.py:81`.
  - [ ] (`P-410`, `P-411`) Proteger `CatalogIndex` com `threading.RLock`, `catalog_version`, `ensure_fresh(ttl_seconds=3600)` e implementar `POST /api/v1/chat/catalog/refresh` autenticado via `X-Internal-Refresh-Token` + `hmac.compare_digest` (fail-closed `503`) limpando `ConversationCacheService` (vinculado a `catalog_version` contra *race condition*).
  - [ ] (`P-412`) Aceitar `image_url: Optional[str] = None` em `ProductSnippetDto` / `ChatOrchestrator` e sincronizar `requirements.txt` (`psycopg2-binary`, `google-genai`, `pyyaml`, `pydantic-settings`).
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`) & Infra]:**
  - [ ] (`P-412`) Ajustar `ProductRes.imageUrl: string | null`, `ProductSnippet.image_url?: string | null`, `ItemCardGalleryComponent` (`isPlaceholderImage` + `effect()` reset), `ModalGalleryComponent` e `DynamicTableComponent` para placeholder `'assets/images/fitoherb-leaf-icon.png'` sem `.fallback-image` acinzentada.
  - [ ] (`P-410`) Expor `triggerDailySync` em `ErpProductsService` (`ROLE_ADMIN` apenas) e preparar variáveis Cloud Scheduler / Secrets no `deploy-prod.yml`.

---

### Tarefa 8 (`US-P8` `[PARALLEL]`): Central de Curadoria Rápida no Admin (`ROLE_USER` e `ROLE_ADMIN`), Modal Pré-Preenchido e Descarte Auditável

**Descritivo Detalhado:**
Disponibilizar no painel administrativo (`/admin`) a **Central de Curadoria Rápida** que alerta automaticamente usuários `ROLE_USER` e `ROLE_ADMIN` logo ao entrar quando houver novos produtos/reativados ativos aguardando imagem (`PENDING_IMAGE`). Ao clicar em um item da lista, o `ModalEntityComponent` abre pré-preenchido com nome, descrição sugerida, categoria, fornecedor e `skus[]` vinculados ao `Id_Pro`, permitindo concluir rapidamente apenas preenchendo a imagem — ou acionar o descarte auditável (*"Ignorar / Não exibir no site"*) para bloquear ressincronização de itens internos/brindes.

**Critérios de Aceite:**
- [ ] (`P-413`) Painel de Curadoria Rápida visível na entrada do `/admin` exclusivamente para `ROLE_USER` e `ROLE_ADMIN` quando houver pendências (`count > 0`, sem poluir quando zerado); `ROLE_SELLER` e anônimos não visualizam e recebem `403`/`401` nos endpoints.
- [ ] (`P-413`) Clique em item pendente abre `ModalEntityComponent` em modo edição pré-preenchido com nome, descrição sugerida, categoria, fornecedor e `skus[]` (`Id_Pro`), com foco na seleção de imagem.
- [ ] (`P-413`, `P-412`) Salvar imagem válida persiste a foto, publica-a na vitrine e remove imediatamente o produto da lista de pendências e do contador; salvar edição sem foto preserva `PENDING_IMAGE`.
- [ ] (`P-413`, `P-410`) Ação *"Ignorar / Não exibir no site"* oculta o produto da vitrine/Chatbot, registra o `Id_Pro` em `erp_ignored_catalog_codes` com trilha auditável e impede recriação/reativação nas sincronizações diárias seguintes.

**Etapas de Execução (Checklist Técnico):**
- **[Trilha Backend Java (`fitoherb-backend-v2`)]:**
  - [ ] (`P-413`) Criar `QuickCurationPendingItemRes`, `IgnoreCurationProductReq`, `IgnoreCurationProductRes` e `ErpCurationService` (`getCurationPending` sem PII de `createdBy`/`updatedBy`, destacando `fallbackCategoryWarning`/`fallbackSupplierWarning`).
  - [ ] (`P-413`, `P-410`) Implementar `ignorePendingProduct(slug, reason)` gravando em `erp_ignored_catalog_codes` (`source = 'ADMIN_IGNORED'`), marcando `active = false` e `curationStatus = IGNORED`, e disparando `AiCatalogRefreshClient` pós-commit.
  - [ ] (`P-413`, `SecOps`) Expor `GET /erp-products/curation-pending` e `POST /erp-products/curation-pending/{slug}/ignore` em `ErpProductController` com `@PreAuthorize("@authorizationService.isAdminOrUser()")` + `requestMatchers` em `SecurityConfigurations.java`.
  - [ ] (`P-412`, `P-413`) Transitar `curationStatus` de `PENDING_IMAGE -> COMPLETED` em `ProductService.updateProductBySlug` ao receber `image` válida (`!image.isEmpty()`), mantendo `PENDING_IMAGE` caso salvo sem foto (`POST /products` mantém imagem obrigatória `IMG-001`).
- **[Trilha Frontend Angular (`fitoherb-frontend-v2`)]:**
  - [ ] (`P-413`) Adicionar `ProductCurationStatus`, `active`/`curationStatus` em `ProductAdminRes` e métodos `getCurationPending` / `ignoreCurationPending` em `ErpProductsService`.
  - [ ] (`P-413`) Implementar componente `QuickCurationPanel` em `AdminComponent` (`ROLE_ADMIN`/`ROLE_USER` apenas quando `pendingCount() > 0`, 8 estados interativos, tokens estritos `DESIGN_SYSTEM.md`, zero emojis AI-slop, oculto e sem fetch para `ROLE_SELLER`).
  - [ ] (`P-413`) Conectar clique na linha pendente ao `ModalEntityComponent` pré-preenchido (`[focusImageUpload]="true"`, ajuste em `isImageValid` para não bloquear edições de metadados em `PENDING_IMAGE` sem foto) e diálogo de confirmação antes de `ignoreCurationPending`.
  - [ ] (`P-408`, `P-411`) Exibir miniatura fallback `'assets/images/fitoherb-leaf-icon.png'` e badge `--tag-danger` `Oculto na Vitrine (Inativo no ERP)` / `Oculto na Vitrine (Ignorado)` na tabela `/admin` quando `active === false`.
  - [ ] (`Hardening Modal`) Adicionar `type = input<'button' | 'submit' | 'reset'>('button')` em `ButtonComponent` e explicitar `type="button"` nos botões auxiliares (`modal-entity`, `modal-confirm`, `dynamic-table`, `QuickCurationPanel`).

**Audit (Testes e Validação):**
*(A ser preenchido pelo Tester/QA na Etapa 3/4 cobrindo RBAC `ROLE_USER`/`ROLE_ADMIN` vs. `ROLE_SELLER`/anônimo, pré-preenchimento do modal, saída automática pós-upload e bloqueio de ressincronização pós-descarte.)*
---

## 3. Condicionantes Obrigatórias de Segurança, Privacidade e Design (Etapa 2)
- [ ] **Autenticação de Scheduler & Privacy by Design (`US-P7`/`US-P8` — `architect` / `privacy_officer`):** Validar mecanismo de autenticação do endpoint `POST /erp-products/sync/daily` (Cloud Scheduler OIDC/HMAC ou token dedicado em Secret Manager) e garantir que `erp_sync_runs.triggered_by` / `erp_ignored_catalog_codes.ignored_by` sigam auditoria interna sem exposição em rotas públicas ou logs (`P-408`).
- [ ] **Contrato de Refresh `fitoherb-backend-v2` → `fitoherb-ai` (`US-P7` — `architect` / `ai_specialist`):** Definir endpoint autenticado interno de recarga/invalidação do `CatalogIndex` e `ConversationCacheService` em `fitoherb-ai` para refletir mudanças de `products.active` e variações ativas sem esperar expiração manual do container.
- [ ] **Design Plan Incremental Onda 4 (`US-P8` — `designer`):** Estender `design/plans/product_code_mapping_flavors.md` com anatomia da Central de Curadoria Rápida no `/admin` e estado visual do fallback institucional na vitrine pública.
- [ ] **LGPD / Allowlist ERP (`privacy_officer`):** Query de extração do ERP SQL Server projeta exclusivamente `Id_Pro`, `Empresa_Pro`, `descricao_pro`, `codbarra_pro`, `Marca.Nome_Marc`, `TipoProd.descricao_tppro`, `inativo_pro` e flag em `Externo01.Produto`. Proibido extrair `Clientes`, vendedores, `dbo.Fornecedor` (PF/MEI/CPF), `Estoque`, custos ou preços (`P-302`, `P-408`).
- [ ] **Blindagem de Credenciais e `.gitignore` (`privacy_officer`):** Atualizar `fitoherb-backend-v2/.gitignore` para ignorar `.env`, `.env.*`, `*.sql`, `*.dump`, `*.bak` e `fitoherb_backup.sql`; remover senha fallback literal `"Dm120394"` em `fitoherb-ai/app/domains/chat/infrastructure/catalog_index.py:81`; sanitizar log de e-mail em `SecurityFilter.java:34` e reforçar `requestMatchers` em `SecurityConfigurations.java`.
- [ ] **Higienização Prod → Local (`P-400` / `dba`):** Restaurar dump de `backup.yml` via banco staging local `fitoherb_prod_raw` (`-n public --no-owner --no-privileges`), validar trava de host local, mascarar/higienizar tabela `users` local pós-restore e remover `fitoherb_backup.sql` após restauração.
- [ ] **Correções Base de UI (`designer`):** Adicionar `type = input<'button' | 'submit' | 'reset'>('button')` em `ButtonComponent` (evitando submits acidentais no modal), aplicar `position: fixed` no popover Multi-SKU da tabela admin (anti-clipping), substituir `"DM Sans"` residual por `var(--font-body)` (`Outfit`) e consolidar `:root` em `styles.scss`.
- [ ] **Hardening `CatalogIndex` (`ai_specialist`):** Normalizar unidades acopladas (`25 ml` ↔ `25ml`, `1 kg` ↔ `1000g`), usar fronteira de palavra `\b` para tokens com dígitos (`5ml` != `25ml`) e pontuar `presentation` junto a `flavours` e `name`.
