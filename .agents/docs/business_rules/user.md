# Business Rules: User

> **Autor:** Analista de Requisitos
> **Objetivo:** Documentar as regras que incidem sobre os perfis de usuários (identidades).

## Permissões (Roles)
- **P-005:** Somente usuários portadores da role `ADMIN` estão autorizados a listar todos os usuários da base de dados e acessar visões globais.
- **P-006:** A mutação e gestão de contas de terceiros (operações PUT e DELETE) é restrita a administradores (role `ADMIN`).
- **P-007:** Qualquer usuário logado pode realizar a sua própria troca de senha (PATCH update-password), sob a condição de que envie a requisição apontando para o seu próprio email (usuário da sessão).

## Deleção
- **P-008:** O fluxo de exclusão de usuário falhará lançando `DatabaseOperationException` se o usuário-alvo possuir amarras fortes de auditoria (ex: registrou criações no log `created_by`), atuando como proteção contra inconsistências e perda de histórico no banco de dados.
