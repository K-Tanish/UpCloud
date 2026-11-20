# UpCloud - Serverless Cloud Cost Monitor

A production-ready serverless web application for monitoring cloud resource waste. Deployed on AWS using Lambda + DynamoDB, demonstrating 13+ cloud computing concepts.

**🚀 Live Demo:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%2B%20DynamoDB-orange)
![Python](https://img.shields.io/badge/Python-3.11-blue)

---

## 📋 Overview

UpCloud is a cloud cost monitoring platform that identifies idle and wasteful resources across AWS, Azure, and GCP. Built as a Cloud Computing semester project, it demonstrates practical serverless architecture and cloud-native design patterns.

**What It Does:**
- Scans cloud infrastructure for wasteful resources
- Estimates monthly cost savings
- Provides risk categorization (High/Medium/Low)
- Real-time dashboard with analytics
- Multi-cloud provider support

**Example Findings:**
- Stopped EC2 instances (still billing for EBS)
- Unattached EBS volumes
- Idle load balancers
- Unused Elastic IPs
- Old snapshots and AMIs
- Idle SageMaker endpoints

---

## 🚀 Live Demo

**Access the application:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

**Features:**
- **Dashboard** - Overview with total findings and monthly waste estimate ($600.66)
- **Findings** - Detailed list with filters and search
- **Reports** - Provider breakdown and cost opportunities
- **Demo Scan** - Simulate cloud scanning in real-time

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   User Browser      │  HTTPS
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  AWS Lambda Function URL        │
│  • Serves frontend (HTML/CSS/JS)│
│  • Handles API requests         │
│  • Auto-scales 0→1000s          │
│  • Python 3.11 runtime          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Amazon DynamoDB                │
│  • NoSQL database               │
│  • On-demand pricing            │
│  • Global Secondary Index       │
│  • 17 demo findings             │
└─────────────────────────────────┘
```

**Supporting Services:**
- **IAM Role** - Least-privilege access control
- **CloudWatch** - Automatic logging and monitoring
- **Lambda Function URL** - Public HTTPS endpoint with CORS

---

## ☁️ Cloud Computing Concepts Demonstrated

This project demonstrates **13+ cloud computing concepts**:

1. **Function as a Service (FaaS)** - AWS Lambda serverless compute
2. **Serverless Architecture** - No server management required
3. **NoSQL Database as a Service** - DynamoDB managed database
4. **Auto-Scaling** - Automatic scaling from 0 to 1000s of requests
5. **High Availability** - Multi-AZ deployment by default
6. **Pay-per-Use Pricing** - Only pay for actual execution time
7. **Infrastructure as Code** - Scripted AWS CLI deployment
8. **RESTful API Design** - Standard HTTP methods with JSON
9. **CORS** - Cross-origin resource sharing for browser security
10. **IAM Role-Based Access** - Least-privilege security model
11. **HTTPS/TLS** - End-to-end encrypted communication
12. **Stateless Applications** - Enables horizontal scaling
13. **Event-Driven Computing** - HTTP-triggered Lambda functions

---

## 🛠️ Technology Stack

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Professional grey-toned responsive design
- No frameworks (demonstrates fundamentals)

**Backend:**
- Python 3.11
- AWS Lambda (512MB memory)
- Boto3 AWS SDK

**Database:**
- Amazon DynamoDB
- NoSQL document store
- Global Secondary Index for queries

**Infrastructure:**
- AWS Lambda Function URL
- IAM roles and policies
- CloudWatch logs and metrics

**Deployment:**
- AWS CLI
- PowerShell automation scripts
- Infrastructure as Code

---

## 📦 Project Structure

```
UpCloud/
├── README.md                 # This file
├── PROJECT_REPORT.md         # 30-page technical report
├── PROJECT_SUMMARY.md        # Project overview
├── DEPLOYMENT.md             # AWS deployment guide
├── QUICK_START.md            # Quick reference
├── SOLUTION.md               # Technical solution details
├── quick_deploy.bat          # Automated deployment script
│
├── upcloud/                  # Web application
│   ├── static/               # Frontend files
│   │   ├── index.html        # Main UI
│   │   ├── app.css           # Styles
│   │   ├── app.js            # Frontend logic
│   │   └── config.js         # API configuration
│   ├── service.py            # Business logic
│   └── seed.py               # Demo data seeder
│
├── lambda_handlers/          # AWS Lambda
│   ├── api.py                # Lambda entry point
│   └── requirements.txt      # Python dependencies
│
└── cleancloud/               # Core scanning logic
    ├── core/                 # Finding models
    ├── providers/            # Cloud provider rules
    │   └── aws/              # AWS scanning rules
    └── demo/                 # Demo data generator
```

---

## 🚀 Deployment

### Prerequisites

- AWS Account (Free Tier eligible)
- AWS CLI installed and configured
- Python 3.10+

### Quick Deploy

```powershell
.\quick_deploy.bat
```

This automated script:
1. Creates IAM role with DynamoDB + CloudWatch permissions
2. Creates DynamoDB table with Global Secondary Index
3. Packages Python code with dependencies
4. Deploys Lambda function
5. Creates public Function URL
6. Seeds demo data (17 findings)

**Deployment time:** ~5 minutes

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend application |
| `/app.css` | GET | Stylesheet |
| `/app.js` | GET | JavaScript |
| `/config.js` | GET | Configuration |
| `/api/health` | GET | Health check |
| `/api/dashboard` | GET | Summary statistics |
| `/api/findings` | GET | List findings (supports filters) |
| `/api/scan` | POST | Run demo scan |

**Example API Call:**
```bash
curl https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/api/dashboard
```

**Response:**
```json
{
  "total_findings": 17,
  "high_risk_findings": 1,
  "estimated_monthly_waste_usd": 600.66,
  "by_provider": {
    "aws": 12,
    "azure": 3,
    "gcp": 2
  }
}
```

---

## 💰 Cost Analysis

**AWS Free Tier (First 12 Months):**
- Lambda: 1 million requests/month FREE
- DynamoDB: 25GB storage + 25 read/write units FREE
- CloudWatch: 5GB logs FREE

**Estimated Monthly Cost (After Free Tier):**
- Lambda: ~$0.20 (based on 100K requests)
- DynamoDB: ~$0.25 (on-demand pricing)
- Data Transfer: ~$0.10
- **Total: <$1/month**

**Comparison to Traditional Hosting:**
- EC2 t3.small: $20/month
- RDS MySQL: $15/month
- Application Load Balancer: $16/month
- **Traditional Total: $51/month**

**Serverless Savings: 98%** 💰

---

## 📊 Demo Data

The application includes **17 pre-seeded findings**:

**By Provider:**
- AWS: 12 findings
- Azure: 3 findings
- GCP: 2 findings

**By Category:**
- Hygiene (unused resources): 16 findings
- AI/ML (idle infrastructure): 1 finding

**Total Monthly Waste:** $600.66

**Risk Levels:**
- High Risk: 1 finding
- Medium Risk: 10 findings
- Low Risk: 6 findings

---

## 🎯 Key Features

### Dashboard
- Total findings count
- Monthly waste estimate
- High-risk findings indicator
- Provider breakdown with charts
- Top 3 cost-saving opportunities

### Findings List
- Filterable by provider (AWS/Azure/GCP)
- Filterable by category (hygiene/ai)
- Searchable by resource ID or title
- Risk-level indicators
- Cost estimates per resource
- Detailed finding information

### Professional UI
- Monochrome grey palette (no bright colors)
- Horizontal top navigation
- Subtle grid background pattern
- Responsive design
- Clean, modern aesthetic

---

## 📚 Documentation

- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** - Comprehensive 30-page technical report with architecture diagrams
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Quick project overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Step-by-step AWS deployment guide
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[SOLUTION.md](SOLUTION.md)** - Technical problem-solving details
- **[PRESENTATION.md](PRESENTATION.md)** - Presentation slide content

---

## 🔒 Security

**Implementation:**
- IAM role-based access (no hardcoded credentials)
- Least-privilege permissions
- HTTPS-only communication
- CORS-enabled for browser access
- CloudWatch audit logging
- No sensitive data exposed

**Best Practices:**
- Temporary AWS credentials via IAM roles
- Public endpoint with controlled CORS
- Input validation on all API endpoints
- Error handling without leaking details
- Monitoring and alerting enabled

---

## 🚦 Testing the Application

### Test Health Endpoint
```powershell
curl https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/api/health
```

### Test Dashboard Data
```powershell
curl https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/api/dashboard
```

### Test Findings with Filters
```powershell
curl "https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/api/findings?provider=aws&category=hygiene"
```

---

## 🔮 Future Enhancements

**Short-term:**
- CloudFront CDN for global performance
- Custom domain with Route 53
- Cognito authentication
- API Gateway rate limiting
- Real-time WebSocket updates

**Long-term:**
- Connect to actual AWS accounts (real scanning)
- Multi-account organization support
- Automated remediation workflows
- Cost forecasting with machine learning
- Email/Slack notifications
- CI/CD pipeline with GitHub Actions

**Enterprise Features:**
- SAML/SSO integration
- Role-based access control (RBAC)
- Audit logging and compliance
- Multi-tenancy support
- White-label deployment

---

## 📖 Academic Context

This project was created as a **Cloud Computing semester project** to demonstrate:
- Practical AWS deployment experience
- Serverless architecture understanding
- Cloud-native application design
- Infrastructure as Code principles
- Cost optimization strategies
- Production-ready development practices

**Key Learning Outcomes:**
- Mastered AWS Lambda and DynamoDB
- Implemented RESTful API design
- Applied cloud security best practices
- Built auto-scaling architecture
- Managed cloud costs effectively

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built as a Cloud Computing semester project demonstrating practical serverless architecture on AWS. The scanning logic is based on cloud hygiene best practices for detecting idle and wasteful resources.

---

## 📞 Support

For questions or issues:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review [PROJECT_REPORT.md](PROJECT_REPORT.md) for technical details
- See [SOLUTION.md](SOLUTION.md) for troubleshooting

---

**Live Application:** https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

**Status:** ✅ Production-ready | 🚀 Deployed on AWS | 💰 <$1/month | 📊 13+ Cloud Concepts
