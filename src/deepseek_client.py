import json
import os
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


def build_readme_translation_prompt(readme_content):
    return (
        "请将下面的 GitHub README 翻译为中文，并标注专业术语。\n\n"
        "输出必须使用以下 Markdown 结构：\n\n"
        "## 中文 README\n"
        "保留原 README 的标题层级、列表、代码块、链接和表格结构，只翻译解释性文字。\n\n"
        "## 专业术语注释\n"
        "用项目上下文解释关键技术词、缩写和容易误解的概念。\n\n"
        "README 原文如下：\n\n"
        f"{readme_content}"
    )


def load_dotenv_values(path=".env"):
    values = {}
    if not os.path.exists(path):
        return values

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class DeepSeekClient:
    def __init__(
        self,
        api_key,
        model=DEFAULT_MODEL,
        endpoint=DEFAULT_ENDPOINT,
        timeout=60,
        transport=urlopen,
    ):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout
        self.transport = transport

    @classmethod
    def from_env(cls, env_path=".env"):
        env_values = load_dotenv_values(env_path)
        api_key = os.environ.get("DEEPSEEK_API_KEY") or env_values.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY")

        model = os.environ.get("DEEPSEEK_MODEL") or env_values.get("DEEPSEEK_MODEL") or DEFAULT_MODEL
        endpoint = (
            os.environ.get("DEEPSEEK_CHAT_ENDPOINT")
            or env_values.get("DEEPSEEK_CHAT_ENDPOINT")
            or DEFAULT_ENDPOINT
        )
        timeout_text = (
            os.environ.get("DEEPSEEK_HTTP_TIMEOUT_SEC")
            or env_values.get("DEEPSEEK_HTTP_TIMEOUT_SEC")
            or "60"
        )
        return cls(api_key=api_key, model=model, endpoint=endpoint, timeout=float(timeout_text))

    def translate_readme(self, readme_content):
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是技术文档翻译助手。输出中文，保持专业、准确、可读。",
                },
                {"role": "user", "content": build_readme_translation_prompt(readme_content)},
            ],
            "temperature": 0.2,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with self.transport(request, timeout=self.timeout) as response:
            response_payload = response.read().decode("utf-8")

        data = json.loads(response_payload)
        return data["choices"][0]["message"]["content"]
