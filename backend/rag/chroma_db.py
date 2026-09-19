from pathlib import Path
import chromadb

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "chroma"
_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        DB_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(DB_PATH))
        _collection = _client.get_or_create_collection("environmental_knowledge")
    return _collection
