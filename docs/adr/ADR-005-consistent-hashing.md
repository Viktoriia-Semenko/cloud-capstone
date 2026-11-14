# ADR-005: Consistent Hashing and Virtual Nodes

**Date:** 2026-11-14  
**Milestone:** 2 - Sharding the Load

## Context

Milestone 2 requires distributing key-value records across multiple storage shards.

The Coordinator must determine which shard is responsible for each record.

The system should also support adding new shards without requiring every key to be reassigned.

## Decision

I will implement **consistent hashing using SHA-256 and 100 virtual nodes per physical shard**.

The Coordinator will:

1. Calculate SHA-256 hashes for shard virtual nodes.
2. Arrange the virtual nodes on a logical hash ring.
3. Calculate a hash for each record using its table name and partition key.
4. Find the first virtual node clockwise from the record's hash position.
5. Route the request to the physical shard associated with that virtual node.

A deterministic encoding of the table name and partition key will be used to prevent ambiguous hash inputs.

All read and write operations will use the same routing algorithm.

The initial deployment will contain two shards, registered before accepting record operations.

## Alternatives considered

### Modulo Hashing

A simple alternative is:

`shard = hash(key) % number_of_shards`

This approach is easy to implement.

However, changing the number of shards can cause a large number of keys to be reassigned.

### Consistent Hashing Without Virtual Nodes

Each physical shard could occupy one position on the hash ring.

This is simpler but can result in uneven distribution, especially when only a few shards exist.

## Consequences

**Positive:**

- Deterministic mapping between records and shards.
- Supports multiple storage shards.
- Virtual nodes help distribute records more evenly.
- Adding a new shard generally affects only part of the keyspace.
- Can be extended for shard rebalancing in Milestone 5.

**Negative:**

- More complex than modulo hashing.
- The Coordinator must maintain the hash ring.
- Virtual nodes require additional metadata and processing.
- Adding shards changes ownership of some existing keys.

## Limitations

Milestone 2 will implement hash ring updates but not automatic data migration.

Shards will register before record operations begin.

Adding a shard after data has been written may make some existing records temporarily inaccessible because their ownership changes.

Automatic data migration and rebalancing will be implemented in Milestone 5.

## Validation

I will verify that:

1. Two shards can register with the Coordinator.
2. Each shard has 100 virtual nodes.
3. The same table and partition key always map to the same shard while the ring remains unchanged.
4. Different keys are distributed across both shards.
5. Read requests reach the shard responsible for the corresponding record.
6. Adding a shard updates the hash ring.
7. The hash ring produces deterministic results across repeated executions.