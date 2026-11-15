#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CLIENT_CIDR="${1:-}"
REVISION="${2:-main}"
REPLACE="${3:-}"

if [[ ! "$CLIENT_CIDR" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}/32$ ]]; then
  echo "Usage: $0 <your-ip/32> [git-ref] [--replace-app]"
  exit 1
fi

echo "Checking AWS identity..."
aws sts get-caller-identity \
  --query Arn --output text

echo "Deploying network..."
aws cloudformation deploy \
  --template-file "$ROOT/infra/network.yaml" \
  --stack-name capstone-network \
  --region "$REGION" \
  --no-fail-on-empty-changeset

echo "Reading network outputs..."

VPC_ID=$(aws cloudformation describe-stacks \
  --stack-name capstone-network \
  --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='VpcId'].OutputValue | [0]" \
  --output text)

SUBNET_ID=$(aws cloudformation describe-stacks \
  --stack-name capstone-network \
  --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='PublicSubnetId'].OutputValue | [0]" \
  --output text)

if [[ "$VPC_ID" == "None" || "$SUBNET_ID" == "None" ]]; then
  echo "Missing network outputs"
  exit 1
fi

if aws cloudformation describe-stacks \
  --stack-name capstone-application \
  --region "$REGION" >/dev/null 2>&1; then

  if [[ "$REPLACE" != "--replace-app" ]]; then
    echo "Application stack already exists."
    echo "Use --replace-app to recreate it."
    echo "WARNING: in-memory data will be lost."
    exit 1
  fi

  echo "Replacing application stack..."
  aws cloudformation delete-stack \
    --stack-name capstone-application \
    --region "$REGION"

  aws cloudformation wait stack-delete-complete \
    --stack-name capstone-application \
    --region "$REGION"
fi

echo "Deploying application..."
aws cloudformation deploy \
  --template-file "$ROOT/infra/application.yaml" \
  --stack-name capstone-application \
  --region "$REGION" \
  --parameter-overrides \
    "VpcId=$VPC_ID" \
    "PublicSubnetId=$SUBNET_ID" \
    "AllowedClientCidr=$CLIENT_CIDR" \
    "CodeRevision=$REVISION"

echo "Deployment outputs:"
aws cloudformation describe-stacks \
  --stack-name capstone-application \
  --region "$REGION" \
  --query 'Stacks[0].Outputs' \
  --output table

echo "CloudFormation deployment complete."
echo "Check Coordinator /health from your MacBook."
