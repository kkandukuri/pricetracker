#!/bin/bash
# AWS Lambda Deployment Script for UPC Price Lookup

set -e

FUNCTION_NAME="upc-price-lookup"
REGION="${AWS_REGION:-us-east-1}"
RUNTIME="python3.11"
HANDLER="lambda_upc_handler.lambda_handler"
MEMORY=512
TIMEOUT=300
ROLE_NAME="lambda-upc-execution-role"

echo "========================================"
echo "AWS Lambda Deployment - UPC Price Lookup"
echo "========================================"

# Step 1: Create IAM role if it doesn't exist
echo "Checking IAM role..."
if ! aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    echo "Creating IAM role..."
    aws iam create-role --role-name $ROLE_NAME \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }'

    # Attach basic execution policy
    aws iam attach-role-policy --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    echo "Waiting for IAM role to be available..."
    sleep 10
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "Using IAM Role: $ROLE_ARN"

# Step 2: Create deployment package
echo "Creating deployment package..."
cd "$(dirname "$0")/.."
mkdir -p lambda_deployment
cd lambda_deployment

# Copy files
cp ../upc_price_lookup.py .
cp ../lambda_upc_handler.py .

# Install dependencies
echo "Installing dependencies..."
pip install requests -t . -q

# Create ZIP
echo "Creating ZIP package..."
zip -r lambda_upc_function.zip . -q

PACKAGE_SIZE=$(du -h lambda_upc_function.zip | cut -f1)
echo "Package size: $PACKAGE_SIZE"

# Step 3: Create or update Lambda function
echo "Deploying Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_upc_function.zip \
        --region $REGION

    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --memory-size $MEMORY \
        --timeout $TIMEOUT \
        --environment 'Variables={RATE_LIMIT=20,COUNTRY_CODE=US,CURRENCY=USD}' \
        --region $REGION
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
        --environment 'Variables={RATE_LIMIT=20,COUNTRY_CODE=US,CURRENCY=USD}' \
        --region $REGION
fi

# Cleanup
cd ..
rm -rf lambda_deployment

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo "Package Size: $PACKAGE_SIZE"
echo ""
echo "Test with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME \\"
echo "  --payload '{\"upcs\":[\"NOW-00453\"]}' \\"
echo "  --region $REGION \\"
echo "  response.json"
echo ""
echo "View logs:"
echo "aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
echo ""
