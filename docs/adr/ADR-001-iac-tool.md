# ADR-001: Choice of Infrastructure as сode еool

**Date:** 2026-11-01  
**Milestone:** 1 - Infrastructure Setup

## Context

The capstone project requires infrastructure to be defined as code so that it can be deployed, deleted, and recreated consistently.

The project runs in the AWS Academy Cloud Architecting Sandbox, which has restricted IAM permissions and a limited credit budget.

We need an Infrastructure as Code (IaC) tool to manage AWS networking resources, including a VPC, public and private subnets, an Internet Gateway, and route tables.

## Decision

I will use **AWS CloudFormation** with YAML templates to define and manage infrastructure resources.

CloudFormation is a native AWS service and can be managed directly through the AWS Management Console.

I will store my templates in GitHub to track infrastructure changes.

## Consequences

**Positive:**

- Native integration with AWS services.
- Infrastructure is described in version-controlled YAML templates.
- CloudFormation manages resource dependencies and stack lifecycle operations.
- Supports repeatable infrastructure deployment and deletion.
- Provides change sets and drift detection capabilities.

**Negative:**

- CloudFormation is specific to AWS and is less portable across cloud providers.
- YAML templates can become verbose as the infrastructure grows.
- Deployment depends on AWS IAM permissions and sandbox restrictions.

## Validation

I will verify that the AWS Academy Sandbox allows CloudFormation stack operations.

I will then deploy the network stack, delete it, and recreate it from the same template.

If sandbox restrictions prevent deployment, I will document the limitation and reconsider the implementation approach.

## Related Requirements

Milestone 1 — Infrastructure Setup:

- Create an IaC stack containing network resources.
- Demonstrate that the infrastructure can be recreated from IaC.
- Document the choice of IaC tool in an ADR.
