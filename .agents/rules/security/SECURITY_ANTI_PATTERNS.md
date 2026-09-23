# Anti-Padrões de Segurança 🛡️

**ATENÇÃO AGENTES DE DESENVOLVIMENTO E REVIEWERS:**
A segurança é inegociável. Qualquer violação destas regras resultará em veto imediato (SecOps / Reviewer).

## 1. Gestão de Sessão e Tokens (Identidade)
- ❌ **PROIBIDO JWT NO LOCAL STORAGE:** É estritamente proibido armazenar *JSON Web Tokens* (JWT) ou qualquer token de acesso sensível no `localStorage` ou `sessionStorage` do navegador, pois ficam vulneráveis a ataques XSS.
- ✅ **A Solução:** Tokens de autenticação DEVEM ser trafegados exclusivamente via **Cookies `HttpOnly`, `Secure` e `SameSite`**, garantindo que o JavaScript do lado do cliente não tenha acesso à leitura da credencial.

## 2. Prevenção a Vazamento de Dados (Data Leak)
- ❌ **Logs de Objetos Inteiros:** É proibido logar requisições ou objetos de usuário indiscriminadamente (ex: `console.log(user)` ou `logger.info(req.body)`). Isso evita que senhas criptografadas, CPFs ou PII (Dados Pessoalmente Identificáveis) fiquem gravados nos logs da nuvem.
- ❌ **Stacktraces em Produção:** O tratamento global de exceções NUNCA deve retornar a *Stacktrace* completa da linguagem para a resposta da API se a aplicação estiver em produção. Retorne apenas uma mensagem amigável (HTTP 500 genérico).

## 3. Injeção e Sanitização (SQLi / XSS)
- ❌ **Concatenação de SQL:** Jamais construa consultas de banco de dados concatenando strings. O uso de parâmetros vinculados (Prepared Statements / Bind Parameters) ou ORMs seguros é obrigatório.
- ❌ **Confiança Cega no Cliente:** Todo e qualquer dado vindo de `body`, `query` ou `params` da API DEVE ser higienizado e validado (via DTOs/Schemas rigorosos) antes de tocar na regra de negócio. O Backend não confia no Frontend.
