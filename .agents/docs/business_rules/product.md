# Business Rules: Product

> **Autor:** Analista de Requisitos
> **Objetivo:** Detalhar a lógica de negócios da vitrine/catálogo de produtos.

## Geração de Slug
- **P-009:** A definição da URL do produto é abstraída do usuário. O sistema obtém o campo "nome", normaliza-o em caracteres minúsculos, sem acentos, e gera o `slug` (ex: "Whey Protein" -> `whey-protein`).
- **P-010:** Operações de cadastro e alteração (POST/PUT) checam a unicidade do slug gerado. Se já existir, a transação é bloqueada, retornando `ResourceAlreadyExistsException`.

## Imagens Opcionais em Updates
- **P-011:** Em operações de alteração de produtos (PUT), o reenvio de arquivo de imagem não é obrigatório. A API inspeciona o objeto multipart e, caso a imagem venha nula, o sistema preserva a referência da imagem anterior já atrelada ao produto.

## Dinâmica de Busca e Filtros
- **P-012:** As listagens de Galeria (frontend) e Administrativa constroem filtros de busca (CriteriaBuilder) dinamicamente. Listas nulas ou vazias de Categorias e Fornecedores não restringem a busca, mas caso enviadas, funcionam em modo restritivo relacional inclusivo (`AND` / `IN`).
