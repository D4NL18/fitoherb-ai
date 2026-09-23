# API Contracts: Auth

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) para Autenticação.

Abaixo apresento o design dos endpoints REST desenhados para gerenciar a segurança e o controle de acesso por JWT.

## `POST /api/auth/login`
- **Descrição:** Endpoint público para emissão de JWT.
- **Request Body (JSON):**
  - `email` (String)
  - `password` (String)
- **Response (200 OK):**
  - `token` (String, Bearer JWT)
  - Detalhes básicos do usuário.

## `POST /api/auth/register`
- **Descrição:** Endpoint público/administrativo para criação do primeiro acesso ou self-registration.
- **Request Body (JSON):**
  - `name` (String)
  - `email` (String)
  - `password` (String)
- **Response:** `200 OK` (sem corpo).
