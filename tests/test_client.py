import json

import httpx
import pytest
import respx
from httpx import Response

from pyrest_model_client import RequestClient, build_header


@pytest.fixture(name="mock_headers")
def _mock_headers() -> dict:
    return build_header(token="test-token")


@pytest.fixture(name="client")
def _client(mock_headers: dict) -> RequestClient:
    return RequestClient(header=mock_headers, base_url="http://api.test")


def test_build_header() -> None:
    header = build_header("my-secret", authorization_type="Bearer")
    assert header["Authorization"] == "Bearer my-secret"
    assert header["Content-Type"] == "application/json"


def test_client_initialization(client: RequestClient) -> None:
    assert client.base_url == "http://api.test"
    assert client.client.headers["Authorization"] == "Token test-token"


@respx.mock
def test_get_request_success(client: RequestClient) -> None:
    # Mock the specific GET call
    route = respx.get("http://api.test/items/").mock(return_value=Response(200, json={"foo": "bar"}))
    response = client.get("items")  # Testing slash normalization
    assert route.called
    assert response == {"foo": "bar"}


@respx.mock
def test_post_request_as_json(client: RequestClient) -> None:
    route = respx.post("http://api.test/create/").mock(return_value=Response(201, json={"status": "created"}))
    payload = {"name": "test"}
    response = client.post("create", data=payload)
    assert route.called
    sent_data = json.loads(route.calls.last.request.content)
    assert sent_data == payload
    assert response == {"status": "created"}


@respx.mock
def test_endpoint_normalization(client: RequestClient) -> None:
    """Verify that 'users', '/users', and 'users/' all result in 'users/'"""
    route = respx.get("http://api.test/users/").mock(return_value=Response(200, json={}))
    client.get("users")
    client.get("/users")
    client.get("users/")
    assert route.call_count == 3


@respx.mock
def test_request_error_raises_exception(client: RequestClient) -> None:
    respx.get("http://api.test/error/").mock(return_value=Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        client.get("error")


@respx.mock
def test_delete_request(client: RequestClient) -> None:
    route = respx.delete("http://api.test/delete/1/").mock(return_value=Response(204, json={"deleted": True}))
    response = client.delete("delete/1")
    assert route.called
    assert response == {"deleted": True}


def test_client_without_trailing_slash() -> None:
    """Test client with trailing slash disabled."""
    headers = build_header(token="test-token")
    client_no_slash = RequestClient(
        header=headers, base_url="http://api.test", add_trailing_slash=False
    )
    assert client_no_slash.add_trailing_slash is False


def test_client_timeout_configuration() -> None:
    """Test client timeout configuration."""
    headers = build_header(token="test-token")
    timeout = httpx.Timeout(60.0, connect=20.0)
    client = RequestClient(header=headers, base_url="http://api.test", timeout=timeout)
    assert client.client.timeout.connect == 20.0
    assert client.client.timeout.read == 60.0


def test_client_limits_configuration() -> None:
    """Test client connection pool limits."""
    headers = build_header(token="test-token")
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    client = RequestClient(header=headers, base_url="http://api.test", limits=limits)

    transport = client.client._transport
    assert transport._pool._max_keepalive_connections == 10
    assert transport._pool._max_connections == 20


@respx.mock
def test_endpoint_without_trailing_slash() -> None:
    """Test endpoint normalization without trailing slash."""
    headers = build_header(token="test-token")
    client_no_slash = RequestClient(
        header=headers, base_url="http://api.test", add_trailing_slash=False
    )
    route = respx.get("http://api.test/users").mock(return_value=Response(200, json={}))
    client_no_slash.get("users")
    assert route.called
