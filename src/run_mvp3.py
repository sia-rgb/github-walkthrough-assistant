import argparse
from pathlib import Path

from src.deepseek_client import DeepSeekClient


def build_output_document(source_label, selected_text, explanation):
    return (
        "# 大白话辅助说明\n\n"
        f"- 来源：{source_label}\n\n"
        "## 选中文本\n\n"
        f"{selected_text.strip()}\n\n"
        "---\n\n"
        f"{explanation.strip()}\n"
    )


def read_selected_text(args):
    if args.text:
        return "command line text", args.text

    input_path = Path(args.input)
    return str(input_path), input_path.read_text(encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a plain-language explanation for selected text.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", help="Selected text to explain")
    input_group.add_argument("--input", help="UTF-8 text file containing selected text")
    parser.add_argument(
        "--output",
        default="outputs/plain_explanation.md",
        help="Markdown output path",
    )
    parser.add_argument("--env", default=".env", help="Environment file path")
    args = parser.parse_args(argv)

    source_label, selected_text = read_selected_text(args)
    explanation = DeepSeekClient.from_env(args.env).generate_plain_explanation(selected_text)
    document = build_output_document(source_label, selected_text, explanation)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
