import json
import unittest

from src.deepseek_client import DeepSeekClient, build_readme_translation_prompt


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload


class FakeTransport:
    def __init__(self):
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        payload = {
            "choices": [
                {
                    "message": {
                        "content": "## 中文 README\n\n翻译结果\n\n## 专业术语注释\n\n- token：词元"
                    }
                }
            ]
        }
        return FakeResponse(json.dumps(payload))


class DeepSeekClientTests(unittest.TestCase):
    def test_build_prompt_requires_translation_and_term_notes(self):
        prompt = build_readme_translation_prompt("# NanoChat\nA minimal ChatGPT clone.")

        self.assertIn("中文 README", prompt)
        self.assertIn("专业术语注释", prompt)
        self.assertIn("# NanoChat", prompt)

    def test_translate_readme_posts_openai_compatible_chat_request(self):
        transport = FakeTransport()
        client = DeepSeekClient(
            api_key="test-key",
            model="deepseek-chat",
            endpoint="https://api.deepseek.com/chat/completions",
            timeout=12,
            transport=transport,
        )

        result = client.translate_readme("# NanoChat")

        self.assertIn("翻译结果", result)
        request, timeout = transport.requests[0]
        self.assertEqual(timeout, 12)
        self.assertEqual(request.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(request.headers["Authorization"], "Bearer test-key")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "deepseek-chat")
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(body["messages"][1]["role"], "user")


if __name__ == "__main__":
    unittest.main()
