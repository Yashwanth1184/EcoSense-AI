from backend.rag.chroma_db import get_collection

def retrieve(query: str, limit: int = 5):
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.query(query_texts=[query], n_results=min(limit, collection.count()))
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    return [{
        "title": m["title"],
        "organization": m["organization"],
        "claim": m["claim"],
        "mechanism": m["mechanism"],
        "source_url": m["source_url"]
    } for m in metas]
