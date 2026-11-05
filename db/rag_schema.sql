-- FITIF Medical RAG schema v1 (PostgreSQL 16 + pgvector)
-- Target database: team_project
-- Does not DROP or ALTER public.* tables; safe to re-run for initial creation.
-- Run with a role allowed to CREATE EXTENSION / CREATE SCHEMA / CREATE TABLE.
-- Existing tables are not migrated by IF NOT EXISTS; coordinate changes with DB owner.

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS rag;

CREATE TABLE IF NOT EXISTS rag.document (
    document_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key        TEXT NOT NULL UNIQUE,
    document_title    TEXT NOT NULL,
    publisher         TEXT,
    publication_year  SMALLINT,
    source_file       TEXT NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rag.chunk (
    chunk_id          TEXT PRIMARY KEY,
    document_id       BIGINT NOT NULL REFERENCES rag.document(document_id) ON DELETE RESTRICT,
    original_chunk_id TEXT,
    region_id         TEXT,
    chunk_text        TEXT NOT NULL CHECK (length(btrim(chunk_text)) > 0),
    pdf_page          INT NOT NULL CHECK (pdf_page > 0),
    spread_side       TEXT,
    review_flags      JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(review_flags) = 'array'),
    requires_review   BOOLEAN NOT NULL DEFAULT FALSE,
    table_ids         JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(table_ids) = 'array'),
    embedding         VECTOR(384) NOT NULL,
    embedding_model   TEXT NOT NULL DEFAULT 'intfloat/multilingual-e5-small',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_rag_chunk_document_id ON rag.chunk(document_id);
CREATE INDEX IF NOT EXISTS ix_rag_chunk_pdf_page ON rag.chunk(document_id, pdf_page);

-- For the first 994 rows, exact cosine search is sufficient without ANN index.
-- Optional later (after measuring recall/speed and checking pgvector version):
-- CREATE INDEX ix_rag_chunk_embedding_hnsw
--     ON rag.chunk USING hnsw (embedding vector_cosine_ops);

COMMIT;

-- Read-only verification (execute separately):
-- SELECT extversion FROM pg_extension WHERE extname = 'vector';
-- SELECT table_schema, table_name FROM information_schema.tables
--  WHERE table_schema = 'rag' ORDER BY table_name;
-- SELECT COUNT(*) FROM rag.chunk;
