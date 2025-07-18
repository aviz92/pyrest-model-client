from typing import Optional

import httpx


def build_header(token: str, authorization_type: str = "Token", content_type: str = "application/json") -> dict:
    return {
        "Content-Type": content_type,
        "Authorization": f"{authorization_type} {token}",
    }


class RequestClient:
    def __init__(self, header: dict, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url)
        self.set_credentials(header=header)

    def set_credentials(self, header: dict):
        self.client.headers.update(header)

    def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            if not endpoint.startswith("/"):  # Ensure endpoint starts with a slash if it's a path (not a full URL)
                endpoint = "/" + endpoint

        if not endpoint.endswith("/"):  # Ensure endpoint ends with a slash
            endpoint = endpoint + "/"

        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        if params is None:
            params = {}
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: Optional[dict] = None) -> httpx.Response:
        if json is None:
            json = {}
        return self.request("POST", endpoint, json=json)

    def put(self, endpoint: str, json: Optional[dict] = None) -> httpx.Response:
        if json is None:
            json = {}
        return self.request("PUT", endpoint, json=json)

    def delete(self, endpoint: str) -> httpx.Response:
        return self.request("DELETE", endpoint)
