from pathlib import Path
import yaml


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_character() -> str:
    config = load_config()
    character_path = Path(config["novel"].get("character_path", "data/character.md"))
    if not character_path.exists():
        return ""
    return character_path.read_text(encoding="utf-8")