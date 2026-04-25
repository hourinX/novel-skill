from fastapi import APIRouter
from pydantic import BaseModel
from ..core.model import ModelClient
from ..core.memory import read_memory, write_memory
from ..core.outline import read_outline, write_outline, get_chapter_info, count_remaining_chapters, append_outline_rows
from ..core.worldview import read_worldview
from ..core.vector_novel import add_chapter
from ..core.preferences import read_preferences, write_preferences
from ..prompts.templates import build_accept_summary_prompt, build_outline_extend_prompt
import json
import re
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def upsert_chapter_in_novel(novel_path: Path, chapter: int, draft: str) -> None:
    """在 novel.md 中替换或追加指定章节，保证重复 accept 不会堆积内容。

    解析已有内容为 {章节号: 正文}，再按章节号排序落盘，保持 1→2→3 顺序。
    """
    novel_path.parent.mkdir(parents=True, exist_ok=True)
    existing = novel_path.read_text(encoding="utf-8") if novel_path.exists() else ""

    parts = re.split(r"(^# 第(\d+)章\b[^\n]*$)", existing, flags=re.MULTILINE)
    sections: dict[int, str] = {}
    i = 1
    while i + 1 < len(parts):
        header_line = parts[i]
        num = int(parts[i + 1])
        body = parts[i + 2] if i + 2 < len(parts) else ""
        sections[num] = f"{header_line}{body}".strip()
        i += 3

    sections[chapter] = f"# 第{chapter}章\n\n{draft.strip()}"
    ordered = [sections[k] for k in sorted(sections.keys())]
    novel_path.write_text("\n\n".join(ordered) + "\n", encoding="utf-8")


class AcceptRequest(BaseModel):
    chapter: int


class AcceptResponse(BaseModel):
    summary: str
    new_foreshadowing: list[str]
    character_updates: list[str]
    unresolved_conflicts: list[str]
    outline_extended: bool


@router.post("/accept", response_model=AcceptResponse)
async def accept_chapter(req: AcceptRequest):
    config = load_config()
    draft_path = Path(config["novel"]["draft_path"])

    if not draft_path.exists():
        return AcceptResponse(
            summary="草稿不存在",
            new_foreshadowing=[],
            character_updates=[],
            unresolved_conflicts=[],
            outline_extended=False,
        )

    draft = draft_path.read_text(encoding="utf-8")

    if not draft.strip():
        return AcceptResponse(
            summary="草稿为空，已跳过接收",
            new_foreshadowing=[],
            character_updates=[],
            unresolved_conflicts=[],
            outline_extended=False,
        )

    # AI 提取摘要
    client = ModelClient()
    summary_prompt = build_accept_summary_prompt(draft, req.chapter)
    summary_json = client.generate(summary_prompt, max_tokens=1024)

    try:
        summary_data = json.loads(summary_json)
    except json.JSONDecodeError:
        summary_data = {
            "summary": summary_json,
            "new_foreshadowing": [],
            "character_updates": [],
            "unresolved_conflicts": [],
        }

    # 保存章节文件
    chapters_dir = Path(config["novel"]["chapters_dir"])
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chapter_file = chapters_dir / f"ch{req.chapter:03d}.md"
    chapter_file.write_text(draft, encoding="utf-8")

    # 同步到 novel.md（已存在同章则替换，保证幂等）
    novel_path = Path(config["novel"]["novel_path"])
    upsert_chapter_in_novel(novel_path, req.chapter, draft)

    # 更新 memory.md
    memory = read_memory()
    memory += f"\n\n## 第{req.chapter}章更新\n"
    for item in summary_data.get("new_foreshadowing", []):
        memory += f"- [伏笔] {item}\n"
    for item in summary_data.get("character_updates", []):
        memory += f"- [人物] {item}\n"
    for item in summary_data.get("unresolved_conflicts", []):
        memory += f"- [冲突] {item}\n"
    write_memory(memory)

    # 向量库存入新章节
    add_chapter(req.chapter, draft)

    # 更新偏好
    prefs = read_preferences()
    write_preferences(prefs)

    # 检查是否需要续写大纲
    outline_extended = False
    remaining = count_remaining_chapters(req.chapter)
    if remaining < 3:
        worldview = read_worldview()
        outline = read_outline()
        memory_now = read_memory()
        extend_prompt = build_outline_extend_prompt(
            worldview=worldview,
            current_outline=outline,
            memory=memory_now,
            last_chapter_num=req.chapter,
        )
        new_rows = client.generate(extend_prompt, max_tokens=2048)
        inserted = append_outline_rows(new_rows)
        outline_extended = inserted > 0

    # 清空草稿
    draft_path.write_text("", encoding="utf-8")

    return AcceptResponse(
        summary=summary_data.get("summary", ""),
        new_foreshadowing=summary_data.get("new_foreshadowing", []),
        character_updates=summary_data.get("character_updates", []),
        unresolved_conflicts=summary_data.get("unresolved_conflicts", []),
        outline_extended=outline_extended,
    )