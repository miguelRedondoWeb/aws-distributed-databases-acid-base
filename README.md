# Exercise 7 — Distributed Databases on AWS

IFCD0078 · Arquitectura Cloud & Data Engineering · Profesor: Manu Herrán

## Scope

1. **ACID:** Amazon RDS MySQL **Multi-AZ DB instance** (one active writer plus synchronous standby), five accounts with an initial total of EUR 10,000, continuous committed transfers, forced failover, RTO/RPO and COMMIT latency.
2. **BASE:** Three independent DynamoDB tables and three Lambda functions in Ireland, Northern Virginia and Tokyo. Regional hashtag counts aggregated by a coordinator, with full, Top-2, Top-3 and one-region-down scenarios. No DynamoDB global tables.

## Important: AWS costs

**Do not run `terraform apply` until ready to perform the tests.** RDS Multi-AZ is billable, including standby, storage and related usage; cross-region services can also incur charges. Destroy immediately after collecting evidence. No resources are deployed by unpacking this repository.

## Requirements

Terraform, AWS CLI, Python 3.11+, authenticated AWS CLI profile `terraform`, IAM permissions to create RDS/VPC/DynamoDB/Lambda/IAM/CloudWatch resources. Existing **default VPC and subnets in `eu-south-2`**. An AWS account with service quotas sufficient for three regional Lambda functions and RDS Multi-AZ.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/base/generar_datos.py
Copy-Item terraform/terraform.tfvars.example terraform/terraform.tfvars
# EDIT terraform/terraform.tfvars and set allowed_cidr to your current public IP /32
cd terraform
terraform init
terraform fmt
terraform validate
terraform plan
# REVIEW COSTS AND RESOURCES BEFORE apply
terraform apply
```

For RDS TLS verification, download the official *public* CA bundle (not a secret):

```powershell
New-Item -ItemType Directory -Force certs
Invoke-WebRequest -Uri "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem" -OutFile "certs/global-bundle.pem"
```

## ACID execution

After RDS is available, from project root:

```powershell
python scripts/acid/estado_az.py
python scripts/acid/inicializar.py
python scripts/acid/transferencias.py
```

While `transferencias.py` runs, in **another PowerShell terminal**, record the primary AZ (`estado_az.py`) and force a Multi-AZ DB **instance** failover:

```powershell
aws rds reboot-db-instance --db-instance-identifier ej7-banco-mysql --force-failover --region eu-south-2 --profile terraform
```

Leave the workload running until successful transactions resume. Stop with Ctrl+C, then:

```powershell
python scripts/acid/estado_az.py
python scripts/acid/verificar.py
```

The `results/transferencias.csv` contains customer-confirmed commits and COMMIT latencies. **RTO must be calculated from observed timestamps around the disruption** (first failed write to first subsequent successful write, or a separately documented measurement convention), not assumed from AWS published estimates. SQL operations use a single transaction and unique transfer ID. A lost TCP connection during COMMIT creates a potentially ambiguous outcome and should not automatically be retried under the same logical operation. `verificar.py` checks all acknowledged transfer IDs exist, no duplicate IDs and balances total EUR 10,000. A statement that RPO=0 is justified **for observed acknowledged transactions**, not unobserved ambiguous commits.

**AZ caveat:** the RDS DB instance API exposes the active primary AZ. AWS chooses the standby AZ in another AZ and does not expose it as a separately addressable DB instance. Evidence should show primary AZ before/after, plus MultiAZ=true and the recorded failover event.

## BASE execution

```powershell
python scripts/base/generar_datos.py
python scripts/base/cargar_datos.py
python scripts/base/coordinador.py
```

Expected by construction: `#cloud` ranks **third in each region** (25 posts), but leads globally at 75. Top-2 misses `#cloud` and produces a wrong/tied regional winner; Top-3 captures it, and full counts agree. All regions have 100 unique messages. The coordinator saves JSON results under ignored `results/`.

For the partial scenario, when prompted by the coordinator, **in a second terminal**:

```powershell
aws lambda put-function-concurrency --function-name ej7-hashtags-tokio --reserved-concurrent-executions 0 --region ap-northeast-1 --profile terraform
```

Then press Enter to calculate the partial result. **Restore Tokyo before cleanup**:

```powershell
aws lambda delete-function-concurrency --function-name ej7-hashtags-tokio --region ap-northeast-1 --profile terraform
```

## Cleanup

```powershell
cd terraform
terraform destroy
terraform state list
```

Verify RDS, three DynamoDB tables, three Lambda functions, three CloudWatch log groups, shared IAM role, SG and subnet group are absent, plus check AWS Billing. Capture real screenshots for `docs/capturas/`. Never commit secrets, tfvars, state, certificate bundles, or local result logs. An evidence report in the previous exercise's style will be placed in `docs/evidencias.pdf` after running the tests.
