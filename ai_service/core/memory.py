from pathlib import Path
import yaml


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_memory() -> str:
    config = load_config()
    memory_path = Path(config["novel"]["memory_path"])
    if not memory_path.exists():
        return ""
    return memory_path.read_text(encoding="utf-8")


def write_memory(content: str) -> None:
    config = load_config()
    memory_path = Path(config["novel"]["memory_path"])
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(content, encoding="utf-8")


def append_memory(section: str, item: str) -> None:
    """在指定 section 下追加一条记录"""
    content = read_memory()
    if section not in content:
        content += f"\n## {section}\n\n- {item}\n"
    else:
        lines = content.splitlines()
        result = []
        in_section = False
        inserted = False
        for line in lines:
            result.append(line)
            if line.strip() == f"## {section}":
                in_section = True
            elif in_section and line.startswith("## ") and not inserted:
                result.insert(-1, f"- {item}")
                inserted = True
                in_section = False
        if in_section and not inserted:
            result.append(f"- {item}")
        content = "\n".join(result)
    write_memory(content)