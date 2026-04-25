import chromadb
from pathlib import Path
from .model import ModelClient


CHROMA_PATH = Path("data/.chroma")
COLLECTION_NAME = "style_refs"
CHUNK_SIZE = 500


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """将长文本切成固定大小的片段"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def add_style_ref(name: str, content: str) -> None:
    """将风格参考小说向量化存入库"""
    client = ModelClient()
    collection = get_collection()
    chunks = chunk_text(content)
    for i, chunk in enumerate(chunks):
        embedding = client.embed(chunk)
        collection.upsert(
            ids=[f"{name}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": name, "chunk": i}],
        )


def search_style(query: str, source: str = None, top_k: int = 5) -> list[str]:
    """检索风格参考片段，可指定来源"""
    client = ModelClient()
    embedding = client.embed(query)
    collection = get_collection()
    if collection.count() == 0:
        return []
    where = {"source": source} if source else None
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
        where=where,
    )
    if not results["documents"]:
        return []
    return results["documents"][0]