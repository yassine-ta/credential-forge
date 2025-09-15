# CredentialForge Examples

## Table of Contents

1. [Basic Usage Examples](#basic-usage-examples)
2. [Advanced Configuration](#advanced-configuration)
3. [Interactive Mode Examples](#interactive-mode-examples)
4. [Custom Credential Types](#custom-credential-types)
5. [Batch Processing](#batch-processing)
6. [LLM Integration Examples](#llm-integration-examples)
7. [File Format Examples](#file-format-examples)
8. [Real-World Scenarios](#real-world-scenarios)

## Basic Usage Examples

### Example 1: Simple Email Generation

Generate a single email file with AWS credentials embedded in system architecture documentation.

```bash
credentialforge generate \
  --output-dir ./test_docs \
  --num-files 1 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture with database integration"
```

**Expected Output:**
```
Generated 1 files in ./test_docs/
- fake_architecture_001.eml (contains AWS access key in email body)
```

### Example 2: Multiple File Formats

Generate documents in multiple formats with different credential types.

```bash
credentialforge generate \
  --output-dir ./bulk_docs \
  --num-files 10 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection \
  --regex-db ./regex_db.json \
  --topics "API documentation, database schemas, system integration" \
  --batch-size 5
```

**Expected Output:**
```
Generated 10 files in ./bulk_docs/
- 4 EML files with embedded credentials
- 3 Excel files with credentials in formulas
- 3 PowerPoint files with credentials in slide content
```

### Example 3: Custom Embedding Strategy

Use specific embedding strategies for different file types.

```bash
credentialforge generate \
  --output-dir ./strategic_docs \
  --num-files 5 \
  --formats eml,excel \
  --credential-types api_key,password \
  --regex-db ./regex_db.json \
  --topics "configuration management" \
  --embed-strategy body
```

## Advanced Configuration

### Example 4: Reproducible Generation

Generate files with a specific seed for reproducible results.

```bash
credentialforge generate \
  --output-dir ./reproducible_docs \
  --num-files 20 \
  --formats eml,excel \
  --credential-types aws_access_key,jwt_token \
  --regex-db ./regex_db.json \
  --topics "microservices architecture" \
  --seed 42 \
  --log-level DEBUG
```

### Example 5: Large Batch Processing

Process a large number of files with optimized batch size.

```bash
credentialforge generate \
  --output-dir ./large_batch \
  --num-files 1000 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection,api_key \
  --regex-db ./regex_db.json \
  --topics "system documentation,API guides,database schemas,security policies" \
  --batch-size 50 \
  --log-level INFO
```

### Example 6: Custom Regex Database

Use a custom regex database with specific patterns.

```json
{
  "credentials": [
    {
      "type": "github_token",
      "regex": "^ghp_[A-Za-z0-9]{36}$",
      "description": "GitHub Personal Access Token",
      "generator": "random_string(40, 'A-Za-z0-9')"
    },
    {
      "type": "slack_token",
      "regex": "^xoxb-[0-9]{11}-[0-9]{11}-[A-Za-z0-9]{24}$",
      "description": "Slack Bot Token",
      "generator": "construct_slack_token()"
    },
    {
      "type": "stripe_key",
      "regex": "^sk_test_[A-Za-z0-9]{24}$",
      "description": "Stripe Test Secret Key",
      "generator": "construct_stripe_key()"
    }
  ]
}
```

```bash
credentialforge generate \
  --output-dir ./custom_docs \
  --num-files 15 \
  --formats eml,excel \
  --credential-types github_token,slack_token,stripe_key \
  --regex-db ./custom_regex_db.json \
  --topics "development workflow, team collaboration, payment integration"
```

## Interactive Mode Examples

### Example 7: Interactive Configuration

Launch interactive mode for guided configuration.

```bash
credentialforge interactive
```

**Interactive Session:**
```
Welcome to CredentialForge Interactive Mode!

Output Directory: ./interactive_docs
Number of Files: 25
File Formats: eml,excel,pptx
Credential Types: aws_access_key,jwt_token,db_connection
Regex Database: ./regex_db.json
Topics: microservices architecture,API documentation,database design

Preview generated content? [y/N]: y

Sample Topic Content:
"Microservices Architecture Overview

This document outlines the microservices architecture for our platform, including:
- API Gateway configuration with authentication tokens
- Database connections for each service
- Inter-service communication patterns

API Gateway Configuration:
The API gateway uses JWT tokens for authentication. Example token: [JWT_TOKEN_PLACEHOLDER]

Database Connections:
Each microservice connects to its dedicated database using connection strings like: [DB_CONNECTION_PLACEHOLDER]

AWS Integration:
Services use AWS access keys for cloud resource management: [AWS_KEY_PLACEHOLDER]"

Continue with generation? [Y/n]: y

Generating files...
[████████████████████████████████] 100% (25/25)

Generation complete! 25 files created in ./interactive_docs/
```

### Example 8: Interactive Preview and Adjustment

Use interactive mode to preview and adjust generation parameters.

```bash
credentialforge interactive
```

**Interactive Session with Adjustments:**
```
Output Directory: ./preview_docs
Number of Files: 5
File Formats: eml
Credential Types: aws_access_key
Topics: system architecture

Preview sample content? [y/N]: y

Sample Content:
"System Architecture Documentation

Our system architecture includes:
- Load balancers with AWS access keys: AKIA1234567890ABCDEF
- Database clusters with connection strings
- API services with authentication tokens

The architecture follows microservices patterns..."

Adjust content style? [y/N]: y
Content Style Options:
1. Technical documentation
2. Email communication
3. Presentation slides
4. Configuration file

Select style [1-4]: 2

Updated Sample Content:
"Subject: System Architecture Update

Hi Team,

I wanted to share an update on our system architecture. We've implemented several new components:

1. Load Balancer Configuration
   - AWS Access Key: AKIA1234567890ABCDEF
   - Region: us-east-1
   - Instance type: t3.medium

2. Database Setup
   - Primary database cluster configured
   - Connection strings distributed to services
   - Backup procedures in place

Let me know if you have any questions.

Best regards,
System Admin"

Continue with this style? [Y/n]: y
```

## Custom Credential Types

### Example 9: Adding Custom Credential Types

Add new credential types to the database.

```bash
# Add GitHub token
credentialforge db add \
  --type github_token \
  --regex "^ghp_[A-Za-z0-9]{36}$" \
  --description "GitHub Personal Access Token" \
  --generator "random_string(40, 'A-Za-z0-9')"

# Add Docker registry token
credentialforge db add \
  --type docker_token \
  --regex "^[A-Za-z0-9+/]{64}={0,2}$" \
  --description "Docker Registry Token" \
  --generator "base64_encode(random_bytes(48))"

# Add custom API key format
credentialforge db add \
  --type custom_api_key \
  --regex "^[A-Z]{3}_[0-9]{8}_[A-Za-z0-9]{16}$" \
  --description "Custom API Key Format" \
  --generator "construct_custom_api_key()"
```

### Example 10: Using Custom Credential Types

Generate files with custom credential types.

```bash
credentialforge generate \
  --output-dir ./custom_creds \
  --num-files 8 \
  --formats eml,excel \
  --credential-types github_token,docker_token,custom_api_key \
  --regex-db ./regex_db.json \
  --topics "development environment setup, container deployment, API integration"
```

## Batch Processing

### Example 11: Parallel Batch Processing

Process multiple batches in parallel for better performance.

```bash
credentialforge generate \
  --output-dir ./parallel_docs \
  --num-files 200 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection,api_key \
  --regex-db ./regex_db.json \
  --topics "system documentation,API guides,database schemas,security policies" \
  --batch-size 25
```

**Performance Output:**
```
Starting batch processing...
Batch 1/8: [████████████████████████████████] 100% (25/25) - 2.3s
Batch 2/8: [████████████████████████████████] 100% (25/25) - 2.1s
Batch 3/8: [████████████████████████████████] 100% (25/25) - 2.4s
...
Total time: 18.7s
Average time per file: 0.094s
```

### Example 12: Memory-Optimized Processing

Process large batches with memory optimization.

```bash
credentialforge generate \
  --output-dir ./memory_optimized \
  --num-files 500 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture" \
  --batch-size 10 \
  --log-level INFO
```

## LLM Integration Examples

### Example 13: Using TinyLlama Model

Generate content using the lightweight TinyLlama model.

```bash
# Download TinyLlama model
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Generate with LLM
credentialforge generate \
  --output-dir ./llm_docs \
  --num-files 10 \
  --formats eml,excel \
  --credential-types aws_access_key,jwt_token \
  --regex-db ./regex_db.json \
  --topics "microservices architecture,API documentation" \
  --llm-model ./tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### Example 14: Using Phi-3 Mini Model

Generate content using the more capable Phi-3 Mini model.

```bash
# Download Phi-3 Mini model
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Generate with enhanced LLM
credentialforge generate \
  --output-dir ./phi3_docs \
  --num-files 20 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection \
  --regex-db ./regex_db.json \
  --topics "enterprise architecture,cloud migration,security policies" \
  --llm-model ./Phi-3-mini-4k-instruct-q4.gguf \
  --batch-size 5
```

### Example 15: LLM Performance Comparison

Compare different models for content generation quality.

```bash
# Test with TinyLlama (fast, lower quality)
time credentialforge generate \
  --output-dir ./tinyllama_test \
  --num-files 5 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture" \
  --llm-model ./tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Test with Phi-3 Mini (slower, higher quality)
time credentialforge generate \
  --output-dir ./phi3_test \
  --num-files 5 \
  --formats eml \
  --credential-types aws_access_key \
  --regex-db ./regex_db.json \
  --topics "system architecture" \
  --llm-model ./Phi-3-mini-4k-instruct-q4.gguf
```

## File Format Examples

### Example 16: EML Email Generation

Generate realistic email files with embedded credentials.

```bash
credentialforge generate \
  --output-dir ./email_docs \
  --num-files 5 \
  --formats eml \
  --credential-types aws_access_key,jwt_token \
  --regex-db ./regex_db.json \
  --topics "system maintenance,security updates,configuration changes" \
  --embed-strategy body
```

**Generated EML Content Example:**
```
From: admin@company.com
To: dev-team@company.com
Subject: System Maintenance - Database Migration

Hi Team,

We're planning to migrate our database to a new cluster this weekend. 
Here are the connection details:

Database Connection String: mysql://admin:securepass123@db-cluster.company.com:3306/production
AWS Access Key for backup: AKIA1234567890ABCDEF

Please ensure all services are updated with the new connection string.

Best regards,
System Admin
```

### Example 17: Excel Spreadsheet Generation

Generate Excel files with credentials in formulas and data.

```bash
credentialforge generate \
  --output-dir ./excel_docs \
  --num-files 3 \
  --formats excel \
  --credential-types aws_access_key,db_connection,api_key \
  --regex-db ./regex_db.json \
  --topics "API configuration,database connections,service endpoints" \
  --embed-strategy body
```

**Generated Excel Content Example:**
```
Worksheet: API Configuration
A1: Service Name
B1: Endpoint
C1: API Key
D1: Status

A2: User Service
B2: https://api.company.com/users
C2: =CONCAT("Bearer ", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
D2: Active

A3: Payment Service
B3: https://api.company.com/payments
C3: =CONCAT("sk_test_", "51tu_test_1234567890abcdef")
D3: Active

Worksheet: Database Connections
A1: Service
B1: Connection String
C1: Status

A2: User DB
B2: =CONCAT("postgres://user:", "securepass123", "@db.company.com:5432/users")
C2: Active
```

### Example 18: PowerPoint Presentation Generation

Generate PowerPoint files with credentials in slide content.

```bash
credentialforge generate \
  --output-dir ./pptx_docs \
  --num-files 2 \
  --formats pptx \
  --credential-types aws_access_key,jwt_token \
  --regex-db ./regex_db.json \
  --topics "system architecture overview,security implementation" \
  --embed-strategy body
```

**Generated PowerPoint Content Example:**
```
Slide 1: System Architecture Overview
Title: Microservices Architecture
Content:
- API Gateway with JWT authentication
- Database services with connection pooling
- AWS integration for cloud resources

JWT Token for API Gateway: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
AWS Access Key: AKIA1234567890ABCDEF

Slide 2: Security Implementation
Title: Authentication and Authorization
Content:
- JWT tokens for service-to-service communication
- AWS IAM roles for resource access
- Database encryption at rest

Service Authentication Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Real-World Scenarios

### Example 19: Security Testing Scenario

Generate test data for security scanning tools.

```bash
# Generate diverse test data for security scanning
credentialforge generate \
  --output-dir ./security_test \
  --num-files 100 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection,api_key,github_token \
  --regex-db ./regex_db.json \
  --topics "development documentation,deployment guides,configuration files,API documentation" \
  --batch-size 20 \
  --seed 12345
```

**Use Case:** Test security scanning tools like GitGuardian, TruffleHog, or custom scanners.

### Example 20: Educational Training Scenario

Generate training materials for security awareness.

```bash
# Generate training materials
credentialforge generate \
  --output-dir ./training_materials \
  --num-files 25 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection \
  --regex-db ./regex_db.json \
  --topics "security best practices,credential management,data protection" \
  --embed-strategy body
```

**Use Case:** Train developers and security teams on identifying exposed credentials.

### Example 21: Compliance Testing Scenario

Generate test data for compliance auditing.

```bash
# Generate compliance test data
credentialforge generate \
  --output-dir ./compliance_test \
  --num-files 50 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection,api_key \
  --regex-db ./regex_db.json \
  --topics "GDPR compliance,SOX compliance,PCI DSS requirements,security policies" \
  --batch-size 10
```

**Use Case:** Test compliance scanning tools and audit procedures.

### Example 22: Development Environment Setup

Generate configuration files for development environments.

```bash
# Generate development configuration
credentialforge generate \
  --output-dir ./dev_config \
  --num-files 10 \
  --formats eml,excel \
  --credential-types aws_access_key,jwt_token,db_connection \
  --regex-db ./regex_db.json \
  --topics "development environment setup,local configuration,testing procedures" \
  --embed-strategy metadata
```

**Use Case:** Create realistic development environment documentation with embedded credentials.

### Example 23: Penetration Testing Scenario

Generate test data for penetration testing exercises.

```bash
# Generate penetration testing data
credentialforge generate \
  --output-dir ./pentest_data \
  --num-files 75 \
  --formats eml,excel,pptx \
  --credential-types aws_access_key,jwt_token,db_connection,api_key,github_token,slack_token \
  --regex-db ./regex_db.json \
  --topics "system documentation,API guides,deployment procedures,incident response" \
  --batch-size 15 \
  --seed 999
```

**Use Case:** Simulate real-world credential exposure scenarios for penetration testing.

### Example 24: CI/CD Pipeline Testing

Generate test data for CI/CD pipeline security testing.

```bash
# Generate CI/CD test data
credentialforge generate \
  --output-dir ./cicd_test \
  --num-files 30 \
  --formats eml,excel \
  --credential-types aws_access_key,jwt_token,db_connection,github_token,docker_token \
  --regex-db ./regex_db.json \
  --topics "CI/CD pipeline configuration,deployment scripts,environment setup" \
  --embed-strategy body
```

**Use Case:** Test CI/CD pipeline security scanning and credential detection.

## Validation Examples

### Example 25: File Validation

Validate generated files for credential detectability.

```bash
# Validate single file
credentialforge validate \
  --file ./test_docs/fake_architecture_001.eml \
  --regex-db ./regex_db.json \
  --verbose

# Validate multiple files
for file in ./test_docs/*.eml; do
  echo "Validating $file"
  credentialforge validate --file "$file" --regex-db ./regex_db.json
done
```

**Validation Output:**
```
Validating ./test_docs/fake_architecture_001.eml
✓ AWS Access Key detected: AKIA1234567890ABCDEF
✓ JWT Token detected: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✓ Database Connection detected: mysql://user:pass@host:3306/db
✓ File format valid: EML
✓ Content relevance: 95% (system architecture)
```

### Example 26: Batch Validation

Validate entire directories of generated files.

```bash
# Create validation script
cat > validate_batch.sh << 'EOF'
#!/bin/bash
OUTPUT_DIR="./test_docs"
REGEX_DB="./regex_db.json"

echo "Validating all files in $OUTPUT_DIR"
total_files=0
valid_files=0

for file in "$OUTPUT_DIR"/*; do
  if [ -f "$file" ]; then
    total_files=$((total_files + 1))
    echo "Validating: $(basename "$file")"
    if credentialforge validate --file "$file" --regex-db "$REGEX_DB"; then
      valid_files=$((valid_files + 1))
    fi
  fi
done

echo "Validation complete: $valid_files/$total_files files valid"
EOF

chmod +x validate_batch.sh
./validate_batch.sh
```

These examples demonstrate the versatility and power of CredentialForge for various security testing, educational, and development scenarios. The tool can be adapted to specific needs through configuration, custom credential types, and different file formats.
