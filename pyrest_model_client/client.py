from typing import Any

import httpx
from custom_python_logger import get_logger

from pyrest_model_client.consts import LOGGER_NAME, HttpMethod


def build_header(
    token: str,
    authorization_type: str = "Token",
    content_type: str = "application/json",
) -> dict[str, str]:
    return {
        "Content-Type": content_type,
        "Authorization": f"{authorization_type} {token}",
    }


class _BaseRestClient:
    """Shared config and endpoint logic for sync and async REST clients."""

    client: httpx.Client | httpx.AsyncClient

    def __init__(self, base_url: str | None, add_trailing_slash: bool) -> None:
        self.logger = get_logger(LOGGER_NAME)
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.add_trailing_slash = add_trailing_slash

    @staticmethod
    def get_default_timeout(timeout: float | httpx.Timeout | None) -> httpx.Timeout:
        if timeout is None:
            return httpx.Timeout(30.0, connect=10.0)
        if isinstance(timeout, httpx.Timeout):
            return timeout
        return httpx.Timeout(timeout, connect=timeout * 0.5)

    @staticmethod
    def get_default_limits(limits: httpx.Limits | None) -> httpx.Limits:
        if limits is None:
            return httpx.Limits(max_keepalive_connections=5, max_connections=10)
        return limits

    def normalize_endpoint(self, endpoint: str, add_trailing_slash: bool = True) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        if add_trailing_slash and not endpoint.endswith("/"):
            endpoint = endpoint + "/"

        if self.base_url:
            endpoint = f'{self.base_url}/{endpoint.lstrip("/")}'

        return endpoint

    def set_credentials(self, header: dict[str, str]) -> None:
        self.client.headers.update(header)


class RestApiClient(_BaseRestClient):
    client: httpx.Client

    def __init__(
        self,
        header: dict[str, str],
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = True,
        add_trailing_slash: bool = True,
        limits: httpx.Limits | None = None,
    ) -> None:
        """Initialize the RestApiClient.

        Args:
            header: HTTP headers dictionary (typically from build_header()).
            base_url: Base URL for all requests.
            timeout: Request timeout in seconds or httpx.Timeout object.
            follow_redirects: Whether to follow HTTP redirects.
            add_trailing_slash: Whether to automatically add trailing slash to endpoints.
            limits: Connection pool limits (max_keepalive_connections, max_connections).
        """
        super().__init__(base_url=base_url, add_trailing_slash=add_trailing_slash)
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.get_default_timeout(timeout=timeout),
            follow_redirects=follow_redirects,
            limits=self.get_default_limits(limits=limits),
        )
        self.set_credentials(header=header)

    def _request(self, method: HttpMethod, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make an HTTP request.

        Args:
            method: HTTP method from HttpMethod enum.
            endpoint: Endpoint path or full URL.
            **kwargs: Additional arguments passed to httpx.Client.request().

        Returns:
            httpx.Response object.
        """
        endpoint = self.normalize_endpoint(endpoint, self.add_trailing_slash)
        self.logger.debug(f"Making {method} request to {endpoint} with kwargs: {kwargs}")
        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: dict | None = None) -> httpx.Response:
        return self._request(HttpMethod.GET, endpoint, params=params or {})

    def post(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return self._request(HttpMethod.POST, endpoint, json=data or {})

    def put(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return self._request(HttpMethod.PUT, endpoint, json=data or {})

    def patch(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return self._request(HttpMethod.PATCH, endpoint, json=data or {})

    def delete(self, endpoint: str) -> httpx.Response:
        return self._request(HttpMethod.DELETE, endpoint)

    def __enter__(self) -> "RestApiClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.client.close()


class AsyncRestApiClient(_BaseRestClient):
    """Asynchronous HTTP client for REST API requests.

    Features:
    - Automatic endpoint normalization
    - Configurable timeout and connection pool settings
    - Automatic error handling
    - Full async/await support
    """

    client: httpx.AsyncClient

    def __init__(
        self,
        header: dict[str, str],
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = True,
        add_trailing_slash: bool = True,
        limits: httpx.Limits | None = None,
    ) -> None:
        """Initialize the AsyncRestApiClient.

        Args:
            header: HTTP headers dictionary (typically from build_header()).
            base_url: Base URL for all requests.
            timeout: Request timeout in seconds or httpx.Timeout object.
            follow_redirects: Whether to follow HTTP redirects.
            add_trailing_slash: Whether to automatically add trailing slash to endpoints.
            limits: Connection pool limits (max_keepalive_connections, max_connections).
        """
        super().__init__(base_url=base_url, add_trailing_slash=add_trailing_slash)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.get_default_timeout(timeout=timeout),
            follow_redirects=follow_redirects,
            limits=self.get_default_limits(limits=limits),
        )
        self.set_credentials(header=header)

    async def _request(self, method: HttpMethod, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make an async HTTP request.

        Args:
            method: HTTP method from HttpMethod enum.
            endpoint: Endpoint path or full URL.
            **kwargs: Additional arguments passed to httpx.AsyncClient.request().

        Returns:
            httpx.Response object.
        """
        endpoint = self.normalize_endpoint(endpoint, self.add_trailing_slash)
        self.logger.debug(f"Making {method} request to {endpoint} with kwargs: {kwargs}")
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, endpoint: str, params: dict | None = None) -> httpx.Response:
        return await self._request(HttpMethod.GET, endpoint, params=params or {})

    async def post(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return await self._request(HttpMethod.POST, endpoint, json=data or {})

    async def put(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return await self._request(HttpMethod.PUT, endpoint, json=data or {})

    async def patch(self, endpoint: str, data: dict | None = None) -> httpx.Response:
        return await self._request(HttpMethod.PATCH, endpoint, json=data or {})

    async def delete(self, endpoint: str) -> httpx.Response:
        return await self._request(HttpMethod.DELETE, endpoint)

    async def aclose(self) -> None:
        """Close the async client and release resources."""
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncRestApiClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()
