-- Sesiones revocadas: invalida access tokens activos al hacer revoke
-- Ejecutar en Supabase → SQL Editor

CREATE TABLE IF NOT EXISTS revoked_sessions (
  family_id   UUID PRIMARY KEY,
  revoked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_revoked_sessions_revoked_at ON revoked_sessions(revoked_at);

ALTER TABLE revoked_sessions ENABLE ROW LEVEL SECURITY;
