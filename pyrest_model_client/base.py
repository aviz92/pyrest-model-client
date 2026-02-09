from typing import TYPE_CHECKING, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from pyrest_model_client.client import AsyncRequestClient, RequestClient


class BaseAPIModel(BaseModel):
    """Base model for API resources with automatic resource path handling.

    Subclasses should define a `resource_path` class variable or instance attribute
    to specify the API endpoint path for this resource.
    """
    id: int | str | None = None
    resource_path: str = ""

    def get_endpoint(self, include_id: bool = False) -> str:
        """Get the endpoint path for this model instance.

        Args:
            include_id: If True and id is set, appends the id to the path.

        Returns:
            The endpoint path (e.g., "users" or "users/123").
        """
        path = self.resource_path
        if include_id and self.id is not None:
            path = f"{path}/{self.id}"
        return path

    def get_resource_url(
        self, client: Union["RequestClient", "AsyncRequestClient"], include_id: bool = False
    ) -> str:
        """Get the full URL for this resource.

        Args:
            client: The RequestClient or AsyncRequestClient instance to get the base URL from.
            include_id: If True and id is set, appends the id to the path.

        Returns:
            The full URL (e.g., "http://api.example.com/users").
        """
        endpoint = self.get_endpoint(include_id=include_id)
        return f"{client.base_url.rstrip('/')}/{endpoint.lstrip('/')}"


def get_model_fields(items: list[dict], model: type[BaseAPIModel]) -> list[BaseAPIModel]:
    """Convert a list of dictionaries to a list of model instances.

    Args:
        items: List of dictionaries representing API response data.
        model: The model class to instantiate.

    Returns:
        List of model instances.
    """
    return [model(**item) for item in items]
