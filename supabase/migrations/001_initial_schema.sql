-- Catálogo profesional — esquema inicial
-- Proyecto: Jhonny-sys's Project
-- Ejecutar en Supabase → SQL Editor

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. INFORMACIÓN PERSONAL
CREATE TABLE IF NOT EXISTS personal_info (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name          TEXT NOT NULL,
  headline           TEXT NOT NULL,
  bio                TEXT,
  email              TEXT,
  phone              TEXT,
  location           TEXT,
  avatar_url         TEXT,
  resume_url         TEXT,
  social_links       JSONB NOT NULL DEFAULT '{}'::jsonb,
  available_for_work BOOLEAN NOT NULL DEFAULT true,
  is_active          BOOLEAN NOT NULL DEFAULT true,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DROP TRIGGER IF EXISTS trg_personal_info_updated ON personal_info;
CREATE TRIGGER trg_personal_info_updated
  BEFORE UPDATE ON personal_info
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 2. EXPERIENCIA
CREATE TABLE IF NOT EXISTS experience (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id       UUID NOT NULL REFERENCES personal_info(id) ON DELETE CASCADE,
  company          TEXT NOT NULL,
  role             TEXT NOT NULL,
  description      TEXT,
  start_date       DATE NOT NULL,
  end_date         DATE,
  is_current       BOOLEAN NOT NULL DEFAULT false,
  location         TEXT,
  company_logo_url TEXT,
  highlights       TEXT[] NOT NULL DEFAULT '{}',
  sort_order       INT NOT NULL DEFAULT 0,
  is_active        BOOLEAN NOT NULL DEFAULT true,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_experience_dates CHECK (
    (is_current = true AND end_date IS NULL)
    OR (is_current = false)
  )
);

CREATE INDEX IF NOT EXISTS idx_experience_profile ON experience(profile_id);

DROP TRIGGER IF EXISTS trg_experience_updated ON experience;
CREATE TRIGGER trg_experience_updated
  BEFORE UPDATE ON experience
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 3. ESTUDIOS
CREATE TABLE IF NOT EXISTS studies (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id       UUID NOT NULL REFERENCES personal_info(id) ON DELETE CASCADE,
  institution      TEXT NOT NULL,
  degree           TEXT NOT NULL,
  field_of_study   TEXT,
  description      TEXT,
  start_date       DATE,
  end_date         DATE,
  is_current       BOOLEAN NOT NULL DEFAULT false,
  certificate_url  TEXT,
  sort_order       INT NOT NULL DEFAULT 0,
  is_active        BOOLEAN NOT NULL DEFAULT true,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_studies_profile ON studies(profile_id);

DROP TRIGGER IF EXISTS trg_studies_updated ON studies;
CREATE TRIGGER trg_studies_updated
  BEFORE UPDATE ON studies
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 4. TECNOLOGÍAS
CREATE TABLE IF NOT EXISTS technologies (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id       UUID NOT NULL REFERENCES personal_info(id) ON DELETE CASCADE,
  name             TEXT NOT NULL,
  category         TEXT NOT NULL CHECK (category IN (
    'frontend', 'backend', 'database', 'devops', 'mobile', 'tools', 'other'
  )),
  proficiency      INT CHECK (proficiency BETWEEN 1 AND 5),
  icon_url         TEXT,
  years_experience NUMERIC(3,1),
  is_featured      BOOLEAN NOT NULL DEFAULT false,
  sort_order       INT NOT NULL DEFAULT 0,
  is_active        BOOLEAN NOT NULL DEFAULT true,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (profile_id, name)
);

CREATE INDEX IF NOT EXISTS idx_technologies_profile ON technologies(profile_id);
CREATE INDEX IF NOT EXISTS idx_technologies_category ON technologies(category);

DROP TRIGGER IF EXISTS trg_technologies_updated ON technologies;
CREATE TRIGGER trg_technologies_updated
  BEFORE UPDATE ON technologies
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- RLS: lectura pública, escritura solo vía service_role (backend)
ALTER TABLE personal_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE experience ENABLE ROW LEVEL SECURITY;
ALTER TABLE studies ENABLE ROW LEVEL SECURITY;
ALTER TABLE technologies ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "public_read_personal_info" ON personal_info;
CREATE POLICY "public_read_personal_info"
  ON personal_info FOR SELECT
  USING (is_active = true);

DROP POLICY IF EXISTS "public_read_experience" ON experience;
CREATE POLICY "public_read_experience"
  ON experience FOR SELECT
  USING (is_active = true);

DROP POLICY IF EXISTS "public_read_studies" ON studies;
CREATE POLICY "public_read_studies"
  ON studies FOR SELECT
  USING (is_active = true);

DROP POLICY IF EXISTS "public_read_technologies" ON technologies;
CREATE POLICY "public_read_technologies"
  ON technologies FOR SELECT
  USING (is_active = true);
