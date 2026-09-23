# Domain: Product

> **Autor:** Especialista DBA
> **Objetivo:** Definir a modelagem de dados segura e estrutural para a tabela de produtos.

A tabela `products` é o core do nosso catálogo. Projetei esta estrutura com campos otimizados e relacionamentos com integridade referencial forte (chaves estrangeiras).

## Estrutura (Tabela: `products`)

- **`id`** (`UUID`, PK): Identificador único do produto, garantindo escalabilidade.
- **`name`** (`VARCHAR`, Único, Non-Null): Nome principal do produto. Protegido com restrição de unicidade para evitar duplicações no e-commerce.
- **`slug`** (`VARCHAR`, Único, Non-Null): Identificador para rotas amigáveis (URL).
- **`image_path`** (`VARCHAR`): Caminho/URL de referência do bucket/storage da imagem.
- **`description`** (`TEXT`): Texto longo com a descrição do produto.
- **`flavours`** (`ARRAY/JSON`): Estrutura para armazenar os sabores disponíveis daquele produto (ex: Morango, Chocolate).
- **`presentation`** (`ARRAY/JSON`): Formatos de apresentação e gramatura (ex: 500g, 1kg).
- **`category_id`** (`UUID`, FK, Non-Null): Referência à tabela `product_categories`. Busca via `FetchType.LAZY` no ORM para otimização de leitura.
- **`supplier_id`** (`UUID`, FK, Non-Null): Referência à tabela `suppliers`. Também em modo `LAZY`.

## Auditoria (Segurança de Dados)
Apliquei o *Auditing* do JPA (listeners) para rastreabilidade automática:
- **`created_at`** (`TIMESTAMP`, Non-Null, Updatable=false): Marcador de criação.
- **`updated_at`** (`TIMESTAMP`): Marcador de atualização.
- **`created_by`** / **`updated_by`** (`VARCHAR`): Usuários responsáveis por manipular o registro.
