#!/bin/bash
#
# AWS SAM DEPLOYMENT (Simplest Method)
#
# This script uses AWS SAM (Serverless Application Model) for deployment.
# SAM is the easiest way to deploy Lambda functions!
#
# Usage: ./deployment/sam_deploy.sh
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       AWS SAM DEPLOYMENT (Recommended Method)                  ║${NC}"
echo -e "${BLUE}║       UPC Price Lookup Tool                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${YELLOW}AWS SAM CLI not found. Installing...${NC}"
    echo ""
    echo "Please install AWS SAM CLI:"
    echo "  macOS:  brew install aws-sam-cli"
    echo "  Linux:  pip install aws-sam-cli"
    echo "  Windows: See https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ AWS SAM CLI found${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${YELLOW}AWS credentials not configured${NC}"
    aws configure
fi

echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Step 1: Build
echo -e "${YELLOW}[Step 1/2]${NC} Building SAM application..."
sam build --use-container 2>&1 | grep -v "^Running"  || sam build
echo -e "${GREEN}✓ Build complete${NC}"
echo ""

# Step 2: Deploy
echo -e "${YELLOW}[Step 2/2]${NC} Deploying to AWS..."
sam deploy \
    --guided \
    --stack-name upc-price-lookup-stack \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides RateLimit=20 CountryCode=US Currency=USD

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 🎉 DEPLOYMENT SUCCESSFUL! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get outputs
STACK_NAME="upc-price-lookup-stack"
REGION=$(aws configure get region || echo "us-east-1")

echo -e "${BLUE}Getting deployment outputs...${NC}"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo -e "${BLUE}Quick Test:${NC}"
echo -e "${YELLOW}sam remote invoke UPCPriceLookupFunction --event '{\"upcs\": [\"733739004536\"]}'${NC}"
echo ""
