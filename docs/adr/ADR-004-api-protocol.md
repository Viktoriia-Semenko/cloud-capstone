# ADR-004: API Protocol and Format

**Date:** 2026-11-14  
**Milestone:** 2 - Sharding the Load

## Context

Milestone 2 requires an API for registering tables and performing CRUD operations on records in a distributed key-value store.

The system will include a Coordinator service and multiple storage shards.

We need an API protocol and data format that are simple to implement, test, document, and extend in future milestones.

## Decision

I will use **REST over HTTP with JSON** as the API protocol and data format.

The application will be implemented in Python using FastAPI.

The Coordinator will expose the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/tables` | Register a table |
| POST | `/tables/{table}/records` | Create a record |
| GET | `/tables/{table}/records/{key}` | Read a record |
| PUT | `/tables/{table}/records/{key}` | Update a record |
| DELETE | `/tables/{table}/records/{key}` | Delete a record |
| GET | `/tables/{table}/records/{key}/exists` | Check record existence |
| POST | `/shards/register` | Register a storage shard |

Requests and responses will use JSON.

The API will be documented using OpenAPI.

The Coordinator will initially support single-node operations. Later, it will forward requests to the appropriate storage shard.

## Alternatives сonsidered

### GraphQL

GraphQL allows clients to request specific fields and combine related data.

However, this project uses simple key-value operations, so GraphQL would introduce unnecessary complexity.

### gRPC

gRPC provides efficient communication using Protocol Buffers and supports strongly typed service definitions.

However, it requires additional tooling and is less convenient for manual testing with standard HTTP clients.

## Consequences

**Positive:**

- Simple API implementation using Python and FastAPI.
- JSON is human-readable and easy to debug.
- REST endpoints can be tested using curl.
- FastAPI supports automatic OpenAPI documentation.
- Easy integration with automated tests and benchmarking tools.

**Negative:**

- JSON may introduce more network overhead than binary formats.
- REST does not provide the same strongly typed contract as gRPC.
- Additional integration work may be required to connect YCSB to the custom API.

## Validation

I will verify that:

1. The Coordinator starts successfully.
2. API documentation is available through OpenAPI.
3. Table registration works.
4. CREATE, READ, UPDATE, DELETE, and EXISTS operations return the expected results.
5. Invalid requests return appropriate HTTP errors.
6. API requests can be routed to downstream shards.
7. The API can be exercised by automated tests.