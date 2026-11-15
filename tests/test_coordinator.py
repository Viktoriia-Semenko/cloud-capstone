import pytest
import httpx
from fastapi.testclient import TestClient

from coordinator.main import app, tables, records, shards, hash_ring


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    tables.clear()
    records.clear()
    shards.clear()
    hash_ring.clear()

    yield

    tables.clear()
    records.clear()
    shards.clear()
    hash_ring.clear()


def test_register_table():
    response = client.post(
        "/tables",
        json={
            "name": "students",
            "partition_key": "student_id",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "name": "students",
        "partition_key": "student_id",
    }


def test_duplicate_table():
    table = {
        "name": "students",
        "partition_key": "student_id",
    }

    client.post("/tables", json=table)

    response = client.post("/tables", json=table)

    assert response.status_code == 409
    assert response.json()["detail"] == "Table already exists"


def test_create_and_read_record():
    client.post(
        "/tables",
        json={
            "name": "students",
            "partition_key": "student_id",
        },
    )

    record = {
        "key": "101",
        "value": {
            "name": "Anna",
            "subject": "Computer Science",
        },
    }

    create_response = client.post(
        "/tables/students/records",
        json=record,
    )

    assert create_response.status_code == 201

    read_response = client.get(
        "/tables/students/records/101"
    )

    assert read_response.status_code == 200
    assert read_response.json() == record


def test_record_exists():
    client.post(
        "/tables",
        json={"name": "students", "partition_key": "student_id"},
    )

    client.post(
        "/tables/students/records",
        json={"key": "101", "value": {"name": "Anna"}},
    )

    existing = client.get(
        "/tables/students/records/101/exists"
    )
    assert existing.status_code == 200
    assert existing.json() == {"exists": True}

    missing = client.get(
        "/tables/students/records/999/exists"
    )
    assert missing.status_code == 200
    assert missing.json() == {"exists": False}


def test_update_record():
    client.post(
        "/tables",
        json={"name": "students", "partition_key": "student_id"},
    )

    client.post(
        "/tables/students/records",
        json={"key": "101", "value": {"name": "Anna"}},
    )

    response = client.put(
        "/tables/students/records/101",
        json={"value": {"name": "Maria"}},
    )

    assert response.status_code == 200
    assert response.json()["value"]["name"] == "Maria"

    read_response = client.get(
        "/tables/students/records/101"
    )
    assert read_response.json()["value"]["name"] == "Maria"


def test_delete_record():
    client.post(
        "/tables",
        json={"name": "students", "partition_key": "student_id"},
    )

    client.post(
        "/tables/students/records",
        json={"key": "101", "value": {"name": "Anna"}},
    )

    response = client.delete(
        "/tables/students/records/101"
    )
    assert response.status_code == 204

    read_response = client.get(
        "/tables/students/records/101"
    )
    assert read_response.status_code == 404

    exists_response = client.get(
        "/tables/students/records/101/exists"
    )
    assert exists_response.json() == {"exists": False}


def test_create_record_errors():
    record = {"key": "101", "value": {"name": "Anna"}}

    missing_table = client.post(
        "/tables/students/records",
        json=record,
    )
    assert missing_table.status_code == 404

    client.post(
        "/tables",
        json={"name": "students", "partition_key": "student_id"},
    )

    client.post(
        "/tables/students/records",
        json=record,
    )

    duplicate = client.post(
        "/tables/students/records",
        json=record,
    )
    assert duplicate.status_code == 409

    invalid = client.post(
        "/tables/students/records",
        json={"key": "", "value": {"name": "Anna"}},
    )
    assert invalid.status_code == 422


def test_shard_registration_updates_hash_ring():
    shard_1 = {
        "shard_id": "shard-1",
        "url": "http://127.0.0.1:8001",
    }

    shard_2 = {
        "shard_id": "shard-2",
        "url": "http://127.0.0.1:8002",
    }

    response_1 = client.post(
        "/shards/register",
        json=shard_1,
    )

    assert response_1.status_code == 201
    assert hash_ring.position_count == 100

    response_2 = client.post(
        "/shards/register",
        json=shard_2,
    )

    assert response_2.status_code == 201
    assert hash_ring.position_count == 200

    assert len(shards) == 2

    selected = hash_ring.get_shard("students", "101")

    assert selected in {"shard-1", "shard-2"}

    duplicate = client.post(
        "/shards/register",
        json=shard_1,
    )

    assert duplicate.status_code == 200
    assert hash_ring.position_count == 200

    conflict = client.post(
        "/shards/register",
        json={
            "shard_id": "shard-1",
            "url": "http://127.0.0.1:9999",
        },
    )

    assert conflict.status_code == 409
    assert hash_ring.position_count == 200


def test_create_record_routes_to_correct_shard(monkeypatch):
    client.post(
        "/tables",
        json={
            "name": "students",
            "partition_key": "student_id",
        },
    )

    for shard_id, port in [
        ("shard-1", 8001),
        ("shard-2", 8002),
    ]:
        client.post(
            "/shards/register",
            json={
                "shard_id": shard_id,
                "url": f"http://127.0.0.1:{port}",
            },
        )

    record = {
        "key": "101",
        "value": {"name": "Anna"},
    }

    expected_shard = hash_ring.get_shard(
        "students", "101"
    )

    captured = {}

    async def fake_post(self, url, **kwargs):
        captured["url"] = url
        captured["record"] = kwargs["json"]

        return httpx.Response(
            201,
            json=kwargs["json"],
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(
        httpx.AsyncClient, "post", fake_post
    )

    response = client.post(
        "/tables/students/records",
        json=record,
    )

    assert response.status_code == 201
    assert response.json() == record

    assert captured["url"] == (
        f"{shards[expected_shard]}"
        "/internal/tables/students/records"
    )

    assert captured["record"] == record

    assert records["students"] == {}


def test_read_record_routes_to_correct_shard(monkeypatch):
    client.post(
        "/tables",
        json={
            "name": "students",
            "partition_key": "student_id",
        },
    )

    for shard_id, port in [
        ("shard-1", 8001),
        ("shard-2", 8002),
    ]:
        client.post(
            "/shards/register",
            json={
                "shard_id": shard_id,
                "url": f"http://127.0.0.1:{port}",
            },
        )

    record = {
        "key": "202",
        "value": {
            "name": "Ivan",
            "subject": "Economics",
        },
    }

    expected_shard = hash_ring.get_shard(
        "students", "202"
    )

    captured = {}

    async def fake_get(self, url, **kwargs):
        captured["url"] = url

        return httpx.Response(
            200,
            json=record,
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(
        httpx.AsyncClient, "get", fake_get
    )

    response = client.get(
        "/tables/students/records/202"
    )

    assert response.status_code == 200
    assert response.json() == record

    assert captured["url"] == (
        f"{shards[expected_shard]}"
        "/internal/tables/students/records/202"
    )

    assert records["students"] == {}
