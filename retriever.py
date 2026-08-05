from pathlib import Path
from typing import Optional

import chromadb

from embeddings import get_embedding_function

CHROMA_DIR = Path(__file__).parent / "data" / "chroma"
COLLECTION_NAME = "kb_articles"

VALID_CATEGORIES = {"plans", "billing", "usage", "troubleshooting", "admin"}


class Retriever:
    def __init__(self):
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = client.get_collection(
            name=COLLECTION_NAME, embedding_function=get_embedding_function()
        )

    def search(self, query: str, category: Optional[str] = None, k: int = 4) -> list[dict]:
        where = {"category": category} if category in VALID_CATEGORIES else None
        results = self.collection.query(
            query_texts=[query], n_results=k, where=where
        )
        hits = []
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            hits.append(
                {
                    "title": meta["title"],
                    "category": meta["category"],
                    "source": meta["source"],
                    "content": doc,
                    "relevance": round(1 - dist, 3),
                }
            )
        return hits
