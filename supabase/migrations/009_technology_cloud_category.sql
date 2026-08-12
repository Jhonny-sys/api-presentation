-- Agrega categoría cloud y migra devops → cloud
ALTER TABLE technologies DROP CONSTRAINT IF EXISTS technologies_category_check;

UPDATE technologies SET category = 'cloud' WHERE category = 'devops';

ALTER TABLE technologies
  ADD CONSTRAINT technologies_category_check CHECK (category IN (
    'frontend', 'backend', 'database', 'cloud', 'mobile', 'tools', 'other'
  ));
