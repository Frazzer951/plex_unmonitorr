from enum import Enum
from typing import Any
from urllib.parse import urljoin

import requests


class MEDIA_TYPE(Enum):
    MOVIE = 1
    SHOW = 2
    SEASON = 3
    EPISODE = 4


class PlexClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Plex-Token": self.token,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, br",
            }
        )

    def _make_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_libraries(self) -> dict[str, Any]:
        return self._make_request("/library/sections")

    def get_library_content(self, library_id: str, media_type: MEDIA_TYPE, limit: int = -1) -> dict[str, Any]:
        """Get all content from a specific library"""
        return self._make_request(
            f"/library/sections/{library_id}/all",
            params={
                "type": media_type.value,
                "X-Plex-Container-Size": limit if limit != -1 else None,
            },
        )

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
