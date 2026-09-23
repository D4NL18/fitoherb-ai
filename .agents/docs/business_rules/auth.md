# Business Rules: Auth

> **Autor:** Analista de Requisitos
> **Objetivo:** Documentar as regras de negócio pertinentes à segurança e login.

## Regras de JWT
- **P-001:** Tokens emitidos na autenticação possuem validade de 2 horas (ZoneOffset "-03:00").
- **P-002:** O *subject* contido no token JWT corresponde obrigatoriamente ao `email` do Usuário autenticado.
- **P-003:** A validação de assinatura do token é feita pelo algoritmo HMAC256. Falhas na verificação lançam imediatamente a `InvalidTokenException`.

## Regras de Registro
- **P-004:** Registros novos efetuados por vias externas públicas não concedem permissões administrativas (comportamento *self-service*). O sistema atribui compulsoriamente apenas a permissão `ROLE_USER`.
