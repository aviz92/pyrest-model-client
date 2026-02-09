import pytest
from pydantic import ValidationError

from pyrest_model_client import BaseAPIModel
from pyrest_model_client.base import get_mode_fields


class User(BaseAPIModel):
    name: str
    email: str
    _resource_path: str = "/users"


def test_base_api_model_initialization() -> None:
    """Test that the BaseAPIModel accepts id as int or str."""
    # Test with int ID
    model_int = BaseAPIModel(id=1)
    assert model_int.id == 1

    # Test with str ID
    model_str = BaseAPIModel(id="uuid-123")
    assert model_str.id == "uuid-123"

    # Test with None ID (default)
    model_none = BaseAPIModel()
    assert model_none.id is None


def test_get_mode_fields_valid_data() -> None:
    """Test mapping a list of dicts to a list of models."""
    raw_data = [
        {"id": 1, "name": "Alice", "email": "alice@test.com"},
        {"id": 2, "name": "Bob", "email": "bob@test.com"},
    ]

    users = get_mode_fields(raw_data, User)

    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[0].name == "Alice"
    assert users[1].id == 2


def test_get_mode_fields_empty_list() -> None:
    """Ensure it returns an empty list when input is empty."""
    assert get_mode_fields([], User) == []


def test_get_mode_fields_invalid_data() -> None:
    """Ensure it raises a ValidationError if data doesn't match the model."""
    invalid_data = [{"id": 1}]  # Missing 'name' and 'email'

    with pytest.raises(ValidationError):
        get_mode_fields(invalid_data, User)


def test_extra_fields_handling() -> None:
    """Check how it handles fields not defined in the model."""
    raw_data = [{"id": 1, "name": "Alice", "email": "a@b.com", "extra": "ignored"}]

    users = get_mode_fields(raw_data, User)

    assert users[0].name == "Alice"
    # By default, Pydantic ignores extra fields unless Config is set to 'forbid'
    assert not hasattr(users[0], "extra")
