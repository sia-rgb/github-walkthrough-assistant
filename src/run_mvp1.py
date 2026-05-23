import argparse
from pathlib import Path

from src.deepseek_client import DeepSeekClient
from src.github_readme import GitHubClient


def build_output_document(source_url, readme, translation):
    return (
        "# README 中文翻译\n\n"
        f"- 来源：{source_url}\n"
        f"- 仓库：{readme.owner}/{readme.repo}\n"
        f"- 默认分支：{readme.default_branch}\n"
        f"- README 路径：{readme.path}\n\n"
        "---\n\n"
        f"{translation.strip()}\n"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch a GitHub README and translate it to Chinese.")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--output",
        default="outputs/readme_translation.md",
        help="Markdown output path",
    )
    parser.add_argument("--env", default=".env", help="Environment file path")
    args = parser.parse_args(argv)

    readme = GitHubClient().fetch_readme(args.repo_url)
    translation = DeepSeekClient.from_env(args.env).translate_readme(readme.content)
    document = build_output_document(args.repo_url, readme, translation)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
