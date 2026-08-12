-- Datos de ejemplo (opcional)
-- Ejecutar DESPUÉS de 001_initial_schema.sql
-- Reemplaza los valores con tu información real

WITH new_profile AS (
  INSERT INTO personal_info (
    full_name,
    headline,
    bio,
    email,
    location,
    social_links,
    available_for_work
  ) VALUES (
    'Jhonny Alexander Fonseca',
    'Desarrollador Full Stack',
    'Desarrollador apasionado por crear soluciones web escalables.',
    'contacto@ejemplo.com',
    'Colombia',
    '{"github": "https://github.com/jhonny", "linkedin": "https://linkedin.com/in/jhonny"}'::jsonb,
    true
  )
  RETURNING id
)
INSERT INTO experience (profile_id, company, role, description, start_date, is_current, location, highlights, sort_order)
SELECT id, 'Empresa XYZ', 'Backend Developer', 'Desarrollo de APIs REST.', '2022-03-01', true, 'Remoto', ARRAY['FastAPI', 'Supabase'], 1
FROM new_profile;

WITH profile AS (SELECT id FROM personal_info WHERE is_active = true ORDER BY created_at DESC LIMIT 1)
INSERT INTO studies (profile_id, institution, degree, field_of_study, start_date, end_date, sort_order)
SELECT id, 'Universidad ABC', 'Ingeniería de Sistemas', 'Desarrollo de Software', '2018-01-01', '2023-06-01', 1
FROM profile;

WITH profile AS (SELECT id FROM personal_info WHERE is_active = true ORDER BY created_at DESC LIMIT 1)
INSERT INTO technologies (profile_id, name, category, proficiency, is_featured, sort_order)
SELECT id, t.name, t.category, t.proficiency, t.is_featured, t.sort_order
FROM profile,
(VALUES
  ('Python', 'backend', 4, true, 1),
  ('FastAPI', 'backend', 4, true, 2),
  ('React', 'frontend', 4, true, 3),
  ('Next.js', 'frontend', 4, true, 4),
  ('Supabase', 'database', 3, false, 5)
) AS t(name, category, proficiency, is_featured, sort_order);
