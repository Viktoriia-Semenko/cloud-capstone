# Milestone 2 — YCSB Performance Baseline

## Environment

- Server: AWS EC2 t3.small, Amazon Linux 2023
- Deployment: Docker Compose
- Services: Coordinator and 2 shards
- Storage: In-memory
- Hashing: SHA-256, 100 virtual nodes per shard
- Client: MacBook Air, macOS, Apple Silicon
- Benchmark: YCSB 0.17.0, custom REST binding
- Client threads: 1
- Records per workload: 1,000
- Operations per workload: 1,000
- Target throughput: Unlimited

## Results

| Metric | Workload A | Workload B |
|---|---:|---:|
| Read / Update ratio | 50/50 | 95/5 |
| Throughput (ops/sec) | 3.99 | 3.26 |
| Runtime (seconds) | 250.60 | 306.69 |
| Successful READ operations | 506 | 957 |
| Successful UPDATE operations | 494 | 43 |
| READ average latency (ms) | 254.90 | 306.75 |
| READ p95 latency (ms) | 496.13 | 704.51 |
| READ p99 latency (ms) | 867.33 | 1047.55 |
| UPDATE average latency (ms) | 245.71 | 300.15 |
| UPDATE p95 latency (ms) | 469.50 | 829.95 |
| UPDATE p99 latency (ms) | 864.26 | 905.73 |
| Failed measured operations | 0 | 0 |

## Interpretation

Both workloads completed 1,000 successful measured
operations.

Workload A achieved higher throughput than Workload B
under the measured conditions.

The benchmark client ran remotely on a MacBook, so
end-to-end HTTP latency includes network latency.

Both shards ran on one EC2 instance. This baseline does
not represent independently hosted physical shards.

Results are intended for comparison with Milestones
3 and 5 under equivalent test conditions.

## Reproduction

Run the benchmark after deploying the application:

    ./benchmark/run-ycsb.sh <COORDINATOR_URL> baseline

Raw output and configurations are preserved under:

    benchmark/results/20261115T185738Z_baseline/
