# ADR-002: CloudFormation Stack Layout

**Date:** 2026-11-01  
**Milestone:** 1 - Infrastructure Setup

## Context

The capstone project will be developed across multiple milestones.

Milestone 1 requires a network infrastructure consisting of a VPC, public and private subnets, an Internet Gateway, and route tables.

Milestone 2 will introduce application components, including a coordinator and two shards.

We need to decide whether to manage all AWS resources in a single CloudFormation stack or separate the networking and application infrastructure.

## Decision

I will use **separate CloudFormation stacks for networking and application resources**.

### Network Stack (Milestone 1)

The network stack will contain:

- One dedicated VPC.
- One public subnet.
- Two private subnets.
- One Internet Gateway.
- Public and private route tables.
- Required route table associations.
- CloudFormation outputs for important network resource IDs.

The network stack will be created and tested in Milestone 1.

### Application Stack (Milestone 2)

A separate application stack will be introduced in Milestone 2.

It will contain the compute and application resources required for the coordinator and two shards.

The application stack will reference networking resources created by the network stack.

Restricted IAM policies and roles will be described in separate IaC templates without deploying them in the sandbox.

## Alternatives Considered

### Single CloudFormation Stack

All networking and application resources could be managed together.

Advantages:
- Simpler initial configuration.
- No need to pass resource IDs between stacks.

Disadvantages:
- Networking and application resources would be tightly coupled.
- Application changes could make the infrastructure harder to manage.
- Reusing the same network for other application components would be less convenient.

## Consequences

**Positive:**

- Clear separation between networking and application infrastructure.
- The network can be managed independently.
- Easier reuse of networking resources in future milestones.
- Infrastructure changes are easier to organise and review.
- Milestone 1 network reproducibility can be tested without deploying application resources.

**Negative:**

- Multiple stacks require additional coordination.
- The application stack needs references to network resource IDs.
- Dependencies between stacks must be managed carefully.
- A network stack cannot be deleted while dependent application resources still require it.

## Validation

During Milestone 1, I will:

1. Deploy the network stack using AWS CloudFormation.
2. Verify that the VPC, subnets, Internet Gateway, and route tables were created correctly.
3. Delete the network stack.
4. Recreate the network stack using the same IaC template.
5. Record the recreation time and any deployment problems.

The existing default VPC will not be modified or deleted.

## Related Requirements

Milestone 1 — Infrastructure Setup:

- Create a VPC with public and private subnets.
- Create an IaC stack containing network resources.
- Demonstrate infrastructure reproducibility.
- Document the choice of stack layout in an ADR.
