-- ============================================================================
-- Exemplo: Migration Segura (Expand-and-Contract) + Mascaramento LGPD (PostgreSQL)
-- ============================================================================
-- Travas de segurança para evitar locks prolongados em produção:
SET lock_timeout = '5s';
SET statement_timeout = '30s';

-- ----------------------------------------------------------------------------
-- PARTE 1: EXPAND (Adição segura sem quebra de compatibilidade)
-- ----------------------------------------------------------------------------
BEGIN;

-- 1. Adiciona coluna pseudonimizada e coluna de status de anonimização
ALTER TABLE clientes
    ADD COLUMN IF NOT EXISTS uuid_titular UUID DEFAULT gen_random_uuid(),
    ADD COLUMN IF NOT EXISTS anonimizado_em TIMESTAMPTZ NULL;

COMMIT;

-- 2. Índice criado fora de transação com CONCURRENTLY (sem bloquear escritas)
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS ux_clientes_uuid_titular
    ON clientes (uuid_titular);

-- 3. Constraint NOT NULL sem table lock prolongado (NOT VALID -> VALIDATE)
ALTER TABLE clientes
    ADD CONSTRAINT chk_clientes_uuid_titular_not_null
    CHECK (uuid_titular IS NOT NULL) NOT VALID;

ALTER TABLE clientes
    VALIDATE CONSTRAINT chk_clientes_uuid_titular_not_null;

-- ----------------------------------------------------------------------------
-- PARTE 2: FUNÇÃO E VIEW DE MASCARAMENTO LGPD (Privacy by Default)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_mascarar_cpf(p_cpf TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN p_cpf IS NULL OR length(regexp_replace(p_cpf, '\D', '', 'g')) <> 11
            THEN '***.***.***-**'
        ELSE '***.' || substr(regexp_replace(p_cpf, '\D', '', 'g'), 4, 3) || '.'
             || substr(regexp_replace(p_cpf, '\D', '', 'g'), 7, 3) || '-**'
    END;
$$;

CREATE OR REPLACE FUNCTION fn_mascarar_email(p_email TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN p_email IS NULL OR position('@' IN p_email) <= 1
            THEN '***@***'
        ELSE left(p_email, 1) || '***' || substring(p_email FROM position('@' IN p_email))
    END;
$$;

-- View segura para consumo de Suporte / BI (sem expor PII em texto claro)
CREATE OR REPLACE VIEW vw_clientes_suporte AS
SELECT
    id,
    uuid_titular,
    fn_mascarar_cpf(cpf) AS cpf_mascarado,
    fn_mascarar_email(email) AS email_mascarado,
    criado_em,
    anonimizado_em
FROM clientes;

-- ----------------------------------------------------------------------------
-- PARTE 3: PROCEDIMENTO DE ANONIMIZAÇÃO IRREVERSÍVEL (Direito do Titular)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_anonimizar_cliente(p_cliente_id BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE clientes
    SET
        nome_completo  = 'ANONIMIZADO',
        cpf            = NULL,
        email          = 'anonimo_' || id || '@excluido.local',
        telefone       = NULL,
        anonimizado_em = NOW()
    WHERE id = p_cliente_id
      AND anonimizado_em IS NULL;
END;
$$;
