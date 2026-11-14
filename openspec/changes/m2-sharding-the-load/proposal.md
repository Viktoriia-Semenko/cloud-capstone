# Proposal: Milestone 2 - Sharding the Load

## Why

Milestone 1 established the AWS networking infrastructure for the capstone project.

Milestone 2 introduces a distributed key-value store that can distribute data across multiple shards.

The goal is to implement horizontal sharding, understand how consistent hashing works, and establish automated deployment and performance benchmarking.

## What changes

- Define an API specification for registering tables and performing CRUD operations on records.
- Implement a Coordinator service supporting CREATE, READ, EXISTS, and DELETE operations in single-node mode.
- Implement shard registration with the Coordinator.
- Distribute write requests across shards using consistent hashing.
- Route read requests to the correct shards.
- Define application infrastructure using AWS CloudFormation.
- Set up a CI/CD pipeline for infrastructure and application updates.
- Benchmark the sharded key-value store using YCSB and save the results for comparison with future milestones.

## Capabilities

### New capabilities

- `key-value-api`: expose operations for managing tables and records.
- `coordinator-service`: process client requests and coordinate data operations.
- `consistent-hashing`: distribute keys across registered shards.
- `sharded-storage`: store and retrieve data from the appropriate shard.
- `application-infrastructure`: deploy application resources using IaC.
- `automated-deployment`: automate infrastructure and application updates.
- `performance-benchmarking`: measure and document system performance using YCSB.

## Impact

- **Environment:** AWS Academy Cloud Architecting Sandbox, region `us-east-1`.
- **Infrastructure:** reuse the network created in Milestone 1 and add application resources.
- **Application:** introduce a Coordinator and multiple storage shards.
- **IaC:** extend the existing CloudFormation-based infrastructure.
- **CI/CD:** introduce a deployment pipeline for future milestones.
- **Documentation:** add architectural decision records, API specifications, deployment instructions, benchmark results, and AI design review.
- **Scope:** replication, durability guarantees, and automated data rebalancing are outside the scope of Milestone 2.