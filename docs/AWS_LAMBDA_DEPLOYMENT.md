# AWS Lambda Deployment Guide - UPC Price Lookup

This guide explains how to deploy the UPC Price Lookup tool as an AWS Lambda function.

## Table of Contents
- [Overview](#overview)
- [Is Lambda Feasible?](#is-lambda-feasible)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Manual Deployment](#manual-deployment)
- [Automated Deployment](#automated-deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The UPC Price Lookup tool can be deployed as an AWS Lambda function, allowing you to:
- Query product prices on-demand via API
- Process UPC lookups serverlessly without maintaining infrastructure
- Scale automatically based on demand
- Pay only for actual usage

---

## Is Lambda Feasible?

**YES**, AWS Lambda is feasible for UPC price lookups with these considerations:

### ✅ Advantages
1. **Cost-effective**: Pay per request, no idle costs
2. **Scalable**: Handles concurrent requests automatically
3. **No infrastructure**: Fully managed service
4. **API Gateway integration**: Easy REST API setup
5. **Low latency**: Fast cold starts for Python

### ⚠️ Limitations & Considerations

#### 1. **Timeout Constraints**
- **Default timeout**: 3 seconds
- **Maximum timeout**: 15 minutes (900 seconds)
- **Recommendation**: Set to 5-15 minutes depending on batch size

**Calculation**:
```
Rate limit: 20 calls/min = 3 seconds per call
Maximum UPCs per invocation = (timeout - 10s buffer) / 3
```

Examples:
- 5-min timeout → ~96 UPCs max
- 10-min timeout → ~196 UPCs max
- 15-min timeout → ~296 UPCs max

#### 2. **Memory**
- **Minimum required**: 256 MB
- **Recommended**: 512 MB for better performance
- More memory = faster CPU = quicker processing

#### 3. **Cold Starts**
- First invocation may take 1-3 seconds to initialize
- Subsequent requests (within 15 min) are "warm" and faster
- Use provisioned concurrency for production if needed

#### 4. **Rate Limiting**
- Configure rate limit to avoid API blocking
- Default: 20 calls/min (configurable)
- Lambda handles the delays automatically

#### 5. **Concurrency**
- Default: 1000 concurrent executions per region
- Each invocation processes its batch independently
- No conflicts with rate limiting per invocation

---

## Prerequisites

### AWS Account Setup
1. AWS account with Lambda access
2. AWS CLI installed and configured
3. IAM permissions for Lambda, API Gateway, CloudWatch

### Local Requirements
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Install packaging tools
pip install boto3
```

---

## Deployment Options

### Option 1: Manual Deployment (Quick Start)
Best for testing and small deployments

### Option 2: Automated Deployment (Production)
Using deployment scripts and CloudFormation/Terraform

### Option 3: Serverless Framework
Using serverless.yml configuration

---

## Manual Deployment

### Step 1: Create Deployment Package

```bash
# Navigate to project directory
cd /home/user/pricetracker

# Create deployment directory
mkdir -p lambda_deployment
cd lambda_deployment

# Copy required files
cp ../upc_price_lookup.py .
cp ../lambda_upc_handler.py .

# Install dependencies to local directory
pip install requests -t .

# Create ZIP package
zip -r lambda_upc_function.zip .
```

### Step 2: Create Lambda Function via AWS Console

1. **Go to AWS Lambda Console**: https://console.aws.amazon.com/lambda

2. **Create Function**:
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `upc-price-lookup`
   - Runtime: `Python 3.11` (or latest)
   - Architecture: `x86_64`
   - Click "Create function"

3. **Upload Code**:
   - In "Code" tab, click "Upload from"
   - Select ".zip file"
   - Upload `lambda_upc_function.zip`
   - Click "Save"

4. **Configure Handler**:
   - In "Runtime settings", click "Edit"
   - Handler: `lambda_upc_handler.lambda_handler`
   - Click "Save"

5. **Configure Settings**:
   - **Memory**: 512 MB (recommended)
   - **Timeout**: 5 minutes (300 seconds) for ~96 UPCs
   - **Environment variables**:
     - `RATE_LIMIT`: `20`
     - `COUNTRY_CODE`: `US`
     - `CURRENCY`: `USD`

### Step 3: Create API Gateway (Optional)

1. **Go to API Gateway Console**: https://console.aws.amazon.com/apigateway

2. **Create REST API**:
   - Click "Create API"
   - Choose "REST API" (not private)
   - API name: `upc-price-lookup-api`
   - Click "Create API"

3. **Create Resource & Method**:
   - Click "Actions" → "Create Resource"
   - Resource name: `lookup`
   - Click "Create Resource"
   - Select `/lookup` → "Actions" → "Create Method"
   - Choose `POST`
   - Integration type: Lambda Function
   - Lambda function: `upc-price-lookup`
   - Click "Save" and confirm permissions

4. **Enable CORS**:
   - Select `/lookup` resource
   - Click "Actions" → "Enable CORS"
   - Click "Enable CORS and replace existing headers"

5. **Deploy API**:
   - Click "Actions" → "Deploy API"
   - Stage: `prod`
   - Click "Deploy"
   - Copy the Invoke URL (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

---

## Automated Deployment

### Using Deployment Script

Create `deployment/deploy_lambda.sh`:

```bash
#!/bin/bash
# AWS Lambda Deployment Script for UPC Price Lookup

set -e

FUNCTION_NAME="upc-price-lookup"
REGION="us-east-1"
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
mkdir -p lambda_deployment
cd lambda_deployment

# Copy files
cp ../upc_price_lookup.py .
cp ../lambda_upc_handler.py .

# Install dependencies
pip install requests -t . -q

# Create ZIP
zip -r lambda_upc_function.zip . -q

echo "Package size: $(du -h lambda_upc_function.zip | cut -f1)"

# Step 3: Create or update Lambda function
echo "Deploying Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME 2>/dev/null; then
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
        --environment Variables={RATE_LIMIT=20,COUNTRY_CODE=US,CURRENCY=USD} \
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
        --environment Variables={RATE_LIMIT=20,COUNTRY_CODE=US,CURRENCY=USD} \
        --region $REGION
fi

# Cleanup
cd ..
rm -rf lambda_deployment

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo ""
echo "Test with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME \\"
echo "  --payload '{\"upcs\":[\"NOW-00453\"]}' \\"
echo "  --region $REGION \\"
echo "  response.json"
echo ""
```

Make it executable:
```bash
chmod +x deployment/deploy_lambda.sh
```

Run deployment:
```bash
./deployment/deploy_lambda.sh
```

---

## Testing

### Test via AWS CLI

```bash
# Single UPC
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upc": "NOW-00453"}' \
  --region us-east-1 \
  response.json

cat response.json | python -m json.tool

# Multiple UPCs
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upcs": ["NOW-00453", "123456789012"], "rate_limit": 20}' \
  --region us-east-1 \
  response.json

cat response.json | python -m json.tool
```

### Test via API Gateway (if configured)

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "upcs": ["NOW-00453"],
    "rate_limit": 20,
    "country_code": "US",
    "currency": "USD"
  }'
```

### Test Locally (Before Deployment)

```bash
python lambda_upc_handler.py
```

---

## Cost Estimation

### Lambda Pricing (us-east-1)
- **Requests**: $0.20 per 1M requests
- **Compute**: $0.0000166667 per GB-second

### Example Calculation
**Scenario**: 1000 UPC lookups per day, 50 UPCs per batch, 512MB memory, 5min timeout

- Requests per day: 20 invocations (1000 UPCs ÷ 50)
- Compute time: 5 min × 20 = 100 minutes = 6000 seconds
- GB-seconds: 0.5 GB × 6000s = 3000 GB-seconds

**Monthly Cost**:
- Requests: 20 × 30 days = 600 requests → **$0.00012**
- Compute: 3000 × 30 days = 90,000 GB-seconds → **$1.50**
- **Total: ~$1.50/month**

**Free Tier** (first 12 months):
- 1M requests/month free
- 400,000 GB-seconds/month free
- Your usage would be **FREE**!

---

## Troubleshooting

### Issue: Function Timeout

**Symptoms**: Lambda times out before completing

**Solutions**:
1. Increase Lambda timeout (max 15 minutes)
2. Reduce batch size per invocation
3. Increase rate limit (but risk API blocking)
4. Split into multiple Lambda invocations

### Issue: Rate Limit Errors from API

**Symptoms**: API returns 429 Too Many Requests

**Solutions**:
1. Decrease rate limit (e.g., from 20 to 10 calls/min)
2. Add exponential backoff retry logic
3. Use multiple Lambda functions with different IPs

### Issue: Cold Start Latency

**Symptoms**: First request takes 3-5 seconds

**Solutions**:
1. Use Lambda Provisioned Concurrency (costs more)
2. Implement warming strategy (scheduled CloudWatch event)
3. Accept cold starts (usually not an issue)

### Issue: Memory Errors

**Symptoms**: Function runs out of memory

**Solutions**:
1. Increase memory allocation (512MB → 1024MB)
2. Process smaller batches
3. Clear results list periodically

### Issue: Package Too Large

**Symptoms**: Deployment package exceeds 50MB limit

**Solutions**:
1. Use Lambda Layers for requests library
2. Minimize dependencies
3. Use S3 for large packages

---

## Production Best Practices

### 1. Monitoring
```bash
# Enable CloudWatch Logs
# Logs are automatically sent to CloudWatch

# Create CloudWatch Alarms
aws cloudwatch put-metric-alarm \
  --alarm-name upc-lookup-errors \
  --alarm-description "Alert on UPC lookup errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### 2. Error Handling
- Implement retry logic for transient failures
- Use Dead Letter Queue (DLQ) for failed invocations
- Log all errors to CloudWatch

### 3. Security
- Use IAM roles with least privilege
- Encrypt environment variables
- Use VPC if accessing private resources
- Enable AWS X-Ray for tracing

### 4. Rate Limiting
- Start conservative (10-15 calls/min)
- Monitor for API errors
- Gradually increase if stable

### 5. Cost Optimization
- Use appropriate memory (512MB is good start)
- Set reasonable timeout (5-10 min)
- Monitor invocations with CloudWatch
- Use reserved concurrency if needed

---

## Alternative: Step Functions for Large Batches

For processing thousands of UPCs, use AWS Step Functions:

```yaml
# Orchestrate multiple Lambda invocations
# Each processes 50 UPCs in parallel
# Aggregates results at the end
```

Benefits:
- Process unlimited UPCs
- Parallel execution
- Built-in retry logic
- Visual monitoring

---

## Conclusion

**AWS Lambda is FEASIBLE and RECOMMENDED for UPC price lookups!**

**Use when**:
- Processing batches of 1-300 UPCs per request
- Sporadic usage patterns
- Want low operational overhead
- Cost-conscious

**Consider alternatives when**:
- Processing thousands of UPCs continuously
- Need sub-second response times
- Have existing server infrastructure

For most use cases, Lambda provides the best balance of cost, scalability, and simplicity.
