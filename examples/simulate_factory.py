"""
Simulation script for Hybrid Factory Example
=============================================

This script uses `simulate_lambda_handler` to test 'lambda_factory_usage.py' 
across all supported event types (HTTP, SQS, Cron) in one go.
"""

import os
import sys

# Add parent directory to path so we can import the example
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orca import simulate_lambda_handler
from lambda_factory_usage import handler

# Force DEV MODE for verbose console output (simulates DevStream)
os.environ["ORCA_DEV_MODE"] = "true"

if __name__ == "__main__":
    print("🧪 Starting Factory Simulation...\n")
    
    # This utility executes:
    # 1. A mock HTTP POST request to /api/v1/send_message
    # 2. A mock SQS Record event
    # 3. A mock Scheduled Event (Cron)
    simulate_lambda_handler(
        handler=handler, 
        message="Hello from the simulator!"
    )
