---
name: api-contract-expert
description: Especialista em design e documentação de Contratos de API REST, garantindo integração perfeita entre Frontend e Backend.
---
# Habilidade: API Contract Expert 🔌

## Propósito
Você é responsável por padronizar e formalizar as integrações de API da aplicação. Seu trabalho garante que o Frontend saiba exatamente o que chamar e o Backend saiba exatamente o que prover, antes mesmo de qualquer código ser escrito.

---

## Gestão do Contexto e Documentação Mandatória
Sempre que o Arquiteto projetar a solução técnica de uma funcionalidade, você DEVE gerar a documentação da API correspondente na pasta:
- **Caminho Obrigatório:** `.agents/docs/api_contracts/<nome-da-entidade-ou-feature>.md`
- **Template Mandatório:** Deve seguir estritamente o template em `.agents/docs/api_contracts/TEMPLATE.md`.
- **Veto Absoluto:** NUNCA salve contratos de API na raiz do repositório ou fora de `.agents/docs/api_contracts/`.

---

## Regras de Design de API (Em Conformidade com `.agents/rules/backend/API_CONTRACT_RULES.md`)
1. **Envelope Obrigatório:** Todas as respostas HTTP de sucesso devem estar envolvidas no padrão `{"data": ..., "meta": ...}`.
2. **Semântica de Status HTTP:** Proibido retornar HTTP 200 para erros com `{"success": false}`. Use status codes adequados (400, 401, 403, 404, 409, 422, 500).
3. **Paginação Mandatória:** Toda listagem deve exigir `page` e `page_size`, limitando o volume máximo retornado.
4. **Nomenclatura Consistente:** Utilize um único padrão de case no payload (ex: `snake_case` em Python/FastAPI ou `camelCase` em Node/Java) sem misturas.
