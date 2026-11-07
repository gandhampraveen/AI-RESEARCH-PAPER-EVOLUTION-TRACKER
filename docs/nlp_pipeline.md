# NLP pipeline

`backend/app/nlp/pipeline.py` provides text cleaning, English stopword filtering, frequency keyword extraction and scikit-learn TF-IDF. Paper similarity uses cosine similarity over title, abstract and assigned topic text. This lightweight local pipeline works without downloaded language models. Lemmatization and unsupervised topic modeling are not implemented in this baseline; topic records are attached through paper entry/import and analytics are calculated from those records.
