-- Idiomas que habla el titular (solo contexto del agente de chat, no UI pública)
ALTER TABLE personal_info
  ADD COLUMN IF NOT EXISTS languages TEXT;
