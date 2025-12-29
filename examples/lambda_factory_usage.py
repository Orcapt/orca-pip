"""
Lambda Handler - Refactored with Orca Factory
Supports HTTP (with SQS offload), SQS (async task), and Cron events automatically.

Usage: 
1. Build: docker build -f Dockerfile.lambda -t my-agent .
2. Deploy: orca ship my-agent --image my-agent
"""

import logging
from orca import create_hybrid_handler
from main import process_message

# Create the universal Lambda handler using the Orca factory
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="Orca SEO Agent Lambda",
    level=logging.INFO
)