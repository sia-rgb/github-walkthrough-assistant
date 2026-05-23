import base64
import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from src.github_readme import parse_github_url


RELEVANT_FILENAMES = {
    "README.md",
    "README.rst",
    "README.txt",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "setup.py",
    "Dockerfile",
    "docker-compose.yml",
    "environment.yml",
    "Cargo.toml",
    "go.mod",
}


@dataclass(frozen=True)
class RepositoryFile:
    path: str
    content: str


@dataclass(frozen=True)
class RepositoryContext:
    owner: str
    repo: str
    default_branch: str
    owner_type: str
    description: str
    files: list


def select_relevant_paths(paths, limit=12):
    selected = []
    for path in paths:
        filename = path.rsplit("/", 1)[-1]
        if filename in RELEVANT_FILENAMES:
            selected.append(path)
    return selected[:limit]


class GitHubRepositoryClient:
    def __init__(self, transport=urlopen, timeout=30, token=None):
        self.transport = transport
        self.timeout = timeout
        self.token = token

    @classmethod
    def from_env(cls, env_path=".env"):
        token = os.environ.get("GITHUB_TOKEN") or _load_env_value(env_path, "GITHUB_TOKEN")
        return cls(token=token)

    def fetch_repository_context(self, repo_url):
        repo = parse_github_url(repo_url)
        metadata = self._get_json(
            f"https://api.github.com/repos/{quote(repo.owner)}/{quote(repo.name)}"
        )
        default_branch = metadata["default_branch"]
        tree = self._get_json(
            "https://api.github.com/repos/"
            f"{quote(repo.owner)}/{quote(repo.name)}/git/trees/{quote(default_branch)}?recursive=1"
        )
        blob_paths = [
            item["path"]
            for item in tree.get("tree", [])
            if item.get("type") == "blob" and item.get("size", 0) <= 120000
        ]
        files = [
            RepositoryFile(path=path, content=self._fetch_file(repo.owner, repo.name, path, default_branch))
            for path in select_relevant_paths(blob_paths)
        ]
        return RepositoryContext(
            owner=repo.owner,
            repo=repo.name,
            default_branch=default_branch,
            owner_type=metadata.get("owner", {}).get("type", "Unknown"),
            description=metadata.get("description") or "",
            files=files,
        )

    def _fetch_file(self, owner, repo, path, ref):
        data = self._get_json(
            "https://api.github.com/repos/"
            f"{quote(owner)}/{quote(repo)}/contents/{quote(path, safe='/')}?ref={quote(ref)}"
        )
        if data.get("encoding") != "base64":
            raise ValueError(f"Unsupported GitHub content encoding for {path}")
        decoded = base64.b64decode(data.get("content", "").encode("ascii"))
        return decoded.decode("utf-8")

    def _get_json(self, url):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-walkthrough-assistant",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(
            url,
            headers=headers,
        )
        try:
            with self.transport(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 403:
                exc.close()
                raise RuntimeError(
                    "GitHub API rate limit exceeded. Set GITHUB_TOKEN in the environment or .env."
                ) from exc
            raise
        return json.loads(payload)


def _load_env_value(path, target_key):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() == target_key:
                return value.strip().strip('"').strip("'")
    return None
