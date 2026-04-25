import chromadb
from pathlib import Path
from .model import ModelClient


CHROMA_PATH = Path("data/.chroma")
COLLECTION_NAME = "novel_chapters"


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def add_chapter(chapter_num: int, content: str) -> None:
    """将章节内容向量化存入库"""
    client = ModelClient()
    embedding = client.embed(content)
    collection = get_collection()
    collection.upsert(
        ids=[f"chapter_{chapter_num}"],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{"chapter": chapter_num}],
    )


def search_similar(query: str, top_k: int = 5) -> list[str]:
    """检索与 query 最相关的章节片段"""
    client = ModelClient()
    embedding = client.embed(query)
    collection = get_collection()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
    )
    if not results["documents"]:
        return []
    return results["documents"][0]


def get_recent_chapters(recent_n: int = 3) -> list[str]:
    """获取最近 N 章的全文"""
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []
    results = collection.get(
        where={"chapter": {"$gte": max(1, total - recent_n + 1)}},
        include=["documents", "metadatas"],
    )
    paired = sorted(
        zip(results["metadatas"], results["documents"]),
        key=lambda x: x[0]["chapter"],
    )
    return [doc for _, doc in paired]