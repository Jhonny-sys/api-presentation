# API Presentation

Backend del catálogo profesional.

## Setup

```bash
cp .env.example .env
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Ejecuta las migraciones en `supabase/migrations/` (en orden).

## Docs

- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) — portfolio
- [`docs/I18N_MODEL.md`](docs/I18N_MODEL.md) — traducciones
- [`docs/STORAGE.md`](docs/STORAGE.md) — archivos

## Endpoints

Ver `/docs` en local.
