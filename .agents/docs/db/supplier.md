# Domain: Supplier

> **Autor:** Especialista DBA
> **Objetivo:** Definir a modelagem de dados da tabela de fornecedores/marcas.

A tabela `suppliers` cadastra os fornecedores e marcas dos produtos, servindo de dependência direta para a tabela de produtos.

## Estrutura (Tabela: `suppliers`)

- **`id`** (`UUID`, PK): Chave primária.
- **`name`** (`VARCHAR`, Único, Non-Null): Nome da marca/fornecedor. Chave única para evitar duplicidades no BD.
- **`slug`** (`VARCHAR`, Único, Non-Null): Slug amigável gerado do nome.
- **`image_path`** (`VARCHAR`): Logo ou imagem de destaque do fornecedor.
- **`is_highlighted`** (`BOOLEAN`): Flag indicativa se o fornecedor ganha seção de destaque no portal.

## Relacionamentos
- Exporta PK como `supplier_id` na tabela `products`. 

## Auditoria
- Campos de tracking padrão: `created_at`, `updated_at`, `created_by`, `updated_by`.
