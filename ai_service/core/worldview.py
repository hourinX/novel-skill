from pathlib import Path
import yaml


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_worldview() -> str:
    config = load_config()
    worldview_path = Path(config["novel"].get("worldview_path", "data/worldview.md"))
    if not worldview_path.exists():
        return ""
    return worldview_path.read_text(encoding="utf-8")