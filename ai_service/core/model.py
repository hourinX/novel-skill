import time

import yaml
import httpx
from pathlib import Path


def load_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ModelClient:
    def __init__(self):
        config = load_config()
        self.provider = config["model"].get("provider", "gemini")
        self.api_key = config["model"]["api_key"]
        self.model_name = config["model"]["model"]
        self.base_url = config["model"].get("base_url", "")
        self.embedding_model = config["model"].get("embedding_model", "")
        self.request_timeout = config["model"].get("request_timeout", 600)

        if self.provider == "gemini":
            import google.generativeai as genai
            import os
            os.environ["GRPC_PROXY"] = "http://127.0.0.1:7890"
            os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
            os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
            os.environ["ALL_PROXY"] = "http://127.0.0.1:7890"
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str, max_tokens: int = 8192) -> str:
        if self.provider == "gemini":
            return self._generate_gemini(prompt, max_tokens)
        else:
            return self._generate_openai_compat(prompt, max_tokens)

    def embed(self, text: str) -> list[float]:
        if self.provider == "gemini":
            return self._embed_gemini(text)
        else:
            return self._embed_fake(text)

    # ── Gemini ────────────────────────────────────────────

    def _generate_gemini(self, prompt: str, max_tokens: int) -> str:
        import google.generativeai as genai
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
            ),
        )
        return response.text

    def _embed_gemini(self, text: str) -> list[float]:
        result = self.genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="RETRIEVAL_DOCUMENT",
        )
        return result["embedding"]

    # ── OpenAI 兼容（龙猫、DeepSeek、Groq 等）────────────

    def _generate_openai_compat(self, prompt: str, max_tokens: int) -> str:
        max_retries = 3
        delays = [2, 5, 10]  # 退避秒数

        with httpx.Client(timeout=self.request_timeout) as client:
            data = None
            for attempt in range(max_retries):
                try:
                    resp = client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": max_tokens,
                            "temperature": 0.9,
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    break
                except httpx.HTTPStatusError as e:
                    code = e.response.status_code
                    if code < 500 and code != 429:
                        raise  # 4xx（鉴权/参数错误）不重试
                    if attempt == max_retries - 1:
                        raise
                    delay = delays[attempt]
                    print(f"[model] {code} transient, retry {attempt + 1}/{max_retries} in {delay}s")
                    time.sleep(delay)
                except (httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = delays[attempt]
                    print(f"[model] {type(e).__name__}, retry {attempt + 1}/{max_retries} in {delay}s")
                    time.sleep(delay)

            # 兼容标准 OpenAI 格式
            if data.get("choices"):
                choice = data["choices"][0]
                message = choice.get("message", {})
                if message.get("content"):
                    return message["content"]
                if message.get("reasoning_content") and not message.get("content"):
                    return message["reasoning_content"]
                if message.get("text"):
                    return message["text"]
                if choice.get("text"):
                    return choice["text"]

            # 龙猫等非标准格式
            if data.get("result"):
                return data["result"]
            if data.get("output"):
                return data["output"]
            if data.get("response"):
                return data["response"]

            raise ValueError(f"无法解析 API 响应：{data}")

    def _embed_fake(self, text: str) -> list[float]:
        """OpenAI 兼容模式暂用哈希伪 embedding，RAG 降级但不影响主流程"""
        import hashlib
        hash_val = hashlib.md5(text.encode()).hexdigest()
        vector = [int(hash_val[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]
        while len(vector) < 768:
            vector.extend(vector[:min(16, 768 - len(vector))])
        return vector[:768]
