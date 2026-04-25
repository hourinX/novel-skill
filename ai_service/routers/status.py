from fastapi import APIRouter
from pydantic import BaseModel
from ..core.vector_novel import get_collection
from ..core.preferences import read_preferences
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class StatusResponse(BaseModel):
    total_chapters: int
    has_draft: bool
    draft_words: int
    preferences: dict


@router.get("/status", response_model=StatusResponse)
async def get_status():
    config = load_config()
    draft_path = Path(config["novel"]["draft_path"])

    # 已完成章节数
    collection = get_collection()
    total_chapters = collection.count()

    # 草稿状态
    has_draft = draft_path.exists() and draft_path.stat().st_size > 0
    draft_words = 0
    if has_draft:
        draft = draft_path.read_text(encoding="utf-8")
        draft_words = sum(1 for c in draft if '\u4e00' <= c <= '\u9fff')

    prefs = read_preferences()

    return StatusResponse(
        total_chapters=total_chapters,
        has_draft=has_draft,
        draft_words=draft_words,
        preferences=prefs,
    )