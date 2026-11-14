
from typing import Any

from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Cloud Capstone Coordinator",
    description="Coordinator for the sharded key-value store",
    version="1.0.0",
)

tables = {}
records = {}


class TableDefinition(BaseModel):
    name: str = Field(min_length=1)
    partition_key: str = Field(min_length=1)

    @field_validator("name", "partition_key")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be blank")
        return value


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
        "service": "coordinator",
    }


@app.post("/tables", status_code=status.HTTP_201_CREATED)
def register_table(table: TableDefinition):
    if table.name in tables:
        raise HTTPException(
            status_code=409,
            detail="Table already exists",
        )

    tables[table.name] = table.model_dump()
    records[table.name] = {}

    return tables[table.name]


@app.post(
    "/tables/{table}/records",
    status_code=status.HTTP_201_CREATED,
)
def create_record(table: str, record: RecordCreate):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if record.key in records[table]:
        raise HTTPException(
            status_code=409,
            detail="Record already exists",
        )

    records[table][record.key] = record.value

    return {
        "key": record.key,
        "value": record.value,
    }


@app.get("/tables/{table}/records/{key}")
def read_record(table: str, key: str):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if key not in records[table]:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    return {
        "key": key,
        "value": records[table][key],
    }


@app.get("/tables/{table}/records/{key}/exists")
def record_exists(table: str, key: str):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    return {
        "exists": key in records[table]
    }


@app.put("/tables/{table}/records/{key}")
def update_record(table: str, key: str, update: ValueUpdate):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if key not in records[table]:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    records[table][key] = update.value

    return {
        "key": key,
        "value": records[table][key],
    }


@app.delete(
    "/tables/{table}/records/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_record(table: str, key: str):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if key not in records[table]:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    del records[table][key]

    return Response(status_code=status.HTTP_204_NO_CONTENT)