-- Sistema i18n con claves de lenguaje y traducciones automáticas
-- Ejecutar en Supabase → SQL Editor

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS i18n_entries (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key          TEXT NOT NULL UNIQUE,
  namespace    TEXT,
  source_lang  TEXT NOT NULL DEFAULT 'es',
  source_text  TEXT NOT NULL,
  description  TEXT,
  is_active    BOOLEAN NOT NULL DEFAULT true,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_i18n_key_format CHECK (key ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$')
);

CREATE INDEX IF NOT EXISTS idx_i18n_entries_namespace ON i18n_entries(namespace);
CREATE INDEX IF NOT EXISTS idx_i18n_entries_active ON i18n_entries(is_active);

DROP TRIGGER IF EXISTS trg_i18n_entries_updated ON i18n_entries;
CREATE TRIGGER trg_i18n_entries_updated
  BEFORE UPDATE ON i18n_entries
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS i18n_translations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entry_id        UUID NOT NULL REFERENCES i18n_entries(id) ON DELETE CASCADE,
  lang_code       TEXT NOT NULL,
  translated_text TEXT NOT NULL,
  is_auto         BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (entry_id, lang_code)
);

CREATE INDEX IF NOT EXISTS idx_i18n_translations_entry ON i18n_translations(entry_id);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_lang ON i18n_translations(lang_code);

DROP TRIGGER IF EXISTS trg_i18n_translations_updated ON i18n_translations;
CREATE TRIGGER trg_i18n_translations_updated
  BEFORE UPDATE ON i18n_translations
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE i18n_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE i18n_translations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "public_read_i18n_entries" ON i18n_entries;
CREATE POLICY "public_read_i18n_entries"
  ON i18n_entries FOR SELECT
  USING (is_active = true);

DROP POLICY IF EXISTS "public_read_i18n_translations" ON i18n_translations;
CREATE POLICY "public_read_i18n_translations"
  ON i18n_translations FOR SELECT
  USING (true);
