![PyPI version](https://img.shields.io/pypi/v/pyrest-model-client)
![Python](https://img.shields.io/badge/python->=3.12-blue)
![Development Status](https://img.shields.io/badge/status-stable-green)
![Maintenance](https://img.shields.io/maintenance/yes/2026)
![PyPI](https://img.shields.io/pypi/dm/pyrest-model-client)
![License](https://img.shields.io/pypi/l/pyrest-model-client)

---

# python-requests-client

A simple, flexible Python HTTP client and API modeling toolkit built on top of [httpx](https://www.python-httpx.org/) and [pydantic](https://docs.pydantic.dev/). Easily integrate robust API requests and resource models into your Python projects.

---

## 🚀 Features
- **Model-driven**: Define and interact with API resources as Python classes.
- **Easy HTTP Requests**: Simple `RequestClient` for GET, POST, PUT, DELETE with automatic header and base URL management.
- **Pydantic API Models**: Define resource models with CRUD helpers (`save`, `delete`, `load`, `find`).
- **Global Client Setup**: Set a global API client for all models with `set_client()`.
- **Type Safety**: All models use Pydantic for validation and serialization.
- **Extensible**: Easily create new models for any RESTful resource.

---

## 📦 Installation
```bash
uv add python-requests-client
```

---

## 🔧 Usage

### 1. Define Your Models
```python
from pyrest_model_client.base import BaseAPIModel
from typing import ClassVar


class User(BaseAPIModel):
  name: str
  email: str
  resource_path: str = "user"


class Environment(BaseAPIModel):
  name: str
  resource_path: str = "environment"
```

### 2. Initialize the Client
```python
import os

from custom_python_logger import build_logger, json_pretty_format
from dotenv import load_dotenv
from python_base_toolkit.utils.data_serialization import default_serialize

from pyrest_model_client import RequestClient, build_header
from pyrest_model_client.base import BaseAPIModel, get_mode_fields

load_dotenv()

logger = build_logger(__name__)

TOKEN = os.getenv("TOKEN")
BASE_URL = f'{os.getenv("BASE_URL")}:{os.getenv("PORT")}'


class FirstApp(BaseAPIModel):
    """
    Model representing the FirstApp API resource. The fields should match the API response structure.
    the app resource path is defined as "first_app" in the API of https://github.com/aviz92/django-basic-app project.
    """

    name: str
    description: str | None = None
    resource_path: str = "first_app"


def main(table_name: str) -> None:
    header = build_header(token=TOKEN)
    client = RequestClient(base_url=BASE_URL, header=header)

    # Example: Get all items from the API (paginated) and convert them to model instances
    item_list = []
    params = None
    while res := client.get(table_name, params=params):  # pylint: disable=W0149
        item_list.extend(get_mode_fields(res["results"], model=FirstApp))

        if not res["next"]:
            break
        params = {"page": res["next"].split("/?page=")[-1]}
    logger.info(f"Response: {json_pretty_format(data=item_list, default=default_serialize)}")
```

---

## 🤝 Contributing
Contributions are welcome! Please fork the repo, create a branch, and submit a pull request.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.
