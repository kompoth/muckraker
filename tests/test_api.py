from fastapi.testclient import TestClient

from muckraker.main import app

client = TestClient(app)


def test_correct(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    assert resp.status_code == 200
    issue_id = resp.json()["issue_id"]

    files = {"image": good_image}
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 200

    resp = client.get(f"/issue/{issue_id}")  # Deletes tempdir
    assert resp.status_code == 200
    with open("file.pdf", "wb") as fd:
        fd.write(resp.content)


def test_thick_body(issue_dict):
    # Won't create tempdir
    issue_dict["body"] = "a" * 6001
    resp = client.post("/issue/", json=issue_dict)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]
    assert detail["type"] == "string_too_long"
    assert detail["loc"] == ["body", "body"]


def test_thick_heading_field(issue_dict):
    # Won't create tempdir
    any_field = list(issue_dict["heading"].keys())[0]
    issue_dict["heading"][any_field] = "a" * 51
    resp = client.post("/issue/", json=issue_dict)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]
    assert detail["type"] == "string_too_long"
    assert detail["loc"] == ["body", "heading", any_field]


def test_thick_image(issue_dict, thick_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]

    files = {"image": thick_image}
    # Deletes tempdir on 413
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 413


def test_issue_not_found(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]  # Deletes tempdir
    client.get(f"/issue/{issue_id}")

    resp = client.get(f"/issue/{issue_id}")
    assert resp.status_code == 404

    files = {"image": good_image}
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 404
