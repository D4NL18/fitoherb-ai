# Domain: User

> **Autor:** Especialista DBA
> **Objetivo:** Estruturar de forma segura o armazenamento de usuários e senhas.

A tabela `users` é crítica, exigindo atenção redobrada na proteção da coluna de senha.

## Estrutura (Tabela: `users`)

- **`id`** (`UUID`, PK): Chave primária de identificação.
- **`email`** (`VARCHAR`, Único, Non-Null): E-mail do usuário. Funciona como *username* e chave natural (única).
- **`name`** (`VARCHAR`, Non-Null): Nome completo do usuário.
- **`password`** (`VARCHAR`, Non-Null): Hash da senha. *Nunca expor no retorno do banco*.
- **`role`** (`TINYINT/VARCHAR`, Non-Null): Enum (UserRole) mapeado para banco indicando os privilégios de acesso (`ADMIN`, `USER`).

## Auditoria e Segurança
- Histórico mantido através de `created_at`, `updated_at`, `created_by`, `updated_by`.
