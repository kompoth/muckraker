from fastapi.testclient import TestClient

from muckraker.main import app

client = TestClient(app)


def test_correct(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    print(resp.json())
    assert resp.status_code == 200
    issue_id = resp.json()["issue_id"]

    files = {"images": good_image}
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 200

    resp = client.get(f"/issue/{issue_id}")  # Deletes tempdir
    assert resp.status_code == 200


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
    any_field = list(issue_dict["header"].keys())[0]
    issue_dict["header"][any_field] = "a" * 51
    resp = client.post("/issue/", json=issue_dict)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]
    assert detail["type"] == "string_too_long"
    assert detail["loc"] == ["body", "header", any_field]


def test_thick_image(issue_dict, thick_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]

    files = {"images": thick_image}
    # Deletes tempdir on 413
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 413


def test_issue_not_found(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]
    client.get(f"/issue/{issue_id}")  # Deletes tempdir

    resp = client.get(f"/issue/{issue_id}")
    assert resp.status_code == 404

    files = {"images": good_image}
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 404


def test_multiple_images(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]

    # Send 4 images
    files = [("images", (f"{no}.png", good_image)) for no in range(1, 5)]
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 200

    resp = client.get(f"/issue/{issue_id}")  # Deletes tempdir
    assert resp.status_code == 200


def test_too_many_images(issue_dict, good_image):
    resp = client.post("/issue/", json=issue_dict)
    issue_id = resp.json()["issue_id"]

    # Send 5 images
    files = [("images", (f"{no}.png", good_image)) for no in range(1, 6)]
    # Deletes tempdir on 413
    resp = client.patch(f"/issue/{issue_id}", files=files)
    assert resp.status_code == 413
