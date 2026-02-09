from pyrest_model_client.base import BaseAPIModel


class User(BaseAPIModel):
    name: str
    email: str
    resource_path: str = "users"


def test_user_model_inheritance() -> None:
    some_model = User(name="John Doe", email="johnd@gmail.com")
    assert isinstance(some_model, BaseAPIModel)
    assert some_model.resource_path == "users"
