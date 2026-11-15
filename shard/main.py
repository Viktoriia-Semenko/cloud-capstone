import os
import httpx
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator


SHARD_ID = os.getenv("SHARD_ID", "shard-1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    coordinator_url = os.getenv(
        "COORDINATOR_URL",
        "http://127.0.0.1:8000",
    ).rstrip("/")

    shard_url = os.environ["SHARD_URL"].rstrip("/")

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            f"{coordinator_url}/shards/register",
            json={
                "shard_id": SHARD_ID,
                "url": shard_url,
            },
        )
        response.raise_for_status()

    print(f"Registered {SHARD_ID} with Coordinator")

    yield


app = FastAPI(
    title="Cloud Capstone Shard",
    description="Storage shard for the distributed key-value store",
    version="1.0.0",
    lifespan=lifespan,
)


records: dict[str, dict[str, dict[str, Any]]] = {}


class RecordCreate(BaseModel):
    key: str = Field(min_length=1)
    value: dict[str, Any]

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Key must not be blank")
        return value


class ValueUpdate(BaseModel):
    value: dict[str, Any]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "shard",
        "shard_id": SHARD_ID,
    }


@app.post(
    "/internal/tables/{table}/records",
    status_code=status.HTTP_201_CREATED,
)
def create_record(table: str, record: RecordCreate):
    table_records = records.setdefault(table, {})

    if record.key in table_records:
        raise HTTPException(
            status_code=409,
            detail="Record already exists",
        )

    table_records[record.key] = record.value

    return {
        "key": record.key,
        "value": record.value,
    }


@app.get("/internal/tables/{table}/records/{key}")
def read_record(table: str, key: str):
    table_records = records.get(table, {})

    if key not in table_records:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    return {
        "key": key,
        "value": table_records[key],
    }


@app.get("/internal/tables/{table}/records/{key}/exists")
def record_exists(table: str, key: str):
    table_records = records.get(table, {})

    return {
        "exists": key in table_records,
    }


@app.put("/internal/tables/{table}/records/{key}")
def update_record(table: str, key: str, update: ValueUpdate):
    table_records = records.get(table, {})

    if key not in table_records:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    table_records[key] = update.value

    return {
        "key": key,
        "value": table_records[key],
    }


@app.delete(
    "/internal/tables/{table}/records/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_record(table: str, key: str):
    table_records = records.get(table, {})

    if key not in table_records:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    del table_records[key]