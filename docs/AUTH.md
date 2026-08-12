# Autenticación JWT

## Diagnóstico del error 401 de Supabase

Si ves este error:

```
Invalid API key — Double check your Supabase `anon` or `service_role` API key
```

**Causas comunes:**

1. Pusiste la **contraseña de la BD** (`sup3radmin2021-`) — no sirve.
2. Pusiste la **publishable key** (`sb_publishable_...`) — es para el frontend, no el backend.
3. Dejaste el placeholder `REEMPLAZA_CON_TU_SERVICE_ROLE_KEY` sin cambiar.

**Solución (Supabase nuevo formato):**

1. Ve a Supabase → **Settings** → **API Keys**
2. En **Secret keys**, copia la key **`default`** (empieza con `sb_secret_...`)
3. Pégala en `.env`:

```env
SUPABASE_SERVICE_KEY=sb_secret_x8ak2...
```

> Supabase cambió las keys. Ya no se llama `service_role` en la UI; ahora es **Secret key**.  
> El formato legacy `eyJ...` (JWT) también funciona en proyectos antiguos.

---

## Claves compartidas entre backend y frontend

| Variable | Backend `.env` | Frontend `.env.local` | Descripción |
|----------|----------------|----------------------|-------------|
| `API_CLIENT_SECRET` | ✅ | ✅ (solo server-side) | Secreto para obtener el JWT |
| `JWT_SECRET` | ✅ | ❌ | Solo backend — firma los tokens |
| `NEXT_PUBLIC_API_URL` | — | ✅ | URL base de la API |

**Algoritmo JWT:** `HS256` (HMAC-SHA256)

> No es un hash de contraseña. Es firma simétrica: backend firma con `JWT_SECRET`, backend valida con el mismo secreto.

---

## Flujo de autenticación

```
Frontend                          Backend
   │                                 │
   │  POST /api/v1/auth/token        │
   │  { "client_secret": "..." }     │
   │ ─────────────────────────────►  │
   │                                 │ valida API_CLIENT_SECRET
   │  { access_token, expires_in }   │ genera JWT con JWT_SECRET
   │ ◄─────────────────────────────  │
   │                                 │
   │  GET /api/v1/portfolio          │
   │  Authorization: Bearer <JWT>    │
   │ ─────────────────────────────►  │
   │                                 │ valida JWT
   │  { profile, experience, ... }   │
   │ ◄─────────────────────────────  │
```

---

## Probar en Insomnia / Swagger

### 1. Obtener token

```http
POST http://localhost:8000/api/v1/auth/token
Content-Type: application/json

{
  "client_secret": "portfolio_front_secret_2026"
}
```

Respuesta:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Usar el token

```http
GET http://localhost:8000/api/v1/portfolio
Authorization: Bearer eyJ...
```

---

## Frontend (Next.js) — ejemplo

`.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
API_CLIENT_SECRET=portfolio_front_secret_2026
```

> `API_CLIENT_SECRET` sin prefijo `NEXT_PUBLIC_` para que no se exponga al navegador.  
> Obtén el token en Server Components o Route Handlers.

```typescript
// lib/api/auth.ts (server-side)
const API_URL = process.env.NEXT_PUBLIC_API_URL!;
const CLIENT_SECRET = process.env.API_CLIENT_SECRET!;

export async function getAccessToken(): Promise<string> {
  const res = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_secret: CLIENT_SECRET }),
    cache: "no-store",
  });

  if (!res.ok) throw new Error("No se pudo obtener el token");
  const data = await res.json();
  return data.access_token;
}

export async function fetchPortfolio() {
  const token = await getAccessToken();
  const res = await fetch(`${API_URL}/portfolio`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { revalidate: 60 },
  });
  return res.json();
}
```

---

## Endpoints públicos vs protegidos

| Ruta | Auth |
|------|------|
| `GET /health` | Pública |
| `POST /api/v1/auth/token` | Pública (requiere `client_secret`) |
| `GET /api/v1/*` | Requiere JWT Bearer |
