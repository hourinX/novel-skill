from pathlib import Path

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

from ..core.model import ModelClient
from ..core.memory import read_memory
from ..core.outline import (
    append_outline_rows,
    get_max_chapter_num,
    read_outline,
)
from ..core.worldview import read_worldview
from ..prompts.templates import build_outline_extend_prompt

router = APIRouter()


RECENT_NOVEL_CHAR_LIMIT = 6000


def _load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_recent_novel() -> str:
    config = _load_config()
    novel_path = Path(config["novel"]["novel_path"])
    if not novel_path.exists():
        return ""
    text = novel_path.read_text(encoding="utf-8").strip()
    if len(text) <= RECENT_NOVEL_CHAR_LIMIT:
        return text
    return "…（前文略）…\n" + text[-RECENT_NOVEL_CHAR_LIMIT:]


def _auto_count(from_chapter: int) -> int:
    """补到下一个 5 的倍数；若已是 5 的倍数则再补 5 章。"""
    next_target = ((from_chapter // 5) + 1) * 5
    return max(1, next_target - from_chapter)


class ExtendOutlineRequest(BaseModel):
    from_chapter: int = 0   # 0 = 自动取 outline 最大章节号
    count: int = 0          # 0 = 自动补到下一个 5 的倍数
    note: str = ""


class ExtendOutlineResponse(BaseModel):
    extended: bool
    from_chapter: int
    count: int


@router.post("/outline/extend", response_model=ExtendOutlineResponse)
async def extend_outline(req: ExtendOutlineRequest):
    from_chapter = req.from_chapter if req.from_chapter > 0 else get_max_chapter_num()
    count = req.count if req.count > 0 else _auto_count(from_chapter)

    worldview = read_worldview()
    outline = read_outline()
    memory = read_memory()
    recent_novel = _read_recent_novel()

    client = ModelClient()
    extend_prompt = build_outline_extend_prompt(
        worldview=worldview,
        current_outline=outline,
        memory=memory,
        last_chapter_num=from_chapter,
        count=count,
        recent_novel=recent_novel,
        note=req.note,
    )
    new_rows = client.generate(extend_prompt, max_tokens=4096)
    inserted = append_outline_rows(new_rows)

    return ExtendOutlineResponse(
        extended=inserted > 0,
        from_chapter=from_chapter,
        count=inserted,
    )