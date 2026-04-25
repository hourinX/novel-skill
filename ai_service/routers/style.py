from fastapi import APIRouter
from pydantic import BaseModel
from ..core.vector_style import add_style_ref
import yaml
from pathlib import Path

router = APIRouter()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class IndexStyleResponse(BaseModel):
    indexed: list[str]
    skipped: list[str]


@router.post("/style/index", response_model=IndexStyleResponse)
async def index_style_refs():
    """扫描 style_refs 目录，把所有 txt 文件向量化入库"""
    config = load_config()
    style_refs_dir = Path(config["novel"]["style_refs_dir"])

    if not style_refs_dir.exists():
        return IndexStyleResponse(indexed=[], skipped=[])

    indexed = []
    skipped = []

    for txt_file in style_refs_dir.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding="utf-8")
            if not content.strip():
                skipped.append(txt_file.stem)
                continue
            add_style_ref(txt_file.stem, content)
            indexed.append(txt_file.stem)
        except Exception as e:
            skipped.append(f"{txt_file.stem}（{str(e)}）")

    return IndexStyleResponse(indexed=indexed, skipped=skipped)