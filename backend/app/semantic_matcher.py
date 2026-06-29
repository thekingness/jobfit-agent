import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ENABLE_EMBEDDING = os.getenv("JOBFIT_ENABLE_EMBEDDING", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

LOCAL_EMBEDDING_MODEL_PATH = os.getenv(
    "JOBFIT_LOCAL_EMBEDDING_MODEL_PATH",
    "",
)


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    只加载本地 embedding 模型，不访问 HuggingFace。
    """

    if not ENABLE_EMBEDDING:
        print("[JobFit] Embedding disabled by JOBFIT_ENABLE_EMBEDDING=false.")
        return None

    if not LOCAL_EMBEDDING_MODEL_PATH:
        print("[JobFit] Embedding disabled: JOBFIT_LOCAL_EMBEDDING_MODEL_PATH is empty.")
        return None

    model_path = Path(LOCAL_EMBEDDING_MODEL_PATH)

    if not model_path.exists():
        print(f"[JobFit] Embedding disabled: local model path not found: {model_path}")
        return None

    try:
        from sentence_transformers import SentenceTransformer

        print(f"[JobFit] Loading local embedding model: {model_path}")
        return SentenceTransformer(str(model_path), local_files_only=True)
    except TypeError:
        try:
            from sentence_transformers import SentenceTransformer

            print(f"[JobFit] Loading local embedding model without local_files_only: {model_path}")
            return SentenceTransformer(str(model_path))
        except Exception as error:
            print(f"[JobFit] Local embedding model load failed, fallback to TF-IDF. Reason: {error}")
            return None
    except Exception as error:
        print(f"[JobFit] Local embedding model load failed, fallback to TF-IDF. Reason: {error}")
        return None


@lru_cache(maxsize=5000)
def fuzzy_similarity(a: str, b: str) -> float:
    a = clean_text(a)
    b = clean_text(b)

    if not a or not b:
        return 0.0

    return fuzz.token_set_ratio(a, b) / 100


@lru_cache(maxsize=5000)
def tfidf_similarity(a: str, b: str) -> float:
    a = clean_text(a)
    b = clean_text(b)

    if not a or not b:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            lowercase=True,
        )
        matrix = vectorizer.fit_transform([a, b])
        score = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(score)
    except Exception:
        return 0.0


@lru_cache(maxsize=5000)
def embedding_similarity(a: str, b: str) -> float:
    """
    本地 embedding 相似度。
    不会联网下载模型。
    """

    if not ENABLE_EMBEDDING:
        return 0.0

    a = clean_text(a)
    b = clean_text(b)

    if not a or not b:
        return 0.0

    model = get_embedding_model()

    if model is None:
        return 0.0

    try:
        embeddings = model.encode(
            [a, b],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        score = float(embeddings[0] @ embeddings[1])
        return max(0.0, min(1.0, score))
    except Exception as error:
        print(f"[JobFit] Embedding similarity failed, fallback to TF-IDF. Reason: {error}")
        return 0.0


def hybrid_similarity(a: str, b: str) -> Tuple[float, str]:
    """
    混合相似度：
    - fuzzy：处理拼写、符号、大小写差异
    - tfidf：处理短文本相似度
    - embedding：本地模型可用时处理语义相近表达
    """

    fuzzy_score = fuzzy_similarity(a, b)

    if fuzzy_score >= 0.88:
        return fuzzy_score, "fuzzy"

    tfidf_score = tfidf_similarity(a, b)

    if tfidf_score >= 0.62:
        return tfidf_score, "tfidf"

    best_score = max(fuzzy_score, tfidf_score)
    best_method = "fuzzy" if fuzzy_score >= tfidf_score else "tfidf"

    if not ENABLE_EMBEDDING:
        return best_score, best_method

    if best_score < 0.18:
        return best_score, best_method

    embedding_score = embedding_similarity(a, b)

    candidates = [
        (embedding_score, "embedding"),
        (tfidf_score, "tfidf"),
        (fuzzy_score, "fuzzy"),
    ]

    return max(candidates, key=lambda item: item[0])


def best_match_score(query: str, candidates: List[str]) -> Tuple[float, str, str]:
    best_score = 0.0
    best_text = ""
    best_method = "none"

    query = clean_text(query)

    for candidate in candidates:
        candidate = clean_text(candidate)

        if not query or not candidate:
            continue

        score, method = hybrid_similarity(query, candidate)

        if score > best_score:
            best_score = score
            best_text = candidate
            best_method = method

    return best_score, best_text, best_method


def is_semantic_match(
    query: str,
    candidates: List[str],
    threshold: float = 0.55,
) -> Tuple[bool, float, str, str]:
    score, matched_text, method = best_match_score(query, candidates)

    return score >= threshold, score, matched_text, method