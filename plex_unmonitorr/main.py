import logging

from dotenv import load_dotenv

from plex_unmonitorr.config import Config
from plex_unmonitorr.library_service import get_watched_content
from plex_unmonitorr.logging_config import setup_logging
from plex_unmonitorr.process_media import process_media
from plex_unmonitorr.radarr_client import RadarrClient
from plex_unmonitorr.sonarr_client import SonarrClient

logger = logging.getLogger()


def main():
    load_dotenv()
    setup_logging()

    logger.debug("Starting Plex Unmonitorr")

    config = Config()

    clients = {}
    for client_name, client_config in config.clients_config.items():
        if client_config["type"] == "sonarr":
            clients[client_name] = SonarrClient(client_config["url"], client_config["api_key"])
        elif client_config["type"] == "radarr":
            clients[client_name] = RadarrClient(client_config["url"], client_config["api_key"])
        else:
            raise ValueError(f"Unsupported client type: {client_config['type']}")

    logger.debug("Getting played media from Plex...")

    watched_media = get_watched_content(config.plex_url, config.plex_token, config.libraries.keys(), config.days_back)
    process_media(
        config.libraries, clients, config.dry_run, watched_media, config.ignored_tmdb_ids, config.ignored_tvdb_ids
    )

    for client in clients.values():
        client.close()


if __name__ == "__main__":
    main()
