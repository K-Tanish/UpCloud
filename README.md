# UpCloud - Cloud Cost Monitor

A serverless web application for monitoring cloud resource waste across AWS, Azure, and GCP. Built as a Cloud Computing semester project demonstrating 13+ cloud concepts on AWS.

**🚀 Live Demo:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

![PyPI](https://img.shields.io/pypi/v/cleancloud)
![Python Versions](https://img.shields.io/pypi/pyversions/cleancloud)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Overview

UpCloud scans cloud infrastructure to identify idle and wasteful resources. Originally a terminal-based tool (CleanCloud), it was transformed into a fully deployed serverless web application on AWS.

**Key Features:**
- Real-time dashboard with cost analytics
- Multi-cloud support (AWS, Azure, GCP)
- AI/ML waste detection for expensive GPU and SageMaker resources
- Professional grey-toned UI with responsive design
- RESTful API with JSON responses

---

## Live Demo

**🚀 Access the live demo:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

The entire application (frontend + API) is served from a single AWS Lambda Function URL with HTTPS.

---

## Architecture

```
User Browser (HTTPS)
    ↓
AWS Lambda Function URL
    ↓
Amazon DynamoDB
```

### AWS Resources
- **Lambda Function** - Python 3.11, 512MB memory
- **Function URL** - Public HTTPS endpoint with CORS
- **DynamoDB** - NoSQL database with Global Secondary Index
- **IAM Role** - Least-privilege access policy
- **CloudWatch** - Automatic logging and monitoring

### Cloud Computing Concepts (13+)

1. **Function as a Service (FaaS)** - AWS Lambda serverless compute
2. **Serverless Architecture** - No server management
3. **NoSQL Database** - DynamoDB with flexible schema
4. **Auto-Scaling** - Handles 0-1000s requests automatically
5. **High Availability** - Multi-AZ deployment
6. **Pay-per-Use Pricing** - Only charged for execution time
7. **Infrastructure as Code** - Scripted deployment
8. **RESTful API Design** - Standard HTTP/JSON interface
9. **CORS** - Cross-origin resource sharing
10. **IAM Role-Based Access** - Least-privilege security
11. **HTTPS/TLS** - Encrypted communication
12. **Stateless Applications** - Horizontal scaling
13. **Event-Driven Computing** - HTTP-triggered functions

---

## Quick Start

### View the Live Application

Simply visit: https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

### Deploy Your Own Instance

**Prerequisites:**
- AWS Account (Free Tier eligible)
- AWS CLI configured with credentials
- Python 3.10+

**Deploy:**
```powershell
.\quick_deploy.bat
```

This script creates:
- Lambda function with Function URL
- DynamoDB table with sample data
- IAM role with necessary permissions

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Project Structure

```
UpCloud/
├── README.md                 # This file
├── PROJECT_REPORT.md         # 30-page detailed report
├── PROJECT_SUMMARY.md        # Project overview
├── DEPLOYMENT.md             # AWS deployment guide
├── QUICK_START.md            # Quick reference
├── SOLUTION.md               # Technical solution details
├── quick_deploy.bat          # Deployment script
├── upcloud/
│   ├── static/               # Frontend (HTML/CSS/JS)
│   └── service.py            # Business logic
├── lambda_handlers/
│   └── api.py                # Lambda entry point
└── cleancloud/               # Core scanning logic
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend application |
| `/api/health` | GET | Health check |
| `/api/dashboard` | GET | Summary statistics |
| `/api/findings` | GET | List findings (filterable) |
| `/api/scan` | POST | Run demo scan |

**Example:**
```bash
curl https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/api/dashboard
```

---

## Features

### Dashboard
- Total findings count
- Monthly waste estimate ($600.66 in demo)
- High-risk findings indicator
- Provider breakdown (AWS, Azure, GCP)
- Top 3 cost-saving opportunities

### UI Design
- Professional monochrome palette (grey tones)
- Horizontal top navigation
- Subtle grid background pattern
- Responsive layout
- No bright colors (no AI-generated look)

### Demo Data
- 17 sample findings across providers
- Hygiene category (unused resources)
- AI category (idle ML infrastructure)
- Real-world cost estimates

---

## Cost Analysis

**AWS Free Tier:**
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage free
- CloudWatch: 5GB logs free

**Estimated Monthly Cost:** <$1 after free tier

---

## Documentation

- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** - Comprehensive 30-page report
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Quick project overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - AWS deployment instructions
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[SOLUTION.md](SOLUTION.md)** - Technical problem-solving details

---

## Technology Stack

- **Backend:** Python 3.11
- **Frontend:** Vanilla JavaScript (no frameworks)
- **Database:** Amazon DynamoDB (NoSQL)
- **Deployment:** AWS Lambda + Function URLs
- **Infrastructure:** AWS CLI scripted deployment

---

## Original CleanCloud CLI

This project is based on CleanCloud, a production CLI tool. To use the original terminal version:

```bash
# Install
pipx install 'cleancloud[aws]'

# Run demo
cleancloud demo

# Scan your AWS account
cleancloud scan aws
```

**Documentation:** [docs/configuration.md](docs/configuration.md) | [docs/design.md](docs/design.md) | [docs/rules.md](docs/rules.md)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Academic Use

This project was created as a Cloud Computing semester project demonstrating practical AWS deployment and serverless architecture. Feel free to use as reference for your own cloud projects.

**Key Learning Outcomes:**
- Serverless application deployment
- AWS service integration
- NoSQL database design
- RESTful API development
- Infrastructure as Code
- Cloud security best practices
