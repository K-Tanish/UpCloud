# UpCloud AWS Deployment Guide

This guide explains how to deploy UpCloud to AWS using serverless architecture.

## Live Application

**URL:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

## Architecture Overview

UpCloud uses a simplified serverless architecture on AWS:

```
User Browser (HTTPS)
    ↓
Lambda Function URL (Frontend + API)
    ↓
DynamoDB (NoSQL Database)
```

**Key Design Decision:** Serving both frontend and API from a single Lambda Function URL solves the mixed content security issue (HTTP/HTTPS) and simplifies deployment to a single endpoint.

### Cloud Computing Concepts Demonstrated

1. **Function as a Service (FaaS) / Serverless Computing**
   - AWS Lambda for compute (no server management)
   - Auto-scaling built-in (handles 0-1000s of requests)
   - Pay-per-use pricing (only pay when code runs)
   - Lambda Function URLs (built-in HTTPS endpoint)

2. **NoSQL Database as a Service**
   - DynamoDB on-demand pricing
   - Global Secondary Indexes for query performance
   - Managed service (no database admin required)

3. **Cloud Security & IAM**
   - IAM roles and policies
   - Least-privilege access
   - Public Lambda Function URL (CORS-enabled)

4. **Infrastructure as Code (IaC)**
   - AWS CLI scripted deployment
   - Reproducible infrastructure
   - Version-controlled configuration

5. **Cloud-Native Application Design**
   - Stateless application architecture
   - API-driven design
   - JSON-based data exchange
   - CORS for browser security

## Prerequisites

Before deploying, ensure you have:

- AWS Account (Free Tier eligible)
- AWS CLI installed and configured with credentials
- Python 3.10+

## Deployment Steps

### Quick Deployment Script

Run the automated deployment:

```powershell
.\quick_deploy.bat
```

This script:
1. Creates IAM role for Lambda
2. Creates DynamoDB table with GSI
3. Packages Python code with dependencies
4. Deploys Lambda function
5. Creates public Function URL
6. Seeds demo data

### Manual Deployment Steps

# Serverless plugins
npm install --save-dev serverless-python-requirements
```

#### Step 2: Deploy Backend

```powershell
# Deploy Lambda, API Gateway, and DynamoDB
serverless deploy --stage dev
```

This creates:
- Lambda function for API handlers
- DynamoDB table for storing findings
- API Gateway for REST endpoints
- IAM roles for Lambda execution
- CloudWatch log groups

#### Step 3: Seed Database

```powershell
# Set environment variables
$env:DYNAMODB_TABLE = "upcloud-serverless-findings-dev"
$env:AWS_REGION = "ap-southeast-2"

# Run seeding script
python scripts\seed_dynamodb.py
```

#### Step 4: Update Frontend Config

Get your API Gateway endpoint:

```powershell
serverless info --stage dev
```

Update `upcloud/static/config.js` with your API endpoint:

```javascript
window.UPCLOUD_API_URL = 'https://YOUR-API-ID.execute-api.ap-southeast-2.amazonaws.com/dev';
```

#### Step 5: Deploy Frontend

```powershell
# Upload to S3
aws s3 sync upcloud/static/ s3://upcloud-serverless-frontend-dev/ --delete
```

#### Step 6: Access Your Application

Your website will be available at:
```
http://upcloud-serverless-frontend-dev.s3-website-ap-southeast-2.amazonaws.com
```

## Architecture Details

### Lambda Function

**File**: `lambda_handlers/api.py`

The Lambda function handles all API requests:
- `/api/health` - Health check
- `/api/dashboard` - Dashboard statistics
- `/api/findings` - List findings with filters
- `/api/scan` - Simulate cloud scan

**Key Features**:
- Serverless compute (no server management)
- Auto-scaling (handles any traffic)
- Pay-per-request pricing
- Cold start optimization

### DynamoDB Table

**Table Name**: `upcloud-serverless-findings-{stage}`

**Schema**:
- Primary Key: `id` (String)
- GSI: `ProviderCategoryIndex` on `provider` + `category`

**Key Features**:
- NoSQL database (flexible schema)
- Automatic scaling
- Pay-per-request billing
- Sub-millisecond latency

### API Gateway

**Type**: REST API

**Key Features**:
- RESTful endpoints
- CORS enabled
- Request/response transformation
- API throttling and caching
- CloudWatch metrics

### S3 Static Website

**Bucket**: `upcloud-serverless-frontend-{stage}`

**Key Features**:
- Static website hosting
- Public read access
- Low-cost storage
- High availability

## Cost Estimate

All services fit within AWS Free Tier:

| Service | Free Tier | Monthly Cost (After Free Tier) |
|---------|-----------|-------------------------------|
| Lambda | 1M requests/month | ~$0.20 per 1M requests |
| DynamoDB | 25 GB storage, 25 WCU, 25 RCU | ~$1.25 per million requests |
| API Gateway | 1M requests/month (12 months) | ~$3.50 per 1M requests |
| S3 | 5 GB storage, 20K GET, 2K PUT | ~$0.023 per GB |
| CloudWatch Logs | 5 GB ingestion | ~$0.50 per GB |

**Estimated Monthly Cost**: $0 (within free tier) to $5-10 for light usage

## Monitoring

### CloudWatch Logs

View Lambda logs:

```powershell
aws logs tail /aws/lambda/upcloud-serverless-dev-api --follow
```

### CloudWatch Metrics

Monitor in AWS Console:
1. Go to CloudWatch
2. Select "Metrics"
3. View Lambda, API Gateway, and DynamoDB metrics

### API Gateway Monitoring

View API calls, latency, and errors in API Gateway Console.

## Security

### IAM Roles

Lambda execution role has minimum required permissions:
- DynamoDB read/write on findings table only
- CloudWatch Logs write
- No access to other AWS resources

### API Security

Current setup:
- Public API (no authentication)
- CORS enabled for browser access

For production:
- Add API keys or AWS Cognito authentication
- Enable WAF for DDoS protection
- Use custom domain with SSL/TLS

### Data Security

- Data encrypted at rest (DynamoDB default encryption)
- Data encrypted in transit (HTTPS)
- S3 bucket policy restricts access

## Troubleshooting

### Lambda Function Fails

Check CloudWatch Logs:
```powershell
aws logs tail /aws/lambda/upcloud-serverless-dev-api --since 10m
```

### DynamoDB Access Denied

Verify IAM role permissions:
```powershell
aws iam get-role-policy --role-name upcloud-serverless-dev-ap-southeast-2-lambdaRole --policy-name dev-upcloud-serverless-lambda
```

### Frontend Not Loading

1. Check S3 bucket policy (must allow public read)
2. Verify config.js has correct API endpoint
3. Check browser console for CORS errors

### API Gateway 502/504 Errors

1. Check Lambda function timeout (default 30s)
2. Verify Lambda has correct environment variables
3. Check CloudWatch Logs for Python errors

## Cleanup

To destroy all resources and avoid charges:

```powershell
# Remove backend (Lambda, API Gateway, DynamoDB)
serverless remove --stage dev

# Remove frontend
aws s3 rm s3://upcloud-serverless-frontend-dev --recursive
aws s3 rb s3://upcloud-serverless-frontend-dev
```

## Scaling Considerations

This architecture automatically scales:

| Component | Scaling Method |
|-----------|----------------|
| Lambda | Concurrent executions (up to account limit) |
| DynamoDB | On-demand capacity (auto-scales) |
| API Gateway | Handles any request volume |
| S3 | Unlimited storage and bandwidth |

For high traffic:
1. Enable API Gateway caching
2. Use CloudFront CDN for S3
3. Optimize Lambda memory/timeout
4. Consider DynamoDB provisioned capacity

## Next Steps

1. **Add Authentication**: Integrate AWS Cognito
2. **Custom Domain**: Use Route 53 + CloudFront
3. **CI/CD Pipeline**: Automate deployment with GitHub Actions
4. **Real Cloud Scanning**: Integrate actual AWS APIs
5. **Multi-Region**: Deploy to multiple regions for HA

## Cloud Computing Concepts Covered

This project demonstrates:

✓ Serverless Architecture (Lambda)
✓ NoSQL Databases (DynamoDB)
✓ API Design (REST API via API Gateway)
✓ Object Storage (S3)
✓ Infrastructure as Code (Serverless Framework)
✓ Monitoring & Logging (CloudWatch)
✓ Security (IAM Roles, Policies)
✓ Auto-scaling
✓ Pay-as-you-go pricing
✓ High Availability
✓ Event-driven architecture
✓ Microservices patterns

## Support

For issues or questions:
- Check CloudWatch Logs
- Review AWS documentation
- Check Serverless Framework docs
