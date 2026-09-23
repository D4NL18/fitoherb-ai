# API Contracts: Products

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) do catálogo de produtos.

Estes endpoints expõem a interface para gestão e exibição dos produtos em loja. Operações de mutação exigem autenticação; métodos marcados como "vitrine" costumam ser públicos.

## `GET /api/products` (Administrativo)
- **Descrição:** Listagem com suporte a múltiplos filtros.
- **Query Params:** `search`, `categories[]`, `suppliers[]`, `page`, `sortField`, `direction`.
- **Response:** Objeto paginado com `ProductRes`.

## `GET /api/products/gallery` (Vitrine Frontend)
- **Descrição:** Endpoint otimizado para a exibição na loja (retorna um subconjunto de dados formatados ou aplica regras de exibição específicas).
- **Query Params:** Padrões de busca análogos.
- **Response:** Lista paginada.

## `GET /api/products/{slug}`
- **Descrição:** Busca detalhes de um produto específico através de sua URL amigável.
- **Path Param:** `slug`.
- **Response (200 OK):** `ProductRes` contendo informações completas (descricao, gramaturas, array de sabores, referências preenchidas de categoria e marca).

## `POST /api/products`
- **Descrição:** Cadastro de novo produto.
- **Content-Type:** `multipart/form-data`.
- **Form Data:**
  - `productReq` (String JSON com dados do produto).
  - `image` (Arquivo File).
- **Response:** `200 OK` (dados salvos).

## `PUT /api/products/{slug}`
- **Descrição:** Atualização completa do produto.
- **Path Param:** `slug`.
- **Content-Type:** `multipart/form-data`.
- **Response:** `200 OK`.

## `DELETE /api/products/{slug}`
- **Descrição:** Exclusão física do produto.
- **Path Param:** `slug`.
- **Response:** `200 OK`.
