"""
Lambda Usage Example
====================

نحوه استفاده از Lexia SDK روی AWS Lambda.

این مثال نشون میده که چطور خیلی راحت agent خودتون رو Lambda-ready کنید.
"""

# ================== مثال 1: استفاده از Decorator ==================

from lexia import LexiaHandler, LambdaAdapter, ChatMessage

# Initialize handler
handler = LexiaHandler(dev_mode=False)

# Initialize adapter
adapter = LambdaAdapter()


@adapter.message_handler
async def process_message(data: ChatMessage):
    """
    Agent logic شما - دقیقاً همون چیزی که روی Docker معمولی مینویسید.
    """
    # Start session
    session = handler.begin(data)
    
    try:
        # Loading
        session.loading.start("thinking")
        
        # Your agent logic here
        response = f"پاسخ به: {data.message}"
        
        session.loading.end("thinking")
        
        # Stream result
        session.stream(response)
        
        # Add button (optional)
        session.button.link("مشاهده بیشتر", "https://example.com")
        
        # Close session
        session.close()
        
    except Exception as e:
        session.error("متأسفانه خطایی رخ داد", exception=e)


@adapter.cron_handler
async def scheduled_task(event):
    """
    Scheduled task (optional) - برای کارهای دوره‌ای.
    """
    print("[CRON] Running maintenance task...")
    # Your scheduled logic here


# Lambda handler
def lambda_handler(event, context):
    """
    این تنها چیزی است که نیاز دارید!
    Adapter خودش همه چیز رو handle میکنه:
    - HTTP requests (Function URL)
    - SQS events
    - Cron events
    """
    return adapter.handle(event, context)


# ================== مثال 2: استفاده از Helper Function ==================

"""
from lexia import LexiaHandler, create_lambda_handler, ChatMessage

handler = LexiaHandler(dev_mode=False)


async def process_message(data: ChatMessage):
    session = handler.begin(data)
    session.stream("Hello from Lambda!")
    session.close()


# یک خطی!
handler_func = create_lambda_handler(process_message)


def lambda_handler(event, context):
    return handler_func(event, context)
"""


# ================== مثال 3: با OpenAI ==================

"""
from lexia import LexiaHandler, LambdaAdapter, ChatMessage
from openai import OpenAI

handler = LexiaHandler(dev_mode=False)
adapter = LambdaAdapter()
client = OpenAI()


@adapter.message_handler
async def process_message(data: ChatMessage):
    session = handler.begin(data)
    
    try:
        session.loading.start("thinking")
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": data.message}],
            stream=True
        )
        
        session.loading.end("thinking")
        
        # Stream response
        for chunk in response:
            if chunk.choices[0].delta.content:
                session.stream(chunk.choices[0].delta.content)
        
        session.close()
        
    except Exception as e:
        session.error("خطا در پردازش درخواست", exception=e)


def lambda_handler(event, context):
    return adapter.handle(event, context)
"""


# ================== نکات مهم ==================

"""
1️⃣  Agent logic شما دقیقاً مثل قبل است!
   فقط باید async باشه.

2️⃣  Adapter خودش handle میکنه:
   - HTTP → direct یا queue to SQS
   - SQS → process message
   - Cron → scheduled task

3️⃣  Environment variables:
   - SQS_QUEUE_URL: اگر set باشه، requests به SQS میرن
   - اگر نباشه، direct process میشن

4️⃣  Deploy با lexia-cli:
   $ lexia ship my-agent --image my-agent:latest
   
   lexia-cli خودش:
   - Image رو push میکنه
   - Lambda function رو create/update میکنه
   - SQS queue رو configure میکنه
   - Function URL رو create میکنه

5️⃣  Dockerfile.lambda:
   FROM public.ecr.aws/lambda/python:3.11
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY lambda_handler.py .
   
   CMD ["lambda_handler.lambda_handler"]
"""

print(__doc__)

