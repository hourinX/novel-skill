import httpx
import yaml
from pathlib import Path


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_fanfic_context(query: str) -> str:
    """用 Serper API 搜索原著相关内容"""
    config = load_config()
    fanfic_cfg = config.get("fanfic", {})

    if not fanfic_cfg.get("enabled", False):
        return ""

    api_key = fanfic_cfg.get("serper_api_key", "")
    reference_book = fanfic_cfg.get("reference_book", "")

    if not api_key or not reference_book:
        return ""

    search_query = f"{reference_book} {query} 剧情 设定"

    try:
        with httpx.Client(proxy="http://127.0.0.1:7890", timeout=15) as client:
            resp = client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": search_query, "num": 5, "hl": "zh-cn"},
            )
            resp.raise_for_status()
            data = resp.json()

        snippets = []
        for item in data.get("organic", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if snippet:
                snippets.append(f"【{title}】{snippet}")

        if not snippets:
            return ""

        return "## 原著参考资料（网络检索）\n\n" + "\n\n".join(snippets)

    except Exception as e:
        return f"## 原著参考资料\n\n（检索失败：{e}）"