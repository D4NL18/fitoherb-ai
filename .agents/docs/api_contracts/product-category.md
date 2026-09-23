# API Contracts: ProductCategory

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) para as Categorias de Produtos.

## `GET /api/product-categories`
- **Descrição:** Lista plana, não paginada (ideal para preencher selects e dropdowns).
- **Response:** `List<ProductCategoryRes>`.

## `GET /api/product-categories/paginated`
- **Descrição:** Lista paginada para gestão no backoffice.
- **Query Params:** `search`, `page`, `sortField`, `direction`.
- **Response:** Objeto paginado.

## `GET /api/product-categories/{slug}`
- **Descrição:** Recupera detalhes de uma categoria via slug.
- **Response:** `ProductCategoryRes`.

## `POST /api/product-categories`
- **Descrição:** Cria nova categoria.
- **Content-Type:** `multipart/form-data`. (Json data + imagem).

## `PUT /api/product-categories/{slug}`
- **Descrição:** Edita categoria existente.

## `DELETE /api/product-categories/{slug}`
- **Descrição:** Deleta a categoria via slug.
