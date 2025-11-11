# 🚀 ONE-CLICK Lambda Deployment

Deploy the UPC Price Lookup tool to AWS Lambda in under 2 minutes!

## Prerequisites

- AWS Account ([Sign up free](https://aws.amazon.com/free))
- Bash shell (Linux/macOS/WSL)

**That's it!** The script handles everything else automatically.

---

## Deploy in 3 Commands

```bash
# 1. Navigate to project
cd /home/user/pricetracker

# 2. Make script executable (first time only)
chmod +x deployment/one_click_deploy.sh

# 3. Deploy!
./deployment/one_click_deploy.sh
```

**Done!** 🎉

---

## What Happens?

The script automatically:

1. ✅ Installs AWS CLI (if needed)
2. ✅ Configures AWS credentials (if needed)
3. ✅ Creates IAM execution role
4. ✅ Packages Python dependencies
5. ✅ Deploys Lambda function (512MB, 5min timeout)
6. ✅ Creates API Gateway endpoint
7. ✅ Tests deployment
8. ✅ Displays all endpoints and test commands

**No manual steps required!**

---

## Output Example

```
╔════════════════════════════════════════════════════════════════╗
║                 🎉 DEPLOYMENT SUCCESSFUL! 🎉                   ║
╚════════════════════════════════════════════════════════════════╝

Function Details:
  Name:     upc-price-lookup
  Region:   us-east-1
  Memory:   512MB
  Timeout:  300s
  Runtime:  python3.11
  Package:  2.5M

Configuration:
  Rate Limit: 20 calls/min
  Country:    US
  Currency:   USD

API Endpoint:
  https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

---

## Quick Test

Test your deployed function:

```bash
# Via AWS CLI
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upcs": ["733739004536"]}' \
  response.json

cat response.json

# Via API (use YOUR endpoint from deployment output)
curl -X POST https://YOUR_API.execute-api.us-east-1.amazonaws.com/prod \
  -H "Content-Type: application/json" \
  -d '{"upcs": ["733739004536"]}'
```

---

## Customization

Set environment variables before deploying:

```bash
# Different region
export AWS_REGION=us-west-2

# More memory
export LAMBDA_MEMORY=1024

# Longer timeout (max 900s = 15min)
export LAMBDA_TIMEOUT=600

# Custom rate limit (calls per minute)
export RATE_LIMIT=30

# Different country/currency
export COUNTRY_CODE=CA
export CURRENCY=CAD

# Deploy with custom settings
./deployment/one_click_deploy.sh
```

---

## Alternative: AWS SAM Deployment

For production environments, use AWS SAM:

```bash
# 1. Install SAM CLI (one time)
pip install aws-sam-cli

# 2. Build and deploy
sam build && sam deploy --guided

# 3. Future updates (one command)
sam deploy
```

**SAM Benefits:**
- Infrastructure as code
- Easy rollbacks
- Parameter management
- Better for teams

---

## Cost

**First 12 months: FREE!**
- AWS Free Tier covers typical usage

**After Free Tier:**
- ~$1.50/month for 1000 lookups/day
- $0.20 per 1M requests
- $0.0000166667 per GB-second

**Example:** 30 lookups/day = **$0.05/month** 💰

---

## Monitoring

```bash
# View logs in real-time
aws logs tail /aws/lambda/upc-price-lookup --follow

# View function details
aws lambda get-function --function-name upc-price-lookup

# View metrics
# Go to AWS Console → Lambda → upc-price-lookup → Monitoring
```

---

## Update Function

```bash
# Just re-run the deployment script!
./deployment/one_click_deploy.sh

# Updates code and configuration automatically
```

---

## Delete Function

```bash
# Delete Lambda function
aws lambda delete-function --function-name upc-price-lookup

# Delete IAM role
aws iam detach-role-policy \
  --role-name lambda-upc-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lambda-upc-execution-role

# Or use SAM (if deployed with SAM)
sam delete --stack-name upc-price-lookup-stack
```

---

## Troubleshooting

### "AWS CLI not found"
```bash
# Script will install automatically, or install manually:
pip install awscli --user
```

### "Invalid credentials"
```bash
# Configure AWS credentials
aws configure
# Enter your Access Key ID and Secret Access Key
```

### "Insufficient permissions"
Your AWS user needs these permissions:
- `lambda:*`
- `iam:CreateRole`, `iam:AttachRolePolicy`
- `apigateway:*`
- `logs:*`

### Function times out
```bash
# Increase timeout
export LAMBDA_TIMEOUT=600
./deployment/one_click_deploy.sh
```

---

## Success Checklist

After deployment:
- [ ] Function deployed successfully ✅
- [ ] API Gateway endpoint created ✅
- [ ] Test passed with sample UPC ✅
- [ ] API endpoint saved ✅
- [ ] CloudWatch Logs accessible ✅

---

## Next Steps

1. **Test with your UPCs**
   ```bash
   aws lambda invoke \
     --function-name upc-price-lookup \
     --payload '{"upcs": ["YOUR_UPC_HERE"]}' \
     response.json
   ```

2. **Integrate API into your app**
   - Use the API endpoint from deployment output
   - Make POST requests with UPC list

3. **Set up monitoring** (optional)
   - Create CloudWatch alarms
   - Set up SNS notifications

4. **Scale up** (optional)
   - Increase memory for faster processing
   - Increase timeout for larger batches
   - Add DynamoDB for caching

---

## Full Documentation

- **Deployment:** [deployment/README_DEPLOY.md](deployment/README_DEPLOY.md)
- **AWS Lambda Guide:** [docs/AWS_LAMBDA_DEPLOYMENT.md](docs/AWS_LAMBDA_DEPLOYMENT.md)
- **Usage Guide:** [docs/UPC_PRICE_LOOKUP_GUIDE.md](docs/UPC_PRICE_LOOKUP_GUIDE.md)

---

## Need Help?

1. Check [deployment/README_DEPLOY.md](deployment/README_DEPLOY.md) for detailed troubleshooting
2. Review [docs/AWS_LAMBDA_DEPLOYMENT.md](docs/AWS_LAMBDA_DEPLOYMENT.md) for in-depth Lambda guide
3. Open an issue on GitHub

---

**Ready? Let's deploy!** 🚀

```bash
./deployment/one_click_deploy.sh
```
