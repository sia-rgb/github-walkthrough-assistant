from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.deepseek_client import DeepSeekClient
from src.github_readme import GitHubClient
from src.github_repository import GitHubRepositoryClient
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


class AnalyzeRequest(BaseModel):
    repo_url: str


class PlainExplainRequest(BaseModel):
    selected_text: str


def build_analyze_response(repo_url, readme_client, repository_client, deepseek_client):
    readme = readme_client.fetch_readme(repo_url)
    repository_context = repository_client.fetch_repository_context(repo_url)
    readme_translation = deepseek_client.translate_readme(readme.content)
    project_overview = deepseek_client.generate_project_overview(repository_context)
    return {
        "repo": f"{readme.owner}/{readme.repo}",
        "default_branch": readme.default_branch,
        "readme_path": readme.path,
        "readme_translation": readme_translation,
        "project_overview": project_overview,
    }


def build_plain_explain_response(selected_text, deepseek_client):
    return {
        "selected_text": selected_text,
        "plain_explanation": deepseek_client.generate_plain_explanation(selected_text),
    }


APP = FastAPI(title="GitHub Walkthrough Assistant")


@APP.post("/api/analyze")
def api_analyze(body: AnalyzeRequest):
    repo_url = body.repo_url.strip()
    if not repo_url:
        return {"error": "Missing repo_url"}
    try:
        deepseek_client = DeepSeekClient.from_env()
        return build_analyze_response(
            repo_url,
            readme_client=GitHubClient.from_env(),
            repository_client=GitHubRepositoryClient.from_env(),
            deepseek_client=deepseek_client,
        )
    except Exception as exc:
        return {"error": str(exc)}


@APP.post("/api/plain-explain")
def api_plain_explain(body: PlainExplainRequest):
    selected_text = body.selected_text.strip()
    if not selected_text:
        return {"error": "Missing selected_text"}
    try:
        deepseek_client = DeepSeekClient.from_env()
        return build_plain_explain_response(selected_text, deepseek_client)
    except Exception as exc:
        return {"error": str(exc)}


APP.mount("/static", StaticFiles(directory=str(FRONTEND_ROOT)), name="frontend-static")
APP.mount("/", StaticFiles(directory=str(FRONTEND_ROOT), html=True), name="static")
