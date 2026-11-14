# Sharding Specification

## ADDED Requirements

### Requirement: Shard Registration

The Coordinator SHALL support registering storage shards through an API.

#### Scenario: Successful shard registration

- **WHEN** a shard registers with a unique identifier and network address
- **THEN** the Coordinator SHALL add it to the list of registered shards
- **AND** update the consistent hashing ring

#### Scenario: Duplicate shard registration

- **WHEN** a shard with the same identifier is already registered
- **THEN** the Coordinator SHALL reject conflicting registration details

### Requirement: Consistent Hashing

The Coordinator SHALL use consistent hashing to determine which shard is responsible for a record.

The hash function and number of virtual nodes SHALL be documented in an ADR.

#### Scenario: Deterministic shard selection

- **WHEN** the Coordinator calculates the destination for the same table and partition key using an unchanged hashing ring
- **THEN** it SHALL select the same shard

#### Scenario: Multiple registered shards

- **WHEN** two or more shards are registered
- **THEN** the Coordinator SHALL distribute records according to the consistent hashing ring

### Requirement: Sharded Writes

The Coordinator SHALL route write operations to the appropriate shard.

#### Scenario: Create a record

- **WHEN** a client creates a record
- **THEN** the Coordinator SHALL determine the responsible shard using consistent hashing
- **AND** forward the write operation to that shard
- **AND** return the operation result to the client

### Requirement: Sharded Reads

The Coordinator SHALL route read operations to the shard responsible for the requested key.

#### Scenario: Read an existing record

- **WHEN** a client requests an existing record
- **THEN** the Coordinator SHALL identify the responsible shard
- **AND** retrieve the record from that shard
- **AND** return the value to the client

### Requirement: Shard Availability

The Coordinator SHALL report an error when the responsible shard cannot be reached.

#### Scenario: Shard unavailable

- **WHEN** a request is routed to an unavailable shard
- **THEN** the Coordinator SHALL return an appropriate service error
- **AND** SHALL NOT report the operation as successful

### Requirement: Dynamic Hash Ring Updates

The Coordinator SHALL support updating the hashing ring when a new shard registers.

#### Scenario: New shard joins

- **WHEN** a new shard registers
- **THEN** the Coordinator SHALL update the hashing ring
- **AND** use the updated ring for subsequent routing decisions

Full migration of existing records between shards is outside the scope of Milestone 2 and is planned for Milestone 5. Until migration is implemented, adding shards after records have been written may make some existing records temporarily inaccessible. The initial Milestone 2 deployment SHALL register its shards before accepting record operations.