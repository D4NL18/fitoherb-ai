---
description: "Anti-padrões de segurança inegociáveis (tokens, secrets, injections, PII) com poder de veto imediato por SecOps e Reviewer."
trigger: always_on
---

# Anti-Padrões de Segurança 🛡️

**ATENÇÃO AGENTES DE DESENVOLVIMENTO, REVIEWERS E SECOPS:**
A segurança da informação é inegociável. Qualquer violação destas regras resultará em veto imediato.

---

## 1. Gestão de Sessão e Tokens (Identidade)
- ❌ **PROIBIDO JWT NO LOCAL STORAGE:** É estritamente proibido armazenar *JSON Web Tokens* (JWT) ou credenciais de sessão no `localStorage` ou `sessionStorage` do navegador devido à vulnerabilidade a ataques XSS.
- ✅ **A Solução:** Tokens de autenticação DEVEM ser trafegados exclusivamente via **Cookies `HttpOnly`, `Secure` e `SameSite`**, garantindo que scripts cliente não acessem as credenciais diretamente.

---

## 2. Prevenção a Vazamento de Dados (Data Leak)
- ❌ **Logs de Objetos Inteiros:** É proibido logar requisições ou entidades completas (ex: `console.log(user)` ou `logger.info(req.body)`), evitando gravação acidental de senhas, cartões, CPFs ou PII em logs de nuvem.
- ❌ **Stacktraces em Produção:** O tratamento global de exceções NUNCA deve retornar a *Stacktrace* completa da aplicação em respostas HTTP de produção. Retorne apenas JSON padronizado com mensagem amigável e código de erro semântico.

---

## 3. Injeção e Sanitização (SQLi / XSS / Comandos)
- ❌ **Concatenação de SQL:** Jamais construa consultas de banco de dados concatenando strings. O uso de parâmetros vinculados (Prepared Statements / Bind Parameters) ou ORMs seguros é obrigatório.
- ❌ **Confiança Cega no Cliente:** Todo e qualquer dado vindo de `body`, `query` ou `params` DEVE ser validado e sanitizado (via DTOs, Bean Validation, Pydantic ou Zod) na entrada da API. O backend nunca confia no frontend.
