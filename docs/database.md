# Database

The MySQL 8 schema is in `database/schema.sql`. It includes users, papers, authors, paper-author links, topics, paper-topic links, keywords, paper-keyword links, citations, yearly trend snapshots, job postings, skills, job-skill links and chat history. Keys, indexes, uniqueness rules and cascades are defined in the schema.

For a quick local demo, backend defaults to `sqlite:///./tracker.db`; tables are created at API startup. Copy `backend/.env.example` to `backend/.env`, set a strong secret, then optionally use `mysql+pymysql://user:password@localhost/literature_tracker` as `DATABASE_URL`. Use `python seed.py` from `backend` for the clearly labeled illustrative sample records.
