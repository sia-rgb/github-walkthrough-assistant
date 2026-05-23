import unittest
from pathlib import Path

from src.github_readme import ReadmeResult
from src.web_app import build_analyze_response, build_plain_explain_response


class FakeReadmeClient:
    def fetch_readme(self, repo_url):
        return ReadmeResult(
            owner="karpathy",
            repo="nanochat",
            default_branch="master",
            path="README.md",
            content="# nanochat",
        )


class FakeRepositoryClient:
    def fetch_repository_context(self, repo_url):
        return "repository context"


class FakeDeepSeekClient:
    def translate_readme(self, readme_content):
        return "## 中文 README\n\n中文翻译\n\n## 专业术语注释\n\n- token：词元"

    def generate_project_overview(self, repository_context):
        return (
            "## 项目目标\n\n目标\n\n"
            "## 解决的问题\n\n问题\n\n"
            "## 核心技术/功能\n\n技术\n\n"
            "## 硬件/软件要求\n\n要求"
        )

    def generate_plain_explanation(self, selected_text):
        return "## 大白话辅助说明\n\n通俗解释"


class WebAppTests(unittest.TestCase):
    def test_build_analyze_response_combines_translation_and_overview(self):
        result = build_analyze_response(
            "https://github.com/karpathy/nanochat",
            readme_client=FakeReadmeClient(),
            repository_client=FakeRepositoryClient(),
            deepseek_client=FakeDeepSeekClient(),
        )

        self.assertEqual(result["repo"], "karpathy/nanochat")
        self.assertEqual(result["default_branch"], "master")
        self.assertIn("## 中文 README", result["readme_translation"])
        self.assertIn("## 项目目标", result["project_overview"])

    def test_build_plain_explain_response_uses_selected_text(self):
        result = build_plain_explain_response(
            "选中的中文文本",
            deepseek_client=FakeDeepSeekClient(),
        )

        self.assertEqual(result["selected_text"], "选中的中文文本")
        self.assertIn("## 大白话辅助说明", result["plain_explanation"])

    def test_frontend_layout_places_overview_left_and_readme_right(self):
        html = Path("frontend/index.html").read_text(encoding="utf-8")

        self.assertIn('id="overviewPane"', html)
        self.assertIn('id="readmePane"', html)
        self.assertLess(html.index('id="overviewPane"'), html.index('id="readmePane"'))
        self.assertIn('id="plainExplainButton"', html)
        self.assertGreater(html.index('id="plainExplainButton"'), html.index('id="readmeContent"'))
        self.assertIn('id="plainExplainPane"', html)
        self.assertIn('class="content-column"', html)
        self.assertLess(html.index('id="readmePane"'), html.index('id="plainExplainPane"'))


if __name__ == "__main__":
    unittest.main()
