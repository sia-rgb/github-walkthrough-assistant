import unittest

from src.run_mvp3 import build_output_document


class RunMvp3Tests(unittest.TestCase):
    def test_build_output_document_includes_original_text_and_explanation(self):
        result = build_output_document(
            source_label="command line text",
            selected_text="depth 参数控制 Transformer 的层数。",
            explanation="## 大白话辅助说明\n\n这里是在说模型层数由 depth 控制。",
        )

        self.assertIn("# 大白话辅助说明", result)
        self.assertIn("来源：command line text", result)
        self.assertIn("## 选中文本", result)
        self.assertNotIn("## 原文", result)
        self.assertIn("depth 参数控制 Transformer 的层数。", result)
        self.assertIn("## 大白话辅助说明", result)


if __name__ == "__main__":
    unittest.main()
