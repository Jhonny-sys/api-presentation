# API Presentation

Backend del catálogo profesional. Consume Supabase como fuente de datos y expone endpoints REST para el frontend (`my-presentation`).

## Estructura

```
api-presentation/
├── app/
│   ├── core/           # Configuración y cliente Supabase
│   ├── schemas/        # Modelos Pydantic (DTOs)
│   ├── repositories/   # Acceso a datos (Supabase)
│   ├── services/       # Lógica de negocio
│   ├── routers/        # Endpoints FastAPI
│   └── main.py
├── docs/
│   └── DATA_MODEL.md   # Modelo de datos documentado
└── supabase/
    └── migrations/     # SQL para crear tablas
```

## Modelo de datos

Ver [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) para la estructura completa de las 4 tablas:

- `personal_info`
- `experience`
- `studies`
- `technologies`

## Configuración

1. Copia las variables de entorno:

```bash
cp .env.example .env
```

2. Completa las variables en `.env`:
   - `SUPABASE_SERVICE_KEY` → Supabase → Settings → **API Keys** → **Secret keys** → `sb_secret_...`
   - `JWT_SECRET` → secreto largo para firmar tokens (mín. 32 caracteres)
   - `API_CLIENT_SECRET` → secreto compartido con el frontend

   > No uses la contraseña de la BD ni la publishable key (`sb_publishable_...`).

3. Instala dependencias:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Ejecuta las migraciones SQL en Supabase → SQL Editor:

```
supabase/migrations/001_initial_schema.sql
supabase/migrations/002_refresh_tokens.sql
supabase/migrations/003_revoked_sessions.sql
```

## Ejecutar la API

```bash
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/v1/auth/token` | No | Obtener access + refresh token |
| POST | `/api/v1/auth/refresh` | No | Renovar tokens (rotación) |
| POST | `/api/v1/auth/revoke` | No | Invalidar sesión (logout) |
| GET | `/api/v1/profile` | JWT | Información personal |
| GET | `/api/v1/experience` | JWT | Experiencia laboral |
| GET | `/api/v1/studies` | JWT | Estudios |
| GET | `/api/v1/technologies` | JWT | Tecnologías |
| GET | `/api/v1/portfolio` | JWT | Todo agregado (para el front) |

## Seguridad

- Nunca expongas `SUPABASE_SERVICE_KEY` ni `JWT_SECRET` en el frontend.
- Access token: **10 minutos**. Refresh token: **7 días** con rotación.
- Ver [`docs/AUTH.md`](docs/AUTH.md) para el flujo completo.
- Rota credenciales si fueron compartidas públicamente.
- Las tablas tienen RLS con lectura pública; escritura solo vía `service_role` desde este backend.
