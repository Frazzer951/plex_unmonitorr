from typing import Any
from urllib.parse import urljoin

import requests

"""
https://sonarr.tv/docs/api/
"""


class SonarrClient:
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

    def get_series(self, tvdb_id: str) -> dict[str, Any]:
        if tvdb_id.startswith("tvdb://"):
            tvdb_id = tvdb_id.split("tvdb://")[-1]

        return self._make_request("/api/v3/series", params={"tvdbId": tvdb_id})

    def get_episodes(self, series_id: str) -> dict[str, Any]:
        return self._make_request("/api/v3/episode", params={"seriesId": series_id})

    def set_episode_monitor(self, episode_ids: list[int], monitored: bool) -> None:
        return self._make_request(
            "/api/v3/episode/monitor", method="PUT", body={"episodeIds": episode_ids, "monitored": monitored}
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
