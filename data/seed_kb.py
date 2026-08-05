"""
Parses the markdown KB articles in data/kb_docs/ and embeds them into a
persistent Chroma collection at data/chroma/.

Run: python data/seed_kb.py
"""

import sys
from pathlib import Path

import chromadb
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from embeddings import fit_vectorizer, get_embedding_function  # noqa: E402

KB_DIR = Path(__file__).parent / "kb_docs"
CHROMA_DIR = Path(__file__).parent / "chroma"
COLLECTION_NAME = "kb_articles"


def parse_doc(path: Path):
    text = path.read_text()
    if not text.startswith("---"):
        raise ValueError(f"{path} is missing YAML frontmatter")
    _, frontmatter, body = text.split("---", 2)
    meta = yaml.safe_load(frontmatter)
    return meta["title"], meta["category"], body.strip()


def main():
    docs = sorted(KB_DIR.glob("*.md"))
    if not docs:
        raise SystemExit(f"No KB docs found in {KB_DIR}")

    ids, texts, metadatas = [], [], []
    for path in docs:
        title, category, body = parse_doc(path)
        ids.append(path.stem)
        # Prepend the title so it's part of what gets embedded/matched, not just metadata.
        texts.append(f"{title}\n\n{body}")
        metadatas.append({"title": title, "category": category, "source": path.name})

    # Fit the TF-IDF vectorizer on the KB corpus itself and persist it, so
    # retrieval later loads the exact same fitted vectorizer (same vocabulary
    # and IDF weights) to embed queries into the same vector space.
    fit_vectorizer(texts)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # Idempotent reseed
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Embedded {len(ids)} KB articles into '{COLLECTION_NAME}' at {CHROMA_DIR}")
    by_category = {}
    for m in metadatas:
        by_category[m["category"]] = by_category.get(m["category"], 0) + 1
    for cat, n in sorted(by_category.items()):
        print(f"  - {cat}: {n}")


if __name__ == "__main__":
    main()
