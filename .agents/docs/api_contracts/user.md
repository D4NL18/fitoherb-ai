# API Contracts: Users

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) para o domínio de Usuários.

Abaixo apresento o design dos endpoints REST responsáveis pela gestão de identidades (users). Todos os endpoints exigem um token Bearer válido (`@PreAuthorize`).

## `GET /api/users`
- **Descrição:** Busca paginada de usuários (uso em backoffices).
- **Parâmetros da Query:**
  - `search`: Termo livre para busca.
  - `page`: Número da página (0-indexed).
  - `sortField` / `direction`: Campo de ordenação e direção (ASC/DESC).
- **Response:** Objeto de paginação Spring contendo listas de `UserRes`.

## `PUT /api/users/{email}`
- **Descrição:** Atualização dos dados cadastrais (exclusivo para Admins).
- **Path Param:** `email` (E-mail do alvo).
- **Request Body:** `UserReq` (name, email, role).
- **Response:** `200 OK`. Retorna 403 caso o invocador não seja ADMIN.

## `PATCH /api/users/update-password/{email}`
- **Descrição:** Troca de credenciais do usuário.
- **Path Param:** `email` do usuário.
- **Request Body:** `PasswordUpdateReq` (nova senha).
- **Response:** `200 OK`.

## `DELETE /api/users/{email}`
- **Descrição:** Exclusão definitiva de uma identidade administrativa (Apenas ADMIN).
- **Path Param:** `email`
- **Response:** `200 OK`.
