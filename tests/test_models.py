from pyrest_model_client.base import BaseAPIModel


class SomeModel(BaseAPIModel):
    """Technology model matching the API response."""

    name: str
    description: str | None = None
    resource_path: str = "some_model"


def test_user_model_inheritance() -> None:
    some_model = SomeModel(name="some name test test", description="some description test test")
    assert isinstance(some_model, BaseAPIModel)
    assert some_model.resource_path == "some_model"
