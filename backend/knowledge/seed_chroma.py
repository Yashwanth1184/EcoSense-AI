import json
from pathlib import Path
from backend.rag.chroma_db import get_collection
from backend.rag.embeddings import build_document_text

ROOT = Path(__file__).resolve().parents[2]
KB = ROOT / "backend" / "knowledge" / "knowledge_base.json"

def seed():
    collection = get_collection()
    items = json.loads(KB.read_text(encoding="utf-8"))
    documents, ids, metadatas = [], [], []
    for i, item in enumerate(items):
        documents.append(build_document_text(item))
        ids.append(str(i + 1))
        metadatas.append({
            "title": item["title"],
            "organization": item["organization"],
            "claim": item["claim"],
            "mechanism": item["mechanism"],
            "metrics": ", ".join(item["metrics"]),
            "source_url": item["source_url"]
        })
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Seeded {len(items)} scientific records into ChromaDB.")

if __name__ == "__main__":
    seed()
