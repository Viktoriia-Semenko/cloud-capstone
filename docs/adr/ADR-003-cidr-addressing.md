# ADR-003: CIDR Addressing Scheme

**Date:** 2026-11-01  
**Milestone:** 1 - Infrastructure Setup

## Context

Milestone 1 requires a dedicated Virtual Private Cloud (VPC) with public and private subnets.

We need to select an IP addressing scheme that provides sufficient address capacity, avoids overlapping subnet ranges, and supports future application components.

In Milestone 2, the infrastructure will host a coordinator and two shards of a distributed key-value store.

The AWS Academy sandbox has a limited credit budget, so the network design should minimise unnecessary infrastructure costs.

## Decision

I will create a dedicated VPC using the private IPv4 CIDR block `10.0.0.0/16` in the `us-east-1` region.

The VPC will contain three subnets:

| Subnet | CIDR | Purpose |
|---|---|---|
| Public Subnet | 10.0.1.0/24 | Resources requiring direct internet routing |
| Private Subnet A | 10.0.2.0/24 | Internal application resources |
| Private Subnet B | 10.0.3.0/24 | Internal application resources in another Availability Zone |

The two private subnets will be placed in different Availability Zones for future availability and fault-tolerance requirements.

## Address Capacity

The VPC CIDR block `/16` provides:

- 65,536 IPv4 addresses in the VPC address range.
- Flexibility to allocate additional subnets in later milestones.

Each `/24` subnet provides:

- 256 total IPv4 addresses.
- Five addresses reserved by AWS.
- 251 usable IPv4 addresses.

The selected subnet CIDR blocks do not overlap and are fully contained within the VPC CIDR block.

The existing default VPC (`172.31.0.0/16`) uses a different address range and will not be modified.

## Network Routing

### Public Subnet

The public subnet will be associated with a route table containing:

- `10.0.0.0/16 → local`
- `0.0.0.0/0 → Internet Gateway`

The Internet Gateway will be attached to the VPC.

For a resource to communicate directly with the internet over IPv4, it will also require an appropriate public IP address and security rules.

### Private Subnets

Both private subnets will use route tables containing local VPC routing.

They will not have a default route (`0.0.0.0/0`) to an Internet Gateway or NAT Gateway in Milestone 1.

Resources within the VPC can communicate through local routing, subject to security groups and network ACL rules.

Private subnets will not have direct internet access.

## NAT Gateway Decision

I will not deploy a NAT Gateway during Milestone 1

Reasons:

- The assignment requires private subnets for internal communication.
- Outbound internet access from private subnets is not currently required.
- NAT Gateway would introduce unnecessary costs in the limited AWS Academy sandbox.

If private resources need outbound internet access in future milestones, we will reconsider NAT Gateway or VPC endpoints and update the architecture accordingly.

## Alternatives Considered

### Smaller VPC CIDR Block

A smaller VPC range, such as `10.0.0.0/20`, would also provide sufficient capacity for the initial project.

However, `/16` offers more flexibility for future subnets and has no additional direct cost solely because of its larger private address range.

### Single Subnet

Using one subnet would simplify the initial configuration.

However, it would not meet the requirement to separate public and private network resources and would limit future deployment flexibility.

### Public Subnets Only

Using only public subnets would simplify internet connectivity.

However, it would unnecessarily expose future application resources to potential external network access and would not satisfy the private subnet requirement.

## Consequences

**Positive:**

- Clear separation between public and private network resources.
- Non-overlapping IP address ranges.
- Sufficient IP capacity for future milestones.
- Private subnets distributed across two Availability Zones.
- No NAT Gateway costs during Milestone 1.
- Network resources can be recreated using CloudFormation.

**Negative:**

- Private resources cannot access the public internet without additional network configuration.
- Future deployment may require VPC endpoints or NAT for external dependencies.
- A large `/16` address range may conflict with other private networks if connectivity is added later.
- Future multi-AZ public-facing load balancers may require an additional public subnet.

## Validation

I will verify that:

1. The dedicated VPC is created with `10.0.0.0/16`.
2. All three subnets exist and have the correct CIDR blocks.
3. No subnet CIDR blocks overlap.
4. The two private subnets are placed in different Availability Zones.
5. The public subnet has a default route through the Internet Gateway.
6. The private subnets have no direct default route to the Internet Gateway.
7. The network stack can be deleted and recreated using CloudFormation.
