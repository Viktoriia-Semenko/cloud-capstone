# ADR-008: YCSB Benchmarking Strategy

**Milestone:** 2 — Sharding the Load

## Context

Milestone 2 requires a reproducible YCSB performance
baseline for comparison with Milestones 3 and 5.

Our distributed key-value store exposes a custom REST
JSON API through a Coordinator.

YCSB does not provide a binding specifically designed
for this API.

## Decision

We will use YCSB 0.17.0 with a custom Java database
binding.

The binding will extend the YCSB DB abstraction and
communicate with the Coordinator over HTTP.

We will use:
- Java 17 (subject to compatibility verification)
- Maven
- YCSB Core 0.17.0
- Workload A: 50% reads, 50% updates
- Workload B: 95% reads, 5% updates

The benchmark client will run on the MacBook.
The Coordinator and two shards will run on AWS EC2.

## Operation Mapping

| YCSB operation | Coordinator API |
|---|---|
| INSERT | POST /tables/{table}/records |
| READ | GET /tables/{table}/records/{key} |
| UPDATE | PUT /tables/{table}/records/{key} |
| DELETE | DELETE /tables/{table}/records/{key} |

SCAN is unsupported because our API does not implement
range queries.

Table creation will be performed before loading data.

The benchmark will use full-record updates because the
Coordinator's PUT operation replaces the record value.

## Benchmark Configuration

We will start with:
- 1,000 records
- 1,000 measured operations per workload
- 1 client thread for the initial baseline
- Fixed workload configuration
- Separate prepared datasets for workloads A and B

We will record throughput, average latency, p95 and p99
latency, error counts, and the environment.

Configuration may be adjusted after initial validation,
but changes must be documented.

## Alternatives Considered

### Custom Python load generator

Rejected as the primary benchmark because the course
explicitly requires YCSB.

Python scripts may still be used for functional tests.

### Existing YCSB database binding

Rejected because none of the standard bindings directly
matches our Coordinator's custom REST JSON API.

### Running YCSB inside the EC2 instance

Rejected for the initial baseline because client load
generation would compete for resources with the store.

## Consequences

Advantages:
- Reproducible benchmark configuration
- Standard YCSB metrics
- Comparable results across milestones
- No changes required to the Coordinator API

Limitations:
- Additional Java integration code is required
- Network latency between MacBook and AWS affects results
- Both shards share one EC2 host
- Data is stored in memory and is not durable
- Results represent this deployment, not a production
  distributed database

## Validation

Before benchmarking:
1. Verify Java 17 compatibility.
2. Build the custom binding using Maven.
3. Run a small functional test against the Coordinator.
4. Load the required dataset.
5. Execute workloads A and B.
6. Preserve raw results and configuration.
