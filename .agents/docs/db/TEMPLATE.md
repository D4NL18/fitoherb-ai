# Documentação de Banco de Dados: [Nome do Módulo/Domínio]

> **Localização Mandatória:** `.agents/docs/db/<nome-do-modulo>.md`  
> **Responsável:** DBA (`dba-expert`)  
> **Referências de Regras:** `.agents/rules/backend/DB_PERFORMANCE_RULES.md`

---

## 1. Visão Geral do Módulo
- **Domínio de Negócio:** [Ex: Financeiro, Usuários, Atendimento]
- **Propósito:** [Explique em 2 a 3 frases o objetivo desse conjunto de dados respeitando a Linguagem Ubíqua do `GLOSSARY.md`]
- **Mecanismo de Persistência:** [Ex: PostgreSQL 16, MySQL 8, Firestore Native]

---

## 2. Estrutura de Tabelas

### 2.1. Tabela: `[nome_da_tabela_plural]`
- **Descrição de Negócio:** [O que cada registro representa]

| Coluna | Tipo Primitivo | Nulo? | Padrão (Default) | Descrição / Regra |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` / `BIGINT` | `NOT NULL` | `gen_random_uuid()` | Chave primária identificadora |
| `[nome_coluna]` | `VARCHAR(255)` | `NOT NULL` | `N/A` | [Descrição do dado] |
| `status` | `VARCHAR(30)` | `NOT NULL` | `'ACTIVE'` | Enum de status: `ACTIVE`, `INACTIVE` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | Timestamp de criação |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | Timestamp da última atualização |

#### Relacionamentos e Chaves Estrangeiras (Foreign Keys)
- `fk_[tabela]_[tabela_origem]`: `origem_id` referencia `tabela_origem(id)` com `ON DELETE RESTRICT` (ou `CASCADE` justificado).

#### Constraints & Validações de Domínio
- **Check Constraint:** `chk_[nome]` [Ex: `valor >= 0`]
- **Unique Key:** `uk_[tabela]_[coluna]` [Ex: `uk_usuarios_email`]

#### Índices e Otimização de Performance
> [!IMPORTANT]
> Toda Foreign Key e coluna usada em filtros frequentes (`WHERE`, `ORDER BY`) DEVE possuir índice explícito para prevenir *Full Table Scan* (N+1).
- `idx_[tabela]_[fk_coluna]`: B-Tree na coluna `origem_id`.
- `idx_[tabela]_status_created`: Índice composto para listagens paginadas.

---

## 3. Estratégia de Migrations
- **Arquivo Migration UP:** `db/migrations/V00X__cria_tabela_[nome].sql`
- **Arquivo Migration DOWN (Rollback Obrigatório):** `db/migrations/undo/U00X__drop_tabela_[nome].sql`

---

## 4. Dados de Teste Realistas (Mock Data Seeds)
> Os scripts completos de inserção devem ser salvos em `.agents/docs/db/seeds/[nome_do_modulo]_seeds.sql`.

Exemplo de inserção respeitando integridade referencial e realismo:
```sql
-- Inserções com dados realistas (evite 'teste1', 'teste2')
INSERT INTO [nome_da_tabela] (id, nome, status, created_at)
VALUES 
  ('a1b2c3d4-0000-0000-0000-000000000001', 'João Carlos Oliveira', 'ACTIVE', NOW()),
  ('a1b2c3d4-0000-0000-0000-000000000002', 'Mariana Santos Silva', 'ACTIVE', NOW());
```
