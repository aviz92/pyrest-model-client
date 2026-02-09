import pytest
import respx
from httpx import Response

from pyrest_model_client import AsyncRequestClient, build_header


@pytest.fixture(name="mock_headers")
def _mock_headers() -> dict:
    return build_header(token="test-token")


@pytest.fixture(name="async_client")
def _async_client(mock_headers: dict) -> AsyncRequestClient:
    return AsyncRequestClient(header=mock_headers, base_url="http://api.test")


@pytest.mark.asyncio
@respx.mock
async def test_async_get_request(async_client: AsyncRequestClient) -> None:
    """Test async GET request."""
    route = respx.get("http://api.test/items/").mock(return_value=Response(200, json={"foo": "bar"}))
    response = await async_client.get("items")
    assert route.called
    assert response == {"foo": "bar"}


@pytest.mark.asyncio
@respx.mock
async def test_async_post_request(async_client: AsyncRequestClient) -> None:
    """Test async POST request."""
    route = respx.post("http://api.test/create/").mock(return_value=Response(201, json={"status": "created"}))
    payload = {"name": "test"}
    response = await async_client.post("create", data=payload)
    assert route.called
    assert response == {"status": "created"}


@pytest.mark.asyncio
@respx.mock
async def test_async_put_request(async_client: AsyncRequestClient) -> None:
    """Test async PUT request."""
    route = respx.put("http://api.test/update/1/").mock(return_value=Response(200, json={"status": "updated"}))
    payload = {"name": "updated"}
    response = await async_client.put("update/1", data=payload)
    assert route.called
    assert response == {"status": "updated"}


@pytest.mark.asyncio
@respx.mock
async def test_async_delete_request(async_client: AsyncRequestClient) -> None:
    """Test async DELETE request."""
    route = respx.delete("http://api.test/delete/1/").mock(return_value=Response(204, json={"deleted": True}))
    response = await async_client.delete("delete/1")
    assert route.called
    assert response == {"deleted": True}


@pytest.mark.asyncio
async def test_async_context_manager(mock_headers: dict) -> None:
    """Test async client as context manager."""
    async with AsyncRequestClient(header=mock_headers, base_url="http://api.test") as client:
        assert client.client.is_closed is False
    # Client should be closed after context exit
    assert client.client.is_closed is True


@pytest.mark.asyncio
async def test_async_client_close(mock_headers: dict) -> None:
    """Test explicit async client close."""
    client = AsyncRequestClient(header=mock_headers, base_url="http://api.test")
    assert client.client.is_closed is False
    await client.aclose()
    assert client.client.is_closed is True
