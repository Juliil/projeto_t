-- ============================================================
--  Projeto T  ·  Schema inicial (POC)
--  Executado automaticamente pelo Postgres no primeiro boot.
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT        NOT NULL UNIQUE,
    senha_hash  TEXT        NOT NULL,
    nome        TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'pre_registro',  -- pre_registro | ativo
    perfil      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS materiais (
    id              BIGSERIAL PRIMARY KEY,
    usuario_id      BIGINT      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome            TEXT        NOT NULL,
    categoria       TEXT,
    unidade         TEXT        NOT NULL DEFAULT 'un',          -- un | ml | g | sessao
    custo_unitario  NUMERIC(12,2) NOT NULL DEFAULT 0,
    estoque         NUMERIC(12,2) NOT NULL DEFAULT 0,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_materiais_usuario ON materiais(usuario_id);

CREATE TABLE IF NOT EXISTS orcamentos (
    id              BIGSERIAL PRIMARY KEY,
    usuario_id      BIGINT      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo          TEXT        NOT NULL,
    horas           NUMERIC(8,2)  NOT NULL DEFAULT 0,
    valor_hora      NUMERIC(12,2) NOT NULL DEFAULT 0,
    margem_pct      NUMERIC(6,2)  NOT NULL DEFAULT 0,
    custo_materiais NUMERIC(12,2) NOT NULL DEFAULT 0,
    custo_mao_obra  NUMERIC(12,2) NOT NULL DEFAULT 0,
    preco_final     NUMERIC(12,2) NOT NULL DEFAULT 0,
    itens           JSONB       NOT NULL DEFAULT '[]'::jsonb,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_orcamentos_usuario ON orcamentos(usuario_id);

-- Loja compartilhada (marketplace de todos os usuários)
CREATE TABLE IF NOT EXISTS loja_anuncios (
    id           BIGSERIAL PRIMARY KEY,
    vendedor_id  BIGINT      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    material_id  BIGINT      REFERENCES materiais(id) ON DELETE SET NULL,
    titulo       TEXT        NOT NULL,
    descricao    TEXT,
    tipo         TEXT        NOT NULL DEFAULT 'fixo',           -- fixo | leilao
    preco        NUMERIC(12,2) NOT NULL DEFAULT 0,              -- fixo: preço; leilao: lance inicial
    status       TEXT        NOT NULL DEFAULT 'ativo',          -- ativo | vendido
    comprador_id BIGINT      REFERENCES usuarios(id) ON DELETE SET NULL,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_anuncios_status ON loja_anuncios(status);

CREATE TABLE IF NOT EXISTS loja_ofertas (
    id          BIGSERIAL PRIMARY KEY,
    anuncio_id  BIGINT      NOT NULL REFERENCES loja_anuncios(id) ON DELETE CASCADE,
    usuario_id  BIGINT      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    valor       NUMERIC(12,2) NOT NULL,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ofertas_anuncio ON loja_ofertas(anuncio_id);
