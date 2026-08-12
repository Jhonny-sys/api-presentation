-- Refresh tokens con rotación y detección de reutilización
-- Ejecutar en Supabase → SQL Editor

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  family_id    UUID NOT NULL,
  token_hash   TEXT NOT NULL UNIQUE,
  subject      TEXT NOT NULL DEFAULT 'portfolio-client',
  expires_at   TIMESTAMPTZ NOT NULL,
  revoked_at   TIMESTAMPTZ,
  replaced_by  UUID REFERENCES refresh_tokens(id),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_family ON refresh_tokens(family_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);

-- Solo el backend (service key) accede a esta tabla
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;
