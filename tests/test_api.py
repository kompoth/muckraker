import copy
from fastapi.testclient import TestClient

from muckraker.main import app


client = TestClient(app)


def test_issue_thick_body(issue):
    issue["body"] = issue["body"] * 100
    resp = client.post("/issue/", json=issue)
    assert resp.status_code == 422


def test_issue_thick_heading(issue):
    for field in issue["config"]["heading"]:
        print(field)
        new_issue = copy.copy(issue)
        new_issue["config"]["heading"][field] = "a" * 1000
        resp = client.post("/issue/", json=new_issue)
        assert resp.status_code == 422


def test_issue_correct(issue):
    resp = client.post("/issue/", json=issue)
    assert resp.status_code == 200
