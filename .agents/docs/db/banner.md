# Domain: Banner

> **Autor:** Especialista DBA
> **Objetivo:** Estruturar a modelagem de banners rotativos do e-commerce.

A tabela `banners` armazena imagens de publicidade e comunicados do sistema, sendo totalmente independente das demais entidades.

## Estrutura (Tabela: `banners`)

- **`id`** (`UUID`, PK): Chave primária.
- **`title`** (`VARCHAR`, Único, Non-Null): Título do banner (trava de unicidade para evitar cadastros repetidos em duplicidade).
- **`subtitle`** (`VARCHAR`): Texto secundário/subtítulo.
- **`image_path`** (`VARCHAR`, Non-Null): Caminho da imagem vinculada no storage.

## Auditoria
- Segue o padrão estabelecido: `created_at`, `updated_at`, `created_by`, `updated_by`.
