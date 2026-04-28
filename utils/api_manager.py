import requests
import time
import logging
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree as ET


logger = logging.getLogger("api")


@dataclass
class ApiResponse:
    body: Any
    status: int
    raw: requests.Response


class APIManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, url: str, **kwargs):
        return self.send_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.send_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.send_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.send_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.send_request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs):
        return self.send_request("HEAD", url, **kwargs)

    def send_request(self, method: str, url: str, **kwargs) -> ApiResponse:
        full_url = f"{self.base_url}{url}"

        start_time = time.time()

        try:
            response = self.session.request(method, full_url, **kwargs)
            parsed = self.parse_response(response)

            duration = int((time.time() - start_time) * 1000)
            logger.info(f"{method} {full_url} -> {response.status_code} ({duration}ms)")

            return parsed

        except Exception as e:
            logger.error(f"API error: {method} {full_url} -> {e}")
            raise

    def parse_response(self, response: requests.Response) -> ApiResponse:
        content_type = response.headers.get("Content-Type", "")

        try:
            if "xml" in content_type:
                body = self.parse_xml(response.text)
            else:
                body = response.json()
        except Exception:
            body = response.text

        return ApiResponse(body=body, status=response.status_code, raw=response)

    def parse_xml(self, text: str):
        return ET.fromstring(text)
