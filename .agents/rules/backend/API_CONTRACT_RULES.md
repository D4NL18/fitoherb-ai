# Padrões de Contrato de API (REST) 🔌

**ATENÇÃO ARQUITETOS E DESENVOLVEDORES:**
Uma API inconsistente gera Frontend engessado. Estes são os padrões rígidos de comunicação.

## 1. O Envelope de Resposta
- ❌ **Respostas Soltas:** O backend NUNCA deve retornar o dado diretamente na raiz do JSON (ex: retornar `[ { "id": 1 } ]` nu e cru).
- ✅ **A Solução:** Toda e qualquer resposta HTTP 2xx DEVE vir padronizada em um "Envelope". 
  Padrão de Sucesso Exigido:
  ```json
  {
    "data": { "seu": "conteudo aqui" },
    "meta": { "timestamp": "...", "page": 1, "total": 100 }
  }
  ```

## 2. A Verdade do HTTP Status
- ❌ **O "Falso 200":** É absolutamente VETADO retornar HTTP `200 OK` quando ocorreu um erro de regra de negócio, apenas injetando um `{ "success": false }` no corpo. 
- ✅ **A Solução:** Respeite a semântica da Web.
  - `400 Bad Request` para erros de validação (com os campos inválidos listados no corpo).
  - `401 Unauthorized` (Sem credenciais) vs `403 Forbidden` (Com credencial mas sem permissão).
  - `404 Not Found` (Recurso não existe).
  - `409 Conflict` (ex: Email já cadastrado).
  - `422 Unprocessable Entity` (Erro em Regra de Negócio específica).

## 3. Padrão de Nomenclatura (Case)
- Defina e mantenha UM padão absoluto de nomenclatura no JSON (geralmente `camelCase` ou `snake_case`). Não misture `first_name` com `lastName` na mesma resposta.
