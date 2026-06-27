import httpx
import pytest
import respx
from httpx import Response

from pyrest_model_client import AsyncRestApiClient, build_header


@pytest.fixture(name="mock_headers")
def _mock_headers() -> dict:
    return build_header(token="test-token")


@pytest.fixture(name="async_client")
def _async_client(mock_headers: dict) -> AsyncRestApiClient:
    return AsyncRestApiClient(header=mock_headers, base_url="http://api.test")


@pytest.mark.asyncio
@respx.mock
async def test_async_get(async_client: AsyncRestApiClient) -> None:
    respx.get("http://api.test/items/").mock(return_value=Response(200, json={"foo": "bar"}))
    response = await async_client.get("items")
    assert isinstance(response, httpx.Response)
    assert response.json() == {"foo": "bar"}


@pytest.mark.asyncio
@respx.mock
async def test_async_post(async_client: AsyncRestApiClient) -> None:
    route = respx.post("http://api.test/create/").mock(return_value=Response(201, json={"status": "created"}))
    response = await async_client.post("create", data={"name": "test"})
    assert route.called
    assert response.json() == {"status": "created"}


@pytest.mark.asyncio
@respx.mock
async def test_async_put(async_client: AsyncRestApiClient) -> None:
    route = respx.put("http://api.test/update/1/").mock(return_value=Response(200, json={"status": "updated"}))
    response = await async_client.put("update/1", data={"name": "updated"})
    assert route.called
    assert response.json() == {"status": "updated"}


@pytest.mark.asyncio
@respx.mock
async def test_async_patch(async_client: AsyncRestApiClient) -> None:
    route = respx.patch("http://api.test/items/1/").mock(return_value=Response(200, json={"name": "updated"}))
    response = await async_client.patch("items/1", data={"name": "updated"})
    assert route.called
    assert response.json() == {"name": "updated"}


@pytest.mark.asyncio
@respx.mock
async def test_async_delete(async_client: AsyncRestApiClient) -> None:
    route = respx.delete("http://api.test/delete/1/").mock(return_value=Response(204, json={"deleted": True}))
    response = await async_client.delete("delete/1")
    assert route.called
    assert response.json() == {"deleted": True}


@pytest.mark.asyncio
async def test_async_context_manager(mock_headers: dict) -> None:
    async with AsyncRestApiClient(header=mock_headers, base_url="http://api.test") as client:
        assert client.client.is_closed is False
    assert client.client.is_closed is True


@pytest.mark.asyncio
async def test_async_client_close(mock_headers: dict) -> None:
    client = AsyncRestApiClient(header=mock_headers, base_url="http://api.test")
    assert client.client.is_closed is False
    await client.aclose()
    assert client.client.is_closed is True
