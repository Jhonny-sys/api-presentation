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

2. Completa `SUPABASE_SERVICE_KEY` desde Supabase → Project Settings → API → `service_role` key.

3. Instala dependencias:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Ejecuta la migración SQL en Supabase → SQL Editor:

```
supabase/migrations/001_initial_schema.sql
```

## Ejecutar la API

```bash
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/profile` | Información personal |
| GET | `/api/v1/experience` | Experiencia laboral |
| GET | `/api/v1/studies` | Estudios |
| GET | `/api/v1/technologies` | Tecnologías |
| GET | `/api/v1/portfolio` | Todo agregado (para el front) |

## Seguridad

- Nunca expongas `SUPABASE_SERVICE_KEY` en el frontend.
- Rota credenciales si fueron compartidas públicamente.
- Las tablas tienen RLS con lectura pública; escritura solo vía `service_role` desde este backend.
