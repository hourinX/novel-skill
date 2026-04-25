from fastapi import APIRouter
from pydantic import BaseModel
from ..core.model import ModelClient
from ..core.outline import read_outline, get_chapter_info
from ..core.memory import read_memory
from ..core.worldview import read_worldview
from ..core.character import read_character
from ..core.fanfic import search_fanfic_context
from ..core.vector_novel import get_recent_chapters
from ..core.validator import check_word_count, split_into_segments
from ..core.pre_analysis import analyze_chapter
from ..core.preferences import read_preferences
from ..prompts.templates import build_generate_prompt
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class RegenerateRequest(BaseModel):
    chapter: int
    words: int = 0
    note: str = ""


class RegenerateResponse(BaseModel):
    chapter: int
    words_actual: int
    content: str


@router.post("/regenerate", response_model=RegenerateResponse)
async def regenerate_chapter(req: RegenerateRequest):
    config = load_config()
    words_per_segment = config["novel"]["words_per_segment"]
    max_retry = config["novel"]["max_retry_rounds"]

    prefs = read_preferences()
    words = req.words or prefs.get("chapter_length", 8000)

    outline = read_outline()
    worldview = read_worldview()
    character = read_character()
    memory = read_memory()
    recent_chapters = get_recent_chapters(config["novel"]["recent_chapters"])
    chapter_info = get_chapter_info(req.chapter)

    fanfic_context = search_fanfic_context(
        f"{chapter_info.get('title', '')} {chapter_info.get('core_event', '')}"
    )

    # 如果有纠错备注，注入到 chapter_info
    if req.note:
        chapter_info["correction_note"] = req.note

    segments = split_into_segments(words, words_per_segment)
    client = ModelClient()
    full_content = ""

    for i, seg_words in enumerate(segments):
        for attempt in range(max_retry):
            prompt = build_generate_prompt(
                chapter_info=chapter_info,
                outline=outline,
                worldview=worldview,
                character=character,
                memory=memory,
                recent_chapters=recent_chapters,
                segment_index=i,
                total_segments=len(segments),
                words=seg_words,
                previous_segments=full_content,
                fanfic_context=fanfic_context,
            )
            segment_text = client.generate(prompt, max_tokens=4096)
            ok, actual = check_word_count(segment_text, seg_words)
            if ok or attempt == max_retry - 1:
                full_content += segment_text
                break

    lines = full_content.splitlines()
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        cleaned_lines.append(line)
        prev_blank = is_blank
    full_content = "\n".join(cleaned_lines)

    draft_path = Path(config["novel"]["draft_path"])
    draft_path.write_text(full_content, encoding="utf-8")

    _, total_actual = check_word_count(full_content, words)

    return RegenerateResponse(
        chapter=req.chapter,
        words_actual=total_actual,
        content=full_content,
    )