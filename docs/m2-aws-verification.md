# Milestone 2 — AWS Deployment Verification

## Deployment

- Infrastructure: AWS CloudFormation
- Network stack: `capstone-network`
- Application stack: `capstone-application`
- Compute: one EC2 `t3.small`
- Operating system: Amazon Linux 2023
- Containers: Coordinator, Shard 1, Shard 2
- Container orchestration: Docker Compose
- Sharding: SHA-256 consistent hashing
- Virtual nodes: 100 per shard (200 total)

## Verification Results

| Test | Observed result | Status |
|---|---|---|
| CloudFormation deployment | CREATE_COMPLETE | PASS |
| Docker Compose installation | v5.6.1 | PASS |
| Docker Buildx installation | v0.20.1 | PASS |
| Docker image build | Built | PASS |
| Coordinator container | Started | PASS |
| Shard 1 container | Started | PASS |
| Shard 2 container | Started | PASS |
| Coordinator health check | HTTP 200 | PASS |
| Shard 1 registration | HTTP 200 (already registered) | PASS |
| Shard 2 registration | HTTP 200 (already registered) | PASS |
| CREATE table and records | HTTP 201 | PASS |
| READ records | HTTP 200 | PASS |
| EXISTS records | HTTP 200 | PASS |
| UPDATE record | HTTP 200 | PASS |
| DELETE record | HTTP 204 | PASS |
| READ deleted record | HTTP 404 | PASS |

## Consistent Hashing

Local verification of the same hashing implementation:

- `students/101` → `shard-1`
- `students/103` → `shard-2`
- Total ring positions: 200

The AWS smoke tests confirm that the Coordinator is
reachable and handles CRUD requests while both shard IDs
are registered.

Direct inspection of each shard's stored records has not
yet been performed.

## Deployment Limitations

- Both shards run on the same EC2 host.
- Data is stored in memory and is not persistent.
- EC2 remains a single point of failure.
- The API uses HTTP without authentication and inbound
  access is restricted to the configured client IP.
- The EC2 instance consumes AWS Sandbox credits while running.

## Troubleshooting

1. Initial deployment failed due to a conflict between
   `curl` and `curl-minimal` on Amazon Linux 2023.
   Fix: removed the redundant `curl` installation.

2. The next deployment failed because Docker Buildx
   was missing.
   Fix: installed Docker Buildx v0.20.1 in UserData.

3. The final deployment successfully built the Docker
   image and started all three containers.

## Evidence

- CloudFormation stack status and outputs
- EC2 console logs showing successful image build
  and container startup
- HTTP responses from the AWS Coordinator
- Local consistent hashing verification
