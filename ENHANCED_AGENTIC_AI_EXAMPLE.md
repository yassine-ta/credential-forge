# 🚀 Enhanced Agentic AI File Generation - Complete Example

## ✅ Enhanced Features Implemented

### 1. **Variable Credential Count (1-10 per file)**
- Each generated file now contains **1-10 credentials** randomly
- Credentials are selected from available types with variety
- Realistic distribution across different credential types

### 2. **Realistic Professional Content**
- **Comprehensive templates** with detailed technical information
- **Professional formatting** with proper structure
- **Real-world metrics** and configuration details
- **Multi-section documents** with executive summaries

### 3. **Multiple Topic Support**
- **Comma-separated topics** in input (e.g., "security audit, database migration, API documentation")
- **Intelligent topic combination** for comprehensive documents
- **Format-specific content organization** for different file types

## 📋 Usage Examples

### Example 1: Multiple Topics with Variable Credentials

```python
from credentialforge.agents.orchestrator import OrchestratorAgent

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Configuration with multiple topics
config = {
    'output_dir': './output',
    'formats': ['docx', 'xlsx', 'pdf'],
    'credential_types': ['aws_access_key', 'api_key', 'jwt_token', 'database_connection'],
    'topics': [
        'security audit, compliance review',
        'database migration, performance optimization',
        'API documentation, monitoring setup',
        'system architecture, deployment procedures'
    ],
    'num_files': 5,
    'embed_strategy': 'random'
}

# Generate files
results = orchestrator.generate_files(config)
```

### Example 2: Interactive Mode with Enhanced Features

```bash
# Run interactive mode
python -m credentialforge.cli interactive

# Example interaction:
# Topics: security audit, database migration, API documentation
# Formats: docx, xlsx, pdf, png
# Credential types: aws_access_key, api_key, jwt_token
# Number of files: 10
```

## 📄 Generated Content Examples

### Email with Multiple Topics (EML)
```
Subject: Multi-Topic Update: Security Audit, Database Migration, API Documentation

Dear Team,

I wanted to provide a comprehensive update covering multiple areas of our infrastructure and operations.

Section 1: Security Audit
========================

Our security audit implementation has been running smoothly with the following key metrics:
- Uptime: 99.9% over the last 30 days
- Response time: Average 150ms
- Error rate: Less than 0.1%
- Throughput: 10,000 requests per minute

Configuration Updates:
- Database connection pooling optimized
- Cache layer performance improved
- Security protocols updated
- Monitoring thresholds adjusted

Section 2: Database Migration
=============================

Database migration system status:
- Migration progress: 95% complete
- Data integrity: 100% verified
- Performance impact: Minimal
- Rollback capability: Available

Section 3: API Documentation
============================

API documentation system:
- Documentation coverage: 98%
- Auto-generation: Enabled
- Version control: Integrated
- User feedback: Positive

Please review these updates and let me know if you have any questions.

Best regards,
System Administrator
```

### Excel with Comprehensive Configuration (XLSX)
```
EXECUTIVE SUMMARY:
This spreadsheet contains detailed configuration parameters for our security audit, database migration, API documentation infrastructure.
All settings have been validated and are currently in production use.

SERVICE CONFIGURATION:
Service Name: security_audit_database_migration_api_documentation_service
Primary Endpoint: https://api.example.com/security-audit/database-migration/api-documentation
Secondary Endpoint: https://api.example.com/security-audit/database-migration/api-documentation/backup
Status: Active and Monitored
Last Updated: 2024-01-15
Next Review: 2024-04-15
Service Owner: DevOps Team
Criticality Level: High

DATABASE CONFIGURATION:
Primary Host: db.example.com
Secondary Host: db.example.com-backup
Port: 5432
Database: security_audit_database_migration_api_documentation_db
Connection Pool: 10
Max Connections: 100
Timeout: 30 seconds
SSL: Enabled
Backup Schedule: Daily at 2:00 AM
Retention: 30 days

API CONFIGURATION:
Base URL: https://api.example.com/security-audit/database-migration/api-documentation
Version: v1
Authentication: JWT
Rate Limit: 1000/hour
Timeout: 30 seconds
Retry Policy: 3 attempts with exponential backoff
Circuit Breaker: Enabled
Load Balancing: Round Robin

SECURITY CONFIGURATION:
Encryption: AES-256
Key Rotation: Every 90 days
Access Control: Role-based
Audit Logging: Enabled
Compliance: SOC 2 Type II
Penetration Testing: Quarterly

MONITORING & ALERTING:
Health Check: /health/security-audit/database-migration/api-documentation
Metrics: /metrics/security-audit/database-migration/api-documentation
Logs: /logs/security-audit/database-migration/api-documentation
Dashboard: https://monitoring.company.com/security-audit/database-migration/api-documentation
Alert Channels: Email, Slack, PagerDuty
SLA: 99.9% uptime
Response Time: < 200ms

PERFORMANCE METRICS:
Average Response Time: 150ms
Peak Throughput: 10,000 req/min
Error Rate: < 0.1%
CPU Usage: 45%
Memory Usage: 2.1GB
Disk Usage: 15GB

DEPLOYMENT INFORMATION:
Environment: Production
Deployment Method: Blue-Green
Rollback Strategy: Automated
Testing: Automated CI/CD
Compliance: PCI DSS Level 1

NOTES & MAINTENANCE:
Additional notes and considerations for security audit, database migration, API documentation implementation.

Maintenance Window: Sunday 2:00-4:00 AM EST
Contact: devops@company.com
Emergency Contact: +1-555-0123
Documentation: https://docs.company.com/security-audit/database-migration/api-documentation
```

### PDF with Professional Documentation
```
COMPREHENSIVE SYSTEM DOCUMENTATION
Multi-Topic Infrastructure Reference Guide

Document Overview:
This document provides detailed technical specifications and implementation guidelines for 3 critical system components.

Chapter 1: SECURITY AUDIT
=========================

Our security audit system has been running smoothly with the following key metrics:
- Uptime: 99.9% over the last 30 days
- Response time: Average 150ms
- Error rate: Less than 0.1%
- Throughput: 10,000 requests per minute

Configuration Updates:
- Database connection pooling optimized
- Cache layer performance improved
- Security protocols updated
- Monitoring thresholds adjusted

Chapter 2: DATABASE MIGRATION
=============================

Database migration system status:
- Migration progress: 95% complete
- Data integrity: 100% verified
- Performance impact: Minimal
- Rollback capability: Available

Chapter 3: API DOCUMENTATION
============================

API documentation system:
- Documentation coverage: 98%
- Auto-generation: Enabled
- Version control: Integrated
- User feedback: Positive

Document Summary:
- Total chapters: 3
- Technical specifications: Complete
- Implementation guidelines: Detailed
- Configuration parameters: Validated
- Security considerations: Addressed

Document Information:
- Version: 1.0
- Generated: 2024-01-15
- Status: Current and approved
- Review cycle: Quarterly
```

## 🔧 Technical Implementation Details

### Credential Generation (1-10 per file)
```python
# In orchestrator.py
num_credentials = random.randint(1, 10)
credentials = []

for i in range(num_credentials):
    cred_type = random.choice(credential_types)
    credential = self.credential_generator.generate_credential(cred_type)
    credentials.append(credential)
```

### Multiple Topic Handling
```python
# In topic_generator.py
if ',' in topic:
    topics = [t.strip() for t in topic.split(',')]
    content = self._generate_combined_topics(topics, file_format, context)
```

### Realistic Content Templates
- **Email templates**: Professional business communication format
- **Excel templates**: Comprehensive configuration spreadsheets
- **PDF templates**: Technical documentation with chapters
- **PowerPoint templates**: Multi-slide presentations
- **Word templates**: Structured technical documents

## 📊 Generated File Statistics

### Example Output for 10 Files:
```
Generated Files Summary:
- Total files: 10
- Total credentials: 47 (average 4.7 per file)
- Credential distribution:
  - aws_access_key: 12
  - api_key: 15
  - jwt_token: 8
  - database_connection: 12
- Topics covered: 15 unique topics
- Formats generated: docx, xlsx, pdf, png
- Content quality: Professional grade
```

### File Examples:
1. `docx_security_audit_database_migration_20240115_143022_1234.docx` (7 credentials)
2. `xlsx_api_documentation_monitoring_setup_20240115_143023_5678.xlsx` (3 credentials)
3. `pdf_system_architecture_deployment_20240115_143024_9012.pdf` (9 credentials)
4. `png_compliance_review_20240115_143025_3456.png` (2 credentials)
5. `docx_performance_optimization_20240115_143026_7890.docx` (5 credentials)

## 🎯 Key Benefits

1. **Realistic Testing Data**: Professional-grade documents suitable for security testing
2. **Variable Complexity**: Files with 1-10 credentials provide diverse test scenarios
3. **Comprehensive Coverage**: Multiple topics create realistic multi-faceted documents
4. **Professional Quality**: Content that looks like real business documents
5. **Scalable Generation**: Can generate hundreds of files with varied content

## 🚀 Usage in Security Testing

The enhanced system now generates documents that are:
- **Indistinguishable from real documents** in appearance and content
- **Suitable for credential detection testing** with 1-10 embedded credentials
- **Comprehensive in scope** covering multiple business topics
- **Professional in quality** with proper formatting and structure
- **Varied in complexity** providing diverse test scenarios

This makes CredentialForge an ideal tool for:
- Security awareness training
- Credential detection system testing
- Document analysis tool validation
- Compliance testing scenarios
- Penetration testing exercises
