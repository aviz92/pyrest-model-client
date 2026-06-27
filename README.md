![PyPI version](https://img.shields.io/pypi/v/pyrest-model-client)
![Python](https://img.shields.io/badge/python->=3.12-blue)
![Development Status](https://img.shields.io/badge/status-stable-green)
![Maintenance](https://img.shields.io/maintenance/yes/2026)
![PyPI](https://img.shields.io/pypi/dm/pyrest-model-client)
![License](https://img.shields.io/pypi/l/pyrest-model-client)

---

# pyrest-model-client

A simple, flexible Python HTTP client and API modeling toolkit built on top of [httpx](https://www.python-httpx.org/) and [pydantic](https://docs.pydantic.dev/). Easily integrate robust API requests and resource models into your Python projects.

---

## 🚀 Features
- **Model-driven**: Define and interact with API resources as Python classes using `BaseAPIModel`.
- **Easy HTTP Requests**: `RestApiClient` for GET, POST, PUT, PATCH, DELETE with automatic header and base URL management.
- **Async Support**: Full async/await support with `AsyncRestApiClient` for high-performance concurrent requests.
- **Automatic Endpoint Normalization**: Configurable endpoint path normalization (trailing slash handling).
- **Resource Path Integration**: Models can use their `resource_path` to generate endpoints and URLs automatically.
- **Flexible Authentication**: Support for Token and Bearer authentication via `build_header()` helper.
- **Response to Model Conversion**: `get_model_fields()` helper converts API responses to typed model instances.
- **Configurable Client**: Customizable timeout, connection pool limits, and redirect handling.
- **Type Safety**: All models use Pydantic for automatic validation and serialization.
- **Error Handling**: Automatic HTTP status error handling with `raise_for_status()`.
- **Extensible**: Easily create new models for any RESTful resource by extending `BaseAPIModel`.

---

## 📦 Installation
```bash
uv add pyrest-model-client
```

---

## 🔧 Usage

### 1. Define Your Models
```python
from pyrest_model_client.base import BaseAPIModel


class User(BaseAPIModel):
    name: str
    email: str
    resource_path: str = "user"


class Environment(BaseAPIModel):
    name: str
    resource_path: str = "environment"
```

### 2. Initialize the Client and Make Requests
```python
import os

import httpx
from dotenv import load_dotenv

from pyrest_model_client import RestApiClient, build_header, get_model_fields
from pyrest_model_client.base import BaseAPIModel

load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_URL = f'{os.getenv("BASE_URL")}:{os.getenv("PORT")}'


class FirstApp(BaseAPIModel):
    name: str
    description: str | None = None
    resource_path: str = "first_app"


# Initialize the client with default settings
header = build_header(token=TOKEN)
client = RestApiClient(base_url=BASE_URL, header=header)

# Or configure the client with custom settings
client = RestApiClient(
    base_url=BASE_URL,
    header=header,
    timeout=httpx.Timeout(60.0, connect=10.0),  # 60s read, 10s connect
    add_trailing_slash=True,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
)

# Use as a context manager (auto-closes the connection)
with RestApiClient(base_url=BASE_URL, header=header) as client:
    # Example: Use resource_path from model
    app = FirstApp(name="My App", description="Test")
    endpoint = app.get_endpoint()           # Returns "first_app"
    full_url = app.get_resource_url(client) # Returns full URL

    # Example: Get all items (paginated) and convert to model instances
    item_list = []
    params = None
    while True:
        res = client.get("first_app", params=params)
        data = res.json()
        item_list.extend(get_model_fields(data["results"], model=FirstApp))
        if not data["next"]:
            break
        params = {"page": data["next"].split("/?page=")[-1]}

    # Example: Create a new item
    new_item = client.post("first_app", data={"name": "My App", "description": "A new app"})

    # Example: Full update
    updated_item = client.put("first_app/1", data={"name": "Updated App"})

    # Example: Partial update
    patched_item = client.patch("first_app/1", data={"description": "New description"})

    # Example: Delete an item
    client.delete("first_app/1")
```

### 3. Using Async Client
```python
import asyncio
import os

from dotenv import load_dotenv

from pyrest_model_client import AsyncRestApiClient, build_header

load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_URL = f'{os.getenv("BASE_URL")}:{os.getenv("PORT")}'


async def main():
    header = build_header(token=TOKEN)

    async with AsyncRestApiClient(base_url=BASE_URL, header=header) as client:
        data = (await client.get("first_app")).json()
        await client.post("first_app", data={"name": "Async App"})
        await client.put("first_app/1", data={"name": "Updated"})
        await client.patch("first_app/1", data={"description": "Patched"})
        await client.delete("first_app/1")


asyncio.run(main())
```

---

## 🤝 Contributing
Contributions are welcome! Please fork the repo, create a branch, and submit a pull request.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.
