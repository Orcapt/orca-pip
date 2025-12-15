# 📦 Lexia Storage SDK - Developer Guide

**Version:** 2.0.0  
**Date:** December 15, 2025  
**Level:** Complete Developer Reference

---

## 🎯 مقدمه

این راهنما همه چیزی که برای استفاده از Lexia SDK نیاز دارید را پوشش می‌دهد. از نصب ساده تا استفاده پیشرفته.

---

## 📥 نصب

### نصب از PyPI (توصیه می‌شود):

```bash
pip install lexia-sdk
```

### نصب از GitHub:

```bash
pip install git+https://github.com/your-org/lexia-sdk.git
```

### نصب در حالت Development:

```bash
git clone https://github.com/your-org/lexia-sdk.git
cd lexia-sdk
pip install -e .
```

---

## 🚀 شروع سریع (Quick Start)

### 1. ساده‌ترین استفاده:

```python
from lexia import LexiaHandler

# ایجاد handler
handler = LexiaHandler(dev_mode=True)  # dev_mode=True برای تست محلی

# شروع session
session = handler.begin(data)

# ارسال محتوا
session.stream("سلام! این یک پیام تستی است.")
session.stream("در حال پردازش...")

# بستن session
response = session.close()
print(response)
```

### 2. با استفاده از Loading و Buttons:

```python
from lexia import LexiaHandler

handler = LexiaHandler(dev_mode=True)
session = handler.begin(data)

# نمایش loading
session.loading.start_loading("thinking")

# پردازش
import time
time.sleep(2)

session.loading.end_loading("thinking")

# ارسال نتیجه
session.stream("پردازش انجام شد!")

# اضافه کردن دکمه
session.button.link("مشاهده بیشتر", "https://example.com")

response = session.close()
```

---

## 🏗️ معماری و ساختار

### Component Layers:

```
lexia/
├── core/              # هسته اصلی (Handler, Session)
├── domain/            # مدل‌ها و interface ها
├── services/          # سرویس‌های business logic
├── infrastructure/    # ارتباط با خارج (API, Streaming)
├── patterns/          # Design patterns (Builder, Middleware)
├── observability/     # Metrics, Profiling, Events
├── common/            # Exception, Decorators, Type Guards
├── helpers/           # کلاس‌های کمکی
├── utils/             # توابع utility
└── web/               # Web framework integration
```

---

## 📚 استفاده کامل

### 1️⃣ ایجاد Handler

#### روش ساده:

```python
from lexia import LexiaHandler

handler = LexiaHandler(dev_mode=True)
```

#### روش پیشرفته (با Builder Pattern):

```python
from lexia import LexiaBuilder

handler = (
    LexiaBuilder()
    .with_dev_mode(True)
    .with_stream_client(custom_client)
    .build()
)
```

### 2️⃣ مدیریت Session

#### شروع و پایان Session:

```python
# شروع session
session = handler.begin(data)

# کار با session
session.stream("محتوای اول")
session.stream("محتوای دوم")

# بستن session
response = session.close()
```

#### استفاده از Context Manager:

```python
from lexia.patterns import SessionContext

with SessionContext(handler, data) as session:
    session.stream("محتوا")
    # session به طور خودکار بسته می‌شود
```

### 3️⃣ Streaming Content

#### Stream ساده:

```python
session.stream("این یک متن ساده است.")
```

#### Stream چند مرحله‌ای:

```python
# مرحله 1
session.stream("در حال بررسی داده‌ها...")

# پردازش
process_data()

# مرحله 2
session.stream("\n\nنتایج:")
for result in results:
    session.stream(f"\n- {result}")
```

#### Stream با Chunking:

```python
# برای محتوای طولانی
long_text = generate_long_response()

# به صورت خودکار chunk می‌شود
session.stream(long_text)
```

### 4️⃣ Loading Markers

```python
from lexia.config import LoadingKind

# انواع loading
session.loading.start_loading("thinking")     # در حال فکر کردن
session.loading.start_loading("searching")    # در حال جستجو
session.loading.start_loading("coding")       # در حال کد نویسی
session.loading.start_loading("analyzing")    # در حال تحلیل
session.loading.start_loading("generating")   # در حال تولید

# انجام کار
do_heavy_work()

# پایان loading
session.loading.end_loading("thinking")
```

### 5️⃣ Buttons

#### دکمه Link:

```python
session.button.link(
    label="مشاهده سایت",
    url="https://example.com",
    row=1,
    color="primary"
)
```

#### دکمه Action:

```python
session.button.action(
    label="تایید",
    action_id="confirm_action",
    row=1,
    color="success"
)
```

#### چند دکمه همزمان:

```python
# شروع batch
session.button.buttons_begin(default_row=1)

# اضافه کردن دکمه‌ها
session.button.buttons_add_link("گزینه 1", "https://example.com/1")
session.button.buttons_add_link("گزینه 2", "https://example.com/2")
session.button.buttons_add_action("انجام عملیات", "do_action")

# پایان batch
session.button.buttons_end()
```

#### استفاده از Helper Method:

```python
session.button.buttons(
    {"type": "link", "label": "لینک 1", "url": "https://example.com"},
    {"type": "action", "label": "عملیات", "action_id": "action_1"},
    defaults={"row": 1, "color": "primary"}
)
```

### 6️⃣ Images

```python
# ارسال تصویر
session.image.image("https://example.com/image.jpg")

# یا
session.pass_image("https://example.com/image.jpg")
```

### 7️⃣ Tracing

```python
# شروع trace
session.tracing.begin("در حال فراخوانی API...", visibility="all")

# اضافه کردن لاگ
session.tracing.append("پاسخ دریافت شد")
session.tracing.append("در حال پردازش...")

# پایان trace
session.tracing.end("پردازش تمام شد")
```

### 8️⃣ Usage Tracking

```python
from lexia.config import TokenType

# ثبت token usage
session.usage.track(
    tokens=1500,
    token_type="prompt",
    cost="0.003",
    label="GPT-4"
)

session.usage.track(
    tokens=500,
    token_type="completion",
    cost="0.001",
    label="GPT-4"
)
```

### 9️⃣ Error Handling

```python
try:
    # کار اصلی
    result = risky_operation()
    session.stream(f"نتیجه: {result}")

except Exception as e:
    # ارسال خطا به کاربر
    session.error(
        error_message="متاسفانه خطایی رخ داد",
        exception=e,
        trace=traceback.format_exc()
    )
```

---

## 🎨 Design Patterns

### 1️⃣ Builder Pattern

```python
from lexia import LexiaBuilder

handler = (
    LexiaBuilder()
    .with_dev_mode(True)
    .with_stream_client(my_client)
    .build()
)
```

### 2️⃣ Context Managers

```python
from lexia.patterns import SessionContext, timed_operation

# Session با cleanup خودکار
with SessionContext(handler, data) as session:
    session.stream("محتوا")

# اندازه‌گیری زمان
with timed_operation("database_query"):
    results = db.query(...)
```

### 3️⃣ Middleware Pattern

```python
from lexia.patterns import (
    MiddlewareChain,
    LoggingMiddleware,
    ValidationMiddleware,
)

# ساخت pipeline
chain = MiddlewareChain()
chain.add(LoggingMiddleware())

def validate(data):
    return 'user_id' in data

chain.add(ValidationMiddleware(validate))

# پردازش
processed = chain.process_request(request_data)
```

---

## 🔭 Observability

### 1️⃣ Metrics

```python
from lexia import get_metrics_collector

collector = get_metrics_collector()

# Counter
requests = collector.counter("api_requests")
requests.inc()

# Gauge
active_users = collector.gauge("active_users")
active_users.set(150)

# Histogram
response_time = collector.histogram("response_time_seconds")
response_time.observe(0.234)

# دریافت metrics
all_metrics = collector.get_metrics()
```

### 2️⃣ Performance Profiling

```python
from lexia import profile

@profile(sort_by='time', limit=10)
def expensive_function():
    # کد پیچیده
    pass

# یا با context manager
from lexia.observability import Profiler

with Profiler() as prof:
    expensive_operation()
prof.print_stats()
```

### 3️⃣ Event System

```python
from lexia import get_event_bus

bus = get_event_bus()

# Subscribe
def on_request(event):
    print(f"Request: {event.data}")

bus.subscribe("api.request", on_request)

# Publish
bus.publish("api.request", {
    "endpoint": "/api/users",
    "method": "GET"
})
```

### 4️⃣ System Monitoring

```python
from lexia import SystemMonitor

monitor = SystemMonitor()

# System stats
stats = monitor.get_system_stats()
print(f"CPU: {stats['cpu_percent']}%")
print(f"Memory: {stats['memory_percent']}%")

# Health checks
def check_db():
    # بررسی دیتابیس
    return True, "DB OK", {}

monitor.add_health_check("database", check_db, critical=True)

health = monitor.check_health()
print(f"Healthy: {health['healthy']}")
```

---

## 🛡️ Error Handling

### Custom Exceptions

```python
from lexia import (
    LexiaException,
    ConfigurationError,
    ValidationError,
    StreamError,
    APIError,
)

try:
    # کار اصلی
    pass
except ValidationError as e:
    # خطای validation
    print(f"Validation error: {e}")
except APIError as e:
    # خطای API
    print(f"API error: {e}")
except LexiaException as e:
    # هر خطای دیگر از Lexia
    print(f"Lexia error: {e}")
```

### Decorators

```python
from lexia import retry, log_execution, handle_errors

@retry(max_attempts=3, delay=1.0)
@log_execution
def unreliable_api_call():
    # فراخوانی API که ممکن است fail شود
    return api.call()

@handle_errors
def risky_operation():
    # عملیات خطرناک
    pass
```

---

## 🌐 Production Usage

### 1️⃣ Configuration

```python
from lexia import LexiaHandler

# Production mode
handler = LexiaHandler(
    dev_mode=False,  # استفاده از Centrifugo واقعی
    # سایر تنظیمات...
)
```

### 2️⃣ با Centrifugo

```python
# data باید شامل این فیلدها باشد:
data = {
    'stream_url': 'https://your-centrifugo-server.com',
    'stream_token': 'your-token',
    'channel': 'channel-name',
    'uuid': 'unique-message-id',
    'thread_id': 'thread-id',
    # سایر فیلدها...
}

handler = LexiaHandler(dev_mode=False)
session = handler.begin(data)
```

### 3️⃣ با API Client

```python
# برای usage tracking و سایر API calls
data = {
    'api_url': 'https://your-api.com',
    'api_token': 'your-api-token',
    # ...
}
```

---

## 📊 مثال کامل Production

```python
from lexia import LexiaHandler, get_metrics_collector
from lexia.patterns import timed_operation
import logging

logger = logging.getLogger(__name__)

def handle_user_request(data):
    """
    Handler اصلی برای پردازش درخواست کاربر.
    """
    # Setup
    handler = LexiaHandler(dev_mode=False)
    collector = get_metrics_collector()
    requests_counter = collector.counter("user_requests")

    try:
        # شروع session
        session = handler.begin(data)
        requests_counter.inc()

        # Loading
        session.loading.start_loading("thinking")

        # پردازش با timing
        with timed_operation("ai_processing"):
            # فراخوانی AI
            result = call_ai_model(data['prompt'])

        session.loading.end_loading("thinking")

        # ارسال نتیجه
        session.stream(result['text'])

        # Usage tracking
        session.usage.track(
            tokens=result['prompt_tokens'],
            token_type="prompt",
            cost=calculate_cost(result['prompt_tokens'], "prompt")
        )
        session.usage.track(
            tokens=result['completion_tokens'],
            token_type="completion",
            cost=calculate_cost(result['completion_tokens'], "completion")
        )

        # دکمه‌ها
        if result.get('has_more'):
            session.button.link("ادامه مطلب", result['more_url'])

        # بستن session
        response = session.close(usage_info=result.get('usage'))

        logger.info(f"Request processed successfully: {data['uuid']}")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)

        # ارسال خطا به کاربر
        if 'session' in locals():
            session.error(
                error_message="متاسفانه خطایی در پردازش رخ داد. لطفاً دوباره تلاش کنید.",
                exception=e
            )

        raise


def call_ai_model(prompt):
    """فراخوانی مدل AI"""
    # پیاده‌سازی واقعی
    pass

def calculate_cost(tokens, token_type):
    """محاسبه هزینه"""
    rates = {
        "prompt": 0.00002,      # $0.02 per 1K tokens
        "completion": 0.00004,  # $0.04 per 1K tokens
    }
    return tokens * rates.get(token_type, 0)
```

---

## 🧪 Testing

### Unit Testing

```python
import unittest
from lexia import LexiaHandler

class TestLexiaHandler(unittest.TestCase):
    def setUp(self):
        self.handler = LexiaHandler(dev_mode=True)
        self.test_data = {
            'channel': 'test-channel',
            'uuid': 'test-uuid',
            'thread_id': 'test-thread',
        }

    def test_basic_streaming(self):
        session = self.handler.begin(self.test_data)
        session.stream("Test message")
        response = session.close()

        self.assertIn('status', response)
        self.assertEqual(response['status'], 'success')

    def test_loading_markers(self):
        session = self.handler.begin(self.test_data)
        session.loading.start_loading("thinking")
        session.loading.end_loading("thinking")
        response = session.close()

        self.assertEqual(response['status'], 'success')
```

### Integration Testing

```python
def test_full_workflow():
    """تست workflow کامل"""
    handler = LexiaHandler(dev_mode=True)

    data = {
        'channel': 'test-channel',
        'uuid': 'test-uuid',
        'thread_id': 'test-thread',
    }

    session = handler.begin(data)

    # Loading
    session.loading.start_loading("thinking")

    # Stream
    session.stream("Processing...")

    # Loading end
    session.loading.end_loading("thinking")

    # Result
    session.stream("Done!")

    # Buttons
    session.button.link("View", "https://example.com")

    # Close
    response = session.close()

    assert response['status'] == 'success'
```

---

## 📖 Best Practices

### 1️⃣ همیشه از Context Manager استفاده کنید:

```python
# ✅ Good
with SessionContext(handler, data) as session:
    session.stream("محتوا")

# ❌ Bad (ممکن است session بسته نشود)
session = handler.begin(data)
session.stream("محتوا")
# فراموش کردن close()
```

### 2️⃣ Error Handling مناسب:

```python
# ✅ Good
try:
    session.stream(risky_operation())
except Exception as e:
    session.error("خطا رخ داد", exception=e)

# ❌ Bad (خطا را ignore می‌کند)
try:
    session.stream(risky_operation())
except:
    pass
```

### 3️⃣ Loading برای عملیات طولانی:

```python
# ✅ Good
session.loading.start_loading("thinking")
result = long_operation()
session.loading.end_loading("thinking")

# ❌ Bad (کاربر منتظر می‌ماند بدون feedback)
result = long_operation()
```

### 4️⃣ Usage Tracking:

```python
# ✅ Good
session.usage.track(tokens=1500, token_type="prompt", cost="0.03")

# ❌ Bad (token usage track نمی‌شود)
# هیچ tracking نداریم
```

### 5️⃣ استفاده از Observability:

```python
# ✅ Good
from lexia import get_metrics_collector

collector = get_metrics_collector()
counter = collector.counter("requests")
counter.inc()

# ❌ Bad (metrics نداریم)
# فقط logging
```

---

## 🔧 Troubleshooting

### مشکل: Session بسته نمی‌شود

```python
# راه حل: استفاده از Context Manager
with SessionContext(handler, data) as session:
    session.stream("محتوا")
```

### مشکل: خطای Connection

```python
# بررسی کنید:
# 1. dev_mode صحیح است؟
# 2. stream_url و stream_token درست هستند؟
# 3. network connectivity

handler = LexiaHandler(dev_mode=True)  # برای تست محلی
```

### مشکل: Performance پایین

```python
# راه حل: استفاده از Profiling
from lexia import profile

@profile(sort_by='cumulative')
def slow_function():
    # کد شما
    pass
```

---

## 📚 منابع بیشتر

- [Architecture Guide](./ARCHITECTURE.md) - معماری کامل
- [Examples](./examples/) - مثال‌های کامل
- [API Reference](./API_REFERENCE.md) - مرجع کامل API
- [Lambda Deploy Guide](./LAMBDA_DEPLOY_GUIDE.md) - راهنمای deploy

---

## 💬 پشتیبانی

- **Issues:** https://github.com/your-org/lexia-sdk/issues
- **Discussions:** https://github.com/your-org/lexia-sdk/discussions
- **Email:** support@your-org.com

---

**این راهنما به طور مداوم به‌روز می‌شود. آخرین به‌روزرسانی: December 15, 2025**
