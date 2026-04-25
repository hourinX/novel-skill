from fastapi import APIRouter
from pydantic import BaseModel
from ..core.model import ModelClient
from ..core.outline import read_outline
from ..core.preferences import read_preferences
from ..prompts.writing_rules import WRITING_RULES
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class IntroResponse(BaseModel):
    preface: str
    prologue: str
    synopsis: str


@router.post("/generate-intro", response_model=IntroResponse)
async def generate_intro():
    outline = read_outline()
    prefs = read_preferences()

    client = ModelClient()

    # 生成序言
    preface_prompt = f"""你是一位专业的中文小说作家。请根据以下大纲，为小说创作一篇序言（300字左右）。
序言应点明主题，引发读者兴趣，但不剧透情节。

## 大纲
{outline}

## 风格偏好
- 类型：{prefs.get('preferred_genre', '玄幻')}
- 写作风格：{prefs.get('writing_style', '紧张大气')}

直接输出序言正文："""
    preface = client.generate(preface_prompt, max_tokens=1024)

    # 生成楔子
    prologue_prompt = f"""你是一位专业的中文小说作家。请根据以下大纲，为小说创作一段楔子（800字左右）。
楔子应制造强烈悬念，直接抓住读者，可以从高潮场景切入，不需要交代背景。

## 大纲
{outline}

{WRITING_RULES}

直接输出楔子正文："""
    prologue = client.generate(prologue_prompt, max_tokens=2048)

    # 生成简介
    synopsis_prompt = f"""你是一位专业的中文小说编辑。请根据以下大纲，为小说创作一段封面简介（200字左右）。
简介应吸引眼球，突出核心冲突，结尾留悬念，风格类似起点中文网的爆款简介。

## 大纲
{outline}

直接输出简介正文："""
    synopsis = client.generate(synopsis_prompt, max_tokens=512)

    return IntroResponse(
        preface=preface,
        prologue=prologue,
        synopsis=synopsis,
    )