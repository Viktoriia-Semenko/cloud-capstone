## ADDED Requirements

### Requirement: YCSB Integration

The system SHALL support benchmarking with YCSB 0.17.0
through a custom Java database binding for the Coordinator
REST API.

#### Scenario: Benchmark client communication
- WHEN YCSB performs a supported database operation
- THEN the binding SHALL send an HTTP request to the
  Coordinator
- AND translate the HTTP response into a YCSB status.

### Requirement: Operation Mapping

The binding SHALL support the following operations:
- INSERT via POST /tables/{table}/records
- READ via GET /tables/{table}/records/{key}
- UPDATE via PUT /tables/{table}/records/{key}
- DELETE via DELETE /tables/{table}/records/{key}

The binding SHALL NOT claim support for SCAN because
the Coordinator does not provide a range-scan API.

#### Scenario: Record retrieval
- WHEN YCSB requests an existing record
- THEN the binding SHALL return the record fields
  and report a successful operation.

#### Scenario: Missing record
- WHEN the Coordinator returns HTTP 404
- THEN the binding SHALL report the record as not found.

### Requirement: Benchmark Workloads

The system SHALL support YCSB Workload A and Workload B.

- Workload A: 50% READ, 50% UPDATE.
- Workload B: 95% READ, 5% UPDATE.

#### Scenario: Benchmark execution
- WHEN a workload is executed
- THEN the required benchmark records SHALL be loaded
  into a dedicated table before measurement
- AND the test configuration SHALL be recorded.

### Requirement: Reproducible Baseline

The benchmark SHALL record:
- YCSB version and workload
- Number of records and operations
- Client threads and target operation rate
- Throughput in operations per second
- Average latency and p95/p99 latency
- Operation errors
- Client and server environment

#### Scenario: Baseline preservation
- WHEN a benchmark run finishes
- THEN its raw output and configuration SHALL be saved
  for comparison with Milestones 3 and 5.

### Requirement: Benchmark Limitations

The benchmark documentation SHALL identify:
- The shared EC2 host used by both shards
- The in-memory, non-durable storage
- The fact that Coordinator PUT replaces record values
- Any incompatibilities or unsupported YCSB operations