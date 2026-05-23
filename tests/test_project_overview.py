import json
import unittest

from src.deepseek_client import DeepSeekClient, build_project_overview_prompt
from src.github_repository import RepositoryContext, RepositoryFile


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
                                "content": (
                                    "## 项目目标\n\n训练小型 LLM。\n\n"
                                    "## 解决的问题\n\n个人开源项目。\n\n"
                                    "## 核心技术/功能\n\nTransformer。\n\n"
                                    "## 硬件/软件要求\n\nPython。"
                                )
                            }
                        }
                    ]
                }
            )
        )


def make_context():
    return RepositoryContext(
        owner="karpathy",
        repo="nanochat",
        default_branch="master",
        owner_type="User",
        description="The best ChatGPT that $100 can buy.",
        files=[
            RepositoryFile(path="README.md", content="# nanochat\nTrain an LLM."),
            RepositoryFile(path="requirements.txt", content="torch\n"),
        ],
    )


class ProjectOverviewTests(unittest.TestCase):
    def test_build_project_overview_prompt_requires_four_sections(self):
        prompt = build_project_overview_prompt(make_context())

        self.assertIn("项目目标", prompt)
        self.assertIn("解决的问题", prompt)
        self.assertIn("核心技术/功能", prompt)
        self.assertIn("硬件/软件要求", prompt)
        self.assertIn("发布者类型：User", prompt)
        self.assertIn("README.md", prompt)

    def test_generate_project_overview_posts_context_to_deepseek(self):
        transport = FakeTransport()
        client = DeepSeekClient(
            api_key="test-key",
            model="deepseek-chat",
            endpoint="https://api.deepseek.com/chat/completions",
            transport=transport,
        )

        result = client.generate_project_overview(make_context())

        self.assertIn("## 项目目标", result)
        body = json.loads(transport.requests[0].data.decode("utf-8"))
        self.assertIn("四点项目概览", body["messages"][1]["content"])
        self.assertIn("User", body["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()
