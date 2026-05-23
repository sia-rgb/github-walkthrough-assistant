import base64
import json
import unittest

from src.github_readme import GitHubClient, parse_github_url


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
            return FakeResponse(json.dumps({"default_branch": "master"}))
        if request.full_url == "https://api.github.com/repos/karpathy/nanochat/readme?ref=master":
            content = base64.b64encode("# NanoChat\n".encode("utf-8")).decode("ascii")
            return FakeResponse(json.dumps({"encoding": "base64", "content": content, "path": "README.md"}))
        raise AssertionError(f"Unexpected URL: {request.full_url}")


class RecordingTransport:
    def __init__(self):
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append(request)
        return FakeResponse(json.dumps({"default_branch": "main"}))


class GitHubReadmeTests(unittest.TestCase):
    def test_parse_github_url_extracts_owner_and_repo(self):
        repo = parse_github_url("https://github.com/karpathy/nanochat")

        self.assertEqual(repo.owner, "karpathy")
        self.assertEqual(repo.name, "nanochat")

    def test_fetch_readme_uses_repository_default_branch(self):
        transport = FakeTransport()
        client = GitHubClient(transport=transport)

        result = client.fetch_readme("https://github.com/karpathy/nanochat")

        self.assertEqual(result.owner, "karpathy")
        self.assertEqual(result.repo, "nanochat")
        self.assertEqual(result.default_branch, "master")
        self.assertEqual(result.path, "README.md")
        self.assertEqual(result.content, "# NanoChat\n")
        self.assertIn("https://api.github.com/repos/karpathy/nanochat/readme?ref=master", transport.urls)

    def test_token_is_sent_as_authorization_header(self):
        transport = RecordingTransport()
        client = GitHubClient(transport=transport, token="secret-token")

        client._get_json("https://api.github.com/repos/example/project")

        self.assertEqual(transport.requests[0].headers["Authorization"], "Bearer secret-token")


if __name__ == "__main__":
    unittest.main()
