# One-Click AWS Lambda Deployment

This directory contains everything you need to deploy the UPC Price Lookup tool to AWS Lambda with a single command.

## 🚀 Quick Start (3 Options)

### Option 1: One-Click Script (Recommended - No SAM Required)

**Easiest method - Just run one command!**

```bash
./deployment/one_click_deploy.sh
```

**What it does:**
- ✅ Checks and installs AWS CLI if needed
- ✅ Configures AWS credentials if needed
- ✅ Creates IAM role automatically
- ✅ Packages dependencies
- ✅ Deploys Lambda function
- ✅ Creates API Gateway endpoint
- ✅ Tests the deployment
- ✅ Displays all endpoints and commands

**Requirements:** Just bash and Python!

---

### Option 2: AWS SAM (Best for Production)

**Most powerful method with infrastructure-as-code**

```bash
# Install SAM CLI (one time only)
pip install aws-sam-cli

# Deploy
sam build && sam deploy --guided
```

**What it does:**
- ✅ Creates Lambda function
- ✅ Creates API Gateway
- ✅ Sets up CloudWatch Logs
- ✅ Manages all permissions
- ✅ Supports easy updates

**Requirements:** AWS SAM CLI

---

### Option 3: Manual Deployment Script

**For customization and control**

```bash
./deployment/deploy_lambda.sh
```

**Requirements:** AWS CLI configured

---

## 📋 Prerequisites

### Minimum Requirements

1. **AWS Account** - [Sign up](https://aws.amazon.com/free)
2. **AWS Credentials** - IAM user with Lambda + IAM + API Gateway permissions

### AWS Credentials Setup

If you haven't configured AWS credentials:

```bash
# Interactive setup
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Permissions needed:**
- `lambda:*` (Lambda full access)
- `iam:CreateRole`, `iam:AttachRolePolicy` (IAM for execution role)
- `apigateway:*` (API Gateway access)
- `logs:*` (CloudWatch Logs)

---

## 🎯 Option 1: One-Click Deployment (Detailed)

### Step-by-Step

```bash
# 1. Navigate to project directory
cd /home/user/pricetracker

# 2. Make script executable (if needed)
chmod +x deployment/one_click_deploy.sh

# 3. Run deployment
./deployment/one_click_deploy.sh

# That's it! ✅
```

### What Happens

```
[Step 1/7] Checking prerequisites
  ✓ AWS CLI installed
  ✓ AWS credentials configured
  ✓ AWS Account: 123456789012
  ✓ Region: us-east-1

[Step 2/7] Creating IAM role
  ✓ IAM role created

[Step 3/7] Creating deployment package
  ✓ Package created (Size: 2.5M)

[Step 4/7] Deploying Lambda function
  ✓ Function created

[Step 5/7] Testing Lambda function
  ✓ Test successful!
  Products found: 1/1

[Step 6/7] Setting up API Gateway
  ✓ API Gateway created

[Step 7/7] Cleaning up
  ✓ Cleanup complete

🎉 DEPLOYMENT SUCCESSFUL! 🎉
```

### Customization

Set environment variables before deployment:

```bash
# Custom function name
export FUNCTION_NAME=my-upc-lookup

# Different region
export AWS_REGION=us-west-2

# More memory
export LAMBDA_MEMORY=1024

# Longer timeout (max 900 seconds = 15 minutes)
export LAMBDA_TIMEOUT=600

# Custom rate limit
export RATE_LIMIT=30

# Different country/currency
export COUNTRY_CODE=CA
export CURRENCY=CAD

# Deploy with custom settings
./deployment/one_click_deploy.sh
```

---

## 🎯 Option 2: AWS SAM Deployment (Detailed)

### Installation

```bash
# macOS
brew install aws-sam-cli

# Linux
pip install aws-sam-cli

# Windows
# Download from: https://aws.amazon.com/serverless/sam/
```

### Deployment Steps

```bash
# 1. Navigate to project root
cd /home/user/pricetracker

# 2. Build
sam build

# 3. Deploy (first time - guided)
sam deploy --guided

# Follow prompts:
# - Stack name: upc-price-lookup-stack
# - Region: us-east-1
# - Parameter RateLimit: 20
# - Parameter CountryCode: US
# - Parameter Currency: USD
# - Allow SAM CLI IAM role creation: Y
# - Allow Lambda URL: N (we use API Gateway)
# - Save arguments to config: Y

# 4. Future deployments (one command)
sam deploy
```

### SAM Template

The `template.yaml` defines:
- Lambda function with 512MB memory, 5min timeout
- HTTP API Gateway with CORS enabled
- CloudWatch Logs with 7-day retention
- Environment variables (RATE_LIMIT, COUNTRY_CODE, CURRENCY)

### SAM Commands

```bash
# Build application
sam build

# Deploy application
sam deploy

# Test locally
sam local invoke UPCPriceLookupFunction -e events/test.json

# View logs
sam logs -n UPCPriceLookupFunction --tail

# Delete stack
sam delete
```

---

## 🎯 Option 3: Manual Script (Detailed)

```bash
# 1. Navigate to project
cd /home/user/pricetracker

# 2. Run deployment
./deployment/deploy_lambda.sh

# 3. Check status
aws lambda get-function --function-name upc-price-lookup
```

---

## 🧪 Testing Your Deployment

### Test via AWS CLI

```bash
# Single UPC
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upc": "733739004536"}' \
  response.json

cat response.json | python -m json.tool

# Multiple UPCs
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upcs": ["733739004536", "NOW-00453"], "rate_limit": 20}' \
  response.json
```

### Test via API Gateway

Get your API endpoint from deployment output, then:

```bash
# Replace YOUR_API_ENDPOINT with actual endpoint
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "upcs": ["733739004536"],
    "rate_limit": 20,
    "country_code": "US",
    "currency": "USD"
  }'
```

### Test via SAM (Local)

```bash
# Test locally before deploying
sam local invoke UPCPriceLookupFunction \
  --event events/test.json
```

---

## 📊 Monitoring

### View Logs

```bash
# AWS CLI
aws logs tail /aws/lambda/upc-price-lookup --follow

# SAM CLI
sam logs -n UPCPriceLookupFunction --tail

# AWS Console
# Go to CloudWatch → Log Groups → /aws/lambda/upc-price-lookup
```

### Metrics

View metrics in AWS Console:
1. Go to Lambda → Functions → upc-price-lookup
2. Click "Monitoring" tab
3. View:
   - Invocations
   - Duration
   - Errors
   - Throttles

---

## 🔄 Updating Your Function

### Update Code

```bash
# Option 1: One-click script (re-run)
./deployment/one_click_deploy.sh

# Option 2: SAM
sam build && sam deploy

# Option 3: Manual script
./deployment/deploy_lambda.sh
```

### Update Configuration

```bash
# Update environment variables
aws lambda update-function-configuration \
  --function-name upc-price-lookup \
  --environment Variables="{RATE_LIMIT=30,COUNTRY_CODE=CA,CURRENCY=CAD}"

# Update timeout
aws lambda update-function-configuration \
  --function-name upc-price-lookup \
  --timeout 600

# Update memory
aws lambda update-function-configuration \
  --function-name upc-price-lookup \
  --memory-size 1024
```

---

## 🗑️ Deleting Resources

### Delete Lambda Function

```bash
# Option 1: AWS CLI
aws lambda delete-function --function-name upc-price-lookup

# Option 2: SAM (deletes entire stack)
sam delete --stack-name upc-price-lookup-stack
```

### Delete IAM Role

```bash
aws iam detach-role-policy \
  --role-name lambda-upc-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name lambda-upc-execution-role
```

### Delete API Gateway

```bash
# Get API ID
API_ID=$(aws apigatewayv2 get-apis --query "Items[?Name=='upc-price-lookup-api'].ApiId" --output text)

# Delete API
aws apigatewayv2 delete-api --api-id $API_ID
```

---

## 💰 Cost Estimate

### AWS Lambda Pricing (us-east-1)

**Free Tier (first 12 months):**
- 1M requests/month FREE
- 400,000 GB-seconds of compute/month FREE

**After Free Tier:**
- Requests: $0.20 per 1M requests
- Compute: $0.0000166667 per GB-second

### Example Cost Calculation

**Scenario:** 1000 UPC lookups/day, 50 UPCs/batch, 512MB memory, 5min timeout

Monthly usage:
- Requests: 600 invocations (20/day × 30 days)
- Compute: 90,000 GB-seconds (0.5GB × 300s × 600)

**Monthly cost:**
- Requests: $0.00012 (negligible)
- Compute: $1.50
- **Total: ~$1.50/month**

**With Free Tier: $0/month** ✨

---

## 🎛️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT` | 20 | API calls per minute |
| `COUNTRY_CODE` | US | Country for pricing |
| `CURRENCY` | USD | Currency code |

### Function Settings

| Setting | Default | Max | Recommendation |
|---------|---------|-----|----------------|
| Memory | 512 MB | 10 GB | 512 MB sufficient |
| Timeout | 300s (5min) | 900s (15min) | 300s for ~100 UPCs |
| Runtime | Python 3.11 | - | Latest Python 3.x |

---

## 🐛 Troubleshooting

### Issue: "AWS CLI not found"

```bash
# Install AWS CLI
pip install awscli --user

# Add to PATH
export PATH=$HOME/.local/bin:$PATH
```

### Issue: "Invalid credentials"

```bash
# Reconfigure AWS credentials
aws configure

# Or check current credentials
aws sts get-caller-identity
```

### Issue: "IAM role creation failed"

**Cause:** Insufficient permissions

**Solution:** Add IAM permissions to your AWS user:
- `iam:CreateRole`
- `iam:AttachRolePolicy`

### Issue: "Function timeout"

**Cause:** Processing too many UPCs

**Solutions:**
1. Increase timeout: `--timeout 600`
2. Reduce batch size
3. Increase rate limit

### Issue: "Package too large"

**Cause:** Dependencies exceed 50MB

**Solution:** Use Lambda Layers (advanced)

---

## 📚 Additional Resources

### Documentation
- [AWS Lambda Deployment Guide](../docs/AWS_LAMBDA_DEPLOYMENT.md)
- [UPC Price Lookup Guide](../docs/UPC_PRICE_LOOKUP_GUIDE.md)

### AWS Documentation
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/)
- [API Gateway](https://docs.aws.amazon.com/apigateway/)

### Support
- GitHub Issues: [Report a problem]
- AWS Support: [AWS Console](https://console.aws.amazon.com/support/)

---

## ✅ Checklist

Before deploying:
- [ ] AWS account created
- [ ] AWS CLI installed (or will be installed automatically)
- [ ] AWS credentials configured
- [ ] Sufficient IAM permissions
- [ ] Deployment script is executable

After deploying:
- [ ] Test with sample UPC
- [ ] Check CloudWatch Logs
- [ ] Save API endpoint
- [ ] Set up monitoring (optional)
- [ ] Update application with endpoint (if applicable)

---

## 🎉 Success!

If you see "DEPLOYMENT SUCCESSFUL", your Lambda function is live!

**Next steps:**
1. Test with your own UPCs
2. Integrate API endpoint into your application
3. Set up CloudWatch alarms for monitoring
4. Consider using DynamoDB for caching (advanced)

---

**Need help?** Check the [troubleshooting section](#-troubleshooting) or open an issue on GitHub.
