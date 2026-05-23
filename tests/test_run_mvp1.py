import unittest

from src.github_readme import ReadmeResult
from src.run_mvp1 import build_output_document


class RunMvp1Tests(unittest.TestCase):
    def test_build_output_document_includes_repo_metadata_and_translation(self):
        readme = ReadmeResult(
            owner="karpathy",
            repo="nanochat",
            default_branch="master",
            path="README.md",
            content="# NanoChat",
        )

        result = build_output_document(
            source_url="https://github.com/karpathy/nanochat",
            readme=readme,
            translation="## 中文 README\n\n翻译结果",
        )

        self.assertIn("# README 中文翻译", result)
        self.assertIn("https://github.com/karpathy/nanochat", result)
        self.assertIn("默认分支：master", result)
        self.assertIn("README 路径：README.md", result)
        self.assertIn("## 中文 README", result)


if __name__ == "__main__":
    unittest.main()
