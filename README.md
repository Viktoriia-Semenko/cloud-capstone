# Milestone 1 
## Service quotas (Task 6)

The service quotas were reviewed in the AWS Academy Cloud Architecting Sandbox using AWS CLI in the `us-east-1` region.

| Service | Quota | Limit | Current Usage / Requirement | Screenshot |
|---|---|---|---|---|
| Amazon EC2 | Running On-Demand Standard instances | 256 vCPUs | Estimated 6 vCPUs for Milestone 2 |<img width="733" height="218" alt="Screenshot 2026-11-01 at 14 40 38" src="https://github.com/user-attachments/assets/d7157e70-bc52-474b-a0a6-db83c319cc0c" /> |
| Amazon VPC | VPCs per Region | 5 | 2 VPCs currently exist (default + capstone) | <img width="596" height="224" alt="Screenshot 2026-11-01 at 14 42 29" src="https://github.com/user-attachments/assets/885a8968-098b-4d2b-984c-300a352f05e6" /> |
| Amazon VPC | Subnets per VPC | 200 | 3 subnets created |<img width="458" height="199" alt="Screenshot 2026-11-01 at 14 44 23" src="https://github.com/user-attachments/assets/0b8dd0d3-e59d-456f-acb6-c230e22c60a3" /> |


### Analysis

Milestone 2 will require one Coordinator and two Shards.

Assuming each component runs on an EC2 `t3.micro` instance with 2 vCPUs, the total requirement is 6 vCPUs.

The EC2 quota of 256 vCPUs is sufficient for this configuration. The existing VPC and subnet quotas are also sufficient.

However, the AWS Academy Sandbox may impose additional restrictions on instance types, available services, and resource creation that are not reflected in standard AWS Service Quotas.

**Conclusion:**  reviewed quotas are not expected to limit the proposed Milestone 2 infrastructure. The main potential constraints are sandbox-specific restrictions and the available credit budget.

---

## Monthly budget estimate (Task 7)

### Infrastructure Assumptions

The estimated infrastructure for Milestone 2 consists of:

- 1 EC2 `t3.micro` instance for the Coordinator
- 2 EC2 `t3.micro` instances for the Shards
- 3 EBS gp3 volumes of 8 GiB each
- 1 public IPv4 address for the Coordinator
- AWS Region: `us-east-1`
- Operating system: Linux
- Pricing model: On-Demand
- Monthly runtime: 730 hours

These resources represent a proposed minimal configuration for cost estimation, not an already deployed Milestone 2 environment.

### Estimated Monthly Costs

| Resource | Calculation | Monthly Cost |
|---|---|---|
| EC2 Coordinator | 730 × $0.0104 | $7.59 |
| EC2 Shard 1 | 730 × $0.0104 | $7.59 |
| EC2 Shard 2 | 730 × $0.0104 | $7.59 |
| EBS gp3 storage | 24 GiB × $0.08 | $1.92 |
| Public IPv4 address | 730 × $0.005 | $3.65 |
| **Total** | | **$28.35** |

### Sandbox Budget Comparison

- **Available sandbox credit ceiling:** $20.00
- **Estimated monthly infrastructure cost:** $28.35
- **Amount exceeding the credit ceiling:** $8.35

The proposed infrastructure would exceed the available sandbox credits if operated continuously for an entire month.

### Cost Optimisation

To reduce costs, the EC2 instances will run only during development and testing sessions instead of continuously.

Assuming 160 hours of EC2 runtime per month, 24 GiB of EBS storage retained throughout the month, and one public IPv4 address used only during those 160 hours:

| Resource | Estimated Cost |
|---|---|
| 3 EC2 instances × 160 hours | $4.99 |
| EBS gp3 storage (24 GiB) | $1.92 |
| Public IPv4 (160 hours) | $0.80 |
| **Total** | **$7.71** |

This reduced-runtime scenario fits within the $20 sandbox credit ceiling, assuming sufficient credits remain available.

The estimate excludes potential additional charges for data transfer, CPU credits, monitoring, and other services. AWS Academy restrictions and any applicable free-tier benefits may affect actual charges.

### Conclusion

The full-month infrastructure estimate exceeds the sandbox budget. Running the infrastructure only when needed is a more suitable approach for Milestone 2

### Pricing References

- [AWS EC2 T3 Pricing](https://aws.amazon.com/ec2/instance-types/t3/)
- [AWS EBS Pricing](https://aws.amazon.com/ebs/pricing/)
- [AWS VPC and Public IPv4 Pricing](https://aws.amazon.com/vpc/pricing/)

---

## Infrastructure Reproducibility (Task 8)

The network infrastructure was deployed using AWS CloudFormation in the `us-east-1` region.

**Stack name:** `capstone-network`  
**IaC template:** `infra/network.yaml`

### Recreation еest

1. The network stack was successfully deployed using CloudFormation.
2. The stack was deleted using AWS CLI.
3. After deletion completed, the same CloudFormation template was used to recreate the network.
4. The recreation completed successfully

### Results

| Metric | Result |
|---|---|
| Initial deployment time | 66.336 seconds |
| Recreation time | 36.284 seconds |
| Recreation status | Successful |
| Errors during recreation | None reported |
<img width="470" height="197" alt="Screenshot 2026-11-01 at 15 01 24" src="https://github.com/user-attachments/assets/736845ae-46e7-41a8-b5bd-d7d79b103aa1" />
<img width="679" height="343" alt="Screenshot 2026-11-01 at 15 01 29" src="https://github.com/user-attachments/assets/12a9ded7-a900-4ee5-9043-91a7035f756d" />


### Conclusion

The network infrastructure was initially deployed using AWS CloudFormation. After deleting the stack, I successfully recreated it using the same YAML template and deployment command. Both deployments were automated, and no manual resource configuration was required. This demonstrates the reproducibility of my Infrastructure as Code approach.
