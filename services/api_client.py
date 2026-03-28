from __future__ import annotations

import time
from urllib.parse import urljoin

import requests

from utils.config import API_TIMEOUT_SECONDS, BASE_URL


TIMEOUT_MESSAGE = "\u96f2\u7aef\u670d\u52d9\u559a\u9192\u4e2d\uff0c\u8acb\u518d\u8a66\u4e00\u6b21"


class ApiClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: int = API_TIMEOUT_SECONDS) -> None:
        resolved_base_url = (base_url or BASE_URL).strip()
        self.base_url = resolved_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        if not self.base_url:
            raise ValueError("Missing BASE_URL.")

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict | None = None) -> requests.Response:
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict | None = None) -> requests.Response:
        return self._request("PUT", path, json=json)

    def delete(self, path: str) -> requests.Response:
        return self._request("DELETE", path)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path)
        print(f"[ApiClient] {method} {url}")
        last_exception: requests.RequestException | None = None

        for attempt in range(2):
            try:
                response = requests.request(
                    method,
                    url,
                    timeout=self.timeout_seconds,
                    **kwargs,
                )
                print(f"[ApiClient] Response status code: {response.status_code}")
                print(f"[ApiClient] Response text: {response.text}")
                response.raise_for_status()
                return response
            except requests.Timeout as exc:
                last_exception = exc
                print(f"[ApiClient] Timeout on attempt {attempt + 1}: {exc}")
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise requests.Timeout(TIMEOUT_MESSAGE) from exc
            except requests.RequestException as exc:
                last_exception = exc
                response = getattr(exc, "response", None)
                if response is not None:
                    print(f"[ApiClient] Response status code: {response.status_code}")
                    print(f"[ApiClient] Response text: {response.text}")
                raise

        if last_exception is not None:
            raise last_exception
        raise RuntimeError("Unexpected API request state.")

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        normalized_path = path.lstrip("/")
        return urljoin(f"{self.base_url}/", normalized_path)
