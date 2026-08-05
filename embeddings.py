import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

VECTORIZER_PATH = Path(__file__).parent / "data" / "tfidf_vectorizer.pkl"


class TfidfEmbeddingFunction:
    """Local, dependency-free embedding function — no pretrained model to
    download, no external API. The vectorizer is fit once on the KB corpus
    at seed time (see data/seed_kb.py) and persisted; both seeding and
    retrieval load that same fitted vectorizer so queries land in the same
    vector space as the documents. Chosen over a sentence-transformers model
    because this deployment environment's egress policy blocks Hugging Face
    Hub downloads — see docs/DEVELOPER_GUIDE.md for the full rationale and
    how to swap in a real embedding model where that's not a constraint."""

    def __init__(self, vectorizer: TfidfVectorizer):
        self._vectorizer = vectorizer

    def __call__(self, input):
        matrix = self._vectorizer.transform(list(input))
        return [row.tolist() for row in matrix.toarray()]

    def embed_query(self, input):
        return self.__call__(input)

    @staticmethod
    def name() -> str:
        return "tfidf_local"

    def get_config(self) -> dict:
        return {}

    @staticmethod
    def build_from_config(config: dict):
        return get_embedding_function()

    def default_space(self) -> str:
        return "cosine"

    def supported_spaces(self) -> list:
        return ["cosine"]

    def validate_config_update(self, old_config: dict, new_config: dict) -> None:
        return

    @staticmethod
    def validate_config(config: dict) -> None:
        return


def fit_vectorizer(texts: list[str]) -> TfidfVectorizer:
    """Fits and persists the vectorizer. Only called from data/seed_kb.py."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=4096)
    vectorizer.fit(texts)
    VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    return vectorizer


def get_embedding_function() -> TfidfEmbeddingFunction:
    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            "No fitted vectorizer found at "
            f"{VECTORIZER_PATH} — run `python data/seed_kb.py` first."
        )
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    return TfidfEmbeddingFunction(vectorizer)
