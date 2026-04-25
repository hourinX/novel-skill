from fastapi import APIRouter
from pydantic import BaseModel
from ..core.model import ModelClient
from ..core.outline import get_chapter_info
from ..core.vector_style import search_style
from ..prompts.templates import build_polish_prompt
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class PolishRequest(BaseModel):
    chapter: int
    style: str = ""


class PolishResponse(BaseModel):
    content: str


@router.post("/polish", response_model=PolishResponse)
async def polish_chapter(req: PolishRequest):
    config = load_config()
    draft_path = Path(config["novel"]["draft_path"])

    if not draft_path.exists():
        return PolishResponse(content="草稿不存在，请先执行 generate")

    draft = draft_path.read_text(encoding="utf-8")
    chapter_info = get_chapter_info(req.chapter)

    # RAG 检索风格参考
    top_k = config["novel"]["vector_top_k"]
    style_source = req.style if req.style else None
    style_refs = search_style(draft[:200], source=style_source, top_k=top_k)

    prompt = build_polish_prompt(
        draft=draft,
        style_refs=style_refs,
        chapter_info=chapter_info,
    )

    client = ModelClient()
    polished = client.generate(prompt, max_tokens=8192)

    # 覆盖草稿
    draft_path.write_text(polished, encoding="utf-8")

    return PolishResponse(content=polished)