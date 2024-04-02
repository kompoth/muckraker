import json
from fastapi.testclient import TestClient

from muckraker.main import app

# TODO: get rid off explicit header setting. I currently have to do that
# as POST /issue/ recieves a complicated multipart data. Maybe it would
# be better to move image uploading to another endpoint
FORM_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
# TODO: add image processing tests. For now TestClient doesn't send them,
# might be due to a mixed multipart data.

client = TestClient(app)


def test_issue_correct(issue_dict):
    content = "issue=" + json.dumps(issue_dict)
    resp = client.post(
        "/issue/",
        content=content,
        headers=FORM_HEADERS
    )
    assert resp.status_code == 200


def test_issue_thick_body(issue_dict):
    issue_dict["body"] = issue_dict["body"] * 100
    content = "issue=" + json.dumps(issue_dict)
    resp = client.post("/issue/", content=content, headers=FORM_HEADERS)
    assert resp.status_code == 422


def test_issue_thick_heading(issue_dict):
    any_field = list(issue_dict["heading"].keys())[0]
    issue_dict["heading"][any_field] = "a" * 100
    content = "issue=" + json.dumps(issue_dict)
    resp = client.post("/issue/", content=content, headers=FORM_HEADERS)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]
    assert detail["type"] == "string_too_long"
    assert detail["loc"] == ["body", "issue", "heading", any_field]
