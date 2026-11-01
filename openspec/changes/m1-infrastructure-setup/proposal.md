# Proposal: Milestone 1 - Infrastructure Setup

## Why

The capstone project requires a reproducible and secure AWS infrastructure foundation before implementing the distributed key-value store in future milestones.

Milestone 1 focuses on understanding IAM permissions, configuring network isolation, estimating infrastructure costs, and using Infrastructure as Code to manage AWS resources.

## What Changes

- Investigate the permissions and restrictions of the AWS Academy sandbox role.
- Define a read-only IAM policy and an assumable IAM role using IaC without deploying restricted IAM resources.
- Create a dedicated VPC with public and private subnets.
- Configure an Internet Gateway and routing for the public subnet while keeping private subnets isolated from direct internet access.
- Define the network infrastructure using AWS CloudFormation.
- Review AWS service quotas relevant to Milestone 2.
- Estimate the monthly infrastructure cost for two shards and compare it with the sandbox credit limit.
- Verify reproducibility by deleting and recreating the network stack from IaC.

## Capabilities

### New Capabilities

- `iam-permission-analysis`: document the sandbox role's verified permissions and restrictions.
- `network-infrastructure`: define a VPC with correctly configured public and private subnets.
- `infrastructure-reproducibility`: deploy, delete, and recreate infrastructure from IaC.
- `infrastructure-cost-planning`: document service quotas and estimate the budget for Milestone 2.

## Impact

- **Environment:** AWS Academy Cloud Architecting Sandbox, region `us-east-1`.
- **IAM:** The sandbox uses the `voclabs` role rather than the `LabRole` referenced in the assignment. This difference will be documented.
- **Infrastructure:** A new dedicated VPC and its networking components.
- **IaC:** CloudFormation YAML templates stored in the repository.
- **Documentation:** Architecture Decision Records (ADRs), IAM analysis, quota review, budget estimate, deployment instructions, and AI design review.
- **Scope:** No application, coordinator, shards, or database implementation in Milestone 1.
