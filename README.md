# Milestone 1 

## IAM Role analysis (Task 1)

### Environment

The project was completed in the AWS Academy Cloud Architecting Sandbox, in the `us-east-1` region.

The assignment refers to `LabRole`, but this role wasn't found in the available IAM roles. The actual assumed role in this sandbox is `voclabs`. Therefore, the IAM permission analysis was performed using `voclabs`.

### Role Identification

The current identity was verified using AWS CLI:

```bash
aws sts get-caller-identity
```
<img width="654" height="205" alt="Screenshot 2026-11-01 at 15 17 26" src="https://github.com/user-attachments/assets/eeb1f6a8-1705-498c-be95-8b05ac1ee20f" />

The returned ARN confirmed the assumed role `voclabs`

### IAM Policies

The following command was used to identify attached managed policies:

```bash
aws iam list-attached-role-policies --role-name voclabs
```
<img width="585" height="171" alt="Screenshot 2026-11-01 at 12 54 35" src="https://github.com/user-attachments/assets/b5fd1a4d-f411-4329-8343-6df028a4bf34" />

**Result:** The managed policy `ReadOnlyAccess` was attached to the role

Inline policies were checked using:

```bash
aws iam list-role-policies --role-name voclabs
```
<img width="465" height="121" alt="Screenshot 2026-11-01 at 12 59 45" src="https://github.com/user-attachments/assets/6983f480-e27e-482a-88a6-b65d2429d6c5" />

**Result:** One inline policy was found: `Pvoclabs`.

However, retrieving its content was denied.
<img width="1401" height="128" alt="Screenshot 2026-11-01 at 13 01 30" src="https://github.com/user-attachments/assets/aa0325c8-ab4f-4113-a9e6-90be05415af7" />

### Verified Permissions and Restrictions

| AWS Action | Result | Verification Method |
|---|---|---|
| `sts:GetCallerIdentity` | Allowed | AWS CLI |
| `iam:ListRoles` | Allowed | AWS Console |
| `iam:ListAttachedRolePolicies` | Allowed | AWS CLI |
| `iam:ListRolePolicies` | Allowed | AWS CLI |
| `ec2:DescribeVpcs` | Allowed | AWS CLI |
| `iam:GetRole` | Explicit Deny | AWS Console |
| `iam:GetRolePolicy` | Explicit Deny | AWS CLI |

### Analysis

The `voclabs` role allows several operations for listing and viewing AWS resources. However, certain IAM operations are explicitly denied by identity-based policies. For example, attempting to retrieve details of an IAM role using `iam:GetRole` resulted in an explicit deny. Similarly, attempting to retrieve the inline policy `Pvoclabs` using `iam:GetRolePolicy` returned `AccessDenied`.
The exact policy statement responsible for these denials could not be identified because access to the relevant policy content was restricted.

### Conclusion

The custom read-only IAM policy and assumable role required by Tasks 2 and 3 were defined separately in `infra/iam-readonly.yaml`. The template was successfully validated using AWS CloudFormation but wasn't deployed.

---

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

## AI Architecture Design Review

**AI reviewer:** ChatGPT (GPT-6)  
**Reviewed architecture:** AWS CloudFormation network stack in `us-east-1`

### AI Critique 1: Single public subnet

The network contains only one public subnet in `us-east-1a`, while the private subnets are distributed across two Availability Zones. This may limit high availability for future public-facing components, such as an Application Load Balancer.

**AI recommendation:** consider adding a second public subnet in another Availability Zone if the future application requires multi-AZ public access.

### AI Critique 2: No Outbound Internet Access for Private Subnets

The private subnets have only local VPC routing, with no NAT Gateway or VPC endpoints.Future application instances may need outbound connectivity to download packages, access external services, or retrieve container images.

**AI recommendation:** reconsider outbound connectivity when implementing Milestone 2, using NAT Gateway or appropriate VPC endpoints if required.

### AI Critique 3: Monthly Cost Exceeds Available Credits

The estimated cost of continuously running the proposed Milestone 2 infrastructure is $28.35 per month, exceeding the $20 sandbox credit ceiling. This creates a risk of exhausting available credits.

**AI recommendation:** Run the infrastructure only during development and testing, monitor remaining credits, and remove resources when they are no longer required.

### My review and secisions

#### 1. Single Public Subnet - ACCEPT and postpone

I agree with the AI critique that having only one public subnet may limit high availability in future milestones. However, Milestone 1 only requires a network with public and private subnets. Our current infrastructure meets this requirement, and we do not deploy a public-facing load balancer at this stage.

#### 2. No Outbound Internet Access for Private Subnets - REJECT FOR MILESTONE 1

I understand that private instances may need outbound internet access in future milestones. However, Milestone 1 explicitly requires private subnets for internal communication. Our private subnets have local VPC routing and do not require internet connectivity at this stage. Adding a NAT Gateway now would introduce unnecessary costs, especially considering the limited $20 sandbox budget.

#### 3. Infrastructure Cost Exceeds Sandbox Credits - ACCEPT

I agree with the AI critique that continuously running the proposed Milestone 2 infrastructure would exceed our sandbox budget.
The estimated monthly cost is $28.35, while the available sandbox credit ceiling is $20. Since this is an educational project, the infrastructure doesnt need to run continuously. Our reduced-runtime estimate of 160 hours per month is approximately $7.71, excluding additional charges. I will run the infrastructure only during development and testing, monitor remaining credits, and stop or delete billable resources when they are not needed. I will also account for storage costs that continue while instances are stopped.


------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------

# Milestone 2 — Sharding the Load

## 1. Overview

Milestone 2 extends the infrastructure developed in Milestone 1 with a sharded key-value store.

The system consists of a Coordinator and two storage Shards. The Coordinator exposes a REST JSON API, manages table definitions and shard registration, and routes record operations using consistent hashing.

**Implemented functionality:**

- Table registration and record CRUD operations
- Single-node mode when no shards are registered
- Two storage shards with automatic startup registration
- SHA-256 consistent hashing with 100 virtual nodes per shard
- Docker Compose for local development
- AWS deployment using CloudFormation
- Automated Python and Java integration tests through GitHub Actions
- YCSB Workload A and B performance benchmarking

## 2. Architecture

```text
                 HTTP Client / YCSB
                         |
                         v
                 Coordinator (FastAPI)
                       :8080
                         |
                Consistent Hash Ring
                         |
                 +-------+-------+
                 |               |
                 v               v
              Shard 1         Shard 2
               :8001           :8002
```

The Coordinator calculates a hash from the table name and record key, then selects the responsible Shard using a consistent hashing ring.

The system uses SHA-256 and 100 virtual nodes per physical shard (200 ring positions in total).

Shards register with the Coordinator automatically during startup.

Both reads and writes are routed to the selected Shard. Shard storage is currently in-memory.

## 3. Project Structure

```text
api/                 OpenAPI specification
coordinator/         REST API, routing and consistent hashing
shard/               Internal key-value storage service
infra/               AWS CloudFormation templates
benchmark/           YCSB binding, workloads and results
tests/               Python tests
docs/adr/            Architecture Decision Records
openspec/changes/    OpenSpec proposals and specifications
.github/workflows/   GitHub Actions CI
```

## 4. Running Locally

### Prerequisites

- Docker and Docker Compose
- Python 3.12 for local tests
- Java 17 and Maven for YCSB

Clone the repository:

```bash
git clone https://github.com/Viktoriia-Semenko/cloud-capstone.git
cd cloud-capstone
```

Build and start the services:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

Verify the Coordinator:

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{"status":"ok","service":"coordinator"}
```

Local service endpoints:

| Service | Address |
|---|---|
| Coordinator | http://localhost:8080 |
| Swagger UI | http://localhost:8080/docs |
| Shard 1 | http://localhost:18001 |
| Shard 2 | http://localhost:18002 |

Shards are registered with the Coordinator on startup.

To stop the application:

```bash
docker compose down
```

## 5. API Verification

The Coordinator supports the following operations:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check Coordinator health |
| POST | `/tables` | Register a table |
| POST | `/tables/{table}/records` | Create a record |
| GET | `/tables/{table}/records/{key}` | Read a record |
| GET | `/tables/{table}/records/{key}/exists` | Check whether a record exists |
| PUT | `/tables/{table}/records/{key}` | Replace a record's value |
| DELETE | `/tables/{table}/records/{key}` | Delete a record |
| POST | `/shards/register` | Register a storage Shard |

### Example: Create a table

```bash
curl -X POST http://localhost:8080/tables \
  -H "Content-Type: application/json" \
  -d '{"name":"students","partition_key":"student_id"}'
```

Expected status: `201 Created`.

### Create a record

```bash
curl -X POST http://localhost:8080/tables/students/records \
  -H "Content-Type: application/json" \
  -d '{"key":"101","value":{"name":"Anna","subject":"Math"}}'
```

Expected status: `201 Created`.

### Read the record

```bash
curl http://localhost:8080/tables/students/records/101
```

Expected status: `200 OK`.

### Update the record

```bash
curl -X PUT http://localhost:8080/tables/students/records/101 \
  -H "Content-Type: application/json" \
  -d '{"value":{"name":"Anna","subject":"Physics"}}'
```

Expected status: `200 OK`.

### Delete the record

```bash
curl -i -X DELETE \
  http://localhost:8080/tables/students/records/101
```

Expected status: `204 No Content`.

Reading the deleted record should return `404 Not Found`.

## 6. Sharding Verification

The hashing algorithm assigns keys to Shards based on the table name and record key.

For the configured ring:

| Record | Assigned Shard |
|---|---|
| `students/101` | `shard-1` |
| `students/103` | `shard-2` |

These assignments were verified using the implementation in `coordinator/hash_ring.py`.

To inspect storage directly during local development, first create both records through the Coordinator, then query the internal Shard endpoints:

```bash
curl http://localhost:18001/internal/tables/students/records/101
```

```bash
curl http://localhost:18002/internal/tables/students/records/103
```

The expected records should be present on their assigned Shards. Requests to the other Shard should return `404`.

In the AWS deployment, Shard ports are not publicly exposed.

## 7. AWS Deployment

The system was deployed in the AWS Academy Cloud Architecting Sandbox, in region `us-east-1`.

### Infrastructure

Two CloudFormation stacks are used:

| Stack | Purpose |
|---|---|
| `capstone-network` | VPC, public/private subnets, internet gateway and routing |
| `capstone-application` | EC2 instance and application Security Group |

The application runs on one `t3.small` EC2 instance with Amazon Linux 2023.

Docker Compose runs three containers:

- Coordinator
- Shard 1
- Shard 2

This is logical sharding on a shared host rather than physical separation across EC2 instances.

The application Security Group permits inbound TCP port 8080 only from the configured client IPv4 CIDR.

### Deployment method

Infrastructure is defined in:

```text
infra/network.yaml
infra/application.yaml
```

Deployment is performed using AWS CLI in CloudShell with the current Sandbox session's permissions.

The CloudShell deployment helper is:

```bash
scripts/deploy-cloudshell.sh
```

Example invocation after obtaining the latest project files in CloudShell:

```bash
bash scripts/deploy-cloudshell.sh YOUR_PUBLIC_IPV4/32
```

Replace the placeholder with the current public IPv4 address of the client machine.

The deployment helper is intended to deploy the network and application stacks without storing AWS credentials in GitHub. Its deployment behaviour must be validated in the active Sandbox session.

EC2 User Data installs Docker, Docker Compose and Buildx, downloads the application from GitHub, and starts the containers.

After deployment, retrieve `CoordinatorURL` from the `capstone-application` CloudFormation Outputs and verify:

```bash
curl http://EC2_PUBLIC_IP:8080/health
```

The `/health` request should be sent from the client IP permitted by the Security Group.

**AWS Sandbox limitation:** resources may be removed when a Sandbox session ends. The infrastructure can be recreated from CloudFormation templates.

### Cleanup

To avoid unnecessary Sandbox costs, delete the application stack after testing:

```bash
aws cloudformation delete-stack \
  --stack-name capstone-application \
  --region us-east-1

aws cloudformation wait stack-delete-complete \
  --stack-name capstone-application \
  --region us-east-1
```

The network stack can be retained for subsequent milestones.

## 8. Testing and Continuous Integration

### Python tests

Run from the repository root:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

The Python test suite verifies API behaviour, consistent hashing, Shard registration and request routing.

### Java YCSB integration tests

Start the local Docker services first, then run:

```bash
COORDINATOR_URL=http://localhost:8080 \
mvn -f benchmark/ycsb-binding/pom.xml clean test
```

The integration test verifies INSERT, READ, UPDATE and DELETE through the Java binding.

### GitHub Actions CI

Workflow: `.github/workflows/ci.yml`

CI runs automatically on pushes to `main` and pull requests.

It installs Python and Java dependencies, runs Python tests, starts Docker Compose, checks Coordinator health and executes Java integration tests.

The GitHub Actions CI workflow was successfully executed during Milestone 2.

### Deployment automation limitation

GitHub-hosted deployment to AWS is not active because the project does not provide AWS credentials to GitHub Actions and the Academy Sandbox restricts IAM configuration.

Instead, deployment is initiated from authenticated AWS CloudShell using Infrastructure as Code.

Therefore, automated CI is verified, while fully automated GitHub-to-AWS CD remains an outstanding limitation.

## 9. YCSB Performance Benchmark

The project uses **YCSB 0.17.0** with a custom Java binding for the Coordinator REST API.

Two workload profiles are implemented:

| Workload | READ | UPDATE |
|---|---:|---:|
| A — Update-heavy | 50% | 50% |
| B — Read-heavy | 95% | 5% |

The benchmark uses full-record updates because the Coordinator's PUT operation replaces the record's value.

SCAN is not supported by the current API.

### Run a local smoke test

```bash
./benchmark/run-ycsb.sh http://localhost:8080 smoke
```

The smoke test uses 30 records and 20 measured operations per workload.

### Run the AWS baseline

After deploying the AWS application:

```bash
./benchmark/run-ycsb.sh http://EC2_PUBLIC_IP:8080 baseline
```

The baseline uses:

- 1,000 records per workload
- 1,000 measured operations per workload
- One client thread
- No target throughput limit

### Milestone 2 baseline results

Date: 15 November 2026

| Metric | Workload A | Workload B |
|---|---:|---:|
| Throughput (ops/sec) | 3.99 | 3.26 |
| READ operations | 506 | 957 |
| UPDATE operations | 494 | 43 |
| READ average latency (ms) | 254.90 | 306.75 |
| READ p95 latency (ms) | 496.13 | 704.51 |
| READ p99 latency (ms) | 867.33 | 1047.55 |
| Failed measured operations | 0 | 0 |

Both workloads completed successfully.

The benchmark client ran on a MacBook and communicated with AWS over the public internet. The measurements therefore include network latency.

These results form the baseline for comparisons in Milestones 3 and 5.

Detailed results: `docs/m2-ycsb-baseline.md`

Raw benchmark outputs: `benchmark/results/20261115T185738Z_baseline/`

## 10. Architecture Decisions and Limitations

Architecture Decision Records are located in `docs/adr/`.

Key decisions include:

- REST JSON API implemented with FastAPI
- SHA-256 consistent hashing
- 100 virtual nodes per Shard
- String partition keys
- Single-EC2 deployment topology for AWS Sandbox
- Custom Java binding for YCSB benchmarking

### Current limitations

- All three services share a single EC2 instance.
- Storage is in memory and is not durable.
- The Coordinator is a single point of failure and potential bottleneck.
- Replication and automatic data migration are not implemented.
- Adding a Shard changes the hash ring but does not migrate existing records.
- The API does not provide authentication or HTTPS.
- AWS deployment is manually initiated from CloudShell.
- Benchmark latency includes client-to-AWS network overhead.

These limitations are intentional or documented trade-offs for the current milestone and provide a basis for future improvements.

## 11. Changes Since Milestone 1

Milestone 1 focused on IAM analysis, AWS network infrastructure, CloudFormation, service quotas and cost estimation.

Milestone 2 adds:

1. A functional REST key-value store.
2. A Coordinator with consistent hashing.
3. Two automatically registered storage Shards.
4. Docker-based local and AWS application deployment.
5. Automated unit and integration tests.
6. GitHub Actions CI.
7. A reproducible YCSB performance baseline.

The existing Milestone 1 infrastructure is reused rather than replaced.

## 12. Supporting Documentation

- `api/openapi.yaml` — public API specification
- `openspec/changes/m2-sharding-the-load/` — design proposal and requirements
- `docs/adr/` — architectural decisions
- `docs/m2-aws-verification.md` — AWS deployment and functional verification
- `docs/m2-ycsb-baseline.md` — YCSB results and interpretation

The implementation, benchmark configurations, IaC templates and recorded measurements provide evidence for the Milestone 2 defence.