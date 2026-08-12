# Storage

Bucket: `portfolio-assets` (público).

## Migración

`supabase/migrations/005_storage_bucket.sql`

## Endpoint

```http
POST /api/v1/uploads
Authorization: Bearer <token>
Content-Type: multipart/form-data

file_1: <archivo>
file_2: <archivo>   (opcional)
file_3: <archivo>   (opcional)
```

## Respuesta

```json
{
  "count": 2,
  "files": [
    {
      "filename": "foto.jpg",
      "path": "2026/08/12/abc123.jpg",
      "url": "https://<project>.supabase.co/storage/v1/object/public/portfolio-assets/2026/08/12/abc123.jpg",
      "content_type": "image/jpeg",
      "size": 102400
    }
  ]
}
```

## Límites

- Máx. 3 archivos por request
- Máx. 5 MB por archivo
- Tipos: jpeg, png, webp, gif, pdf
