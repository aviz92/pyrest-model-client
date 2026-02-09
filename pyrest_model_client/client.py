from typing import Any

import httpx


def build_header(
    token: str,
    authorization_type: str = "Token",
    content_type: str = "application/json",
) -> dict:
    return {
        "Content-Type": content_type,
        "Authorization": f"{authorization_type} {token}",
    }


class RequestClient:
    client: httpx.Client

    def __init__(
        self,
        header: dict,
        base_url: str = "http://localhost:8000",
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = True,
        add_trailing_slash: bool = True,
        limits: httpx.Limits | None = None,
    ) -> None:
        """Initialize the RequestClient.

        Args:
            header: HTTP headers dictionary (typically from build_header()).
            base_url: Base URL for all requests.
            timeout: Request timeout in seconds or httpx.Timeout object.
            follow_redirects: Whether to follow HTTP redirects.
            add_trailing_slash: Whether to automatically add trailing slash to endpoints.
            limits: Connection pool limits (max_keepalive_connections, max_connections).
        """
        self.base_url = base_url.rstrip("/")
        self.add_trailing_slash = add_trailing_slash

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.get_default_timeout(timeout=timeout),
            follow_redirects=follow_redirects,
            limits=self.get_default_limits(limits=limits),
        )
        self.set_credentials(header=header)

    @staticmethod
    def get_default_timeout(timeout: float | httpx.Timeout | None) -> httpx.Timeout:
        if timeout is None:
            return httpx.Timeout(30.0, connect=10.0)
        elif isinstance(timeout, httpx.Timeout):
            return timeout
        else:
            return httpx.Timeout(timeout, connect=timeout * 0.5)

    @staticmethod
    def get_default_limits(limits: httpx.Limits | None) -> httpx.Limits:
        if limits is None:
            return httpx.Limits(max_keepalive_connections=5, max_connections=10)
        else:
            return limits

    @staticmethod
    def normalize_endpoint(endpoint: str, add_trailing_slash: bool = True) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        if add_trailing_slash and not endpoint.endswith("/"):
            endpoint = endpoint + "/"
        return endpoint

    def set_credentials(self, header: dict) -> None:
        self.client.headers.update(header)

    def request(self, method: str, endpoint: str, as_json: bool = False, **kwargs: Any) -> httpx.Response | dict:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: Endpoint path or full URL.
            as_json: Whether to return JSON response (True) or Response object (False).
            **kwargs: Additional arguments passed to httpx.Client.request().

        Returns:
            JSON dict if as_json=True, otherwise httpx.Response object.
        """
        endpoint = self.normalize_endpoint(endpoint, self.add_trailing_slash)
        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json() if as_json else response

    def get(self, endpoint: str, params: dict | None = None, as_json: bool = True) -> httpx.Response | dict:
        if params is None:
            params = {}
        return self.request("GET", endpoint, params=params, as_json=as_json)

    def post(self, endpoint: str, data: dict, as_json: bool = True) -> httpx.Response | dict:
        if data is None:
            data = {}
        return self.request("POST", endpoint, json=data, as_json=as_json)

    def put(self, endpoint: str, data: dict, as_json: bool = True) -> httpx.Response | dict:
        if data is None:
            data = {}
        return self.request("PUT", endpoint, json=data, as_json=as_json)

    def delete(self, endpoint: str, as_json: bool = True) -> httpx.Response | dict:
        return self.request("DELETE", endpoint, as_json=as_json)


class AsyncRequestClient:
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
        header: dict,
        base_url: str = "http://localhost:8000",
        timeout: float | httpx.Timeout | None = None,
        follow_redirects: bool = True,
        add_trailing_slash: bool = True,
        limits: httpx.Limits | None = None,
    ) -> None:
        """Initialize the AsyncRequestClient.

        Args:
            header: HTTP headers dictionary (typically from build_header()).
            base_url: Base URL for all requests.
            timeout: Request timeout in seconds or httpx.Timeout object.
            follow_redirects: Whether to follow HTTP redirects.
            add_trailing_slash: Whether to automatically add trailing slash to endpoints.
            limits: Connection pool limits (max_keepalive_connections, max_connections).
        """
        self.base_url = base_url.rstrip("/")
        self.add_trailing_slash = add_trailing_slash

        # Reuse RequestClient's static methods for defaults
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=RequestClient.get_default_timeout(timeout=timeout),
            follow_redirects=follow_redirects,
            limits=RequestClient.get_default_limits(limits=limits),
        )
        self.set_credentials(header=header)

    def set_credentials(self, header: dict) -> None:
        """Update the client's HTTP headers.

        Args:
            header: Dictionary of HTTP headers to set.
        """
        self.client.headers.update(header)

    async def request(
        self, method: str, endpoint: str, as_json: bool = False, **kwargs: Any
    ) -> httpx.Response | dict:
        endpoint = RequestClient.normalize_endpoint(endpoint, self.add_trailing_slash)
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json() if as_json else response

    async def get(self, endpoint: str, params: dict | None = None, as_json: bool = True) -> httpx.Response | dict:
        if params is None:
            params = {}
        return await self.request("GET", endpoint, params=params, as_json=as_json)

    async def post(self, endpoint: str, data: dict, as_json: bool = True) -> httpx.Response | dict:
        if data is None:
            data = {}
        return await self.request("POST", endpoint, json=data, as_json=as_json)

    async def put(self, endpoint: str, data: dict, as_json: bool = True) -> httpx.Response | dict:
        if data is None:
            data = {}
        return await self.request("PUT", endpoint, json=data, as_json=as_json)

    async def delete(self, endpoint: str, as_json: bool = True) -> httpx.Response | dict:
        return await self.request("DELETE", endpoint, as_json=as_json)

    async def aclose(self) -> None:
        """Close the async client and release resources."""
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncRequestClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
