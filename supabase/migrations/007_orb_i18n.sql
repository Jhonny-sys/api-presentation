-- Traducciones para títulos de orbes (es → en, pt vía API i18n)
INSERT INTO i18n_entries (key, namespace, source_lang, source_text, description)
VALUES
  ('orb.profile', 'orb', 'es', 'Perfil', 'Título orbe perfil'),
  ('orb.experience', 'orb', 'es', 'Experiencia', 'Título orbe experiencia'),
  ('orb.studies', 'orb', 'es', 'Estudios', 'Título orbe estudios'),
  ('orb.technologies', 'orb', 'es', 'Stack', 'Título orbe tecnologías')
ON CONFLICT (key) DO NOTHING;

INSERT INTO i18n_translations (entry_id, lang_code, translated_text, is_auto)
SELECT e.id, 'en', v.text, false
FROM i18n_entries e
JOIN (VALUES
  ('orb.profile', 'Profile'),
  ('orb.experience', 'Experience'),
  ('orb.studies', 'Studies'),
  ('orb.technologies', 'Stack')
) AS v(key, text) ON e.key = v.key
ON CONFLICT (entry_id, lang_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;

INSERT INTO i18n_translations (entry_id, lang_code, translated_text, is_auto)
SELECT e.id, 'pt', v.text, false
FROM i18n_entries e
JOIN (VALUES
  ('orb.profile', 'Perfil'),
  ('orb.experience', 'Experiência'),
  ('orb.studies', 'Estudos'),
  ('orb.technologies', 'Stack')
) AS v(key, text) ON e.key = v.key
ON CONFLICT (entry_id, lang_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
