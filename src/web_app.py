import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from src.deepseek_client import DeepSeekClient
from src.github_readme import GitHubClient
from src.github_repository import GitHubRepositoryClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


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


class WebAppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path in {"/", "/index.html"}:
            self._send_static_file(FRONTEND_ROOT / "index.html", "text/html; charset=utf-8")
            return
        if self.path == "/styles.css":
            self._send_static_file(FRONTEND_ROOT / "styles.css", "text/css; charset=utf-8")
            return
        if self.path == "/app.js":
            self._send_static_file(FRONTEND_ROOT / "app.js", "application/javascript; charset=utf-8")
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        try:
            payload = self._read_json()
            deepseek_client = DeepSeekClient.from_env()
            if self.path == "/api/analyze":
                repo_url = payload.get("repo_url", "").strip()
                if not repo_url:
                    self._send_json({"error": "Missing repo_url"}, status=400)
                    return
                result = build_analyze_response(
                    repo_url,
                    readme_client=GitHubClient.from_env(),
                    repository_client=GitHubRepositoryClient.from_env(),
                    deepseek_client=deepseek_client,
                )
                self._send_json(result)
                return
            if self.path == "/api/plain-explain":
                selected_text = payload.get("selected_text", "").strip()
                if not selected_text:
                    self._send_json({"error": "Missing selected_text"}, status=400)
                    return
                self._send_json(build_plain_explain_response(selected_text, deepseek_client))
                return
            self._send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        if not payload:
            return {}
        return json.loads(payload)

    def _send_static_file(self, path, content_type):
        if not path.exists():
            self._send_json({"error": "Static file not found"}, status=404)
            return
        body = path.read_bytes()
        self._write_response(200, content_type, body)

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._write_response(status, "application/json; charset=utf-8", body)

    def _write_response(self, status, content_type, body):
        reason = {200: "OK", 400: "Bad Request", 404: "Not Found", 500: "Internal Server Error"}.get(
            status,
            "OK",
        )
        header = (
            f"HTTP/1.1 {status} {reason}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("ascii")
        self.request.sendall(header + body)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the GitHub walkthrough web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args(argv)

    server = HTTPServer((args.host, args.port), WebAppHandler)
    print(f"http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
