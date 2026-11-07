# Architecture

LitScope uses a React/Vite single-page interface with a FastAPI REST API and SQLAlchemy persistence. SQLite is the default development database so the project runs without a MySQL service; set `DATABASE_URL` to a PyMySQL MySQL URL for deployment. The React client sends requests to `/api` and stores the JWT in browser local storage.

```text
React + Recharts → Axios → FastAPI routes → SQLAlchemy → SQLite or MySQL
                                          ↘ NLP / TF-IDF services
```

The backend package separates settings, database sessions, ORM models, Pydantic schemas, security, NLP utilities and analytics services. `database/schema.sql` documents the normalized MySQL schema. The ORM currently keeps a few demonstration convenience fields (for example comma-separated job skills) alongside normalized relationship tables; production ingestion should use the normalized links consistently.
