import argparse
from pathlib import Path

from src.deepseek_client import DeepSeekClient
from src.github_repository import GitHubRepositoryClient


def build_output_document(source_url, context, overview):
    analyzed_files = ", ".join(file_item.path for file_item in context.files)
    return (
        "# 项目概览\n\n"
        f"- 来源：{source_url}\n"
        f"- 仓库：{context.owner}/{context.repo}\n"
        f"- 默认分支：{context.default_branch}\n"
        f"- 发布者类型：{context.owner_type}\n"
        f"- 仓库描述：{context.description}\n"
        f"- 分析文件：{analyzed_files}\n\n"
        "---\n\n"
        f"{overview.strip()}\n"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a four-part GitHub project overview.")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--output",
        default="outputs/project_overview.md",
        help="Markdown output path",
    )
    parser.add_argument("--env", default=".env", help="Environment file path")
    args = parser.parse_args(argv)

    context = GitHubRepositoryClient.from_env(args.env).fetch_repository_context(args.repo_url)
    overview = DeepSeekClient.from_env(args.env).generate_project_overview(context)
    document = build_output_document(args.repo_url, context, overview)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
