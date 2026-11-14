# Key-Value API Specification

## ADDED Requirements

### Requirement: Table Registration

The system SHALL support registering a table definition with a unique table name and a partition key.

#### Scenario: Successful table registration

- **WHEN** a client registers a table with a valid unique name
- **THEN** the Coordinator SHALL register the table
- **AND** the table SHALL become available for record operations

#### Scenario: Duplicate table registration

- **WHEN** a client attempts to register a table that already exists
- **THEN** the system SHALL return an appropriate error

### Requirement: Create Record

The system SHALL support creating key-value records in a registered table.

#### Scenario: Successful record creation

- **WHEN** a client submits a valid key and value
- **THEN** the system SHALL store the record
- **AND** the record SHALL be available for subsequent reads

### Requirement: Read Record

The system SHALL support retrieving a stored value by its key.

#### Scenario: Existing record

- **WHEN** a client requests an existing key
- **THEN** the system SHALL return the corresponding value

#### Scenario: Missing record

- **WHEN** a client requests a key that does not exist
- **THEN** the system SHALL return a not-found response

### Requirement: Update Record

The system SHALL support replacing the value of an existing record.

#### Scenario: Successful update

- **WHEN** a client updates an existing record
- **THEN** the system SHALL replace its previous value
- **AND** subsequent reads SHALL return the updated value

### Requirement: Delete Record

The system SHALL support deleting a record by its key.

#### Scenario: Successful deletion

- **WHEN** a client deletes an existing record
- **THEN** the system SHALL remove the record
- **AND** subsequent reads SHALL return a not-found response

### Requirement: Check Record Existence

The system SHALL support checking whether a record exists.

#### Scenario: Existence check

- **WHEN** a client checks an existing key
- **THEN** the system SHALL indicate that the record exists

- **WHEN** a client checks a missing key
- **THEN** the system SHALL indicate that the record does not exist

### Requirement: Single-Node Operation

The Coordinator SHALL initially support all record operations without downstream shards.

#### Scenario: Single-node operation

- **WHEN** the Coordinator runs in single-node mode
- **THEN** CREATE, READ, UPDATE, DELETE, and EXISTS operations SHALL work without additional shard services