# API Contracts: Supplier

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) para Fornecedores / Marcas.

## `GET /api/suppliers`
- **Descrição:** Lista plana de todos os fornecedores (útil em combobox/filtros).

## `GET /api/suppliers/paginated`
- **Descrição:** Listagem com suporte a paginação e buscas textuais.

## `GET /api/suppliers/{slug}`
- **Descrição:** Recupera fornecedor por URL amigável.

## `POST /api/suppliers` e `PUT /api/suppliers/{slug}`
- **Content-Type:** `multipart/form-data`.
- Permitem associação de uma logo/imagem oficial da marca.

## `DELETE /api/suppliers/{slug}`
- **Descrição:** Remove o fornecedor.
- **Query Param (Opcional):** `cascade` (Booleano) - sinaliza ao backend se os produtos filhos devem ser destruídos em conjunto.
