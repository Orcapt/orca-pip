# نصب Local برای استفاده در Repo دیگر

وقتی می‌خوای از این package توی یه پروژه/repo دیگه استفاده کنی.

## روش ۱: Editable Install (بهترین روش برای Development)

توی پروژه‌ی دیگه‌ات این دستور رو بزن:

```bash
# از مسیر کامل package
pip install -e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# یا اگر توی همون directory هستی
pip install -e ../lexia-pip
```

**مزایا:**

- ✅ هر تغییری توی lexia بزنی، توی پروژه دیگه هم اعمال میشه
- ✅ نیازی به reinstall نیست
- ✅ عالی برای development

**مثال:**

```bash
# فرض کن پروژه‌ت اینجاست:
cd /home/younes/Desktop/my-agent-project

# نصب lexia از local
pip install -e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# حالا می‌تونی استفاده کنی
python your_agent.py
```

## روش ۲: نصب از Git Repository

اگر کدت رو push کردی به git:

```bash
# نصب از git
pip install git+https://github.com/your-org/lexia-pip.git

# یا branch خاص
pip install git+https://github.com/your-org/lexia-pip.git@main

# یا commit خاص
pip install git+https://github.com/your-org/lexia-pip.git@commit-hash
```

## روش ۳: استفاده در requirements.txt

توی `requirements.txt` پروژه‌ت:

```txt
# از local path (editable)
-e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# یا از git
git+https://github.com/your-org/lexia-pip.git@main

# یا از PyPI (بعد از publish)
lexia>=2.0.0
```

بعد:

```bash
pip install -r requirements.txt
```

## روش ۴: استفاده در setup.py/pyproject.toml

اگر پروژه‌ت package هست:

**setup.py:**

```python
setup(
    name="my-agent",
    install_requires=[
        # از local (فقط برای dev)
        "lexia @ file:///home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip",

        # یا از git
        "lexia @ git+https://github.com/your-org/lexia-pip.git",

        # یا از PyPI
        "lexia>=2.0.0",
    ],
)
```

**pyproject.toml:**

```toml
[project]
dependencies = [
    "lexia @ file:///home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip",
]
```

## مثال کامل: استفاده در Agent

فرض کن این ساختار رو داری:

```
/home/younes/Desktop/
├── lexia-repo/
│   └── lexia-pip/           # Package لکسیا
└── my-chatbot-agent/         # پروژه Agent تو
    ├── agent.py
    ├── requirements.txt
    └── venv/
```

### قدم‌ها:

**۱. برو توی پروژه agent:**

```bash
cd /home/younes/Desktop/my-chatbot-agent
```

**۲. Virtual environment بساز (اختیاری اما توصیه میشه):**

```bash
python3 -m venv venv
source venv/bin/activate
```

**۳. نصب lexia از local:**

```bash
pip install -e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip
```

**۴. تست کن:**

```python
# agent.py
from lexia import LexiaHandler

handler = LexiaHandler(dev_mode=True)
print("✅ Lexia works!")

# استفاده معمولی
def process_message(data):
    session = handler.begin(data)
    session.stream("Hello from my agent!")
    session.close()
```

**۵. اجرا:**

```bash
python agent.py
```

## چک کردن نصب

```bash
# ببین package از کجا نصب شده
pip show lexia

# خروجی:
# Name: lexia
# Version: 2.0.0
# Location: /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip
# ...
```

```python
# توی Python
import lexia
print(lexia.__file__)
# باید مسیر local رو نشون بده
```

## تغییر دادن Package و تست

**۱. تغییرات رو توی lexia بزن:**

```bash
cd /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip
# ویرایش فایل‌ها...
```

**۲. بدون نیاز به reinstall، توی agent تست کن:**

```bash
cd /home/younes/Desktop/my-chatbot-agent
python agent.py  # تغییرات اعمال شده!
```

## Docker استفاده می‌کنی؟

اگر agent تو داخل Docker اجرا میشه:

**Dockerfile:**

```dockerfile
FROM python:3.11

# کپی کردن lexia package
COPY /path/to/lexia-pip /app/lexia-pip

# نصب
RUN pip install /app/lexia-pip

# کپی کردن agent
COPY . /app
WORKDIR /app

CMD ["python", "agent.py"]
```

**یا با volume mount برای development:**

```bash
docker run -v /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip:/lexia \
           -v $(pwd):/app \
           python:3.11 \
           bash -c "pip install -e /lexia && python /app/agent.py"
```

## Multiple Projects

اگر چند پروژه داری که همشون باید از lexia استفاده کنن:

```bash
# پروژه ۱
cd /path/to/project1
pip install -e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# پروژه ۲
cd /path/to/project2
pip install -e /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# حالا هر تغییری توی lexia بزنی، توی همه projects اعمال میشه!
```

## Uninstall کردن

اگر خواستی uninstall کنی:

```bash
pip uninstall lexia
```

## مشکلات متداول

### ۱. ImportError بعد از تغییر

**حل:**

```python
# Restart Python interpreter
# یا
import importlib
import lexia
importlib.reload(lexia)
```

### ۲. Version قدیمی نشون میده

**حل:**

```bash
pip uninstall lexia
pip install -e /path/to/lexia-pip
```

### ۳. Changes اعمال نمیشه

**چک کن:**

```bash
pip show lexia
# باید Location برابر با مسیر local باشه
```

## Best Practice برای Team

اگر با تیم کار می‌کنی:

**requirements-dev.txt:**

```txt
# Development dependencies
-e ../lexia-pip  # relative path

# یا
-e /absolute/path/to/lexia-pip
```

**requirements.txt (production):**

```txt
# Production - از git یا PyPI
git+https://github.com/your-org/lexia-pip.git@v2.0.0
```

**README.md پروژه‌ت:**

````markdown
## Development Setup

1. Clone both repos:
   ```bash
   git clone https://github.com/your-org/lexia-pip.git
   git clone https://github.com/your-org/my-agent.git
   ```
````

2. Install lexia in dev mode:

   ```bash
   cd my-agent
   pip install -e ../lexia-pip
   ```

3. Run agent:
   ```bash
   python agent.py
   ```

````

## خلاصه دستورات

```bash
# نصب از local (editable)
pip install -e /path/to/lexia-pip

# نصب از git
pip install git+https://github.com/your-org/lexia-pip.git

# چک کردن نصب
pip show lexia

# Uninstall
pip uninstall lexia

# تست import
python -c "from lexia import LexiaHandler; print('OK')"
````

---

**نکته مهم:** بهترین روش برای development همین `pip install -e` هست چون:

- ✅ تغییرات فوری اعمال میشن
- ✅ نیازی به reinstall نیست
- ✅ راحت debug می‌کنی
- ✅ مثل production کار می‌کنه
