# Business Rules: Supplier

> **Autor:** Analista de Requisitos
> **Objetivo:** Definir como as marcas/fornecedores são validados na aplicação.

## Mecanismo de Slug
- **P-015:** Fornecedores possuem slug gerado automaticamente com garantia estrita de unicidade em banco.

## Exclusão Suave vs Cascata
- **P-016:** Por padrão, a deleção de Fornecedor é segura. O sistema bloqueará se houver produtos atrelados, visando não corromper o catálogo.
- **P-017:** A API disponibiliza, mediante flag deliberada (`cascade=true`), a possibilidade de executar a exclusão em cascata, superando a trava protetiva descrita na regra **P-016**.
