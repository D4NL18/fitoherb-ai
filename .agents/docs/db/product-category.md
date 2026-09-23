# Domain: ProductCategory

> **Autor:** Especialista DBA
> **Objetivo:** Definir a modelagem de dados segura para categorias de produtos.

A tabela `product_categories` armazena as categorias para agrupar nossos produtos. É fundamental garantir que a deleção acidental não prejudique a integridade dos produtos atrelados.

## Estrutura (Tabela: `product_categories`)

- **`id`** (`UUID`, PK): Identificador único gerado automaticamente.
- **`name`** (`VARCHAR`, Único, Non-Null): Nome da categoria. Possui trava de unicidade no banco.
- **`slug`** (`VARCHAR`, Único, Non-Null): Chave URL-friendly, indexada e única.
- **`image_path`** (`VARCHAR`): Referência da imagem da categoria no storage.

## Relacionamentos
- Serve como chave estrangeira (`category_id`) para a tabela `products`.

## Auditoria
- Campos de tracking ativados: `created_at`, `updated_at`, `created_by`, `updated_by`. Protegidos contra updates indevidos através das restrições do JPA e do banco.
