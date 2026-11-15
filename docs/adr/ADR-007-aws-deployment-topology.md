# ADR-007: AWS Deployment Topology for Milestone 2

**Status:** Accepted
**Date:** 2026-11-15

## Context

Milestone 2 requires deploying a distributed key-value store consisting of a Coordinator and at least two Shards.
The application has already been tested locally using Docker Compose with three independent containers.

The deployment must use Infrastructure as Code and operate within the limited AWS Academy Sandbox budget.
Milestone 1 provides a VPC with one public subnet and two private subnets.

## Decision

For the initial Milestone 2 deployment, we will use:

- One Amazon EC2 `t3.small` instance running Amazon Linux 2023.
- The existing public subnet from the Milestone 1 VPC.
- Docker Compose to run three independent containers: Coordinator, Shard 1 and Shard 2.
- Consistent hashing with SHA-256 and 100 virtual nodes per Shard.
- AWS CloudFormation to define the application infrastructure.
- A separate application stack from the existing network stack.

Only the Coordinator API will be exposed for client access. The Shard APIs will communicate with the Coordinator through the internal Docker network.

Inbound network access will be restricted through an EC2 security group.

## Alternatives Considered

### Three separate EC2 instances

**Rejected for the initial Sandbox deployment.**

This would provide better infrastructure isolation and demonstrate sharding across separate machines.

However, it would increase costs and operational complexity. Private-subnet instances would also require an additional solution for downloading application dependencies and container images without direct internet access.

### One EC2 instance with Docker Compose

**Accepted for the initial Milestone 2 deployment.**

This allows us to reuse the tested Docker Compose configuration, reduce AWS costs and demonstrate consistent hashing across independent Shard processes.

## Consequences and Trade-offs

**Advantages:**
- Lower infrastructure costs.
- Simpler CloudFormation deployment.
- No NAT Gateway required.
- Existing Docker Compose configuration can be reused.
- Suitable for demonstrating API routing, consistent hashing and sharded CRUD operations.

**Limitations:**
- All containers share the same EC2 host, creating a single point of failure.
- Sharding is logical rather than distributed across physical machines.
- CPU and memory resources are shared between all containers.
- Records are currently stored in memory and are lost when a Shard process or container restarts.
- Adding a Shard changes key ownership, but automatic data migration is not yet implemented.

## Future Evolution

A future deployment can place Shards on separate EC2 instances or use a managed container orchestration service.

Replication, durability, monitoring and automatic rebalancing will be addressed in later milestones.

The CI/CD deployment mechanism will be designed separately, taking into account temporary AWS Academy Sandbox credentials and permissions.