import re
from pathlib import Path
import yaml


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_outline() -> str:
    config = load_config()
    outline_path = Path(config["novel"]["outline_path"])
    if not outline_path.exists():
        return ""
    return outline_path.read_text(encoding="utf-8")


def write_outline(content: str) -> None:
    config = load_config()
    outline_path = Path(config["novel"]["outline_path"])
    outline_path.parent.mkdir(parents=True, exist_ok=True)
    outline_path.write_text(content, encoding="utf-8")


def get_chapter_info(chapter_num: int) -> dict:
    """从大纲中提取指定章节的信息"""
    content = read_outline()
    lines = content.splitlines()
    for line in lines:
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 7:
            continue
        if f"第{chapter_num}章" in cols[0] or str(chapter_num) in cols[0]:
            return {
                "chapter": cols[0],
                "title": cols[1],
                "core_event": cols[2],
                "character_arc": cols[3],
                "foreshadowing": cols[4],
                "tone": cols[5],
                "hook_type": cols[6],
            }
    return {}

def get_max_chapter_num() -> int:
    """返回 outline.md 中已存在的最大章节号，不存在则返回 0。"""
    content = read_outline()
    max_num = 0
    for line in content.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if not cols:
            continue
        num = "".join(c for c in cols[0] if c.isdigit())
        if num:
            max_num = max(max_num, int(num))
    return max_num


def count_remaining_chapters(current_chapter: int) -> int:
    """统计当前章节之后还有几章大纲"""
    content = read_outline()
    lines = content.splitlines()
    count = 0
    for line in lines:
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        if "章节" in cols[0] or "---" in cols[0]:
            continue
        # 提取章节号
        chapter_str = cols[0]
        num = ""
        for c in chapter_str:
            if c.isdigit():
                num += c
        if num and int(num) > current_chapter:
            count += 1
    return count


_CHAPTER_ROW_RE = re.compile(r"^\|\s*第\s*\d+\s*章\b")


def append_outline_rows(rows: str) -> int:
    """把新生成的大纲行追加到 outline.md，返回实际落盘的行数。

    兼容不同模型的输出：剥离 markdown 代码栅栏，仅保留形如
    ``| 第N章 | ... |`` 且列数达标的表格行，不依赖关键字黑名单，
    避免 longcat 等模型把表头词（"核心事件""标题"等）写进正文时误杀。
    """
    content = read_outline()

    sanitized = re.sub(r"```[^\n]*", "", rows)

    clean_rows = []
    for line in sanitized.splitlines():
        line = line.strip()
        if not _CHAPTER_ROW_RE.match(line):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 7 or any(not c for c in cols):
            continue
        clean_rows.append(line)

    if clean_rows:
        content = content.rstrip() + "\n" + "\n".join(clean_rows) + "\n"
        write_outline(content)
    return len(clean_rows)