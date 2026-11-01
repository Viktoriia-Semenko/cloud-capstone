# Network Infrastructure Specification

## ADDED Requirements

### Requirement: Dedicated VPC

The infrastructure SHALL provide a dedicated Amazon VPC in the `us-east-1` AWS Region.

The VPC SHALL use the IPv4 CIDR block `10.0.0.0/16`.

#### Scenario: VPC creation

- **WHEN** the network CloudFormation stack is successfully deployed
- **THEN** a VPC with CIDR `10.0.0.0/16` SHALL exist
- **AND** the existing default VPC SHALL remain unchanged

### Requirement: Public and Private Subnets

The infrastructure SHALL create three subnets within the dedicated VPC.

The subnets SHALL use the following CIDR blocks:

- Public Subnet: `10.0.1.0/24`
- Private Subnet A: `10.0.2.0/24`
- Private Subnet B: `10.0.3.0/24`

The two private subnets SHALL be located in different Availability Zones.

#### Scenario: Subnet verification

- **WHEN** the VPC subnets are inspected
- **THEN** all three subnets SHALL exist
- **AND** their CIDR blocks SHALL be non-overlapping
- **AND** both private subnets SHALL reside in different Availability Zones

### Requirement: Public Internet Routing

The infrastructure SHALL attach an Internet Gateway to the VPC.

The public subnet SHALL use a route table with a default IPv4 route to the Internet Gateway.

#### Scenario: Public subnet routing

- **WHEN** the public subnet route table is inspected
- **THEN** it SHALL contain a `0.0.0.0/0` route targeting the Internet Gateway
- **AND** it SHALL retain the local VPC route

### Requirement: Private Network Isolation

The private subnets SHALL NOT have a direct default route to the Internet Gateway.

No NAT Gateway SHALL be deployed during Milestone 1.

#### Scenario: Private subnet routing

- **WHEN** the private subnet route tables are inspected
- **THEN** they SHALL provide local VPC routing
- **AND** they SHALL NOT contain a default route to an Internet Gateway or NAT Gateway

### Requirement: Infrastructure as Code

All required network resources SHALL be defined using AWS CloudFormation YAML templates.

The network stack SHALL expose the VPC ID and subnet IDs through CloudFormation Outputs for future milestones.

#### Scenario: Infrastructure deployment

- **WHEN** the CloudFormation template is deployed with valid permissions
- **THEN** the network stack SHALL reach the `CREATE_COMPLETE` state
- **AND** all required network resources SHALL be present

### Requirement: Network Reproducibility

The network infrastructure SHALL be reproducible from its CloudFormation template without manually recreating resources.

#### Scenario: Network stack recreation

- **WHEN** the network stack is deleted and subsequently deployed again using the same template
- **THEN** the stack SHALL reach `CREATE_COMPLETE`
- **AND** the recreated network SHALL satisfy the same CIDR and routing requirements
- **AND** the recreation time and any deployment errors SHALL be documented
