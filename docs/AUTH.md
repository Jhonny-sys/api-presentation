# Auth

Variables: ver `.env.example`.

## Migraciones

- `002_refresh_tokens.sql`
- `003_revoked_sessions.sql`

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | Login admin (usuario + contraseña) |
| GET | `/api/v1/auth/me` | JWT | Verificar sesión activa |
| POST | `/api/v1/auth/token` | No | Token de servicio (client_secret) |
| POST | `/api/v1/auth/refresh` | No | Renovar tokens |
| POST | `/api/v1/auth/revoke` | No | Cerrar sesión |

Rutas protegidas: header `Authorization: Bearer <access_token>`.

Toda la API bajo `/api/v1` exige JWT, excepto:

- `POST /auth/login`
- `POST /auth/token` (solo servidor Next.js con `API_CLIENT_SECRET`)
- `POST /auth/refresh`
- `POST /auth/revoke`

`/health` queda público para monitoreo.
