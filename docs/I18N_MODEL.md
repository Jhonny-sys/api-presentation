# I18N_MODEL — Traducciones con claves

> Versión: 1.0  
> Motor: servicio externo configurado en `.env`

---

## Concepto

Todo texto del catálogo se guarda con una **clave única** (`key`) y un **texto fuente** (`source_text`, idioma `es` por defecto).  
Al crear o actualizar, el backend traduce automáticamente a todos los idiomas configurados.

**No hay DELETE** — solo Create, Read, Update.

---

## Tablas

### `i18n_entries` — Claves de contenido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | uuid | PK |
| key | text | Clave única, formato `namespace.slug` (ej: `profile.headline`) |
| namespace | text | Agrupación opcional (`profile`, `experience`, `studies`) |
| source_lang | text | Idioma fuente (default `es`) |
| source_text | text | Texto original |
| description | text | Nota interna para el admin |
| is_active | boolean | Soft visibility |

**Formato de key:** `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`

Ejemplos válidos:
- `profile.headline`
- `profile.bio`
- `experience.company_1.role`
- `studies.degree_title`

### `i18n_translations` — Traducciones por idioma

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | uuid | PK |
| entry_id | uuid | FK → `i18n_entries.id` |
| lang_code | text | Código ISO (`en`, `pt`, `fr`...) |
| translated_text | text | Texto traducido |
| is_auto | boolean | `true` = generado por API; `false` = editado manualmente |

---

## Idiomas soportados (default)

Configurables en `.env` → `I18N_TARGET_LANGUAGES`:

```
en, pt
```

Fuente: `I18N_SOURCE_LANG=es`

**Total por defecto: 3 idiomas** (`es` + `en` + `pt`).

---

## Endpoints (requieren JWT)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/i18n` | Crear clave + traducir automáticamente |
| GET | `/api/v1/i18n` | Listar entradas (`?namespace=profile`) |
| GET | `/api/v1/i18n/bundle/{lang}` | Diccionario `{ key: texto }` para el front |
| GET | `/api/v1/i18n/{key}` | Detalle con todas las traducciones |
| PUT | `/api/v1/i18n/{key}` | Actualizar `source_text` y re-traducir |
| PATCH | `/api/v1/i18n/{key}/translations/{lang}` | Override manual de un idioma |

---

## Ejemplo: crear entrada

```http
POST /api/v1/i18n
Authorization: Bearer <token>
Content-Type: application/json

{
  "key": "profile.headline",
  "source_text": "Desarrollador Full Stack",
  "namespace": "profile",
  "description": "Título principal del hero"
}
```

**Respuesta:**

```json
{
  "key": "profile.headline",
  "namespace": "profile",
  "source_lang": "es",
  "source_text": "Desarrollador Full Stack",
  "translations": {
    "es": "Desarrollador Full Stack",
    "en": "Full Stack Developer",
    "pt": "Desenvolvedor Full Stack",
    "fr": "Développeur Full Stack"
  }
}
```

---

## Ejemplo: bundle para el frontend

```http
GET /api/v1/i18n/bundle/en
Authorization: Bearer <token>
```

```json
{
  "lang": "en",
  "messages": {
    "profile.headline": "Full Stack Developer",
    "profile.bio": "Passionate developer..."
  }
}
```

---

## Flujo automático de traducción

```
POST/PUT con source_text (es)
        ↓
MyMemory API (gratis)
https://api.mymemory.translated.net/get
        ↓
Guarda en i18n_translations (is_auto=true)
        ↓
Front consume GET /i18n/bundle/{lang}
```

---

## Changelog

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-08-11 | Modelo i18n + CRU sin delete |
