from .model import ModelClient
from .outline import get_chapter_info
from .memory import read_memory
from .worldview import read_worldview
from .character import read_character
from ..prompts.templates import build_pre_analysis_prompt


def analyze_chapter(chapter_num: int) -> str:
    chapter_info = get_chapter_info(chapter_num)
    memory = read_memory()
    worldview = read_worldview()
    character = read_character()

    if not chapter_info:
        return f"未在大纲中找到第 {chapter_num} 章的信息，请检查大纲格式。"

    prompt = build_pre_analysis_prompt(
        chapter_info=chapter_info,
        worldview=worldview,
        character=character,
        memory=memory,
    )

    client = ModelClient()
    return client.generate(prompt, max_tokens=1024)