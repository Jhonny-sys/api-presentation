# DATA_MODEL — Catálogo profesional Jhonny

> Versión: 1.0  
> Base de datos: Supabase (PostgreSQL)  
> Proyecto: Jhonny-sys's Project  
> API REST Supabase: `https://nptjrxtiaaadgcpguwrl.supabase.co/rest/v1/`

---

## Convenciones globales

| Regla | Valor |
|-------|-------|
| PK | `uuid` generado con `gen_random_uuid()` |
| Timestamps | `created_at`, `updated_at` (auto) |
| Soft delete | `is_active boolean DEFAULT true` |
| Orden visual | `sort_order int DEFAULT 0` (menor = primero) |
| FK perfil | `experience`, `studies` y `technologies` referencian `personal_info.id` |

---

## 1. `personal_info` — Información personal

**Propósito:** Perfil principal del catálogo. Normalmente 1 fila activa.

| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| id | uuid | ✅ | PK |
| full_name | text | ✅ | Nombre completo |
| headline | text | ✅ | Título profesional corto |
| bio | text | ⬜ | Resumen / about me |
| email | text | ⬜ | Email público |
| phone | text | ⬜ | Teléfono |
| location | text | ⬜ | Ciudad, País |
| avatar_url | text | ⬜ | URL foto de perfil |
| resume_url | text | ⬜ | URL CV en PDF |
| social_links | jsonb | ⬜ | `{ "github": "...", "linkedin": "...", "website": "..." }` |
| available_for_work | boolean | ✅ | default `true` |
| is_active | boolean | ✅ | default `true` |
| created_at | timestamptz | ✅ | auto |
| updated_at | timestamptz | ✅ | auto |

**Ejemplo JSON:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Jhonny Alexander Fonseca",
  "headline": "Desarrollador Full Stack",
  "bio": "Desarrollador con experiencia en backend y frontend.",
  "email": "contacto@ejemplo.com",
  "phone": "+57 3000000000",
  "location": "Colombia",
  "avatar_url": "https://example.com/avatar.jpg",
  "resume_url": "https://example.com/cv.pdf",
  "social_links": {
    "github": "https://github.com/jhonny",
    "linkedin": "https://linkedin.com/in/jhonny",
    "website": "https://jhonny.dev"
  },
  "available_for_work": true
}
```

---

## 2. `experience` — Experiencia laboral

**Propósito:** Historial profesional ordenado cronológicamente.

| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| id | uuid | ✅ | PK |
| profile_id | uuid | ✅ | FK → `personal_info.id` |
| company | text | ✅ | Nombre empresa |
| role | text | ✅ | Cargo |
| description | text | ⬜ | Responsabilidades y logros |
| start_date | date | ✅ | Inicio |
| end_date | date | ⬜ | Fin (`null` si actual) |
| is_current | boolean | ✅ | default `false` |
| location | text | ⬜ | Modalidad / ciudad |
| company_logo_url | text | ⬜ | Logo empresa |
| highlights | text[] | ⬜ | Bullets de logros |
| sort_order | int | ✅ | Orden en UI |
| is_active | boolean | ✅ | default `true` |
| created_at | timestamptz | ✅ | auto |
| updated_at | timestamptz | ✅ | auto |

**Reglas de negocio:**

- Si `is_current = true` → `end_date` debe ser `null`
- Ordenar por: `is_current DESC`, `start_date DESC`, `sort_order ASC`

**Ejemplo JSON:**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "company": "Empresa XYZ",
  "role": "Backend Developer",
  "description": "Desarrollo de APIs REST con FastAPI.",
  "start_date": "2022-03-01",
  "end_date": null,
  "is_current": true,
  "location": "Remoto",
  "highlights": [
    "Diseñé arquitectura con FastAPI",
    "Integré Supabase como base de datos"
  ],
  "sort_order": 1
}
```

---

## 3. `studies` — Estudios / formación

**Propósito:** Educación formal, cursos relevantes y certificaciones.

| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| id | uuid | ✅ | PK |
| profile_id | uuid | ✅ | FK → `personal_info.id` |
| institution | text | ✅ | Universidad / plataforma |
| degree | text | ✅ | Título o certificación |
| field_of_study | text | ⬜ | Área académica |
| description | text | ⬜ | Detalle adicional |
| start_date | date | ⬜ | Inicio |
| end_date | date | ⬜ | Graduación |
| is_current | boolean | ✅ | default `false` |
| certificate_url | text | ⬜ | Link al diploma/certificado |
| sort_order | int | ✅ | Orden en UI |
| is_active | boolean | ✅ | default `true` |
| created_at | timestamptz | ✅ | auto |
| updated_at | timestamptz | ✅ | auto |

**Ejemplo JSON:**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "institution": "Universidad ABC",
  "degree": "Ingeniería de Sistemas",
  "field_of_study": "Desarrollo de Software",
  "start_date": "2018-01-01",
  "end_date": "2023-06-01",
  "is_current": false,
  "certificate_url": null,
  "sort_order": 1
}
```

---

## 4. `technologies` — Tecnologías

**Propósito:** Stack técnico con categorías y nivel de dominio.

| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| id | uuid | ✅ | PK |
| profile_id | uuid | ✅ | FK → `personal_info.id` |
| name | text | ✅ | Ej: "Python", "React" |
| category | text | ✅ | `frontend` \| `backend` \| `database` \| `devops` \| `mobile` \| `tools` \| `other` |
| proficiency | int | ⬜ | 1–5 (1 básico, 5 experto) |
| icon_url | text | ⬜ | Logo/icono |
| years_experience | numeric(3,1) | ⬜ | Años de uso |
| is_featured | boolean | ✅ | Destacar en hero/home |
| sort_order | int | ✅ | Orden dentro de categoría |
| is_active | boolean | ✅ | default `true` |
| created_at | timestamptz | ✅ | auto |
| updated_at | timestamptz | ✅ | auto |

**Ejemplo JSON:**

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "FastAPI",
  "category": "backend",
  "proficiency": 4,
  "years_experience": 2.5,
  "is_featured": true,
  "sort_order": 1
}
```

---

## Endpoints API (FastAPI)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/profile` | Información personal activa |
| GET | `/api/v1/experience` | Lista de experiencias |
| GET | `/api/v1/studies` | Lista de estudios |
| GET | `/api/v1/technologies` | Lista de tecnologías |
| GET | `/api/v1/portfolio` | Respuesta agregada para el frontend |

---

## Respuesta agregada `/api/v1/portfolio`

```json
{
  "profile": { "...": "..." },
  "experience": [ { "...": "..." } ],
  "studies": [ { "...": "..." } ],
  "technologies": [ { "...": "..." } ]
}
```

---

## Changelog

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-08-11 | Modelo inicial — 4 tablas |
