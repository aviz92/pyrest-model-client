import json

import httpx
import pytest
import respx
from httpx import Response

from pyrest_model_client import RestApiClient, build_header


@pytest.fixture(name="mock_headers")
def _mock_headers() -> dict:
    return build_header(token="test-token")


@pytest.fixture(name="client")
def _client(mock_headers: dict) -> RestApiClient:
    return RestApiClient(header=mock_headers, base_url="http://api.test")


def test_build_header() -> None:
    header = build_header("my-secret", authorization_type="Bearer")
    assert header["Authorization"] == "Bearer my-secret"
    assert header["Content-Type"] == "application/json"


def test_client_initialization(client: RestApiClient) -> None:
    assert client.base_url == "http://api.test"
    assert client.client.headers["Authorization"] == "Token test-token"


@respx.mock
def test_get_returns_response(client: RestApiClient) -> None:
    respx.get("http://api.test/items/").mock(return_value=Response(200, json={"foo": "bar"}))
    response = client.get("items")
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@respx.mock
def test_get_as_json_returns_dict(client: RestApiClient) -> None:
    route = respx.get("http://api.test/items/").mock(return_value=Response(200, json={"foo": "bar"}))
    response = client.get_as_json("items")
    assert route.called
    assert response == {"foo": "bar"}


@respx.mock
def test_post_as_json(client: RestApiClient) -> None:
    route = respx.post("http://api.test/create/").mock(return_value=Response(201, json={"status": "created"}))
    payload = {"name": "test"}
    response = client.post_as_json("create", data=payload)
    assert route.called
    sent_data = json.loads(route.calls.last.request.content)
    assert sent_data == payload
    assert response == {"status": "created"}


@respx.mock
def test_endpoint_normalization(client: RestApiClient) -> None:
    """Verify that 'users', '/users', and 'users/' all result in 'users/'"""
    route = respx.get("http://api.test/users/").mock(return_value=Response(200, json={}))
    client.get("users")
    client.get("/users")
    client.get("users/")
    assert route.call_count == 3


@respx.mock
def test_request_error_raises_exception(client: RestApiClient) -> None:
    respx.get("http://api.test/error/").mock(return_value=Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        client.get("error")


@respx.mock
def test_patch_sends_partial_data(client: RestApiClient) -> None:
    route = respx.patch("http://api.test/items/1/").mock(return_value=Response(200, json={"name": "updated"}))
    payload = {"name": "updated"}
    response = client.patch_as_json("items/1", data=payload)
    assert route.called
    sent_data = json.loads(route.calls.last.request.content)
    assert sent_data == payload
    assert response == {"name": "updated"}


@respx.mock
def test_patch_returns_response_object(client: RestApiClient) -> None:
    respx.patch("http://api.test/items/1/").mock(return_value=Response(200, json={"name": "updated"}))
    response = client.patch("items/1", data={"name": "updated"})
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@respx.mock
def test_delete_as_json(client: RestApiClient) -> None:
    route = respx.delete("http://api.test/delete/1/").mock(return_value=Response(204, json={"deleted": True}))
    response = client.delete_as_json("delete/1")
    assert route.called
    assert response == {"deleted": True}


def test_client_without_trailing_slash() -> None:
    headers = build_header(token="test-token")
    client_no_slash = RestApiClient(header=headers, base_url="http://api.test", add_trailing_slash=False)
    assert client_no_slash.add_trailing_slash is False


def test_client_timeout_configuration() -> None:
    headers = build_header(token="test-token")
    timeout = httpx.Timeout(60.0, connect=20.0)
    client = RestApiClient(header=headers, base_url="http://api.test", timeout=timeout)
    assert client.client.timeout.connect == 20.0
    assert client.client.timeout.read == 60.0


def test_client_limits_configuration() -> None:
    headers = build_header(token="test-token")
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    client = RestApiClient(header=headers, base_url="http://api.test", limits=limits)
    transport = client.client._transport
    assert transport._pool._max_keepalive_connections == 10
    assert transport._pool._max_connections == 20


@respx.mock
def test_endpoint_without_trailing_slash() -> None:
    headers = build_header(token="test-token")
    client_no_slash = RestApiClient(header=headers, base_url="http://api.test", add_trailing_slash=False)
    route = respx.get("http://api.test/users").mock(return_value=Response(200, json={}))
    client_no_slash.get("users")
    assert route.called
