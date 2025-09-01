from typing import Any
from urllib.parse import urljoin

import requests

"""
https://radarr.video/docs/api/
"""


class RadarrClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Api-Key": self.api_key,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, br",
            }
        )

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        body: dict[str | Any] | None = None,
    ) -> dict[str, Any]:
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, params=params, json=body)
        response.raise_for_status()
        return response.json()

    def get_movie(self, tmdb_id: str) -> dict[str, Any]:
        if tmdb_id.startswith("tmdb://"):
            tmdb_id = tmdb_id.split("tmdb://")[-1]

        return self._make_request("/api/v3/movie", params={"tmdbId": tmdb_id})

    def update_movie(self, movie_id: int, movie_data: dict[str, Any]) -> None:
        return self._make_request(f"/api/v3/movie/{movie_id}", method="PUT", body=movie_data)

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
