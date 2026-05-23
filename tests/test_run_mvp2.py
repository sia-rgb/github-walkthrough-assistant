import unittest

from src.github_repository import RepositoryContext, RepositoryFile
from src.run_mvp2 import build_output_document


class RunMvp2Tests(unittest.TestCase):
    def test_build_output_document_includes_metadata_and_overview(self):
        context = RepositoryContext(
            owner="karpathy",
            repo="nanochat",
            default_branch="master",
            owner_type="User",
            description="The best ChatGPT that $100 can buy.",
            files=[RepositoryFile(path="README.md", content="# nanochat")],
        )

        result = build_output_document(
            source_url="https://github.com/karpathy/nanochat",
            context=context,
            overview="## 项目目标\n\n训练 LLM。",
        )

        self.assertIn("# 项目概览", result)
        self.assertIn("https://github.com/karpathy/nanochat", result)
        self.assertIn("默认分支：master", result)
        self.assertIn("发布者类型：User", result)
        self.assertIn("分析文件：README.md", result)
        self.assertIn("## 项目目标", result)


if __name__ == "__main__":
    unittest.main()
