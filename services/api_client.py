from __future__ import annotations

import os
from urllib.parse import urljoin

import requests


class ApiClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: int = 15) -> None:
        resolved_base_url = (base_url or os.getenv("BRAINFORGE_API_BASE_URL", "")).strip()
        self.base_url = resolved_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        if not self.base_url:
            raise ValueError("Missing BRAINFORGE_API_BASE_URL.")

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict | None = None) -> requests.Response:
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict | None = None) -> requests.Response:
        return self._request("PUT", path, json=json)

    def delete(self, path: str) -> requests.Response:
        return self._request("DELETE", path)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        response = requests.request(
            method,
            self._build_url(path),
            timeout=self.timeout_seconds,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def _build_url(self, path: str) -> str:
        normalized_path = path.lstrip("/")
        return urljoin(f"{self.base_url}/", normalized_path)
