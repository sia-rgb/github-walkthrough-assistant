import json
import unittest

from src.deepseek_client import DeepSeekClient, build_plain_explanation_prompt


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
        self.requests.append(request)
        return FakeResponse(
            json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "这段话的意思是：只调一个 depth 参数，其他训练参数会自动算好。"
                            }
                        }
                    ]
                }
            )
        )


class PlainExplanationTests(unittest.TestCase):
    def test_build_prompt_keeps_plain_explanation_as_auxiliary(self):
        prompt = build_plain_explanation_prompt("nanochat 会自动计算所有其他超参数。")

        self.assertIn("大白话辅助说明", prompt)
        self.assertIn("中文选中文本", prompt)
        self.assertIn("不替代原文", prompt)
        self.assertIn("nanochat 会自动计算所有其他超参数。", prompt)

    def test_generate_plain_explanation_posts_selected_text(self):
        transport = FakeTransport()
        client = DeepSeekClient(
            api_key="test-key",
            model="deepseek-chat",
            endpoint="https://api.deepseek.com/chat/completions",
            transport=transport,
        )

        result = client.generate_plain_explanation("nanochat 会自动计算所有其他超参数。")

        self.assertIn("depth 参数", result)
        body = json.loads(transport.requests[0].data.decode("utf-8"))
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(body["messages"][1]["role"], "user")
        self.assertIn("nanochat 会自动计算所有其他超参数。", body["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()
