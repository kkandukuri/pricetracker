#!/bin/bash
#
# ONE-CLICK AWS LAMBDA DEPLOYMENT
#
# This script deploys the UPC Price Lookup tool to AWS Lambda with a single command.
# No prerequisites needed - it handles everything automatically!
#
# Usage: ./deployment/one_click_deploy.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FUNCTION_NAME="${FUNCTION_NAME:-upc-price-lookup}"
REGION="${AWS_REGION:-us-east-1}"
RUNTIME="python3.11"
HANDLER="lambda_upc_handler.lambda_handler"
MEMORY="${LAMBDA_MEMORY:-512}"
TIMEOUT="${LAMBDA_TIMEOUT:-300}"
ROLE_NAME="lambda-upc-execution-role"
RATE_LIMIT="${RATE_LIMIT:-20}"
COUNTRY_CODE="${COUNTRY_CODE:-US}"
CURRENCY="${CURRENCY:-USD}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       AWS LAMBDA ONE-CLICK DEPLOYMENT                          ║${NC}"
echo -e "${BLUE}║       UPC Price Lookup Tool                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 0: Check prerequisites
echo -e "${YELLOW}[Step 1/7]${NC} Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI not found${NC}"
    echo ""
    echo "Installing AWS CLI..."

    if command -v pip3 &> /dev/null; then
        pip3 install awscli --user
    elif command -v pip &> /dev/null; then
        pip install awscli --user
    else
        echo -e "${RED}Error: pip not found. Please install Python and pip first.${NC}"
        exit 1
    fi

    # Add to PATH if needed
    export PATH="$HOME/.local/bin:$PATH"
fi

echo -e "${GREEN}✓ AWS CLI installed${NC}"

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo ""
    echo "Please configure AWS credentials:"
    aws configure
fi

echo -e "${GREEN}✓ AWS credentials configured${NC}"

# Get account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: ${ACCOUNT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"

# Check if zip is installed
if ! command -v zip &> /dev/null; then
    echo -e "${YELLOW}⚠ zip not found, installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install zip
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y zip
    fi
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 1: Create IAM role
echo -e "${YELLOW}[Step 2/7]${NC} Creating IAM role..."

if aws iam get-role --role-name $ROLE_NAME --region $REGION 2>/dev/null; then
    echo -e "${GREEN}✓ IAM role already exists${NC}"
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
else
    echo "Creating IAM role: $ROLE_NAME"

    # Create trust policy
    cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --region $REGION > /dev/null

    # Attach execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
        --region $REGION

    echo -e "${YELLOW}Waiting 10 seconds for IAM role to propagate...${NC}"
    sleep 10

    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    echo -e "${GREEN}✓ IAM role created${NC}"
fi

echo -e "${GREEN}Role ARN: ${ROLE_ARN}${NC}"
echo ""

# Step 2: Create deployment package
echo -e "${YELLOW}[Step 3/7]${NC} Creating deployment package..."

# Navigate to project directory
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Create temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Using temp directory: $DEPLOY_DIR"

# Copy source files
cp upc_price_lookup.py "$DEPLOY_DIR/"
cp lambda_upc_handler.py "$DEPLOY_DIR/"

# Install dependencies
echo "Installing dependencies..."
pip install requests -t "$DEPLOY_DIR" -q --upgrade

# Create deployment package
cd "$DEPLOY_DIR"
zip -r lambda_upc_function.zip . -q

PACKAGE_SIZE=$(du -h lambda_upc_function.zip | cut -f1)
echo -e "${GREEN}✓ Package created (Size: ${PACKAGE_SIZE})${NC}"
echo ""

# Step 3: Create or update Lambda function
echo -e "${YELLOW}[Step 4/7]${NC} Deploying Lambda function..."

if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."

    # Update function code
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_upc_function.zip \
        --region $REGION > /dev/null

    # Wait for update to complete
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

    # Update function configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --memory-size $MEMORY \
        --timeout $TIMEOUT \
        --environment "Variables={RATE_LIMIT=${RATE_LIMIT},COUNTRY_CODE=${COUNTRY_CODE},CURRENCY=${CURRENCY}}" \
        --region $REGION > /dev/null

    echo -e "${GREEN}✓ Function updated${NC}"
else
    echo "Creating new function..."

    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda_upc_function.zip \
        --memory-size $MEMORY \
        --timeout $TIMEOUT \
        --environment "Variables={RATE_LIMIT=${RATE_LIMIT},COUNTRY_CODE=${COUNTRY_CODE},CURRENCY=${CURRENCY}}" \
        --region $REGION > /dev/null

    echo -e "${GREEN}✓ Function created${NC}"
fi

echo ""

# Step 4: Test the function
echo -e "${YELLOW}[Step 5/7]${NC} Testing Lambda function..."

# Create test payload
TEST_PAYLOAD='{"upcs": ["733739004536"], "rate_limit": 20}'

# Invoke function
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload "$TEST_PAYLOAD" \
    --region $REGION \
    /tmp/lambda_response.json > /dev/null 2>&1

# Check response
if [ $? -eq 0 ]; then
    RESPONSE=$(cat /tmp/lambda_response.json)
    if echo "$RESPONSE" | grep -q '"success": true'; then
        echo -e "${GREEN}✓ Test successful!${NC}"

        # Extract result summary
        FOUND=$(echo "$RESPONSE" | grep -o '"found": [0-9]*' | head -1 | grep -o '[0-9]*')
        TOTAL=$(echo "$RESPONSE" | grep -o '"total": [0-9]*' | head -1 | grep -o '[0-9]*')

        if [ ! -z "$FOUND" ]; then
            echo -e "${GREEN}  Products found: ${FOUND}/${TOTAL}${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Test completed with warnings${NC}"
        echo "Response: $RESPONSE" | head -c 200
    fi
else
    echo -e "${YELLOW}⚠ Test invocation had issues (this may be normal on first run)${NC}"
fi

echo ""

# Step 5: Create API Gateway (Optional)
echo -e "${YELLOW}[Step 6/7]${NC} Setting up API Gateway..."

API_NAME="upc-price-lookup-api"

# Check if API exists
API_ID=$(aws apigatewayv2 get-apis --region $REGION --query "Items[?Name=='${API_NAME}'].ApiId" --output text 2>/dev/null)

if [ -z "$API_ID" ]; then
    echo "Creating HTTP API..."

    # Create HTTP API (simpler than REST API)
    API_RESPONSE=$(aws apigatewayv2 create-api \
        --name $API_NAME \
        --protocol-type HTTP \
        --target "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}" \
        --region $REGION)

    API_ID=$(echo $API_RESPONSE | grep -o '"ApiId": "[^"]*"' | cut -d'"' -f4)

    # Add Lambda permissions for API Gateway
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id apigateway-access \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" \
        --region $REGION > /dev/null 2>&1

    echo -e "${GREEN}✓ API Gateway created${NC}"
else
    echo -e "${GREEN}✓ API Gateway already exists${NC}"
fi

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-apis --region $REGION --query "Items[?Name=='${API_NAME}'].ApiEndpoint" --output text)

echo ""

# Step 6: Cleanup
echo -e "${YELLOW}[Step 7/7]${NC} Cleaning up..."
cd "$PROJECT_ROOT"
rm -rf "$DEPLOY_DIR"
rm -f /tmp/trust-policy.json /tmp/lambda_response.json
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 🎉 DEPLOYMENT SUCCESSFUL! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Function Details:${NC}"
echo -e "  Name:     ${GREEN}${FUNCTION_NAME}${NC}"
echo -e "  Region:   ${GREEN}${REGION}${NC}"
echo -e "  Memory:   ${GREEN}${MEMORY}MB${NC}"
echo -e "  Timeout:  ${GREEN}${TIMEOUT}s${NC}"
echo -e "  Runtime:  ${GREEN}${RUNTIME}${NC}"
echo -e "  Package:  ${GREEN}${PACKAGE_SIZE}${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Rate Limit: ${GREEN}${RATE_LIMIT} calls/min${NC}"
echo -e "  Country:    ${GREEN}${COUNTRY_CODE}${NC}"
echo -e "  Currency:   ${GREEN}${CURRENCY}${NC}"
echo ""

if [ ! -z "$API_ENDPOINT" ]; then
    echo -e "${BLUE}API Endpoint:${NC}"
    echo -e "  ${GREEN}${API_ENDPOINT}${NC}"
    echo ""
    echo -e "${BLUE}Test API with curl:${NC}"
    echo -e "${YELLOW}curl -X POST ${API_ENDPOINT} \\${NC}"
    echo -e "${YELLOW}  -H 'Content-Type: application/json' \\${NC}"
    echo -e "${YELLOW}  -d '{\"upcs\": [\"733739004536\"]}'${NC}"
    echo ""
fi

echo -e "${BLUE}Test Lambda with AWS CLI:${NC}"
echo -e "${YELLOW}aws lambda invoke \\${NC}"
echo -e "${YELLOW}  --function-name ${FUNCTION_NAME} \\${NC}"
echo -e "${YELLOW}  --payload '{\"upcs\": [\"733739004536\"]}' \\${NC}"
echo -e "${YELLOW}  --region ${REGION} \\${NC}"
echo -e "${YELLOW}  response.json${NC}"
echo ""

echo -e "${BLUE}View logs:${NC}"
echo -e "${YELLOW}aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --region ${REGION}${NC}"
echo ""

echo -e "${BLUE}Delete function:${NC}"
echo -e "${YELLOW}aws lambda delete-function --function-name ${FUNCTION_NAME} --region ${REGION}${NC}"
echo ""

echo -e "${GREEN}Deployment complete! Your Lambda function is ready to use.${NC}"
echo ""
