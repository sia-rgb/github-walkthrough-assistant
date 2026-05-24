from fastapi.testclient import TestClient

from src.app import APP


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
    assert 'href="/static/styles.css"' in response.text
    assert 'src="/static/app.js"' in response.text
