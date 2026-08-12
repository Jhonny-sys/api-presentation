# Autenticación JWT + Refresh Token

## Resumen de seguridad

| Token | Duración | Formato | Almacenamiento |
|-------|----------|---------|----------------|
| **Access token** | 10 minutos | JWT firmado (HS256) | Memoria del cliente |
| **Refresh token** | 7 días | Opaco (`secrets.token_urlsafe(64)`) | Solo hash SHA-256 + pepper en Supabase |

### Medidas de seguridad implementadas

1. **Access token corto (10 min)** — ventana mínima si se filtra.
2. **Refresh token opaco** — no es JWT; no se puede decodificar.
3. **Hash en BD** — nunca se guarda el refresh token en texto plano.
4. **Pepper (`REFRESH_TOKEN_PEPPER`)** — secreto adicional al hashear.
5. **Rotación** — cada refresh invalida el token anterior y emite uno nuevo.
6. **Detección de reutilización** — si usan un refresh token ya revocado, se invalida toda la familia de tokens (posible robo).
7. **Revocación inmediata** — al hacer `/auth/revoke`, el access token deja de funcionar al instante (tabla `revoked_sessions` + claim `fid` en el JWT).
8. **Limpieza automática** — registros vencidos se purgan al arrancar la API y en operaciones de auth (máx. cada 1 hora).

---

## Limpieza automática de tokens

| Tabla | Qué se elimina | Cuándo |
|-------|----------------|--------|
| `refresh_tokens` | Filas con `expires_at` en el pasado | Al iniciar la API + en `/auth/*` (cada 1 h) |
| `revoked_sessions` | Sesiones revocadas hace más de 15 min | Idem (ya no hay access tokens válidos de esa sesión) |

Los refresh tokens **revocados pero no expirados** se conservan hasta su `expires_at` para detectar reutilización (posible robo).

No necesitas cron manual: la API lo hace sola. En `/auth/revoke` la limpieza corre siempre de inmediato.

---

## Variables de entorno

### Backend (`.env`)

```env
JWT_SECRET=...                    # Firma access tokens (solo backend)
JWT_EXPIRE_MINUTES=10             # Access token: 10 minutos
JWT_REFRESH_EXPIRE_DAYS=7         # Refresh token: 7 días
REFRESH_TOKEN_PEPPER=...          # Pepper para hash de refresh tokens (solo backend)
API_CLIENT_SECRET=...             # Compartido con frontend (server-side)
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
API_CLIENT_SECRET=portfolio_front_secret_2026
```

> El frontend **nunca** recibe `JWT_SECRET` ni `REFRESH_TOKEN_PEPPER`.

---

## Migración requerida

Ejecuta en Supabase → SQL Editor:

```
supabase/migrations/002_refresh_tokens.sql
supabase/migrations/003_revoked_sessions.sql
```

---

## Flujo completo

```
1. POST /auth/token     → access_token (10m) + refresh_token (7d)
2. GET  /portfolio      → Authorization: Bearer <access_token>
3. POST /auth/refresh   → cuando access expira, envía refresh_token
                          → nuevo par (rotación)
4. POST /auth/revoke    → logout, invalida toda la familia
```

---

## Endpoints

### Obtener tokens iniciales

```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "client_secret": "portfolio_front_secret_2026"
}
```

**Respuesta:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "xK9f...",
  "token_type": "bearer",
  "expires_in": 600,
  "refresh_expires_in": 604800
}
```

### Refrescar (rotación automática)

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "xK9f..."
}
```

**Respuesta:** nuevo par completo. El refresh token anterior queda invalidado.

### Revocar sesión (logout)

```http
POST /api/v1/auth/revoke
Content-Type: application/json

{
  "refresh_token": "xK9f..."
}
```

Respuesta: `204 No Content`

### Usar API protegida

```http
GET /api/v1/portfolio
Authorization: Bearer <access_token>
```

---

## Frontend (Next.js) — patrón recomendado

Guarda el `refresh_token` solo en el servidor (cookie `httpOnly` o variable en memoria del Route Handler).

```typescript
let cachedAccessToken: { token: string; expiresAt: number } | null = null;
let refreshToken: string | null = null;

async function authenticate() {
  const res = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_secret: process.env.API_CLIENT_SECRET }),
  });
  const data = await res.json();
  cachedAccessToken = {
    token: data.access_token,
    expiresAt: Date.now() + data.expires_in * 1000 - 30_000, // 30s margen
  };
  refreshToken = data.refresh_token;
}

async function getValidAccessToken(): Promise<string> {
  if (!cachedAccessToken || Date.now() >= cachedAccessToken.expiresAt) {
    if (refreshToken) {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (res.ok) {
        const data = await res.json();
        cachedAccessToken = {
          token: data.access_token,
          expiresAt: Date.now() + data.expires_in * 1000 - 30_000,
        };
        refreshToken = data.refresh_token;
        return cachedAccessToken.token;
      }
    }
    await authenticate();
  }
  return cachedAccessToken!.token;
}
```

---

## Supabase API key

Ver sección anterior: usa `sb_secret_...` en `SUPABASE_SERVICE_KEY`.

---

## Changelog auth

| Versión | Cambio |
|---------|--------|
| 2.0 | Access 10 min + refresh opaco con rotación y detección de reutilización |
| 1.0 | JWT simple sin refresh |
