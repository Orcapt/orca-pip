# 🔧 Lexia Storage SDK Developer Guide

This guide explains how to build your own Lexia Storage SDKs (or reuse the official ones) for any language. Lexia Storage exposes a **workspace-scoped JSON API** that sits in front of our internal S3/Spaces buckets. SDKs only need to wrap these REST endpoints, forward the required headers, and—optionally—present an AWS S3-style interface for drop‑in compatibility.

---

## 1. Prerequisites

- A Lexia workspace and API token with storage permissions.
- The public Storage endpoint (usually `https://<your-domain>/api/v1/storage`).
- Familiarity with your language’s HTTP + multipart upload libraries.
- Optional: `lexia-cli` to create buckets and test uploads quickly.

> **Authentication:** All requests must include `x-workspace`, `x-token`, and `x-mode` headers. Tokens behave like AWS access keys.

> **What you receive:** Each integrator only needs a base URL (e.g. ` `), a `workspace` slug, an API token, and the `mode` (`dev`/`prod`). Treat the API as a managed black box—you never need to interact with our internal services or AWS directly.

> **Single entry point:** Every client and SDK **must** call the provided Storage API URL. There is no public access to any underlying infrastructure, so keep all requests within `https://<your-domain>/api/v1/storage/...`.

---

## 2. API Fundamentals

### Base URL

```
{BASE_URL} = https://your-domain.com/api/v1/storage
```

### Required Headers

| Header        | Value                 | Description                            |
| ------------- | --------------------- | -------------------------------------- |
| `x-workspace` | Workspace slug/handle | Determines the tenant/account          |
| `x-token`     | API token             | Authenticates the request              |
| `x-mode`      | `dev` or `prod`       | Switches between staging/prod backends |

### Common Endpoints

| Area        | Method & Path                   | Purpose                      |
| ----------- | ------------------------------- | ---------------------------- |
| Buckets     | `POST /bucket/create`           | Create bucket                |
|             | `GET /bucket/list`              | List buckets                 |
|             | `GET /bucket/{name}`            | Bucket metadata              |
|             | `DELETE /bucket/{name}`         | Delete bucket (`force=true`) |
| Files       | `POST /{bucket}/upload`         | Upload (multipart/form-data) |
|             | `GET /{bucket}/files`           | List files with pagination   |
|             | `GET /{bucket}/download/{key}`  | Generate signed download URL |
|             | `GET /{bucket}/file-info/{key}` | Fetch metadata before upload |
|             | `DELETE /{bucket}/file/{key}`   | Delete single object         |
| Permissions | `POST /{bucket}/permission/add` | Grant ACL                    |
|             | `GET /{bucket}/permissions`     | List ACLs                    |
|             | `DELETE /permission/{id}`       | Revoke ACL                   |

> These endpoints live under `/api/v1/storage/...` on the managed Storage API. All S3/Spaces operations happen server-side—your SDK only speaks to this JSON surface.

### Error Format

```json
{
  "message": "Human readable error",
  "errors": {...optional...},
  "code": "INTERNAL_ERROR"
}
```

Always bubble up the `message` in SDK exceptions.

---

## 3. SDK Implementation Blueprint

1. **Configuration struct/class**
   - Accept `workspace`, `token`, `mode`, optional `base_url`.
2. **Request helper**
   - Centralize header injection and error normalization.
3. **Bucket service**
   - Wrap `create`, `list`, `info`, `delete`.
4. **File service**
   - Add helpers for `upload_file`, `upload_buffer`, `list_files`, `download_file`, `get_download_url`, `delete_file`.
5. **Permissions**
   - Optional but recommended for team collaboration.
6. **Utilities**
   - Storage stats, multiple environments, retries/backoff.

Pseudo-structure:

```python
class LexiaStorage:
    def __init__(self, workspace, token, base_url, mode='prod'):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'x-workspace': workspace,
            'x-token': token,
            'x-mode': mode
        }

    def _request(self, method, path, *, json=None, data=None, files=None, params=None):
        url = f"{self.base_url}{path}"
        resp = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=json if files is None else None,
            data=data if files else None,
            files=files,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
```

---

## 4. Feature Recipes

### Bucket CRUD

```python
def create_bucket(self, name, visibility='private', encryption=True):
    payload = {
        'bucket_name': name,
        'visibility': visibility,
        'encryption_enabled': encryption
    }
    return self._request('POST', '/bucket/create', json=payload)['bucket']
```

Use `force=true` when deleting buckets with existing files.

### File Upload (multipart)

```python
with open(file_path, 'rb') as f:
    files = {'file': (os.path.basename(file_path), f)}
    data = {
        'folder_path': folder or '',
        'visibility': visibility,
        'generate_url': 'true',
    }
    response = self._request('POST', f'/{bucket}/upload', data=data, files=files)
    return response['file']
```

Supports optional `metadata`/`tags` (JSON strings) and returns the download URL if `generate_url=true`.

### File Listing + Pagination

```javascript
const { files, pagination } = await storage.listFiles("my-bucket", {
  folderPath: "users/123",
  page: 1,
  perPage: 50,
});
```

### Pre-signed Downloads

```python
url = storage.get_download_url('bucket', 'folder/file.jpg')['download_url']
```

### Permissions

```php
$storage->addPermission('reports', [
    'target_type' => 'workspace',
    'target_id' => 'team-ops',
    'resource_type' => 'folder',
    'resource_path' => '2025/',
    'can_read' => true,
    'can_list' => true,
]);
```

### AWS S3 Drop-in Compatibility

The `LexiaS3` client mimics `boto3.client('s3')`, but under the hood it still talks to the JSON API listed above. You can build the same façade in other languages so existing AWS-oriented code keeps working:

```python
from lexia_s3 import LexiaS3

s3 = LexiaS3(
    workspace='my-workspace',
    api_token='token',
    endpoint_url='https://api.example.com'
)

s3.create_bucket(Bucket='demo')
s3.upload_file('report.pdf', 'demo', 'reports/2025/report.pdf')
```

Key differences vs AWS:

- `workspace/token` replace AWS key/secret.
- No concept of regions beyond cosmetic `region_name`.
- Signed download URLs come directly from Lexia instead of AWS SigV4.

---

## 5. Reference Implementations

### Python (High-level SDK)

```start:52:lexia-cli/docs/examples/lexia_storage.py
class LexiaStorage:
    """Lexia Storage S3-Compatible Client"""
    def __init__(self, workspace, token, mode='dev',
                 base_url='http://localhost:8000/api/v1/storage'):
        if not workspace or not token:
            raise ValueError('Workspace and token are required')
        self.headers = {
            'x-workspace': workspace,
            'x-token': token,
            'x-mode': mode
        }

    def _request(self, method, endpoint, data=None, files=None, params=None):
        url = f"{self.config['base_url']}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data if data and not files else None,
            data=data if files else None,
            files=files,
            params=params
        )
        response.raise_for_status()
        return response.json()
```

- Includes helpers for buffer uploads, metadata/tags, pagination, and permissions.
- Example CLI flow lives in the `if __name__ == '__main__'` block for quick smoke tests.

### Python (boto3-style Drop-in)

```start:32:lexia-cli/docs/examples/lexia_s3.py
class LexiaS3:
    """S3-Compatible Storage Client"""
    def __init__(self, workspace, api_token, endpoint_url='http://localhost:8000', region_name='us-east-1'):
        self.headers = {
            'x-workspace': workspace,
            'x-token': api_token,
            'x-mode': 'prod'
        }

    def put_object(self, Bucket, Key, Body, **kwargs):
        files = {'file': (os.path.basename(Key), io.BytesIO(Body))}
        data = {
            'folder_path': os.path.dirname(Key) or '',
            'visibility': 'public' if kwargs.get('ACL') == 'public-read' else 'private',
            'generate_url': 'true'
        }
        return self._request('POST', f'/{Bucket}/upload', data=data, files=files)
```

Use this pattern when you want to swap AWS S3 calls with Lexia without touching business logic.

### Node.js / JavaScript

```start:27:lexia-cli/docs/examples/lexia-storage-sdk.js
class LexiaStorage {
  constructor({ workspace, token, mode = 'dev', baseUrl = 'http://localhost:8000/api/v1/storage' }) {
    if (!workspace || !token) {
      throw new Error('Workspace and token are required');
    }
    this.headers = { 'x-workspace': workspace, 'x-token': token, 'x-mode': mode };
    this.config = { baseUrl };
  }

  async _request(method, endpoint, data = null, options = {}) {
    const response = await axios({
      method,
      url: `${this.config.baseUrl}${endpoint}`,
      headers: { ...this.headers, ...options.headers },
      data,
      params: options.params,
      ...options,
    });
    return response.data;
  }
}
```

- Uses `form-data` for uploads and streams downloads directly to disk.
- Exposes Promise-based helpers for create/list/upload/download/delete/permissions.

### PHP

```start:26:lexia-cli/docs/examples/LexiaStorage.php
class LexiaStorage
{
    public function __construct(array $config)
    {
        if (empty($config['workspace']) || empty($config['token'])) {
            throw new LexiaStorageException('Workspace and token are required');
        }
        $this->headers = [
            'x-workspace: ' . $config['workspace'],
            'x-token: ' . $config['token'],
            'x-mode: ' . ($config['mode'] ?? 'dev')
        ];
    }

    private function request($method, $endpoint, $data = null, $isMultipart = false)
    {
        $url = $this->config['base_url'] . $endpoint;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        // ...
    }
}
```

- Relies on `CURLFile` for uploads and handles buffer uploads via temp files.
- Includes a CLI example showing bucket creation → upload → download → cleanup.

---

## 6. Building Your Own SDK

1. **Copy a reference implementation** closest to your language.
2. **Swap the HTTP layer** (e.g., `fetch`, `OkHttp`, `HttpClient`, `Guzzle`).
3. **Mirror the helper surface** you need (bucket/file/permission).
4. **Add tests** that hit a local Lexia Storage instance (or staging) using mock buckets.
5. **Distribute** via package managers (PyPI, npm, Composer, etc.).

> Tip: keep the public API symmetrical with AWS S3 helpers so teams can migrate gradually.

---

## 7. Testing & Troubleshooting

| Symptom                        | Quick Fix                                                             |
| ------------------------------ | --------------------------------------------------------------------- |
| `401 Unauthorized`             | Check `workspace/token/mode` headers                                  |
| Multipart upload fails         | Ensure you remove custom headers that conflict with `form-data` libs  |
| Download URL expired           | Regenerate via `GET /{bucket}/download/{key}` (expires in 60 minutes) |
| `bucket not found`             | Verify CLI bucket name matches case + workspace                       |
| `Request failed: ECONNREFUSED` | Base URL incorrect or storage service offline                         |

Use `lexia storage upload ... --debug` to capture the raw HTTP exchange when debugging SDKs.

---

## 8. Next Steps

- Publish your SDKs under your organization namespace.
- Add CI tests that hit Lexia Storage using service tokens.
- Contribute improvements back to the examples in `docs/examples/`.

Happy building! 🚀
