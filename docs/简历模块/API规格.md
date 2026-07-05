# 简历模块 — API 规格（English paths only）

Base: `/api/v1/resume`  
Auth: `Authorization: Bearer <jwt>`（除 templates 可匿名）

## Endpoints

### GET `/templates`

Response: `{ "items": [{ "id", "title", "description", "prompt_hint" }] }`

### GET `/visual-templates`

Visual layout templates for resume-edit tab.  
Response: `{ "items": [{ "id", "title", "description" }] }`

### POST `/files`

Multipart: `file`  
Response: `{ "file_id", "filename", "mime", "size_bytes" }`  
Errors: 413 file too large

### POST `/`

Create profile. Body: `{ "title?", "prompt?", "file_id?", "jd_file_id?", "template_id?" }`  

| 场景 | 行为 |
|------|------|
| 仅 `template_id`（RS3 编辑 Tab） | 创建空白版本 + compile visual；**不扣配额** |
| `prompt` / `file_id` / `jd_file_id` | 与 V1 相同；前端随后调 `generate`；可组合简历文件 + JD 文件 + 提示词 |

Response: `{ "public_id", "title", ... }`  
Errors: 409 max 5 resumes

### POST `/{public_id}/generate`

First generation: parse + diagnose + generate resume.  
Body: `{ "prompt?", "file_id?", "jd_file_id?" }`  
Response: `{ "public_id", "version_no", "structured", "messages", "sidecar" }`  
Quota: **1 on success** (402 if exceeded)

### POST `/{public_id}/optimize`

Body: `{ "prompt": "..." }`  
Response: same shape as generate  
Quota: **1 on success**

### GET `/{public_id}`

Detail + current version + sidecar summary.  
Response includes `structured` and `visual_document` (`template_id`, `photo_file_id`, `styles`, `pages[]` with `{ id, structured, styles }` per A4 page).

### GET `/{public_id}/messages`

Chat history: `{ "items": [{ "id", "role", "content", "message_type", "created_at" }] }`

### PUT `/{public_id}`

Body: `{ "title?", "structured?", "visual_document?" }` — save manual edits (no quota).

### GET `/{public_id}/export?format=pdf|docx`

Template-aware file download (classic-blue layout).

### GET `/`

List current user's resumes: `{ "items": [{ "public_id", "title", "thumbnail_url", "updated_at" }] }`

### GET `/{public_id}/thumbnail`

Returns PNG preview image (`image/png`). Requires auth; 404 if profile missing, expired, or thumbnail not generated yet.  
`thumbnail_url` in list items points to this path when `thumbnail_path` exists on the profile.

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
