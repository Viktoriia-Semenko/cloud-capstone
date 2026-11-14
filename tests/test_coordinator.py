import pytest
from fastapi.testclient import TestClient

from coordinator.main import app, tables, records


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    tables.clear()
    records.clear()

    yield

    tables.clear()
    records.clear()


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
