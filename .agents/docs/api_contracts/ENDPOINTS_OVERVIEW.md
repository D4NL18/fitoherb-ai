# Referência de Endpoints — Fitoherb Backend v2

> **Data de criação:** 2026-09-23  
> **Base URL (prod):** `https://api.fitoherb.com.br`  
> **Base URL (dev):** `http://localhost:8080`  
> **Formato:** JSON / multipart/form-data  
> **Autenticação:** `Authorization: Bearer <token>` ou Cookie `fitoherb_jwt`

---

## Legenda de Autenticação

| Símbolo | Significado |
|---------|------------|
| 🔓 Público | Sem autenticação necessária |
| 🔑 Autenticado | Qualquer usuário com token JWT válido |
| 🛡️ Admin | Requer `ROLE_ADMIN` |

---

## 1. Auth (`/auth`)

### `POST /auth/login` 🔓

Autentica o usuário e retorna o JWT. Define cookies `fitoherb_jwt` (HttpOnly) e `fitoherb_user_email`.

**Request Body:**
```json
{
  "email": "admin@fitoherb.com.br",
  "password": "MinhaSenh@123",
  "rememberMe": true
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | ✅ | E-mail cadastrado |
| `password` | string | ✅ | Senha do usuário |
| `rememberMe` | boolean | ❌ | Se `true`, cookie dura 30 dias; senão, sessão |

**Response `200 OK`:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Erros:**

| Status | Descrição | Exemplo |
|--------|-----------|---------|
| `400` | Validação falhou | `{"status":"BAD_REQUEST","message":"Validation failed...","errors":{"email":"must be a well-formed email address"}}` |
| `401` | Credenciais inválidas | `{"status":"UNAUTHORIZED","message":"E-mail or password invalid."}` |

---

### `POST /auth/register` 🛡️ Admin

Registra um novo usuário. A senha é gerada automaticamente e enviada por e-mail.

**Request Body:**
```json
{
  "email": "novo.usuario@fitoherb.com.br",
  "name": "Daniel Marinho",
  "role": "USER"
}
```

| Campo | Tipo | Obrigatório | Valores |
|-------|------|-------------|---------|
| `email` | string | ✅ | E-mail válido |
| `name` | string | ✅ | Nome completo |
| `role` | string enum | ✅ | `ADMIN` \| `USER` |

**Response `201 Created`:**
```
HTTP/1.1 201 Created
Location: /auth/register/{id}
```
(sem body)

**Erros:**

| Status | Descrição |
|--------|-----------|
| `400` | Validação de campos |
| `409` | E-mail já cadastrado |
| `500` | Falha ao salvar no banco |

---

### `POST /auth/refresh` 🔓

Renova o token JWT. Aceita token via cookie `fitoherb_jwt` ou header `Authorization`.

**Response `200 OK`:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Erros:**

| Status | Descrição |
|--------|-----------|
| `400` | Nenhum token encontrado no cookie nem no header |

---

### `POST /auth/logout` 🔓

Limpa os cookies de autenticação.

**Response `200 OK`:** (sem body)

---

## 2. Users (`/users`)

### `GET /users` 🔑 Autenticado

Lista usuários com paginação, busca e ordenação.

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `search` | string | — | Filtra por nome ou email |
| `page` | int | `0` | Índice da página (base 0) |
| `sortField` | string | `name` | Campo de ordenação: `name`, `email`, `role`, `createdAt` |
| `direction` | string | `ASC` | Direção: `ASC` \| `DESC` |

**Response `200 OK`:**
```json
{
  "content": [
    {
      "email": "admin@fitoherb.com.br",
      "name": "Administrador Fitoherb",
      "role": "ADMIN",
      "createdAt": "23-09-2026 10:00:00"
    }
  ],
  "totalElements": 5,
  "totalPages": 1,
  "size": 10,
  "number": 0
}
```

---

### `GET /users/{email}` 🔑 Autenticado

Retorna o perfil de um usuário pelo e-mail.

**Path Parameter:** `email` — e-mail do usuário

**Response `200 OK`:**
```json
{
  "email": "daniel@fitoherb.com.br",
  "name": "Daniel Marinho",
  "role": "ADMIN",
  "createdAt": "23-09-2026 10:00:00"
}
```

**Erros:**

| Status | Descrição |
|--------|-----------|
| `404` | Usuário não encontrado |
| `401` | Token inválido ou expirado |

---

### `PUT /users/{email}` 🛡️ Admin

Atualiza os dados do perfil do usuário (exceto senha).

**Path Parameter:** `email` — e-mail do usuário alvo

**Request Body:**
```json
{
  "name": "Daniel Marinho Silva",
  "role": "ADMIN"
}
```

**Response `200 OK`:** (sem body)

**Erros:**

| Status | Descrição |
|--------|-----------|
| `400` | Validação de campos |
| `403` | Sem permissão de admin |
| `404` | Usuário não encontrado |
| `500` | Falha ao atualizar no banco |

---

### `PATCH /users/update-password/{email}` 🔑 Autenticado

Atualiza a senha do usuário.

**Path Parameter:** `email` — e-mail da conta

**Request Body:**
```json
{
  "password": "NovaSenha@456"
}
```

**Response `200 OK`:** (sem body)

**Erros:**

| Status | Descrição |
|--------|-----------|
| `400` | Senha fora dos limites de tamanho |
| `404` | Usuário não encontrado |
| `401` | Token inválido |
| `500` | Falha ao salvar nova senha |

---

### `DELETE /users/{email}` 🛡️ Admin

Remove permanentemente um usuário do sistema.

**Path Parameter:** `email` — e-mail do usuário a remover

**Response `200 OK`:** (sem body)

**Erros:**

| Status | Descrição |
|--------|-----------|
| `403` | Sem permissão de admin |
| `404` | Usuário não encontrado |
| `500` | Erro de integridade referencial |

---

## 3. Products (`/products`)

### `GET /products/gallery` 🔓 Público

Galeria pública de produtos para o site. Suporta filtros e paginação.

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `search` | string | — | Busca pelo nome do produto |
| `category` | string[] | — | Filtra por slugs de categoria (ex: `chas,ervas`) |
| `supplier` | string[] | — | Filtra por slugs de fornecedor |
| `page` | int | `0` | Índice da página |
| `size` | int | `15` | Itens por página |
| `direction` | string | `ASC` | `ASC` \| `DESC` |

**Response `200 OK`:**
```json
{
  "content": [
    {
      "name": "Chá de Camomila Orgânico",
      "imageUrl": "https://storage.googleapis.com/.../camomila.jpg",
      "description": "Flores de camomila desidratadas...",
      "flavours": ["Natural"],
      "presentation": ["100g", "250g"],
      "slug": "cha-de-camomila-organico",
      "category": {
        "name": "Chás e Infusões",
        "slug": "chas-e-infusoes",
        "imageUrl": "..."
      },
      "supplier": {
        "name": "Fitoherb Natural",
        "slug": "fitoherb-natural",
        "imageUrl": "...",
        "isHighlighted": true
      },
      "createdAt": "23-09-2026 10:00:00"
    }
  ],
  "totalElements": 120,
  "totalPages": 8,
  "size": 15,
  "number": 0
}
```

---

### `GET /products` 🔑 Autenticado

Lista produtos para o painel administrativo (paginada).

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `search` | string | — | Busca pelo nome |
| `category` | string[] | — | Filtra por slugs de categoria |
| `supplier` | string[] | — | Filtra por slugs de fornecedor |
| `page` | int | `0` | Índice da página |
| `sortField` | string | `name` | `name`, `createdAt` |
| `direction` | string | `ASC` | `ASC` \| `DESC` |

**Response `200 OK`:** mesmo formato da galeria, com 10 itens por página padrão.

---

### `GET /products/{slug}` 🔑 Autenticado

Detalhes de um produto por slug.

**Path Parameter:** `slug` — slug URL do produto

**Response `200 OK`:**
```json
{
  "name": "Chá de Camomila Orgânico",
  "imageUrl": "https://...",
  "description": "Flores de camomila desidratadas...",
  "flavours": ["Natural"],
  "presentation": ["100g", "250g"],
  "slug": "cha-de-camomila-organico",
  "category": { "name": "Chás e Infusões", "slug": "chas-e-infusoes", "imageUrl": "..." },
  "supplier": { "name": "Fitoherb Natural", "slug": "fitoherb-natural", "imageUrl": "...", "isHighlighted": true },
  "createdAt": "23-09-2026 10:00:00"
}
```

**Erros:**

| Status | Descrição |
|--------|-----------|
| `404` | Produto não encontrado |
| `403` | Acesso negado |

---

### `POST /products` 🔑 Autenticado

Cria um novo produto com imagem.

**Content-Type:** `multipart/form-data`

**Form Parts:**

| Part | Content-Type | Obrigatório | Descrição |
|------|-------------|-------------|-----------|
| `product` | `application/json` | ✅ | Dados do produto (veja abaixo) |
| `image` | `image/*` | ✅ | Arquivo de imagem do produto |

**Part `product` (JSON):**
```json
{
  "name": "Chá de Camomila Orgânico",
  "description": "Flores de camomila desidratadas, ideais para infusões relaxantes.",
  "categorySlug": "chas-e-infusoes",
  "supplierSlug": "fitoherb-natural",
  "flavours": ["Natural", "Mel"],
  "presentation": ["100g", "250g", "500g"]
}
```

**Response `201 Created`:**
```
HTTP/1.1 201 Created
Location: /products/{id}
```

**Erros:**

| Status | Descrição |
|--------|-----------|
| `400` | Validação de campos |
| `404` | Categoria ou fornecedor não encontrado pelo slug |
| `409` | Produto com mesmo nome ou slug já existe |

---

### `PUT /products/{slug}` 🔑 Autenticado

Atualiza produto existente. Imagem é opcional.

**Content-Type:** `multipart/form-data`

| Part | Obrigatório | Descrição |
|------|-------------|-----------|
| `product` | ✅ | Dados atualizados (mesmo schema do POST) |
| `image` | ❌ | Nova imagem (se omitida, mantém a existente) |

**Response `200 OK`:** (sem body)

---

### `DELETE /products/{slug}` 🔑 Autenticado

Remove o produto e sua imagem do armazenamento.

**Path Parameter:** `slug` — slug do produto

**Response `200 OK`:** (sem body)

---

## 4. Product Categories (`/product_categories`)

### `GET /product_categories/get-all` 🔓 Público

Lista todas as categorias sem paginação (para dropdowns/filtros).

**Response `200 OK`:**
```json
[
  {
    "name": "Chás e Infusões",
    "slug": "chas-e-infusoes",
    "imageUrl": "https://..."
  },
  {
    "name": "Suplementos",
    "slug": "suplementos",
    "imageUrl": "https://..."
  }
]
```

---

### `GET /product_categories` 🔑 Autenticado

Lista categorias com paginação para o painel.

**Query Parameters:** `search`, `page`, `sortField` (`name`, `createdAt`), `direction`

**Response `200 OK`:** lista paginada de `ProductCategoryRes`

---

### `GET /product_categories/{slug}` 🔑 Autenticado

Detalhes de uma categoria pelo slug.

**Response `200 OK`:**
```json
{
  "name": "Chás e Infusões",
  "slug": "chas-e-infusoes",
  "imageUrl": "https://..."
}
```

---

### `POST /product_categories` 🔑 Autenticado

Cria nova categoria com imagem.

**Content-Type:** `multipart/form-data`

| Part | Obrigatório | Descrição |
|------|-------------|-----------|
| `category` (JSON) | ✅ | `{"name": "Probióticos"}` |
| `image` | ✅ | Imagem da categoria |

**Response `201 Created`**

---

### `PUT /product_categories/{slug}` 🔑 Autenticado

Atualiza categoria existente.

**Parts:** `category` (JSON, obrigatório), `image` (opcional)

**Response `200 OK`**

---

### `DELETE /product_categories/{slug}` 🔑 Autenticado

Remove categoria e imagem.

**Response `200 OK`**

---

## 5. Suppliers (`/suppliers`)

### `GET /suppliers/get-all` 🔓 Público

Lista todos os fornecedores sem paginação.

**Response `200 OK`:**
```json
[
  {
    "name": "Fitoherb Natural",
    "slug": "fitoherb-natural",
    "imageUrl": "https://...",
    "isHighlighted": true
  }
]
```

---

### `GET /suppliers` 🔑 Autenticado

Lista fornecedores com paginação.

**Query Parameters:** `search`, `page`, `sortField` (`name`, `createdAt`), `direction`

---

### `GET /suppliers/{slug}` 🔑 Autenticado

Detalhes de um fornecedor pelo slug.

**Response `200 OK`:**
```json
{
  "name": "Fitoherb Natural",
  "slug": "fitoherb-natural",
  "imageUrl": "https://...",
  "isHighlighted": true
}
```

---

### `POST /suppliers` 🔑 Autenticado

Cria novo fornecedor com imagem.

**Content-Type:** `multipart/form-data`

| Part | Obrigatório |
|------|-------------|
| `supplier` (JSON) | ✅ |
| `image` | ✅ |

**JSON do fornecedor:**
```json
{
  "name": "Vita Supplements",
  "isHighlighted": false
}
```

**Response `201 Created`**

---

### `PUT /suppliers/{slug}` 🔑 Autenticado

Atualiza fornecedor. Imagem opcional.

**Response `200 OK`**

---

### `DELETE /suppliers/{slug}` 🔑 Autenticado

Remove fornecedor. Parâmetro `deleteProducts=true` permite remoção em cascata.

**Query Parameter:** `deleteProducts` (boolean, padrão: `false`)

> ⚠️ Sem `deleteProducts=true`, a exclusão falha se houver produtos vinculados.

**Response `200 OK`**

---

## 6. Banners (`/banners`)

### `GET /banners/active` 🔓 Público

Retorna banners ativos ordenados por posição (para a homepage).

**Response `200 OK`:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Promoção de Inverno",
    "imagePath": "banner_inverno.jpg",
    "imageUrl": "https://storage.googleapis.com/.../banner_inverno.jpg",
    "isActive": true,
    "position": 0,
    "createdAt": "23-09-2026 10:00:00",
    "updatedAt": "23-09-2026 12:00:00"
  }
]
```

---

### `GET /banners` 🔑 Autenticado

Lista banners com paginação para o painel.

**Query Parameters:** `search`, `page`, `sortField` (`position`, `title`, `createdAt`), `direction`

---

### `GET /banners/{id}` 🔑 Autenticado

Detalhes de um banner pelo ID.

**Path Parameter:** `id` — UUID do banner

**Response `200 OK`:** objeto `BannerRes`

---

### `POST /banners` 🔑 Autenticado

Cria novo banner com imagem.

**Content-Type:** `multipart/form-data`

| Part | Obrigatório |
|------|-------------|
| `banner` (JSON) | ✅ |
| `image` | ✅ |

**JSON do banner:**
```json
{
  "title": "Promoção de Inverno",
  "isActive": true,
  "position": 0
}
```

**Response `201 Created`**

---

### `PUT /banners/{id}` 🔑 Autenticado

Atualiza banner. Imagem opcional.

**Parts:** `banner` (JSON, obrigatório), `image` (opcional)

**Response `200 OK`**

---

### `DELETE /banners/{id}` 🔑 Autenticado

Remove banner e imagem do armazenamento.

**Response `200 OK`**

---

## 7. Respostas de Erro Padrão

### Erro simples (`RestErrorMessage`)
```json
{
  "status": "NOT_FOUND",
  "message": "Product not found with slug: cha-de-camomila"
}
```

### Erro de validação (`RestValidationErrorMessage`)
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

### Tabela de códigos HTTP utilizados

| Código | Situação |
|--------|---------|
| `200 OK` | Operação bem-sucedida |
| `201 Created` | Recurso criado (header `Location` presente) |
| `400 Bad Request` | Erro de validação de campos |
| `401 Unauthorized` | Token ausente, inválido ou expirado |
| `403 Forbidden` | Autenticado, mas sem permissão |
| `404 Not Found` | Recurso não encontrado |
| `409 Conflict` | Conflito de unicidade (slug, email, nome) |
| `500 Internal Server Error` | Erro inesperado (banco, storage, e-mail) |
