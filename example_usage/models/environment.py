from typing import ClassVar

from pyrest_model_client.base import BaseAPIModel


class Environment(BaseAPIModel):
    name: str

    _resource_path: ClassVar[str] = "environment"
