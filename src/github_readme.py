import base64
import json
from dataclasses import dataclass
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class RepoRef:
    owner: str
    name: str


@dataclass(frozen=True)
class ReadmeResult:
    owner: str
    repo: str
    default_branch: str
    path: str
    content: str


def parse_github_url(url):
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise ValueError("Expected a GitHub repository URL")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("Expected URL path format /owner/repo")

    repo_name = parts[1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    return RepoRef(owner=parts[0], name=repo_name)


class GitHubClient:
    def __init__(self, transport=urlopen, timeout=30):
        self.transport = transport
        self.timeout = timeout

    def fetch_readme(self, repo_url):
        repo = parse_github_url(repo_url)
        default_branch = self.get_default_branch(repo)
        readme = self._get_json(
            "https://api.github.com/repos/"
            f"{quote(repo.owner)}/{quote(repo.name)}/readme?ref={quote(default_branch)}"
        )
        content = self._decode_readme_content(readme)
        return ReadmeResult(
            owner=repo.owner,
            repo=repo.name,
            default_branch=default_branch,
            path=readme.get("path", "README.md"),
            content=content,
        )

    def get_default_branch(self, repo):
        metadata = self._get_json(
            f"https://api.github.com/repos/{quote(repo.owner)}/{quote(repo.name)}"
        )
        default_branch = metadata.get("default_branch")
        if not default_branch:
            raise ValueError("GitHub repository metadata did not include default_branch")
        return default_branch

    def _get_json(self, url):
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "github-walkthrough-assistant",
            },
        )
        with self.transport(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    def _decode_readme_content(self, readme):
        if readme.get("encoding") != "base64":
            raise ValueError("GitHub README response was not base64 encoded")
        raw_content = readme.get("content", "")
        decoded = base64.b64decode(raw_content.encode("ascii"))
        return decoded.decode("utf-8")
