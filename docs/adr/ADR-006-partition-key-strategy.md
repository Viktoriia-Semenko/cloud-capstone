# ADR-006: Partition Key Strategy

**Date:** 2026-11-14  
**Milestone:** 2 - Sharding the Load

## Context

Milestone 2 requires a key-value store that distributes records across multiple storage shards.

The Coordinator needs a deterministic way to identify the shard responsible for each record.

The partition key strategy affects data distribution, lookup efficiency, and the risk of creating hot partitions.

## Decision

I will use a **single string-based partition key**, unique within each table.

Each registered table will define the name of its partition key.

For Milestone 2, records will be accessed through this key, without an additional sort key.

The Coordinator will combine the table name and partition key using an unambiguous encoding before calculating the SHA-256 hash.

The resulting hash will be used with the consistent hashing ring defined in ADR-005.

### Key Rules

1. Every record must have a non-empty partition key.
2. Partition keys must be unique within a table.
3. Different tables may contain identical partition key values.
4. The same table and partition key must always produce the same hash input.
5. CREATE must reject a record if its partition key already exists in the table.
6. UPDATE must modify an existing record without changing its partition key.
7. READ, DELETE, and EXISTS must locate records using the same routing strategy.

## Alternatives Considered

### Compound Primary Key

A compound key combines a partition key and a sort key.

This supports storing multiple related records under the same partition key and querying them in a defined order.

However, it introduces additional complexity that is not required for Milestone 2.

### Random Partition Assignment

Records could be assigned to randomly selected shards.

However, the Coordinator would need additional metadata to remember where each record was stored.

### Low-Cardinality Partition Keys

Attributes such as country or status could be used as partition keys.

However, they may create uneven data distribution and hot partitions when many records share the same value.

## Consequences

**Positive:**

- Simple implementation and API.
- Efficient key-based lookups.
- Deterministic shard selection.
- Compatible with consistent hashing.
- Easy to demonstrate and test.

**Negative:**

- No sort-key-based queries.
- No efficient range queries.
- Poorly distributed or frequently accessed keys can still create hot partitions.
- Changing the partition key strategy later may require data migration.

## Validation

I will verify that:

1. Records can be created with valid partition keys.
2. Duplicate keys in the same table are rejected.
3. The same key can exist in different tables.
4. Missing or empty partition keys are rejected.
5. The Coordinator consistently selects the correct shard.
6. Records can be retrieved and deleted using their partition keys.
7. Test records are distributed across both initial shards.