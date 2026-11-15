## ADDED Requirements

### Requirement: Infrastructure as Code

The system SHALL define its AWS application infrastructure
using CloudFormation.

#### Scenario: Application stack creation
- WHEN the application CloudFormation template is deployed
- THEN it SHALL create the resources required to run the
  Coordinator and two Shards.

### Requirement: Existing Network Reuse

The application SHALL use the VPC and public subnet defined
in Milestone 1.

#### Scenario: Deployment into existing VPC
- WHEN the application stack is created
- THEN it SHALL deploy into the specified existing VPC
  and subnet without creating another VPC.

### Requirement: Containerised Deployment

The application SHALL run the Coordinator and two Shards
as independent Docker containers on one EC2 instance.

#### Scenario: Service startup
- WHEN the EC2 instance finishes initialisation
- THEN all three services SHALL start
- AND the Shards SHALL register with the Coordinator.

### Requirement: Network Access

The deployment SHALL expose only the Coordinator API
to external clients.

#### Scenario: External API access
- WHEN an authorised client accesses the Coordinator
- THEN the client SHALL be able to call its API
- AND the Shard APIs SHALL not be directly exposed
  through the EC2 host.

### Requirement: Deployment Verification

The deployment SHALL provide a way to verify that
distributed CRUD operations work.

#### Scenario: Sharded record access
- WHEN a client creates a record through the Coordinator
- THEN the Coordinator SHALL route it to the correct Shard
- AND the client SHALL be able to read it through
  the Coordinator.
