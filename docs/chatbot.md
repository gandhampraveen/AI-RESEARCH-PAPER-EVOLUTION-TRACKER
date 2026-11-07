# Literature assistant

The assistant uses local catalogue retrieval, returns retrieved paper references, reports catalogue citations for citation questions, and computes topic movement from stored records for trend questions. Every answer is explicitly limited to indexed local data. It does not call an external LLM and cannot answer facts that are absent from the catalogue. Exchanges are stored in `chat_history`.
