from typing import ClassVar
from pydantic import EmailStr

from pyrest_model_client.base import BaseAPIModel


class User(BaseAPIModel):
    name: str
    email: EmailStr

    _resource_path: ClassVar[str] = "user"
