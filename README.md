# VulnPatch AI - Intelligent Vulnerability Patch Management System

<div align="center">

![VulnPatch AI Logo](https://img.shields.io/badge/VulnPatch-AI-blue?style=for-the-badge&logo=shield&logoColor=white)

**Automate vulnerability assessment and patch management using AI-powered analysis of Nmap scan results**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Google Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)

</div>

## Problem Statement

This project addresses the critical challenge of **automated vulnerability patch management** using Large Language Models (LLMs). Developed for the Société Générale Hackathon 2026, VulnPatch AI transforms traditional vulnerability management by:

- **Automating patch management workflow** with AI-powered analysis
- **Parsing Nmap service scan XML outputs** for comprehensive security assessment  
- **Leveraging Google Gemini 2.5 Flash** for intelligent vulnerability analysis and remediation recommendations
- **Providing actionable insights** through natural language processing and conversation interfaces

## Key Features

### **AI-Powered Vulnerability Analysis**
- **Google Gemini 2.5 Flash Integration** with structured output formatting
- **Multiple Analysis Types**: Vulnerability assessment, business impact analysis, patch prioritization
- **Intelligent CVE Mapping** with National Vulnerability Database integration
- **Automated CVSS Scoring** and risk categorization

### **Comprehensive Dashboard & Analytics**
- **Real-time Security Metrics** with interactive charts
- **Vulnerability Trend Analysis** over 30-day periods
- **Severity Distribution Visualization** using Recharts
- **Patch Completion Rate Tracking** and performance metrics

### **Conversational AI Assistant**
- **Natural Language Queries** about vulnerability data
- **Conversation Memory Persistence** across sessions
- **Context-Aware Responses** based on user's security posture
- **Pre-built Security Questions** for quick insights

### **Professional Report Generation**
- **PDF Reports** with executive summaries and technical details
- **OS-Specific Remediation Commands** (Ubuntu, Windows, macOS)
- **Risk Assessment Charts** and compliance mappings

### **Advanced Vulnerability Management**
- **Nmap XML Processing** with real-time status updates
- **Service Version Detection** and vulnerability pattern matching
- **Multi-Status Tracking** (open, patched, ignored, false positive)
- **Bulk Operations** for efficient vulnerability handling

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        UI[Material-UI Components]
        PAGES[Dashboard, Scans, Reports, AI Assistant]
        API_CLIENT[Axios API Client]
    end
    
    subgraph "Backend (FastAPI + Python)"
        AUTH[JWT Authentication]
        API[RESTful API Endpoints]
        SERVICES[Business Logic Services]
        LLM[Google Gemini Integration]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL Database)]
        REDIS[(Redis Cache)]
        FILES[File Storage]
    end
    
    subgraph "External Services"
        GEMINI[Google Gemini 2.5 Flash]
        NVD[National Vulnerability Database]
    end
    
    UI --> API_CLIENT
    API_CLIENT --> API
    API --> AUTH
    API --> SERVICES
    SERVICES --> LLM
    SERVICES --> POSTGRES
    SERVICES --> REDIS
    LLM --> GEMINI
    SERVICES --> NVD
    SERVICES --> FILES
```

### **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.11+ | RESTful API with async support |
| **Frontend** | React 18 + TypeScript | Modern SPA with type safety |
| **Database** | PostgreSQL + SQLAlchemy | Relational data with ORM |
| **Cache** | Redis | Session management & CVE caching |
| **AI/LLM** | Google Gemini 2.5 Flash | Intelligent analysis & recommendations |
| **UI Framework** | Material-UI (MUI) | Consistent design system |
| **Charts** | Recharts | Interactive data visualization |
| **Reports** | ReportLab + Matplotlib | Professional PDF generation |
| **Authentication** | JWT + bcrypt | Secure user management |
| **Containerization** | Docker + Docker Compose | Development & deployment |

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Google Gemini API Key** (free tier available)
- **Git** for cloning the repository

### 1. Clone Repository

```bash
git clone <repository-url>
cd VulnPatchAI
```

### 2. Environment Setup

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit the environment file with your Gemini API key
nano backend/.env
```

**Required Environment Variables:**
```env
# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Database Configuration
DATABASE_URL=postgresql://vulnpatch:password@db:5432/vulnpatch
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional: External API Configuration
NVD_API_KEY=your_nvd_api_key_here  # For rate limit increases
```

### 3. Start Application

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run automated setup and start services
./scripts/setup.sh
```

**Manual Docker Commands (Alternative):**
```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Demo user is automatically created during setup
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Demo Credentials**: 
  - Email: `demo@vulnpatch.ai`
  - Password: `demo123`

## Usage Guide

### **Scanning Workflow**

1. **Upload Nmap XML Files**
   - Navigate to "Upload Scan" page
   - Drag & drop or select Nmap XML files
   - Monitor real-time processing status

2. **Generate Nmap Scans**
   ```bash
   # Ubuntu/Linux - Basic service scan
   sudo nmap -sV -sC -oX scan_results.xml <target_ip>
   
   # macOS - Install nmap first
   brew install nmap && nmap -sV -sC -oX scan_results.xml <target_ip>
   
   # Comprehensive scan with vulnerability scripts
   sudo nmap -sV -sC --script=vuln -oX detailed_scan.xml <target_ip>
   ```

3. **Review Results**
   - Check Dashboard for security metrics
   - Explore Vulnerabilities page for detailed analysis
   - Use AI Assistant for natural language queries

### **Vulnerability Management**

#### **Vulnerability Status Management**
- **Open**: Newly discovered vulnerabilities requiring attention
- **Patched**: Vulnerabilities that have been resolved
- **Ignored**: Accepted risks or false positives
- **False Positive**: Incorrectly identified vulnerabilities

#### **Advanced Filtering**
```typescript
// Available filter options
{
  severity: ["Critical", "High", "Medium", "Low"],
  status: ["open", "patched", "ignored", "false_positive"],
  services: ["ssh", "http", "https", "ftp", "telnet"],
  cvssMin: 0.0,
  cvssMax: 10.0,
  searchQuery: "string"
}
```

### **AI Assistant Usage**

#### **Example Queries**
```plaintext
# Security Assessment
"What are my most critical vulnerabilities?"
"Analyze my latest scan for security risks"
"What's my overall security posture?"

# Patch Management
"Which vulnerabilities should I patch first?"
"Show me remediation steps for SSH vulnerabilities"
"What patches are available for my Apache server?"
```

#### **AI Analysis Types**
- **Vulnerability Assessment**: Comprehensive security analysis 
- **Patch Recommendation**: Specific remediation guidance
- **Risk Analysis**: Risk scoring and prioritization
- **Compliance Mapping**: Regulatory framework alignment

### **Report Generation**

#### **Report Types**
1. **Executive Summary**: High-level overview for management
2. **Technical Report**: Detailed analysis for IT teams
3. **Compliance Report**: Regulatory framework mappings
4. **Patch Management**: Prioritized remediation guide

#### **Report Contents**
- **Vulnerability Statistics** with severity breakdown
- **Detailed Findings** with CVE references and CVSS scores
- **Remediation Commands** for Ubuntu, Windows, and macOS
- **Risk Assessment Charts** and trend analysis
- **Compliance Mappings** for security frameworks

## 🔧 Development Guide

### **Local Development Setup**

#### **Backend Development**
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run development server
python main.py

# Database migrations
python create_migration.py

# Run tests
pytest
```

#### **Frontend Development**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### **API Development**

#### **Key API Endpoints**
```python
# Authentication
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/logout

# Scan Management  
POST /api/v1/scan/upload
GET /api/v1/scan/
GET /api/v1/scan/{scan_id}

# Vulnerability Management
GET /api/v1/vulnerabilities/
PUT /api/v1/vulnerabilities/{vuln_id}/status
POST /api/v1/vulnerabilities/bulk-update

# AI Analysis
POST /api/v1/ai/query
POST /api/v1/ai/analyze
GET /api/v1/conversation/

# Reports
POST /api/v1/reports/generate
GET /api/v1/reports/
GET /api/v1/reports/{report_id}/download
```

#### **Database Models**
```python
# Core Models
class User(Base):
    # User management with roles and MFA
    
class Scan(Base):
    # Nmap XML file processing and metadata
    
class Vulnerability(Base):
    # Service vulnerabilities with CVE integration
    
class Report(Base):
    # Generated reports with multiple formats
    
class Conversation(Base):
    # AI assistant conversation memory
```

### **Docker Development**

#### **Service Configuration**
```yaml
# docker-compose.yml structure
services:
  backend:    # FastAPI application
  frontend:   # React development server
  db:         # PostgreSQL database
  redis:      # Redis cache
  
volumes:
  postgres_data:  # Persistent database storage
  uploads:        # Nmap XML file storage
```

#### **Development Commands**
```bash
# Rebuild specific service
docker-compose up -d --build backend

# View service logs
docker-compose logs -f backend frontend

# Access service shell
docker-compose exec backend bash
docker-compose exec db psql -U vulnpatch

# Reset environment
docker-compose down -v
docker-compose up -d --build
```

## Security Features

### **Authentication & Authorization**
- **JWT-based authentication** with configurable token expiration
- **Role-based access control** (user, admin, analyst)
- **Multi-factor authentication** with TOTP and backup codes
- **Secure password hashing** using bcrypt with salt

### **Input Validation & Security**
- **Comprehensive input validation** for all API endpoints
- **SQL injection prevention** through SQLAlchemy ORM
- **File upload validation** with size and format restrictions
- **Rate limiting** on API endpoints to prevent abuse
- **CORS configuration** for secure cross-origin requests

### **Data Protection**
- **Environment-based secrets** management
- **Database encryption** for sensitive data
- **Secure file storage** with access controls
- **Audit logging** for security events and user actions

## Deployment Guide

### **Production Deployment**

#### **Environment Variables**
```env
# Production Configuration
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@db-host:5432/vulnpatch
REDIS_URL=redis://redis-host:6379/0

# Security
SECRET_KEY=production_secret_key_256_bits
ALLOWED_ORIGINS=https://yourdomain.com

# External Services
GEMINI_API_KEY=your_production_gemini_key
NVD_API_KEY=your_nvd_api_key
```

#### **Docker Production Setup**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Health checks
docker-compose ps
curl http://localhost:8000/health
```

### **Scaling & Performance**

#### **Performance Optimizations**
- **Redis caching** for CVE data and AI responses
- **Database indexing** on frequently queried columns
- **Connection pooling** for database efficiency
- **Async processing** for file uploads and AI analysis
- **CDN integration** for static asset delivery

#### **Monitoring & Logging**
```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "timestamp": datetime.utcnow()
    }
```

## Testing

### **Backend Testing**
```bash
# Run all tests
cd backend && pytest

# Run specific test categories
pytest tests/test_ai_service.py
pytest tests/test_vulnerability_api.py
pytest tests/test_xml_parser.py

# Test coverage
pytest --cov=app tests/
```

### **Frontend Testing**
```bash
# Run React tests
cd frontend && npm test

# Run tests with coverage
npm test -- --coverage

# E2E testing (if configured)
npm run test:e2e
```

### **Integration Testing**
```bash
# Test full workflow
./scripts/test_integration.sh

# API testing with sample data
curl -X POST http://localhost:8000/api/v1/scan/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_scans/nmap_scan.xml"
```

## Contributing

### **Development Workflow**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

### **Coding Standards**
- **Python**: Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript**: Strict mode enabled, consistent naming conventions
- **Git**: Conventional commit messages, feature-based branching
- **Testing**: Maintain >80% code coverage, integration tests for workflows

## Additional Resources

### **Sample Data**
- **Nmap XML samples** in `sample_scans/` directory
- **Demo vulnerabilities** for testing AI analysis
- **Sample reports** showing expected output formats

### **API Documentation**
- **Interactive Swagger UI**: http://localhost:8000/docs
- **OpenAPI Specification**: http://localhost:8000/openapi.json
- **Postman Collection**: Available in `docs/api/` directory

### **External Documentation**
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [National Vulnerability Database API](https://nvd.nist.gov/developers)
- [Nmap XML Output Format](https://nmap.org/book/output-formats-xml-output.html)

## Troubleshooting

### **Common Issues**

#### **Docker Issues**
```bash
# Port already in use
docker-compose down
sudo lsof -ti:3000 | xargs kill -9

# Database connection issues
docker-compose logs db
docker-compose restart db

# Permission issues
sudo chown -R $USER:$USER .
```

#### **API Issues**
```bash
# Check backend logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep GEMINI

# Database migration issues
docker-compose exec backend python create_migration.py
```

#### **Frontend Issues**
```bash
# Clear node modules and reinstall
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install

# Check for API connectivity
curl http://localhost:8000/health
```


## 👥 Team & Acknowledgments

Developed as part of the Société Générale Hackathon focusing on innovative vulnerability management solutions using AI/LLM technologies.

### **Development Team**
- **Ishan Gupta** - [@ishangtxl](https://github.com/ishangtxl)
- **Joel Stephen Mathew** - [@playinpixel](https://github.com/playinpixel)
- **Bhumi Lakhani** - [@bhumilakhani2022](https://github.com/bhumilakhani2022)

---

<div align="center">



[![Made for Hackathon](https://img.shields.io/badge/Made%20for-SocGen%20Hackathon%202026-orange?style=for-the-badge)](https://societegenerale.neohire.ai/)

</div>