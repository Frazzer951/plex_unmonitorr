import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("config")


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Look for config.yaml in project root
            project_root = Path(__file__).parent.parent
            config_path = Path.joinpath(project_root, "config", "config.yaml")

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        logger.debug(f"Loading config from {self.config_path}")
        with open(self.config_path) as file:
            return yaml.safe_load(file)

    @property
    def plex_url(self) -> str:
        return self._config["plex"]["url"]

    @property
    def plex_token(self) -> str:
        return self._config["plex"]["token"]

    @property
    def libraries(self) -> dict[str, str]:
        return self._config["libraries"]

    @property
    def clients_config(self) -> dict[str, dict[str, str]]:
        return self._config["clients"]

    @property
    def days_back(self) -> int:
        return self._config["settings"]["days_back"]

    @property
    def dry_run(self) -> bool:
        return self._config["settings"]["dry_run"]
