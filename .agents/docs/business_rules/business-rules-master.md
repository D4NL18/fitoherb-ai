# Business Rules Master — Fitoherb Backend v2

> **Data de criação:** 2026-09-23  
> **Escopo:** Todas as regras de negócio consolidadas do sistema

> [!IMPORTANT]
> Este documento é a referência canônica de regras de negócio para LLMs. Consulte-o ao gerar código, revisar PRs ou implementar novas funcionalidades.

---

## 1. Regras de Autenticação e Segurança

### AUTH-001: Senha nunca informada pelo cliente no registro
O endpoint `POST /auth/register` não aceita campo `password`. O servidor gera uma senha aleatória de 10 caracteres (maiúscula, minúscula, dígito, especial) usando `SecureRandom` e envia por e-mail.

### AUTH-002: Senha armazenada com BCrypt
Toda senha armazenada no banco de dados está hasheada com `BCryptPasswordEncoder`. Nunca armazenar texto plano.

### AUTH-003: Somente ADMIN registra usuários
`@PreAuthorize("@authorizationService.isAdmin()")` protege `POST /auth/register`. Um `ROLE_USER` recebe `403 Forbidden`.

### AUTH-004: Token JWT válido por 2 horas
Token emitido em `POST /auth/login` expira após 2 horas (fuso BRT -03:00). Algoritmo: HMAC256 com secret configurável via `api.security.token.secret`.

### AUTH-005: Refresh aceita token expirado com assinatura válida
`POST /auth/refresh` usa `validateAndGetSubjectEvenIfExpired()`. Tokens forjados (assinatura inválida) são rejeitados mesmo que não estejam expirados.

### AUTH-006: Cookie JWT é HttpOnly
O cookie `fitoherb_jwt` é configurado com `HttpOnly = true`, protegendo contra XSS. O JavaScript do frontend não pode acessá-lo.

### AUTH-007: rememberMe determina duração do cookie
- `rememberMe = true` → `MaxAge = 30 dias`
- `rememberMe = false` ou ausente → `MaxAge = -1` (sessão de browser)

### AUTH-008: Logout invalida cookies via MaxAge=0
`POST /auth/logout` redefine `fitoherb_jwt` e `fitoherb_user_email` com `MaxAge = 0`, efetivamente removendo-os do browser.

### AUTH-009: E-mail único por conta
Tentar registrar e-mail já existente retorna `409 CONFLICT`.

### AUTH-010: Falha de persistência não expõe detalhes
Exceções de banco no registro são capturadas e relançadas como `DatabaseOperationException` com mensagem genérica.

---

## 2. Regras de Controle de Acesso (RBAC)

### RBAC-001: Hierarquia de roles
- `ROLE_ADMIN` → herda `ROLE_USER` (tem ambas as authorities)
- `ROLE_USER` → apenas `ROLE_USER`

### RBAC-002: Endpoints públicos (sem autenticação)
```
GET  /products/gallery
GET  /product_categories/get-all
GET  /suppliers/get-all
GET  /banners/active
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /swagger-ui/**
GET  /v3/api-docs/**
```

### RBAC-003: Endpoints que requerem qualquer autenticação
```
GET  /users
GET  /users/{email}
GET  /products
GET  /products/{slug}
POST /products
PUT  /products/{slug}
DELETE /products/{slug}
GET  /product_categories
GET  /product_categories/{slug}
POST /product_categories
PUT  /product_categories/{slug}
DELETE /product_categories/{slug}
GET  /suppliers
GET  /suppliers/{slug}
POST /suppliers
PUT  /suppliers/{slug}
DELETE /suppliers/{slug}
GET  /banners
GET  /banners/{id}
POST /banners
PUT  /banners/{id}
DELETE /banners/{id}
PATCH /users/update-password/{email}
```

### RBAC-004: Endpoints exclusivos para ADMIN
```
POST /auth/register
PUT  /users/{email}
DELETE /users/{email}
```

> **Nota:** Embora muitos endpoints de CRUD de produtos/categorias/fornecedores/banners usem `isAuthenticated()` no código atual, a intenção arquitetural é que somente admins realizem operações de escrita. Futuras versões podem reforçar `isAdmin()`.

---

## 3. Regras de CRUD Geral

### CRUD-001: Paginação padrão é de 10 itens
Todos os endpoints de listagem paginada administrativa retornam 10 itens por página por padrão (Spring Data `Pageable`).

### CRUD-002: Galeria pública tem size configurável
`GET /products/gallery` aceita parâmetro `size` (padrão: 15). Máximo não validado explicitamente no código.

### CRUD-003: Ordenação dinâmica por campo e direção
Todos os endpoints de listagem aceitam `sortField` e `direction` (ASC|DESC). Campos válidos variam por módulo.

### CRUD-004: Resposta 201 inclui header Location
Ao criar recursos (POST), a resposta inclui o header `Location` com a URI do recurso criado.

### CRUD-005: Resposta 200 sem body em update/delete
`PUT`, `PATCH` e `DELETE` bem-sucedidos retornam `200 OK` com body vazio.

---

## 4. Regras de Slug

### SLUG-001: Slug gerado automaticamente
O slug é sempre calculado a partir do campo `name` via `StringUtils.toSlug()`. O cliente nunca informa o slug.

### SLUG-002: Algoritmo de geração de slug
`StringUtils.toSlug()` realiza: normalização Unicode → remoção de acentos → lowercase → substituição de espaços e caracteres não alfanuméricos por hífens → remoção de hífens duplicados/inicial/final.

Exemplos:
- `"Chá de Camomila Orgânico"` → `"cha-de-camomila-organico"`
- `"Óleo de Lavanda 100%"` → `"oleo-de-lavanda-100"`

### SLUG-003: Slug é único por entidade
Cada tabela tem UNIQUE constraint no campo `slug`. O serviço valida antes de salvar para retornar `409` informativo.

### SLUG-004: Slug atualizado automaticamente ao renomear
`@PreUpdate` regenera o slug quando o nome é alterado. Isso pode quebrar URLs existentes — considere manter redirecionamentos no frontend.

### SLUG-005: Slug validado no path variable
O path variable `{slug}` é validado contra regex `SLUG_REGEX` (letras minúsculas, dígitos e hífens). Slugs inválidos retornam `400` sem acessar o banco.

---

## 5. Regras de Upload de Imagem

### IMG-001: Imagem obrigatória na criação
`POST` em produtos, categorias, fornecedores e banners exige o part `image` no multipart. Sem imagem → `400 Bad Request`.

### IMG-002: Imagem opcional na atualização
`PUT` aceita `image` como part opcional. Se ausente, a imagem existente é mantida.

### IMG-003: Imagem antiga deletada ao atualizar
Quando uma nova imagem é fornecida no `PUT`, a imagem anterior é removida do armazenamento (local ou GCS) antes de salvar a nova. Garante ausência de imagens órfãs.

### IMG-004: Imagem deletada junto com o recurso
`DELETE` em qualquer entidade com imagem remove o arquivo do armazenamento via `FileStorageService`.

### IMG-005: Strategy Pattern para armazenamento
- Desenvolvimento: `LocalFileStorageService` — salva em disco local
- Produção: `GcsFileStorageService` — salva no Google Cloud Storage
- A seleção é feita via configuração Spring (property ou annotation)

### IMG-006: Compressão de imagem via Thumbnailator
Imagens são processadas/redimensionadas pela biblioteca `Thumbnailator` antes do armazenamento para otimização de tamanho e qualidade.

---

## 6. Regras de Validação de Dados

### VAL-001: Bean Validation em todos os DTOs de request
Todos os campos obrigatórios usam `@NotNull`, `@NotBlank` conforme necessário. Tamanhos são controlados por `@Size`. Formato de e-mail por `@Email`.

### VAL-002: Constantes de validação centralizadas
As constantes de validação (`MIN_STRING_LENGTH`, `MAX_STRING_LENGTH`, `MAX_TEXT_LENGTH`, etc.) são definidas em `ValidationConstants` e reutilizadas em todos os DTOs.

### VAL-003: Erros de validação retornam 400 com mapa de campos
`MethodArgumentNotValidException` é tratado pelo `RestExceptionHandler` e retorna `RestValidationErrorMessage` com mapa `campo → mensagem`.

### VAL-004: Description nula se string vazia
O setter de `description` em `ProductReq` converte string vazia ou apenas espaços para `null`, evitando strings vazias no banco.

---

## 7. Regras de Auditoria

### AUD-001: Todos os entities têm 4 campos de auditoria
`created_at`, `updated_at`, `created_by`, `updated_by` estão presentes em todas as tabelas.

### AUD-002: Campos de criação são imutáveis
`created_at` usa `updatable = false`. `created_by` usa `updatable = false`. Nunca são modificados após a criação.

### AUD-003: Campos de auditoria são preenchidos automaticamente
`AuditorAwareImpl` lê o email do principal autenticado no `SecurityContextHolder`. Spring Data JPA preenche os campos automaticamente via `@EntityListeners(AuditingEntityListener.class)`.

### AUD-004: Auditoria usa e-mail como identificador
`created_by` e `updated_by` armazenam o **e-mail** (não o ID) do usuário responsável pela operação.

---

## 8. Regras de Integridade Referencial

### REF-001: Produto requer categoria e fornecedor existentes
Ao criar/atualizar produto, `categorySlug` e `supplierSlug` devem corresponder a registros existentes. Caso contrário → `404 Not Found`.

### REF-002: Deleção de categoria/fornecedor bloqueada se houver produtos
Deletar categoria ou fornecedor com produtos vinculados resulta em `500` por violação de FK, a menos que produtos sejam removidos antes.

### REF-003: Deleção em cascata de fornecedor via parâmetro
`DELETE /suppliers/{slug}?deleteProducts=true` permite remover o fornecedor e todos os seus produtos em cascata. Operação irreversível.

---

## 9. Regras de Negócio Específicas por Entidade

### Banners
- `is_active = false` → banner não aparece no endpoint público `/banners/active`
- `position` determina a ordem (menor valor = exibido primeiro)
- Identificados por UUID, não slug

### Suppliers
- `is_highlighted = true` → fornecedor pode ter tratamento visual especial no frontend
- `is_highlighted` é nullable (null = não definido, diferente de `false`)

### Products
- `flavours` e `presentation` são arrays PostgreSQL (`TEXT[]`)
- Um produto deve ter exatamente 1 categoria e 1 fornecedor
- Slug único por produto garante URLs SEO únicas

### Users
- `ROLE_ADMIN` herda permissões de `ROLE_USER`
- A senha não é retornada em nenhum response
- E-mail é imutável após criação (usado como identificador único)
