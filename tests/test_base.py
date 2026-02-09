import pytest
from pydantic import ValidationError

from pyrest_model_client import BaseAPIModel, RequestClient, build_header
from pyrest_model_client.base import get_model_fields


class User(BaseAPIModel):
    name: str
    email: str
    resource_path: str = "users"


def test_base_api_model_initialization() -> None:
    """Test that the BaseAPIModel accepts id as int or str."""

    model_int = BaseAPIModel(id=1)
    assert model_int.id == 1

    model_str = BaseAPIModel(id="uuid-123")
    assert model_str.id == "uuid-123"

    model_none = BaseAPIModel()
    assert model_none.id is None


def test_get_model_fields_valid_data() -> None:
    """Test mapping a list of dicts to a list of models."""

    raw_data = [
        {"id": 1, "name": "Alice", "email": "alice@test.com"},
        {"id": 2, "name": "Bob", "email": "bob@test.com"},
    ]
    users = get_model_fields(raw_data, User)

    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[0].name == "Alice"
    assert users[1].id == 2


def test_get_model_fields_empty_list() -> None:
    """Ensure it returns an empty list when input is empty."""

    assert get_model_fields([], User) == []


def test_get_model_fields_invalid_data() -> None:
    """Ensure it raises a ValidationError if data doesn't match the model."""

    invalid_data = [{"id": 1}]  # Missing 'name' and 'email'
    with pytest.raises(ValidationError):
        get_model_fields(invalid_data, User)


def test_extra_fields_handling() -> None:
    """Check how it handles fields not defined in the model."""
    raw_data = [{"id": 1, "name": "Alice", "email": "a@b.com", "extra": "ignored"}]
    users = get_model_fields(raw_data, User)
    assert users[0].name == "Alice"
    assert not hasattr(users[0], "extra")  # By default, Pydantic ignores extra fields unless Config is set to 'forbid'


def test_get_endpoint() -> None:
    """Test get_endpoint method."""
    user = User(name="Alice", email="alice@test.com", resource_path="users")
    assert user.get_endpoint() == "users"
    assert user.get_endpoint(include_id=False) == "users"

    user_with_id = User(id=123, name="Alice", email="alice@test.com", resource_path="users")
    assert user_with_id.get_endpoint() == "users"
    assert user_with_id.get_endpoint(include_id=True) == "users/123"


def test_get_resource_url() -> None:
    """Test get_resource_url method."""

    user = User(name="Alice", email="alice@test.com", resource_path="users")
    client = RequestClient(header=build_header("test"), base_url="http://api.test")

    assert user.get_resource_url(client) == "http://api.test/users"

    user_with_id = User(id=123, name="Alice", email="alice@test.com", resource_path="users")
    assert user_with_id.get_resource_url(client) == "http://api.test/users"
    assert user_with_id.get_resource_url(client, include_id=True) == "http://api.test/users/123"
