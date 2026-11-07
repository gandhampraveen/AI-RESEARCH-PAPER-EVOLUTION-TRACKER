# API reference

Interactive OpenAPI docs: `http://localhost:8002/docs` when run with the project README command.

Main endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`; `GET/POST /api/papers`, `GET/PUT/DELETE /api/papers/{id}`, `GET /api/papers/{id}/recommendations`; `GET /api/topics`, `/api/topics/emerging`, `/api/topics/declining`, `/api/topics/{id}`; `GET /api/trends`, `/api/trends/yearly`, `/api/dashboard`; `GET /api/search?q=...`; `POST /api/chat`; `GET /api/jobs/analytics`, `/api/career-insights`, `/api/predictions`; `POST /api/nlp/keywords?text=...`; protected `POST /api/admin/import/{papers|jobs}` and `GET /api/admin/stats`.

Paper writes require a signed-in user. Admin import requires role `ADMIN`; registration creates `USER` accounts. Provision an administrator by changing a trusted account's role directly in the database. Never expose the signing key.
