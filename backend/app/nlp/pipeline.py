import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


def clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+|[^a-zA-Z0-9\s-]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str, limit: int = 10) -> list[str]:
    words = [w for w in clean_text(text).split() if len(w) > 2 and w not in ENGLISH_STOP_WORDS]
    return [word for word, _ in Counter(words).most_common(limit)]


def tfidf_matrix(texts: list[str]):
    if not texts:
        return None, None
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
    return vectorizer.fit_transform(texts), vectorizer
