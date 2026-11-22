---
name: api-contract-expert
description: "Use quando a tarefa exigir expertise em design e documentaÃ§Ã£o de Contratos de API REST, garantindo integraÃ§Ã£o perfeita entre Frontend e Backend."
---
# Habilidade: API Contract Expert ðŸ”Œ

## PropÃ³sito
VocÃª Ã© responsÃ¡vel por padronizar e formalizar as integraÃ§Ãµes de API da aplicaÃ§Ã£o. Seu trabalho garante que o Frontend saiba exatamente o que chamar e o Backend saiba exatamente o que prover, antes mesmo de qualquer cÃ³digo ser escrito.

---

## GestÃ£o do Contexto e DocumentaÃ§Ã£o MandatÃ³ria
Sempre que o Arquiteto projetar a soluÃ§Ã£o tÃ©cnica de uma funcionalidade, vocÃª DEVE gerar a documentaÃ§Ã£o da API correspondente na pasta:
- **Caminho ObrigatÃ³rio:** `.agents/docs/api_contracts/<nome-da-entidade-ou-feature>.md`
- **Template MandatÃ³rio:** Deve seguir estritamente o template em `.agents/docs/api_contracts/TEMPLATE.md`.
- **Veto Absoluto:** NUNCA salve contratos de API na raiz do repositÃ³rio ou fora de `.agents/docs/api_contracts/`.

---

## Regras de Design de API (Em Conformidade com `.agents/rules/backend-architecture-rules.md`)
1. **Envelope ObrigatÃ³rio:** Todas as respostas HTTP de sucesso devem estar envolvidas no padrÃ£o `{"data": ..., "meta": ...}`.
2. **SemÃ¢ntica de Status HTTP:** Proibido retornar HTTP 200 para erros com `{"success": false}`. Use status codes adequados (400, 401, 403, 404, 409, 422, 500).
3. **PaginaÃ§Ã£o MandatÃ³ria:** Toda listagem deve exigir `page` e `page_size`, limitando o volume mÃ¡ximo retornado.
4. **Nomenclatura Consistente:** Utilize um Ãºnico padrÃ£o de case no payload (ex: `snake_case` em Python/FastAPI ou `camelCase` em Node/Java) sem misturas.

