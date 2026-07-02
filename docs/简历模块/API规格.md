# 简历模块 — API 规格（English paths only）

Base: `/api/v1/resume`  
Auth: `Authorization: Bearer <jwt>`（除 templates 可匿名）

## Endpoints

### GET `/templates`

Response: `{ "items": [{ "id", "title", "description", "prompt_hint" }] }`

### POST `/files`

Multipart: `file`  
Response: `{ "file_id", "filename", "mime", "size_bytes" }`  
Errors: 413 file too large

### POST `/`

Create profile. Body: `{ "title?", "prompt?", "file_id?" }`  
Response: `{ "public_id", "title", ... }`  
Errors: 409 max 5 resumes

### POST `/{public_id}/generate`

First generation: parse + diagnose + generate resume.  
Body: `{ "prompt?", "file_id?" }`  
Response: `{ "public_id", "version_no", "structured", "messages", "sidecar" }`  
Quota: **1 on success** (402 if exceeded)

### POST `/{public_id}/optimize`

Body: `{ "prompt": "..." }`  
Response: same shape as generate  
Quota: **1 on success**

### GET `/{public_id}`

Detail + current version + sidecar summary.

### GET `/{public_id}/messages`

Chat history: `{ "items": [{ "id", "role", "content", "message_type", "created_at" }] }`

### PUT `/{public_id}`

Body: `{ "title?", "structured?" }` — save manual edits.

### GET `/{public_id}/export?format=pdf|docx`

File download.

### GET `/`

List current user's resumes: `{ "items": [{ "public_id", "title", "thumbnail_url", "updated_at" }] }`

### DELETE `/{public_id}`

Delete resume and files.

## Error codes

| Code | Meaning |
|------|---------|
| 402 | Quota exceeded |
| 409 | Max 5 resumes |
| 413 | File > 5MB |
| 422 | Content policy / invalid input |
| 404 | Not found or expired |
