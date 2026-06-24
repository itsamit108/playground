"""Integration tests for the core note-taking API (preserved behavior)."""

from __future__ import annotations

from tests.conftest import register_and_login


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "overtake"


def test_register_login_me(client):
    token = register_and_login(client, "bob")
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "bob"


def test_duplicate_registration_conflicts(client):
    register_and_login(client, "carol")
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "password123"},
    )
    assert resp.status_code == 409


def test_note_crud_and_search(client):
    token = register_and_login(client, "dave")
    h = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/notes",
        json={"title": "Meeting", "content": "Discuss roadmap", "is_pinned": True},
        headers=h,
    )
    assert created.status_code == 201
    note_id = created.json()["id"]

    listed = client.get("/api/v1/notes?search=roadmap", headers=h)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = client.put(
        f"/api/v1/notes/{note_id}", json={"title": "Meeting v2"}, headers=h
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Meeting v2"

    deleted = client.delete(f"/api/v1/notes/{note_id}", headers=h)
    assert deleted.status_code == 204


def test_multi_user_isolation(client):
    token_a = register_and_login(client, "ua")
    token_b = register_and_login(client, "ub")
    ha = {"Authorization": f"Bearer {token_a}"}
    hb = {"Authorization": f"Bearer {token_b}"}

    created = client.post(
        "/api/v1/notes", json={"title": "Secret", "content": "mine"}, headers=ha
    )
    note_id = created.json()["id"]

    # User B cannot see or fetch user A's note.
    assert client.get("/api/v1/notes", headers=hb).json()["total"] == 0
    assert client.get(f"/api/v1/notes/{note_id}", headers=hb).status_code == 404


def test_attachment_upload_download_delete(client):
    token = register_and_login(client, "eve")
    h = {"Authorization": f"Bearer {token}"}
    note_id = client.post(
        "/api/v1/notes", json={"title": "Has files", "content": "x"}, headers=h
    ).json()["id"]

    up = client.post(
        f"/api/v1/notes/{note_id}/attachments",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        headers=h,
    )
    assert up.status_code == 201
    att_id = up.json()["id"]

    dl = client.get(f"/api/v1/attachments/{att_id}/download", headers=h)
    assert dl.status_code == 200
    assert dl.content == b"hello world"

    rm = client.delete(f"/api/v1/attachments/{att_id}", headers=h)
    assert rm.status_code == 204


def test_unauthenticated_rejected(client):
    assert client.get("/api/v1/notes").status_code == 401
