# UpCloud - Project Summary

## Overview

UpCloud is a cloud cost monitoring application that scans AWS, Azure, and GCP for wasteful resources. It was transformed from a terminal-based Python tool into a fully deployed AWS serverless web application for a Cloud Computing semester project.

## Live Application

**URL:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

## Architecture

```
┌─────────────────────────────────────────────────┐
│  User Browser (HTTPS)                           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  AWS Lambda Function URL                        │
│  • Serves HTML/CSS/JS (frontend)                │
│  • Handles API requests (/api/*)                │
│  • Auto-scales 0→1000s requests                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Amazon DynamoDB                                │
│  • NoSQL database                               │
│  • On-demand pricing                            │
│  • Global Secondary Index for queries           │
└─────────────────────────────────────────────────┘
```

## AWS Resources

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **Lambda Function** | Compute + Web Server | Python 3.11, 512MB, ap-southeast-2 |
| **Function URL** | HTTPS endpoint | Public, CORS-enabled |
| **DynamoDB Table** | Data storage | On-demand, GSI: ProviderCategoryIndex |
| **IAM Role** | Security | DynamoDB read/write, CloudWatch logs |

## Cloud Computing Concepts (10+)

1. **Function as a Service (FaaS)** - AWS Lambda serverless compute
2. **Serverless Architecture** - No server management required
3. **NoSQL Database** - DynamoDB flexible schema
4. **Auto-Scaling** - Lambda scales automatically with traffic
5. **High Availability** - Multi-AZ deployment by default
6. **Pay-per-Use Pricing** - Only charged for actual execution time
7. **Infrastructure as Code** - Deployment scripted with AWS CLI
8. **RESTful API Design** - Standard HTTP methods and JSON
9. **CORS (Cross-Origin)** - Browser security headers
10. **IAM Role-Based Access** - Least-privilege security model
11. **HTTPS/TLS** - Encrypted communication built-in
12. **Stateless Applications** - No session storage, horizontal scaling
13. **Event-Driven Computing** - Lambda triggered by HTTP requests

## Features

### Frontend (Professional Grey Design)
- **Horizontal top navigation** (not sidebar)
- **Monochrome palette** - Shades of grey, no bright colors
- **Subtle grid background** - Professional aesthetic
- **Responsive dashboard** with:
  - Total findings count
  - Monthly waste estimate
  - High-risk findings
  - Provider breakdown charts
  - Top 3 cost opportunities

### Backend API
- `GET /api/health` - Health check
- `GET /api/dashboard` - Summary statistics
- `GET /api/findings` - List findings (filterable)
- `POST /api/scan` - Run demo scan

### Demo Data
- 17 sample findings across AWS, Azure, GCP
- Categories: hygiene (unused resources), ai (ML waste)
- Estimated monthly waste: $600.66
- 1 high-risk finding

## Technology Stack

- **Backend**: Python 3.11
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Database**: DynamoDB (NoSQL)
- **Deployment**: AWS CLI + PowerShell
- **Styling**: Custom CSS (monochrome design)

## Key Technical Decisions

### Why Lambda Function URL instead of API Gateway + S3?
**Problem**: S3 website hosting uses HTTP, Lambda uses HTTPS. Browsers block HTTP→HTTPS requests (mixed content security).

**Solution**: Serve both frontend and API from Lambda Function URL. Everything uses HTTPS from same origin. Simpler architecture, fewer services, no mixed content issues.

### Why DynamoDB instead of RDS?
- No server management
- Auto-scaling capacity
- On-demand pricing (pay per request)
- Fast query performance with GSI
- Better fit for serverless architecture

### Why not use frameworks (React, Vue)?
- Demonstrates core web technologies
- No build step complexity
- Faster loading (no large bundles)
- Shows understanding of fundamentals

## Cost Analysis

**Free Tier Eligible:**
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage, 25 read/write units free
- CloudWatch: 5GB logs free

**Estimated Monthly Cost (after free tier):**
- Lambda: ~$0 (very low traffic)
- DynamoDB: ~$0 (minimal data)
- **Total: <$1/month**

## Files & Documentation

- `README.md` - Main project documentation
- `PROJECT_REPORT.md` - 30-page detailed report with diagrams
- `DEPLOYMENT.md` - AWS deployment guide
- `QUICK_START.md` - Quick reference
- `SOLUTION.md` - Technical problem-solving details
- `quick_deploy.bat` - Automated deployment script

## Demonstration Points

For your semester presentation:

1. **Live Demo** - Show the working application at the Lambda URL
2. **Architecture** - Explain serverless vs traditional servers
3. **Scalability** - Demo auto-scaling (refresh rapidly)
4. **Cost Model** - Show pay-per-use vs always-on servers
5. **Security** - Explain IAM roles and HTTPS
6. **Database** - Show DynamoDB data in AWS Console
7. **Monitoring** - Show CloudWatch logs/metrics
8. **Code** - Walk through Lambda handler routing

## Success Criteria

✅ **Fully functional** - All features working end-to-end  
✅ **Deployed to cloud** - Running on real AWS infrastructure  
✅ **Professional UI** - Grey-toned, clean design  
✅ **10+ concepts** - Demonstrates comprehensive cloud knowledge  
✅ **Under budget** - Uses only AWS free tier  
✅ **Documented** - Complete guides and reports  
✅ **Reproducible** - Scripted deployment for grading  

## Accessing the Project

**Live Application:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

**Repository Structure:**
```
UpCloud/
├── README.md                 # Main documentation
├── PROJECT_REPORT.md         # Detailed 30-page report
├── PROJECT_SUMMARY.md        # This file
├── DEPLOYMENT.md             # Deployment guide
├── QUICK_START.md            # Quick reference
├── SOLUTION.md               # Technical solution details
├── quick_deploy.bat          # Deployment script
├── upcloud/
│   ├── static/               # Frontend files
│   │   ├── index.html
│   │   ├── app.css
│   │   ├── app.js
│   │   └── config.js
│   └── service.py            # Business logic
├── lambda_handlers/
│   └── api.py                # Lambda entry point
└── cleancloud/               # Core scanning logic
```

## Next Steps (Optional Enhancements)

If you have extra time:

1. **CloudFront CDN** - Add caching layer for faster global access
2. **Custom Domain** - Use Route 53 for custom URL
3. **Authentication** - Add Cognito user login
4. **CI/CD Pipeline** - GitHub Actions auto-deployment
5. **Multiple Environments** - dev/staging/prod separation

---

**Project Status:** ✅ COMPLETE - Ready for submission and demonstration
