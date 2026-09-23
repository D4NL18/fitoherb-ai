# Tratamento de Erros e Exceções (Error Handling) 🚨

**ATENÇÃO DESENVOLVEDORES E ARQUITETOS:**
Erros silenciosos e blocos genéricos de `try/catch` são os maiores inimigos da manutenção. O tratamento de erro deve ser explícito, rastreável e semântico.

## 1. Proibição do Abafamento de Erro
- ❌ **Try-Catch Mudo:** É ESTRITAMENTE PROIBIDO capturar um erro e não fazer nada com ele (ex: `catch (e) { }` ou `catch (e) { console.log(e); }`).
- ✅ **A Solução:** Se você capturou um erro que não pode ser resolvido naquele nível, você DEVE disparar o erro para cima (`throw`) englobando-o em uma classe de erro de domínio, ou registrá-lo formalmente no serviço de Log.

## 2. Tipagem Customizada de Exceções
- ❌ **Lançamento de Erro Genérico:** Nunca utilize a classe genérica `Error` para regras de negócio (ex: `throw new Error("Usuário não encontrado")`). Isso impede que o middleware diferencie um erro de infraestrutura de uma validação de negócio.
- ✅ **A Solução:** O projeto DEVE possuir classes próprias de exceção herdando de `Error`. 
  - Ex: `class NotFoundException extends DomainException`
  - Ex: `class BusinessRuleViolationException extends DomainException`

## 3. Códigos de Erro Internos
- ❌ **Tratamento Baseado em Mensagens de Texto:** Nunca deixe o frontend validar strings para saber qual erro ocorreu (ex: `if (err.message === "Saldo insuficiente")`).
- ✅ **A Solução:** Toda exceção de domínio deve retornar um **Código Interno (Internal Code)** único em sua resposta.
  - Formato Obrigatório: `TRES_LETRAS_PREFIXO-NUMERO`.
  - Exemplo Payload: `{ "error": "Insufficient Funds", "code": "FIN-001" }`.

## 4. Centralização em Middleware/Global Handler
- ❌ **Tratamento Repetido nos Controllers:** Não coloque `try/catch` em toda rota da API apenas para retornar HTTP 500.
- ✅ **A Solução:** A interceptação primária deve acontecer em um único **Global Error Handler** (Middleware) que captura todas as exceções lançadas pela aplicação, loga corretamente e traduz o erro nativo em um contrato JSON limpo.
