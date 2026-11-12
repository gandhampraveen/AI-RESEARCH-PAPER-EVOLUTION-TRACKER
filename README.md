# AI Scientific Literature Evolution Tracker

LitScope is an academic demonstration platform for exploring publication records, topic activity, paper similarity, local literature retrieval, and illustrative job-skill demand. It combines a React/Vite dashboard with a Python/FastAPI API and SQLAlchemy database layer.

## Abstract and objectives

Research outputs grow quickly and are difficult to scan as a connected, time-based landscape. This project brings publication records, authors, topics and citations into one searchable view. It demonstrates topic frequency and yearly activity, TF-IDF paper similarity, retrieval-based question answering and a transparent research-to-career skill mapping. It is an educational prototype: included records and job postings are illustrative, not verified bibliometric or live market data.

## System

The proposed system provides a modular REST API and responsive research dashboard. Compared with manual keyword searches and static spreadsheets, it can filter linked records, summarize topic counts, compare yearly topic activity and retrieve related papers locally. There is no paid API dependency.

## Features implemented

- JWT registration, login, profile lookup, password hashing and role claims.
- Paper CRUD API, DOI duplicate checks, search/filter/pagination, paper details/recommendations, and an author directory.
- TF-IDF cosine-similarity recommendations and local keyword extraction.
- API-backed dashboard, topic detail/trend endpoints, yearly charts and emerging/declining rankings.
- Local retrieval chatbot with reference records and stored chat exchanges.
- Illustrative job skill/role/location analytics and explainable keyword career mapping.
- Directional one-year trend estimate where sufficient yearly history exists, with a frontend estimate view.
- Admin-protected row-tolerant CSV import for papers and jobs, with a frontend upload view.
- Normalized MySQL schema and SQLite development fallback.

See [implementation checklist](docs/implementation-checklist.md) for incomplete items and limitations.

## Stack and architecture

React 18, Vite, JavaScript, React Router, Axios, Recharts, FastAPI, Pydantic, SQLAlchemy, PyMySQL, scikit-learn, Pandas and NumPy. Architecture notes are in `docs/architecture.md`; schema notes are in `docs/database.md`.

## Project structure

```text
backend/app/       API, settings, ORM, auth, analytics and NLP
backend/tests/     pytest API checks
frontend/src/      React pages, API client and styles
database/          MySQL schema and seed instructions
docs/              Architecture, API, NLP, chatbot, jobs and testing notes
```

## Setup on Windows

Open PowerShell at the project root. Python 3.11+ and Node.js 20+ are recommended.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8002
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open frontend at `http://localhost:5173`, API at `http://localhost:8002`, Swagger at `http://localhost:8002/docs`, health at `http://localhost:8002/health`. Port 8000 was occupied in the inspected workspace, so the project defaults to 8002.

## MySQL

Install and start MySQL 8, then execute `database/schema.sql` in a MySQL client. Set `DATABASE_URL` in `backend/.env` to `mysql+pymysql://USER:PASSWORD@localhost/literature_tracker`. The SQL seed note explains that the Python seed loader creates illustrative development records. SQLite is the default so the demo can start without MySQL.

## Render deployment

The API entry point is `backend/app/main.py`, and its FastAPI instance is named `app`. Deploy the backend as a Render web service with **Root Directory** set to `backend`, **Build Command** `pip install -r requirements.txt`, and **Start Command** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. The root-level `render.yaml` applies these settings as a Blueprint. From the repository root, use `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` if you need to launch it without changing directories.

## Environment

Backend variables are documented in `backend/.env.example`: `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_MINUTES`, `CORS_ORIGINS`. Frontend API origin is `VITE_API_URL` in `frontend/.env.example`. Change the development secret before sharing/deployment.

## API and tests

Browse OpenAPI at `/docs`. See [API notes](docs/api.md). Frontend production build: `cd frontend; npm run build`. Backend pytest suite: `cd backend; python -m pytest`. Current verification: 5 API tests pass, the production frontend build succeeds, and browser smoke checks confirmed dashboard statistics, paper records, and related-paper recommendations. See [testing notes](docs/testing.md).

## Demo accounts

No demo account or password is pre-created. Register an account through `POST /api/auth/register`. To test administrator-only import, set a trusted user's `role` to `ADMIN` in the database.

## Limitations and future work

This is a working starter implementation, not completion of every requested production module. The seed contains 20 illustrative papers, a shared demonstration author, 12 topics and 108 synthetic job postings. Paper/author counts do not meet the requested 100+/50+ targets. The seeded job rows are fictional and clearly marked as samples, not live hiring information. Full author management, admin CRUD for users/jobs/topics, frontend paper editing, more extensive API tests, robust topic modeling/lemmatization, citation graph management, normalized job-skill ingestion and model evaluation remain to be built. Trend metrics from sparse samples are descriptive only. Do not use sample citations as verified citation counts.
