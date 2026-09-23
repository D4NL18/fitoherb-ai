# Banco de Dados — Fitoherb Backend v2

> **Data de criação:** 2026-09-23  
> **SGBD:** PostgreSQL  
> **ORM:** JPA/Hibernate (Spring Data JPA)

---

## 1. Diagrama Entidade-Relacionamento (ER)

```
┌─────────────────────────────────────────┐
│               users                     │
│─────────────────────────────────────────│
│ id          UUID  PK                    │
│ email       VARCHAR UNIQUE NOT NULL     │
│ name        VARCHAR NOT NULL            │
│ password    VARCHAR NOT NULL (BCrypt)   │
│ role        VARCHAR NOT NULL (ENUM)     │
│ created_at  TIMESTAMP NOT NULL          │
│ updated_at  TIMESTAMP                   │
│ created_by  VARCHAR                     │
│ updated_by  VARCHAR                     │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────┐        ┌─────────────────────────────────────────┐
│          product_categories             │        │               suppliers                 │
│─────────────────────────────────────────│        │─────────────────────────────────────────│
│ id          UUID  PK                    │        │ id             UUID  PK                 │
│ name        VARCHAR UNIQUE NOT NULL     │        │ name           VARCHAR UNIQUE NOT NULL  │
│ slug        VARCHAR UNIQUE NOT NULL     │        │ slug           VARCHAR UNIQUE NOT NULL  │
│ image_path  VARCHAR                     │        │ image_path     VARCHAR                  │
│ created_at  TIMESTAMP NOT NULL          │        │ is_highlighted BOOLEAN                  │
│ updated_at  TIMESTAMP                   │        │ created_at     TIMESTAMP NOT NULL       │
│ created_by  VARCHAR                     │        │ updated_at     TIMESTAMP                │
│ updated_by  VARCHAR                     │        │ created_by     VARCHAR                  │
└────────────────┬────────────────────────┘        │ updated_by     VARCHAR                  │
                 │ 1                               └──────────────────┬──────────────────────┘
                 │                                                    │ 1
                 │ N                                                  │ N
                 └──────────────┐           ┌────────────────────────┘
                                ▼           ▼
                 ┌──────────────────────────────────────────────────┐
                 │                    products                      │
                 │──────────────────────────────────────────────────│
                 │ id           UUID  PK                            │
                 │ name         VARCHAR NOT NULL                    │
                 │ slug         VARCHAR UNIQUE NOT NULL             │
                 │ image_path   VARCHAR                             │
                 │ description  TEXT                                │
                 │ flavours     TEXT[]                              │
                 │ presentation TEXT[]                              │
                 │ category_id  UUID  FK → product_categories.id   │
                 │ supplier_id  UUID  FK → suppliers.id            │
                 │ created_at   TIMESTAMP NOT NULL                  │
                 │ updated_at   TIMESTAMP                           │
                 │ created_by   VARCHAR                             │
                 │ updated_by   VARCHAR                             │
                 └──────────────────────────────────────────────────┘


┌─────────────────────────────────────────┐
│                banners                  │
│─────────────────────────────────────────│
│ id          UUID  PK                    │
│ title       VARCHAR NOT NULL            │
│ image_path  VARCHAR NOT NULL            │
│ is_active   BOOLEAN NOT NULL DEFAULT true│
│ position    INTEGER NOT NULL DEFAULT 0  │
│ created_at  TIMESTAMP NOT NULL          │
│ updated_at  TIMESTAMP                   │
│ created_by  VARCHAR                     │
│ updated_by  VARCHAR                     │
└─────────────────────────────────────────┘
```

---

## 2. DDL SQL — Criação das Tabelas

### 2.1 Tabela `users`

```sql
CREATE TABLE users (
    id          VARCHAR(36)  PRIMARY KEY,  -- UUID gerado pelo JPA
    email       VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    password    VARCHAR(255) NOT NULL,     -- Hash BCrypt
    role        VARCHAR(50)  NOT NULL,     -- Enum: 'ADMIN' | 'USER'
    created_at  TIMESTAMP    NOT NULL,
    updated_at  TIMESTAMP,
    created_by  VARCHAR(255),             -- Email do usuário que criou
    updated_by  VARCHAR(255)              -- Email do usuário que modificou
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role  ON users(role);
```

### 2.2 Tabela `product_categories`

```sql
CREATE TABLE product_categories (
    id          VARCHAR(36)  PRIMARY KEY,  -- UUID gerado pelo JPA
    name        VARCHAR(255) NOT NULL UNIQUE,
    slug        VARCHAR(255) NOT NULL UNIQUE, -- Gerado automaticamente via @PrePersist
    image_path  VARCHAR(500),             -- Caminho/URL da imagem
    created_at  TIMESTAMP    NOT NULL,
    updated_at  TIMESTAMP,
    created_by  VARCHAR(255),
    updated_by  VARCHAR(255)
);

CREATE INDEX idx_product_categories_slug ON product_categories(slug);
```

### 2.3 Tabela `suppliers`

```sql
CREATE TABLE suppliers (
    id             VARCHAR(36)  PRIMARY KEY,
    name           VARCHAR(255) NOT NULL UNIQUE,
    slug           VARCHAR(255) NOT NULL UNIQUE, -- Gerado automaticamente via @PrePersist
    image_path     VARCHAR(500),
    is_highlighted BOOLEAN,
    created_at     TIMESTAMP    NOT NULL,
    updated_at     TIMESTAMP,
    created_by     VARCHAR(255),
    updated_by     VARCHAR(255)
);

CREATE INDEX idx_suppliers_slug         ON suppliers(slug);
CREATE INDEX idx_suppliers_highlighted  ON suppliers(is_highlighted);
```

### 2.4 Tabela `products`

```sql
CREATE TABLE products (
    id           VARCHAR(36)  PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    slug         VARCHAR(255) NOT NULL UNIQUE, -- Gerado automaticamente via @PrePersist
    image_path   VARCHAR(500),
    description  TEXT,
    flavours     TEXT[],                       -- Array PostgreSQL de strings
    presentation TEXT[],                      -- Array PostgreSQL de strings
    category_id  VARCHAR(36)  NOT NULL,
    supplier_id  VARCHAR(36)  NOT NULL,
    created_at   TIMESTAMP    NOT NULL,
    updated_at   TIMESTAMP,
    created_by   VARCHAR(255),
    updated_by   VARCHAR(255),

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES product_categories(id),
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE INDEX idx_products_slug        ON products(slug);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_supplier_id ON products(supplier_id);
CREATE INDEX idx_products_name        ON products(name);
```

### 2.5 Tabela `banners`

```sql
CREATE TABLE banners (
    id          VARCHAR(36)  PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    image_path  VARCHAR(500) NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    position    INTEGER      NOT NULL DEFAULT 0,
    created_at  TIMESTAMP    NOT NULL,
    updated_at  TIMESTAMP,
    created_by  VARCHAR(255),
    updated_by  VARCHAR(255)
);

CREATE INDEX idx_banners_is_active ON banners(is_active);
CREATE INDEX idx_banners_position  ON banners(position);
```

---

## 3. Descrição Detalhada das Tabelas

### 3.1 `users`

| Coluna | Tipo | Obrigatório | Único | Descrição |
|--------|------|-------------|-------|-----------|
| `id` | VARCHAR(36) | ✅ | ✅ | UUID gerado automaticamente pelo JPA |
| `email` | VARCHAR(255) | ✅ | ✅ | E-mail único do usuário, usado como login |
| `name` | VARCHAR(255) | ✅ | ❌ | Nome completo do usuário |
| `password` | VARCHAR(255) | ✅ | ❌ | Senha hasheada com BCrypt |
| `role` | VARCHAR(50) | ✅ | ❌ | Papel do usuário: `ADMIN` ou `USER` |
| `created_at` | TIMESTAMP | ✅ | ❌ | Data/hora de criação (automático, imutável) |
| `updated_at` | TIMESTAMP | ❌ | ❌ | Data/hora da última modificação (automático) |
| `created_by` | VARCHAR(255) | ❌ | ❌ | Email do usuário que criou o registro |
| `updated_by` | VARCHAR(255) | ❌ | ❌ | Email do usuário que modificou o registro |

**Enum `UserRole`:**
- `ADMIN` — acesso total ao sistema
- `USER` — acesso limitado (leitura)

**Autoridades Spring Security:**
- `ADMIN` → `ROLE_ADMIN` + `ROLE_USER`
- `USER` → `ROLE_USER`

---

### 3.2 `product_categories`

| Coluna | Tipo | Obrigatório | Único | Descrição |
|--------|------|-------------|-------|-----------|
| `id` | VARCHAR(36) | ✅ | ✅ | UUID gerado automaticamente |
| `name` | VARCHAR(255) | ✅ | ✅ | Nome único da categoria |
| `slug` | VARCHAR(255) | ✅ | ✅ | Slug URL-friendly (gerado automaticamente do name) |
| `image_path` | VARCHAR(500) | ❌ | ❌ | Caminho ou URL da imagem da categoria |
| `created_at` | TIMESTAMP | ✅ | ❌ | Data/hora de criação |
| `updated_at` | TIMESTAMP | ❌ | ❌ | Data/hora da última modificação |
| `created_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — criador |
| `updated_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — último modificador |

---

### 3.3 `suppliers`

| Coluna | Tipo | Obrigatório | Único | Descrição |
|--------|------|-------------|-------|-----------|
| `id` | VARCHAR(36) | ✅ | ✅ | UUID gerado automaticamente |
| `name` | VARCHAR(255) | ✅ | ✅ | Nome único do fornecedor |
| `slug` | VARCHAR(255) | ✅ | ✅ | Slug URL-friendly (gerado automaticamente do name) |
| `image_path` | VARCHAR(500) | ❌ | ❌ | Caminho ou URL do logotipo do fornecedor |
| `is_highlighted` | BOOLEAN | ❌ | ❌ | Se o fornecedor deve ser destacado na vitrine |
| `created_at` | TIMESTAMP | ✅ | ❌ | Data/hora de criação |
| `updated_at` | TIMESTAMP | ❌ | ❌ | Data/hora da última modificação |
| `created_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — criador |
| `updated_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — último modificador |

---

### 3.4 `products`

| Coluna | Tipo | Obrigatório | Único | Descrição |
|--------|------|-------------|-------|-----------|
| `id` | VARCHAR(36) | ✅ | ✅ | UUID gerado automaticamente |
| `name` | VARCHAR(255) | ✅ | ❌ | Nome do produto |
| `slug` | VARCHAR(255) | ✅ | ✅ | Slug URL-friendly único (gerado automaticamente) |
| `image_path` | VARCHAR(500) | ❌ | ❌ | Caminho ou URL da imagem principal do produto |
| `description` | TEXT | ❌ | ❌ | Descrição detalhada do produto |
| `flavours` | TEXT[] | ❌ | ❌ | Array de sabores disponíveis |
| `presentation` | TEXT[] | ❌ | ❌ | Array de apresentações disponíveis (ex: 100g, 250g) |
| `category_id` | VARCHAR(36) | ✅ | ❌ | FK para `product_categories.id` |
| `supplier_id` | VARCHAR(36) | ✅ | ❌ | FK para `suppliers.id` |
| `created_at` | TIMESTAMP | ✅ | ❌ | Data/hora de criação |
| `updated_at` | TIMESTAMP | ❌ | ❌ | Data/hora da última modificação |
| `created_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — criador |
| `updated_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — último modificador |

**Relações:**
- `category_id` → `product_categories.id` (MANY_TO_ONE, LAZY)
- `supplier_id` → `suppliers.id` (MANY_TO_ONE, LAZY)

---

### 3.5 `banners`

| Coluna | Tipo | Obrigatório | Único | Descrição |
|--------|------|-------------|-------|-----------|
| `id` | VARCHAR(36) | ✅ | ✅ | UUID gerado automaticamente |
| `title` | VARCHAR(255) | ✅ | ❌ | Título do banner |
| `image_path` | VARCHAR(500) | ✅ | ❌ | Caminho ou URL da imagem do banner |
| `is_active` | BOOLEAN | ✅ | ❌ | Indica se o banner está ativo (default: `true`) |
| `position` | INTEGER | ✅ | ❌ | Ordem de exibição (default: `0`) |
| `created_at` | TIMESTAMP | ✅ | ❌ | Data/hora de criação |
| `updated_at` | TIMESTAMP | ❌ | ❌ | Data/hora da última modificação |
| `created_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — criador |
| `updated_by` | VARCHAR(255) | ❌ | ❌ | Auditoria — último modificador |

---

## 4. Campos de Auditoria

Todas as tabelas possuem os mesmos quatro campos de auditoria, gerenciados automaticamente pelo Spring Data JPA Auditing:

| Campo | Annotation JPA | Comportamento |
|-------|---------------|--------------|
| `created_at` | `@CreatedDate` | Preenchido na inserção, imutável (`updatable = false`) |
| `updated_at` | `@LastModifiedDate` | Atualizado automaticamente em cada modificação |
| `created_by` | `@CreatedBy` | Email do usuário autenticado no momento da criação, imutável |
| `updated_by` | `@LastModifiedBy` | Email do usuário autenticado no momento da última modificação |

O `AuditorAwareImpl` lê o principal do `SecurityContextHolder`:

```java
@Component
public class AuditorAwareImpl implements AuditorAware<String> {
    @Override
    public Optional<String> getCurrentAuditor() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) return Optional.empty();
        return Optional.of(auth.getName()); // retorna o email
    }
}
```

---

## 5. Convenções e Observações

### 5.1 Geração de UUID
- Todos os IDs são gerados pelo JPA via `@GeneratedValue(strategy = GenerationType.UUID)`
- Resultado: strings UUID v4 no formato `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 5.2 Geração de Slug
- `ProductCategory`, `Supplier` e `Product` geram o slug automaticamente via `@PrePersist` e `@PreUpdate`
- A função `StringUtils.toSlug(name)` converte para lowercase, remove acentos e substitui espaços/caracteres especiais por hífens
- Exemplo: `"Chá de Camomila Orgânico"` → `"cha-de-camomila-organico"`

### 5.3 Arrays PostgreSQL
- Os campos `flavours` e `presentation` da tabela `products` são arrays nativos do PostgreSQL (`TEXT[]`)
- O mapeamento JPA usa `List<String>` com suporte via Hibernate e type adapter

### 5.4 Fetch Type LAZY
- Os relacionamentos `@ManyToOne` em `Product` (category e supplier) são `LAZY`
- Evita N+1 queries em listagens; o Spring Data JPA gerencia joins quando necessário nas queries

### 5.5 Restrição de Integridade Referencial
- Ao tentar deletar um `Supplier` ou `ProductCategory` que possua `Products` vinculados sem usar a flag `deleteProducts=true`, a operação falha com erro de integridade referencial (`INTERNAL_SERVER_ERROR`)
