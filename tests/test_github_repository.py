import base64
import json
import unittest
from urllib.error import HTTPError

from src.github_repository import GitHubRepositoryClient, select_relevant_paths


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload


class FakeTransport:
    def __init__(self):
        self.urls = []

    def __call__(self, request, timeout):
        self.urls.append(request.full_url)
        if request.full_url == "https://api.github.com/repos/karpathy/nanochat":
            return FakeResponse(
                json.dumps(
                    {
                        "full_name": "karpathy/nanochat",
                        "description": "The best ChatGPT that $100 can buy.",
                        "default_branch": "master",
                        "owner": {"type": "User"},
                    }
                )
            )
        if request.full_url == "https://api.github.com/repos/karpathy/nanochat/git/trees/master?recursive=1":
            return FakeResponse(
                json.dumps(
                    {
                        "tree": [
                            {"path": "README.md", "type": "blob", "size": 100},
                            {"path": "requirements.txt", "type": "blob", "size": 20},
                            {"path": "dev/nanochat.png", "type": "blob", "size": 4000},
                            {"path": "notes.txt", "type": "blob", "size": 10},
                        ]
                    }
                )
            )
        if request.full_url == "https://api.github.com/repos/karpathy/nanochat/contents/README.md?ref=master":
            content = base64.b64encode("# NanoChat\n".encode("utf-8")).decode("ascii")
            return FakeResponse(json.dumps({"encoding": "base64", "content": content}))
        if request.full_url == "https://api.github.com/repos/karpathy/nanochat/contents/requirements.txt?ref=master":
            content = base64.b64encode("torch\n".encode("utf-8")).decode("ascii")
            return FakeResponse(json.dumps({"encoding": "base64", "content": content}))
        raise AssertionError(f"Unexpected URL: {request.full_url}")


class RecordingTransport:
    def __init__(self):
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append(request)
        return FakeResponse(json.dumps({"default_branch": "main"}))


class RateLimitedTransport:
    def __call__(self, request, timeout):
        raise HTTPError(
            request.full_url,
            403,
            "rate limit exceeded",
            hdrs=None,
            fp=None,
        )


class GitHubRepositoryTests(unittest.TestCase):
    def test_select_relevant_paths_keeps_project_context_files(self):
        paths = select_relevant_paths(
            [
                "README.md",
                "requirements.txt",
                "dev/nanochat.png",
                "notes.txt",
                "pyproject.toml",
            ]
        )

        self.assertEqual(paths, ["README.md", "requirements.txt", "pyproject.toml"])

    def test_fetch_repository_context_reads_metadata_tree_and_key_files(self):
        transport = FakeTransport()
        client = GitHubRepositoryClient(transport=transport)

        context = client.fetch_repository_context("https://github.com/karpathy/nanochat")

        self.assertEqual(context.owner, "karpathy")
        self.assertEqual(context.repo, "nanochat")
        self.assertEqual(context.default_branch, "master")
        self.assertEqual(context.owner_type, "User")
        self.assertEqual(context.description, "The best ChatGPT that $100 can buy.")
        self.assertEqual([item.path for item in context.files], ["README.md", "requirements.txt"])
        self.assertEqual(context.files[0].content, "# NanoChat\n")
        self.assertEqual(context.files[1].content, "torch\n")

    def test_token_is_sent_as_authorization_header(self):
        transport = RecordingTransport()
        client = GitHubRepositoryClient(transport=transport, token="secret-token")

        client._get_json("https://api.github.com/repos/example/project")

        self.assertEqual(transport.requests[0].headers["Authorization"], "Bearer secret-token")

    def test_rate_limit_error_mentions_github_token(self):
        client = GitHubRepositoryClient(transport=RateLimitedTransport())

        with self.assertRaisesRegex(RuntimeError, "GITHUB_TOKEN"):
            client._get_json("https://api.github.com/repos/example/project")


if __name__ == "__main__":
    unittest.main()
