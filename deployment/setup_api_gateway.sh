#!/bin/bash
#
# Setup API Gateway for existing Lambda function
# This creates an HTTP API that allows web access to your Lambda function
#

set -e

# Configuration
FUNCTION_NAME="${FUNCTION_NAME:-upc-price-lookup}"
REGION="${AWS_REGION:-us-east-1}"
API_NAME="upc-price-lookup-api"

echo "========================================"
echo "Setting up API Gateway for Lambda"
echo "========================================"
echo ""

# Get AWS Account ID
echo "Getting AWS account information..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# Check if API already exists
echo "Checking for existing API Gateway..."
API_ID=$(aws apigatewayv2 get-apis --region $REGION --query "Items[?Name=='${API_NAME}'].ApiId" --output text 2>/dev/null)

if [ -z "$API_ID" ]; then
    echo "Creating new HTTP API Gateway..."

    # Create HTTP API with Lambda integration
    API_RESPONSE=$(aws apigatewayv2 create-api \
        --name "$API_NAME" \
        --protocol-type HTTP \
        --target "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}" \
        --region $REGION)

    API_ID=$(echo $API_RESPONSE | grep -o '"ApiId": "[^"]*"' | cut -d'"' -f4)

    echo "✓ API Gateway created (ID: $API_ID)"

    # Add Lambda permission for API Gateway to invoke the function
    echo "Adding Lambda permissions..."
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id apigateway-access \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" \
        --region $REGION > /dev/null 2>&1 || echo "Permission already exists"

    echo "✓ Permissions configured"
else
    echo "✓ API Gateway already exists (ID: $API_ID)"
fi

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api --api-id $API_ID --region $REGION --query 'ApiEndpoint' --output text)

echo ""
echo "========================================"
echo "✅ API Gateway Ready!"
echo "========================================"
echo ""
echo "API Endpoint:"
echo "  $API_ENDPOINT"
echo ""
echo "Test with curl:"
echo "  curl -X POST $API_ENDPOINT \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"upcs\": [\"733739004536\"]}'"
echo ""
echo "Test with browser (GET request):"
echo "  ${API_ENDPOINT}?upcs=733739004536"
echo ""
echo "Delete API Gateway:"
echo "  aws apigatewayv2 delete-api --api-id $API_ID --region $REGION"
echo ""
