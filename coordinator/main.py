import httpx
from typing import Any

from fastapi import FastAPI, HTTPException, status, Response
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator
from coordinator.hash_ring import ConsistentHashRing

app = FastAPI(
    title="Cloud Capstone Coordinator",
    description="Coordinator for the sharded key-value store",
    version="1.0.0",
)

tables = {}
records = {}
shards: dict[str, str] = {}
hash_ring = ConsistentHashRing(virtual_nodes=100)


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


class ShardRegistration(BaseModel):
    shard_id: str = Field(min_length=1)
    url: AnyHttpUrl

    @field_validator("shard_id")
    @classmethod
    def validate_shard_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Shard ID must not be blank")
        return value


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
async def create_record(table: str, record: RecordCreate):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if shards:
        shard_id = hash_ring.get_shard(table, record.key)
        shard_url = shards[shard_id]

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                shard_response = await client.post(
                    f"{shard_url}/internal/tables/{table}/records",
                    json=record.model_dump(),
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Shard unavailable",
            ) from None

        if shard_response.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail="Record already exists",
            )

        if shard_response.status_code != 201:
            raise HTTPException(
                status_code=502,
                detail="Unexpected response from shard",
            )

        return shard_response.json()

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
async def read_record(table: str, key: str):
    if table not in tables:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if shards:
        shard_id = hash_ring.get_shard(table, key)
        shard_url = shards[shard_id]

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                shard_response = await client.get(
                    f"{shard_url}/internal/tables/{table}/records/{key}"
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Shard unavailable",
            ) from None

        if shard_response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Record not found",
            )

        if shard_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Unexpected response from shard",
            )

        return shard_response.json()

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


@app.post(
    "/shards/register",
    status_code=status.HTTP_201_CREATED,
)
def register_shard(shard: ShardRegistration, response: Response):
    shard_url = str(shard.url).rstrip("/")

    existing_url = shards.get(shard.shard_id)

    if existing_url is not None:
        if existing_url != shard_url:
            raise HTTPException(
                status_code=409,
                detail="Shard ID already registered with another URL",
            )

        response.status_code = status.HTTP_200_OK
        return {
            "shard_id": shard.shard_id,
            "url": shard_url,
        }

    shards[shard.shard_id] = shard_url

    hash_ring.add_shard(shard.shard_id)

    return {
        "shard_id": shard.shard_id,
        "url": shard_url,
    }