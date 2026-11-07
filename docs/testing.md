# Testing

Install backend dependencies in a virtual environment, start the API, and check `/health` and `/docs`. Run `python -m pytest` from `backend`. The current suite covers health, authentication, paper CRUD, authorization, topics, NLP keyword extraction, chatbot fallback, job analytics, predictions, and search (5 tests passing). The frontend production build passes, and a browser smoke check confirmed dashboard data, paper records and recommendations. Broader browser flows and invalid CSV edge cases still need dedicated automation.
