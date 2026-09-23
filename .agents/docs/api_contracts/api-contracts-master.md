# API Contracts Master — Fitoherb Backend v2

> **Data de criação:** 2026-09-23  
> **Versão:** 0.0.1-SNAPSHOT  
> **Base URL:** `https://api.fitoherb.com.br` (prod) | `http://localhost:8080` (dev)  
> **Formato padrão:** JSON (exceto uploads: `multipart/form-data`)  
> **Autenticação:** `Authorization: Bearer <jwt>` **ou** Cookie `fitoherb_jwt`

> [!IMPORTANT]
> Este documento é a **referência canônica** de todos os contratos de API. Use-o para geração de código, testes e integrações.

---

## Resumo de Endpoints

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/login` | 🔓 | Autenticar e receber JWT |
| POST | `/auth/register` | 🛡️ Admin | Registrar novo usuário |
| POST | `/auth/refresh` | 🔓 | Renovar token |
| POST | `/auth/logout` | 🔓 | Limpar cookies |
| GET | `/users` | 🔑 | Listar usuários (paginado) |
| GET | `/users/{email}` | 🔑 | Buscar usuário por e-mail |
| PUT | `/users/{email}` | 🛡️ Admin | Atualizar perfil |
| PATCH | `/users/update-password/{email}` | 🔑 | Atualizar senha |
| DELETE | `/users/{email}` | 🛡️ Admin | Deletar usuário |
| GET | `/products/gallery` | 🔓 | Galeria pública paginada |
| GET | `/products` | 🔑 | Listar produtos (admin) |
| GET | `/products/{slug}` | 🔑 | Detalhes de produto |
| POST | `/products` | 🔑 | Criar produto (multipart) |
| PUT | `/products/{slug}` | 🔑 | Atualizar produto (multipart) |
| DELETE | `/products/{slug}` | 🔑 | Deletar produto |
| GET | `/product_categories/get-all` | 🔓 | Todas as categorias (sem paginação) |
| GET | `/product_categories` | 🔑 | Listar categorias (admin) |
| GET | `/product_categories/{slug}` | 🔑 | Detalhes de categoria |
| POST | `/product_categories` | 🔑 | Criar categoria (multipart) |
| PUT | `/product_categories/{slug}` | 🔑 | Atualizar categoria (multipart) |
| DELETE | `/product_categories/{slug}` | 🔑 | Deletar categoria |
| GET | `/suppliers/get-all` | 🔓 | Todos os fornecedores (sem paginação) |
| GET | `/suppliers` | 🔑 | Listar fornecedores (admin) |
| GET | `/suppliers/{slug}` | 🔑 | Detalhes de fornecedor |
| POST | `/suppliers` | 🔑 | Criar fornecedor (multipart) |
| PUT | `/suppliers/{slug}` | 🔑 | Atualizar fornecedor (multipart) |
| DELETE | `/suppliers/{slug}` | 🔑 | Deletar fornecedor |
| GET | `/banners/active` | 🔓 | Banners ativos (homepage) |
| GET | `/banners` | 🔑 | Listar banners (admin) |
| GET | `/banners/{id}` | 🔑 | Detalhes de banner |
| POST | `/banners` | 🔑 | Criar banner (multipart) |
| PUT | `/banners/{id}` | 🔑 | Atualizar banner (multipart) |
| DELETE | `/banners/{id}` | 🔑 | Deletar banner |

---

## 1. Auth

### POST /auth/login
```
Auth: nenhuma
Content-Type: application/json

Request:
{
  "email": "admin@fitoherb.com.br",   // string, required, email format
  "password": "MinhaSenh@123",        // string, required
  "rememberMe": true                  // boolean, optional
}

Response 200:
{
  "token": "eyJhbGci..."
}
Cookies definidos: fitoherb_jwt (HttpOnly), fitoherb_user_email

Erros: 400 (validation), 401 (credenciais inválidas)
```

### POST /auth/register
```
Auth: ROLE_ADMIN
Content-Type: application/json

Request:
{
  "email": "novo@fitoherb.com.br",   // string, required, email, unique
  "name": "Nome Completo",            // string, required, 1-255
  "role": "USER"                      // enum: ADMIN | USER, required
}

Response 201: Location header com /auth/register/{id}
Efeito colateral: Envia e-mail com senha temporária gerada pelo servidor

Erros: 400 (validation), 409 (email duplicado), 500 (falha DB)
```

### POST /auth/refresh
```
Auth: nenhuma (token via cookie fitoherb_jwt OU header Authorization: Bearer)

Response 200: { "token": "eyJhbGci..." }
Response 400: token não encontrado
```

### POST /auth/logout
```
Auth: nenhuma
Response 200: (sem body, limpa cookies)
```

---

## 2. Users

### GET /users
```
Auth: autenticado (qualquer role)
Query: search? (string), page? (int=0), sortField? (name|email|role|createdAt), direction? (ASC|DESC)

Response 200: Page<UserRes>
{
  "content": [{ "email": "...", "name": "...", "role": "ADMIN", "createdAt": "23-09-2026 10:00:00" }],
  "totalElements": 5, "totalPages": 1, "size": 10, "number": 0
}
```

### GET /users/{email}
```
Auth: autenticado
Path: email (string, email format)

Response 200: { "email": "...", "name": "...", "role": "USER", "createdAt": "..." }
Erros: 401, 404
```

### PUT /users/{email}
```
Auth: ROLE_ADMIN
Path: email (string)
Content-Type: application/json

Request: { "name": "Novo Nome", "role": "ADMIN" }

Response 200: (sem body)
Erros: 400, 403, 404, 500
```

### PATCH /users/update-password/{email}
```
Auth: autenticado
Path: email (string)
Content-Type: application/json

Request: { "password": "NovaSenha@456" }   // 8-100 chars

Response 200: (sem body)
Erros: 400, 401, 404, 500
```

### DELETE /users/{email}
```
Auth: ROLE_ADMIN
Path: email (string)

Response 200: (sem body)
Erros: 403, 404, 500
```

---

## 3. Products

### GET /products/gallery
```
Auth: nenhuma (público)
Query: search?, category[]?, supplier[]?, page? (int=0), size? (int=15), direction? (ASC|DESC)

Response 200: Page<ProductRes>
{
  "content": [{
    "name": "...", "imageUrl": "...", "description": "...",
    "flavours": ["Natural"], "presentation": ["100g"],
    "slug": "cha-de-camomila", "createdAt": "...",
    "category": { "name": "...", "slug": "...", "imageUrl": "..." },
    "supplier": { "name": "...", "slug": "...", "imageUrl": "...", "isHighlighted": true }
  }],
  "totalElements": 120, "totalPages": 8, "size": 15, "number": 0
}
Erros: 404 (categoria/fornecedor não encontrado pelo slug do filtro)
```

### GET /products
```
Auth: autenticado
Query: search?, category[]?, supplier[]?, page? (int=0), sortField? (name|createdAt), direction? (ASC|DESC)

Response 200: Page<ProductRes> (tamanho 10)
```

### GET /products/{slug}
```
Auth: autenticado
Path: slug (letras minúsculas, dígitos e hífens)

Response 200: ProductRes (objeto único)
Erros: 403, 404
```

### POST /products
```
Auth: autenticado
Content-Type: multipart/form-data

Parts:
  product (application/json, required):
  {
    "name": "...",             // string, required, 1-255
    "description": "...",      // string, optional, max 5000
    "categorySlug": "...",     // string, required (slug existente)
    "supplierSlug": "...",     // string, required (slug existente)
    "flavours": ["..."],       // string[], optional, max 50
    "presentation": ["..."]    // string[], optional, max 50
  }
  image (image/*, required)

Response 201: Location: /products/{id}
Erros: 400, 404 (categoria/fornecedor), 409 (nome/slug duplicado)
```

### PUT /products/{slug}
```
Auth: autenticado
Content-Type: multipart/form-data

Parts: product (application/json, required), image (optional)

Response 200: (sem body)
Erros: 404, 409, 500
```

### DELETE /products/{slug}
```
Auth: autenticado
Path: slug

Response 200: (sem body)
Erros: 404, 500
```

---

## 4. Product Categories

### GET /product_categories/get-all
```
Auth: nenhuma (público)

Response 200: List<ProductCategoryRes>
[{ "name": "...", "slug": "...", "imageUrl": "..." }]
```

### GET /product_categories
```
Auth: autenticado
Query: search?, page? (int=0), sortField? (name|createdAt), direction? (ASC|DESC)

Response 200: Page<ProductCategoryRes>
```

### GET /product_categories/{slug}
```
Auth: autenticado
Path: slug

Response 200: ProductCategoryRes
Erros: 404
```

### POST /product_categories
```
Auth: autenticado
Content-Type: multipart/form-data

Parts:
  category (application/json, required): { "name": "..." }  // required, unique
  image (image/*, required)

Response 201: Location: /product_categories/{id}
Erros: 400, 409
```

### PUT /product_categories/{slug}
```
Auth: autenticado
Parts: category (required), image (optional)

Response 200: (sem body)
Erros: 404, 409, 500
```

### DELETE /product_categories/{slug}
```
Auth: autenticado
Response 200: (sem body)
Erros: 404, 500 (produtos vinculados)
```

---

## 5. Suppliers

### GET /suppliers/get-all
```
Auth: nenhuma (público)

Response 200: List<SupplierRes>
[{ "name": "...", "slug": "...", "imageUrl": "...", "isHighlighted": true }]
```

### GET /suppliers
```
Auth: autenticado
Query: search?, page? (int=0), sortField? (name|createdAt), direction? (ASC|DESC)

Response 200: Page<SupplierRes>
```

### GET /suppliers/{slug}
```
Auth: autenticado
Path: slug

Response 200: SupplierRes
Erros: 404
```

### POST /suppliers
```
Auth: autenticado
Content-Type: multipart/form-data

Parts:
  supplier (application/json, required):
  {
    "name": "...",           // string, required, unique
    "isHighlighted": false   // boolean, optional
  }
  image (image/*, required)

Response 201: Location: /suppliers/{id}
Erros: 400, 409
```

### PUT /suppliers/{slug}
```
Auth: autenticado
Parts: supplier (required), image (optional)

Response 200: (sem body)
Erros: 404, 409, 500
```

### DELETE /suppliers/{slug}
```
Auth: autenticado
Query: deleteProducts? (boolean, default false)

Response 200: (sem body)
Erros: 404, 500 (sem deleteProducts=true quando há produtos)
```

---

## 6. Banners

### GET /banners/active
```
Auth: nenhuma (público)

Response 200: List<BannerRes> — apenas is_active=true, ordenados por position ASC
[{
  "id": "uuid", "title": "...", "imagePath": "...", "imageUrl": "...",
  "isActive": true, "position": 0, "createdAt": "...", "updatedAt": "..."
}]
```

### GET /banners
```
Auth: autenticado
Query: search?, page? (int=0), sortField? (position|title|createdAt), direction? (ASC|DESC)

Response 200: Page<BannerRes>
```

### GET /banners/{id}
```
Auth: autenticado
Path: id (UUID string, not blank)

Response 200: BannerRes
Erros: 404
```

### POST /banners
```
Auth: autenticado
Content-Type: multipart/form-data

Parts:
  banner (application/json, required):
  {
    "title": "...",     // string, required, 1-255
    "isActive": true,   // boolean, optional, default true
    "position": 0       // int, optional, default 0
  }
  image (image/*, required)

Response 201: Location: /banners/{id}
Erros: 400, 500
```

### PUT /banners/{id}
```
Auth: autenticado
Parts: banner (required), image (optional)

Response 200: (sem body)
Erros: 404, 500
```

### DELETE /banners/{id}
```
Auth: autenticado
Path: id (UUID)

Response 200: (sem body)
Erros: 404, 500
```

---

## Schemas de Resposta de Erro

### RestErrorMessage
```json
{
  "status": "NOT_FOUND",
  "message": "Product not found with slug: cha-de-camomila"
}
```

### RestValidationErrorMessage
```json
{
  "status": "BAD_REQUEST",
  "message": "Validation failed for one or more fields",
  "errors": {
    "name": "must not be blank",
    "categorySlug": "This field cannot be empty or null"
  }
}
```

### Códigos HTTP

| Código | Situação |
|--------|---------|
| 200 | OK — operação bem-sucedida |
| 201 | Created — recurso criado |
| 400 | Bad Request — validação de campos |
| 401 | Unauthorized — sem token ou token inválido |
| 403 | Forbidden — autenticado mas sem permissão |
| 404 | Not Found — recurso não encontrado |
| 409 | Conflict — unicidade violada (slug, email, nome) |
| 500 | Internal Server Error — falha inesperada |
