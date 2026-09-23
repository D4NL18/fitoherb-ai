# Business Rules: ProductCategory

> **Autor:** Analista de Requisitos
> **Objetivo:** Regras que orbitam as Categorias de Produtos.

## Mecanismo de Slug
- **P-013:** Categorias obedecem ao mesmo fluxo de `slug` gerado de forma automática e silenciosa a partir do nome cadastrado, visando URLs *SEO-friendly*. Violações de unicidade bloqueiam a ação (`ResourceAlreadyExistsException`).

## Integridade na Deleção
- **P-014:** É vedada a exclusão de uma categoria se ela contiver produtos vinculados. A regra delega a falha de constraint diretamente ao banco, convertida em erro mapeado: "Verifique se não há registros vinculados a este cadastro."
