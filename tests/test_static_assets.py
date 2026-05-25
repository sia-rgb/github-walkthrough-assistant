from pathlib import Path

from fastapi.testclient import TestClient

from src.app import APP


def read_frontend_app_js():
    return (
        Path(__file__).resolve().parent.parent / "frontend" / "app.js"
    ).read_text(encoding="utf-8")


def test_static_assets_are_served_under_static_prefix():
    client = TestClient(APP)

    css_response = client.get("/static/styles.css")
    js_response = client.get("/static/app.js")

    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    assert js_response.status_code == 200
    assert "javascript" in js_response.headers["content-type"]


def test_homepage_references_static_assets():
    client = TestClient(APP)

    response = client.get("/")

    assert response.status_code == 200
    assert 'href="static/styles.css"' in response.text
    assert 'src="static/app.js"' in response.text


def test_frontend_api_requests_use_relative_paths():
    app_js = read_frontend_app_js()

    assert '"api/analyze"' in app_js
    assert 'postJson("api/plain-explain"' in app_js
    assert 'postJson("/api/' not in app_js
    assert '"/api/' not in app_js


def test_analyze_payload_uses_trimmed_repo_url():
    app_js = read_frontend_app_js()

    assert "var rawRepoUrl = repoUrlInput.value;" in app_js
    assert "var repoUrl = rawRepoUrl.trim();" in app_js
    assert "var analyzePayload = { repo_url: repoUrl };" in app_js
    assert "{ repo_url: repoUrlInput.value }" not in app_js


def test_frontend_logs_request_and_full_error_details():
    app_js = read_frontend_app_js()

    assert "function buildHttpErrorMessage(response, data)" in app_js
    assert "data.detail" in app_js
    assert "response.status" in app_js
    assert 'console.info("[postJson] request"' in app_js
    assert 'console.info("[postJson] response"' in app_js
    assert 'console.info("[analyze] input"' in app_js
