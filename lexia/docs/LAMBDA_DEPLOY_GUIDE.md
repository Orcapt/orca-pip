# 🚀 Lambda Deploy Guide - Lexia SDK

**Version:** 2.0.0  
**Date:** December 15, 2025  
**Level:** Complete Deployment Guide

---

## 🎯 مقدمه

این راهنما همه چیزی که برای deploy کردن Lexia SDK روی AWS Lambda نیاز دارید را پوشش می‌دهد.

---

## 📋 پیش‌نیازها

### 1️⃣ AWS Account

- حساب AWS فعال
- IAM User با دسترسی Lambda
- AWS CLI نصب شده

### 2️⃣ ابزارهای مورد نیاز

```bash
# AWS CLI
pip install awscli

# SAM CLI (اختیاری اما توصیه می‌شود)
pip install aws-sam-cli

# Serverless Framework (جایگزین SAM)
npm install -g serverless
```

### 3️⃣ تنظیمات AWS

```bash
# Configure AWS CLI
aws configure

# ورودی‌ها:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

---

## 📦 آماده‌سازی پروژه

### ساختار پروژه

```
lambda-function/
├── lambda_function.py      # Handler اصلی
├── requirements.txt        # Dependencies
├── template.yaml          # SAM template (اختیاری)
├── serverless.yml         # Serverless config (اختیاری)
└── .env                   # Environment variables (local only)
```

### فایل `requirements.txt`

```txt
lexia-sdk>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0

# Optional dependencies
psutil>=5.9.0  # برای System Monitoring
```

---

## 🔧 پیاده‌سازی Lambda Function

### روش 1: Lambda Function ساده

**فایل: `lambda_function.py`**

```python
"""
Lambda Handler for Lexia SDK
"""

import json
import os
from lexia import LexiaHandler
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda handler

    Args:
        event: Lambda event (API Gateway format)
        context: Lambda context

    Returns:
        Response dict
    """
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))

        # Extract data
        data = {
            'channel': body.get('channel'),
            'uuid': body.get('uuid'),
            'thread_id': body.get('thread_id'),
            'prompt': body.get('prompt'),
            'stream_url': os.environ.get('CENTRIFUGO_URL'),
            'stream_token': os.environ.get('CENTRIFUGO_TOKEN'),
            'api_url': os.environ.get('API_URL'),
            'api_token': os.environ.get('API_TOKEN'),
        }

        # Validate
        required_fields = ['channel', 'uuid', 'thread_id', 'prompt']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"Missing required field: {field}")

        # Process request
        result = process_request(data)

        return success_response(result)

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return error_response(str(e))


def process_request(data):
    """Process user request with Lexia SDK"""

    # Create handler
    handler = LexiaHandler(dev_mode=False)

    # Start session
    session = handler.begin(data)

    try:
        # Loading
        session.loading.start_loading("thinking")

        # Process
        response_text = generate_response(data['prompt'])

        session.loading.end_loading("thinking")

        # Stream result
        session.stream(response_text)

        # Add button
        session.button.link("مشاهده بیشتر", "https://example.com")

        # Close session
        result = session.close()

        return result

    except Exception as e:
        # Send error to user
        session.error(
            error_message="متاسفانه خطایی رخ داد.",
            exception=e
        )
        raise


def generate_response(prompt):
    """
    Generate AI response
    این تابع را با مدل AI خود جایگزین کنید
    """
    # مثال ساده
    return f"پاسخ به: {prompt}"


def success_response(data):
    """Create success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }


def error_response(message, status_code=400):
    """Create error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
```

---

### روش 2: با Observability

```python
"""
Lambda Handler with Observability
"""

import json
import os
from lexia import (
    LexiaHandler,
    get_metrics_collector,
    get_event_bus,
)
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Setup observability
collector = get_metrics_collector()
bus = get_event_bus()

# Metrics
requests_counter = collector.counter("lambda_requests")
errors_counter = collector.counter("lambda_errors")
response_time = collector.histogram("lambda_response_time")


def lambda_handler(event, context):
    """Main Lambda handler with observability"""

    import time
    start_time = time.time()

    try:
        # Track request
        requests_counter.inc()

        # Publish event
        bus.publish("lambda.request", {
            "request_id": context.request_id,
            "function_name": context.function_name,
        })

        # Process
        body = json.loads(event.get('body', '{}'))
        result = process_request(body)

        # Track timing
        duration = time.time() - start_time
        response_time.observe(duration)

        # Publish success event
        bus.publish("lambda.success", {
            "request_id": context.request_id,
            "duration": duration,
        })

        return success_response(result)

    except Exception as e:
        # Track error
        errors_counter.inc()

        # Publish error event
        bus.publish("lambda.error", {
            "request_id": context.request_id,
            "error": str(e),
        })

        logger.error(f"Error: {e}", exc_info=True)
        return error_response(str(e))


def process_request(data):
    """Process with Lexia"""
    # ... (همان کد قبلی)
    pass
```

---

## 🏗️ Deploy با SAM (AWS Serverless Application Model)

### 1️⃣ فایل `template.yaml`

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Description: Lexia SDK Lambda Function

Globals:
  Function:
    Timeout: 300
    MemorySize: 512
    Runtime: python3.11

Resources:
  LexiaFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_function.lambda_handler
      Description: Lexia SDK Handler
      Environment:
        Variables:
          CENTRIFUGO_URL: !Ref CentrifugoUrl
          CENTRIFUGO_TOKEN: !Ref CentrifugoToken
          API_URL: !Ref ApiUrl
          API_TOKEN: !Ref ApiToken
          LOG_LEVEL: INFO
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /process
            Method: post
      Policies:
        - CloudWatchLogsFullAccess

Parameters:
  CentrifugoUrl:
    Type: String
    Description: Centrifugo server URL

  CentrifugoToken:
    Type: String
    Description: Centrifugo authentication token
    NoEcho: true

  ApiUrl:
    Type: String
    Description: Backend API URL

  ApiToken:
    Type: String
    Description: API authentication token
    NoEcho: true

Outputs:
  LexiaFunctionApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/process/"

  LexiaFunctionArn:
    Description: "Lambda Function ARN"
    Value: !GetAtt LexiaFunction.Arn
```

### 2️⃣ Deploy با SAM

```bash
# Build
sam build

# Deploy (اولین بار)
sam deploy --guided

# ورودی‌ها:
# Stack Name: lexia-lambda-stack
# AWS Region: us-east-1
# Parameter CentrifugoUrl: https://your-centrifugo.com
# Parameter CentrifugoToken: your-token
# Parameter ApiUrl: https://your-api.com
# Parameter ApiToken: your-api-token
# Confirm changes before deploy: Y
# Allow SAM CLI IAM role creation: Y
# Save arguments to configuration file: Y

# Deploy بعدی (بدون سوال)
sam deploy
```

---

## 🚀 Deploy با Serverless Framework

### 1️⃣ فایل `serverless.yml`

```yaml
service: lexia-lambda

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  memorySize: 512
  timeout: 300

  environment:
    CENTRIFUGO_URL: ${env:CENTRIFUGO_URL}
    CENTRIFUGO_TOKEN: ${env:CENTRIFUGO_TOKEN}
    API_URL: ${env:API_URL}
    API_TOKEN: ${env:API_TOKEN}
    LOG_LEVEL: INFO

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: "*"

functions:
  process:
    handler: lambda_function.lambda_handler
    description: Lexia SDK Handler
    events:
      - http:
          path: process
          method: post
          cors: true

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
    layer: true
```

### 2️⃣ نصب Plugin

```bash
npm install --save-dev serverless-python-requirements
```

### 3️⃣ فایل `.env` (برای local)

```bash
CENTRIFUGO_URL=https://your-centrifugo.com
CENTRIFUGO_TOKEN=your-token
API_URL=https://your-api.com
API_TOKEN=your-api-token
```

### 4️⃣ Deploy

```bash
# Deploy به dev
serverless deploy --stage dev

# Deploy به production
serverless deploy --stage prod

# Deploy فقط function (سریع‌تر)
serverless deploy function -f process
```

---

## 📦 Deploy دستی با AWS CLI

### 1️⃣ ساخت Deployment Package

```bash
# Create directory
mkdir lambda-package
cd lambda-package

# Install dependencies
pip install -r ../requirements.txt -t .

# Copy handler
cp ../lambda_function.py .

# Create zip
zip -r ../lambda-function.zip .
cd ..
```

### 2️⃣ Create Lambda Function

```bash
# Create IAM role
aws iam create-role \
  --role-name lexia-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policy
aws iam attach-role-policy \
  --role-name lexia-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create function
aws lambda create-function \
  --function-name lexia-function \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lexia-lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-function.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{
    CENTRIFUGO_URL=https://your-centrifugo.com,
    CENTRIFUGO_TOKEN=your-token,
    API_URL=https://your-api.com,
    API_TOKEN=your-api-token
  }"
```

### 3️⃣ Update Function

```bash
# Update code
aws lambda update-function-code \
  --function-name lexia-function \
  --zip-file fileb://lambda-function.zip

# Update environment
aws lambda update-function-configuration \
  --function-name lexia-function \
  --environment Variables="{
    CENTRIFUGO_URL=https://new-url.com,
    CENTRIFUGO_TOKEN=new-token
  }"
```

---

## 🔌 API Gateway Integration

### با SAM/Serverless

API Gateway به طور خودکار ایجاد می‌شود.

### ایجاد دستی

```bash
# Create REST API
aws apigateway create-rest-api \
  --name lexia-api \
  --description "Lexia SDK API"

# Get REST API ID
REST_API_ID=xxxxx

# Get root resource ID
aws apigateway get-resources \
  --rest-api-id $REST_API_ID

# Create resource
aws apigateway create-resource \
  --rest-api-id $REST_API_ID \
  --parent-id ROOT_RESOURCE_ID \
  --path-part process

# Create POST method
aws apigateway put-method \
  --rest-api-id $REST_API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id $REST_API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:REGION:ACCOUNT_ID:function:lexia-function/invocations

# Deploy
aws apigateway create-deployment \
  --rest-api-id $REST_API_ID \
  --stage-name prod
```

---

## 🧪 Testing

### Local Testing با SAM

```bash
# Invoke local
sam local invoke LexiaFunction \
  --event test-event.json

# Start API local
sam local start-api
```

**فایل `test-event.json`:**

```json
{
  "body": "{\"channel\": \"test-channel\", \"uuid\": \"test-uuid\", \"thread_id\": \"test-thread\", \"prompt\": \"Hello\"}",
  "headers": {
    "Content-Type": "application/json"
  },
  "httpMethod": "POST",
  "path": "/process"
}
```

### Testing Remote

```bash
# با AWS CLI
aws lambda invoke \
  --function-name lexia-function \
  --payload '{"body": "{\"channel\": \"test\", \"uuid\": \"123\", \"thread_id\": \"456\", \"prompt\": \"Hello\"}"}' \
  response.json

cat response.json
```

### Testing با curl

```bash
curl -X POST https://YOUR_API_GATEWAY_URL/prod/process \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "test-channel",
    "uuid": "test-uuid",
    "thread_id": "test-thread",
    "prompt": "سلام، چطوری؟"
  }'
```

---

## 📊 Monitoring & Logging

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/lambda/lexia-function --follow

# Filter logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/lexia-function \
  --filter-pattern "ERROR"
```

### CloudWatch Metrics

Lambda automatically logs:

- Invocations
- Duration
- Errors
- Throttles

### Custom Metrics با Lexia

```python
from lexia import get_metrics_collector

collector = get_metrics_collector()

# در Lambda handler
requests = collector.counter("custom_requests")
requests.inc()

# Log metrics
logger.info(f"Metrics: {collector.get_metrics()}")
```

---

## ⚙️ بهینه‌سازی Performance

### 1️⃣ Cold Start Optimization

```python
# Global variables (خارج از handler)
# فقط یک بار initialize می‌شوند

from lexia import LexiaHandler

# Handler را global تعریف کنید
_handler = None

def get_handler():
    global _handler
    if _handler is None:
        _handler = LexiaHandler(dev_mode=False)
    return _handler

def lambda_handler(event, context):
    handler = get_handler()  # Reuse handler
    # ...
```

### 2️⃣ Memory Optimization

```yaml
# template.yaml
MemorySize: 1024 # افزایش memory = افزایش CPU

# تست کنید: 512MB, 1024MB, 2048MB
```

### 3️⃣ Timeout

```yaml
Timeout: 300 # 5 minutes (max)
```

### 4️⃣ Provisioned Concurrency

```bash
# برای کاهش cold start
aws lambda put-provisioned-concurrency-config \
  --function-name lexia-function \
  --provisioned-concurrent-executions 2
```

---

## 🔐 Security Best Practices

### 1️⃣ Environment Variables

```bash
# از SSM Parameter Store استفاده کنید
aws ssm put-parameter \
  --name /lexia/centrifugo-token \
  --value "your-secret-token" \
  --type SecureString
```

```python
# در Lambda
import boto3

ssm = boto3.client('ssm')

def get_parameter(name):
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

CENTRIFUGO_TOKEN = get_parameter('/lexia/centrifugo-token')
```

### 2️⃣ IAM Permissions

```yaml
# Minimum permissions
iamRoleStatements:
  - Effect: Allow
    Action:
      - logs:CreateLogGroup
      - logs:CreateLogStream
      - logs:PutLogEvents
    Resource: "*"

  - Effect: Allow
    Action:
      - ssm:GetParameter
    Resource: "arn:aws:ssm:*:*:parameter/lexia/*"
```

### 3️⃣ VPC Configuration

```yaml
# اگر نیاز به دسترسی به منابع private دارید
vpc:
  securityGroupIds:
    - sg-xxxxxx
  subnetIds:
    - subnet-xxxxxx
    - subnet-yyyyyy
```

---

## 💰 Cost Optimization

### 1️⃣ Pricing Calculator

```
Lambda Pricing:
- First 1M requests/month: FREE
- $0.20 per 1M requests after
- $0.0000166667 per GB-second

Example (512MB, 2s duration):
- 1M requests = $208
- 100K requests = $21
```

### 2️⃣ Optimization Tips

```python
# 1. Reduce dependencies
# فقط چیزهایی که نیاز دارید را import کنید

# 2. Use layers برای libraries بزرگ
# psutil, numpy, etc.

# 3. Optimize memory
# تست کنید و minimum memory لازم را پیدا کنید

# 4. Reduce cold starts
# با warm-up requests یا provisioned concurrency
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

**فایل: `.github/workflows/deploy.yml`**

```yaml
name: Deploy to Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install aws-sam-cli

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: SAM Build
        run: sam build

      - name: SAM Deploy
        run: |
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset \
            --parameter-overrides \
              CentrifugoUrl=${{ secrets.CENTRIFUGO_URL }} \
              CentrifugoToken=${{ secrets.CENTRIFUGO_TOKEN }} \
              ApiUrl=${{ secrets.API_URL }} \
              ApiToken=${{ secrets.API_TOKEN }}
```

---

## 📚 مثال کامل Production-Ready

```python
"""
Production-ready Lambda Handler
"""

import json
import os
import logging
import boto3
from typing import Dict, Any
from lexia import (
    LexiaHandler,
    get_metrics_collector,
    get_event_bus,
    SystemMonitor,
)
from lexia.patterns import timed_operation

# Setup logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Global handler (reuse across invocations)
_handler = None
_metrics_collector = get_metrics_collector()
_event_bus = get_event_bus()

# SSM client for secrets
ssm = boto3.client('ssm')


def get_handler() -> LexiaHandler:
    """Get or create handler (singleton pattern)"""
    global _handler
    if _handler is None:
        _handler = LexiaHandler(dev_mode=False)
        logger.info("Handler initialized")
    return _handler


def get_secret(name: str) -> str:
    """Get secret from SSM Parameter Store"""
    try:
        response = ssm.get_parameter(
            Name=name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error getting secret {name}: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler with full observability

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response dict
    """
    # Metrics
    requests = _metrics_collector.counter("lambda_requests")
    errors = _metrics_collector.counter("lambda_errors")
    duration_hist = _metrics_collector.histogram("lambda_duration")

    import time
    start_time = time.time()

    try:
        # Log request
        logger.info(f"Request ID: {context.request_id}")
        logger.info(f"Function: {context.function_name}")
        logger.info(f"Memory: {context.memory_limit_in_mb}MB")

        # Track metrics
        requests.inc()

        # Publish event
        _event_bus.publish("lambda.request.started", {
            "request_id": context.request_id,
            "function": context.function_name,
        })

        # Parse body
        body = json.loads(event.get('body', '{}'))

        # Validate
        required = ['channel', 'uuid', 'thread_id', 'prompt']
        for field in required:
            if not body.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Get secrets
        data = {
            'channel': body['channel'],
            'uuid': body['uuid'],
            'thread_id': body['thread_id'],
            'prompt': body['prompt'],
            'stream_url': get_secret('/lexia/centrifugo-url'),
            'stream_token': get_secret('/lexia/centrifugo-token'),
            'api_url': get_secret('/lexia/api-url'),
            'api_token': get_secret('/lexia/api-token'),
        }

        # Process with timing
        with timed_operation("request_processing"):
            result = process_request(data, context)

        # Track duration
        duration = time.time() - start_time
        duration_hist.observe(duration)

        # Log metrics
        logger.info(f"Metrics: {_metrics_collector.get_metrics()}")

        # Publish success event
        _event_bus.publish("lambda.request.completed", {
            "request_id": context.request_id,
            "duration": duration,
        })

        return success_response(result)

    except Exception as e:
        # Track error
        errors.inc()

        # Log error
        logger.error(f"Error processing request: {e}", exc_info=True)

        # Publish error event
        _event_bus.publish("lambda.request.failed", {
            "request_id": context.request_id,
            "error": str(e),
        })

        return error_response(str(e))


def process_request(data: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Process request with Lexia SDK"""

    handler = get_handler()
    session = handler.begin(data)

    try:
        # Loading
        session.loading.start_loading("thinking")

        # Generate response
        response_text = generate_ai_response(data['prompt'])

        session.loading.end_loading("thinking")

        # Stream
        session.stream(response_text)

        # Buttons
        session.button.link("ادامه", "https://example.com")

        # Close
        result = session.close()

        return result

    except Exception as e:
        session.error(
            error_message="متاسفانه خطایی رخ داد.",
            exception=e
        )
        raise


def generate_ai_response(prompt: str) -> str:
    """
    Generate AI response
    اینجا باید مدل AI خودتان را فراخوانی کنید
    """
    # TODO: Implement your AI model
    return f"پاسخ به: {prompt}"


def success_response(data: Any) -> Dict[str, Any]:
    """Create success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }


def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Create error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
```

---

## ✅ Checklist قبل از Deploy

- [ ] Dependencies در `requirements.txt` کامل است
- [ ] Environment variables تنظیم شده‌اند
- [ ] IAM role و permissions درست هستند
- [ ] Timeout مناسب است (300s recommended)
- [ ] Memory size بهینه است (512MB-1024MB recommended)
- [ ] Logging به درستی کار می‌کند
- [ ] Error handling کامل است
- [ ] Testing local انجام شده
- [ ] Security best practices رعایت شده
- [ ] Monitoring و alerts تنظیم شده

---

## 📞 پشتیبانی

- **AWS Documentation:** https://docs.aws.amazon.com/lambda/
- **SAM Documentation:** https://docs.aws.amazon.com/serverless-application-model/
- **Serverless Framework:** https://www.serverless.com/framework/docs/
- **Lexia Issues:** https://github.com/your-org/lexia-sdk/issues

---

**این راهنما به طور مداوم به‌روز می‌شود. آخرین به‌روزرسانی: December 15, 2025**
