import logging
import re
from collections import defaultdict

from plex_unmonitorr.library_service import Media
from plex_unmonitorr.sonarr_client import SonarrClient

logger = logging.getLogger("process_media")


def extract_tvdb_id_from_filepath(filepath: str) -> str | None:
    """Extract TVDB ID from filepath pattern like {tvdb-123456}"""
    match = re.search(r"\{tvdb-(\d+)\}", filepath)
    return match.group(1) if match else None


def process_media(
    libraries: dict[str, str],
    clients: dict[str, SonarrClient],
    dry_run: bool,
    watched_media: dict[str, list[Media]],
):
    for library_title, media in watched_media.items():
        logger.debug(f"Library: {library_title}")

        # Skip movie libraries for now
        if library_title in ["Movies", "Anime Movies"]:
            logger.debug(f"Skipping movie library: {library_title}")
            continue

        # Get appropriate client for this library
        client = clients.get(libraries.get(library_title, ""))
        if not client:
            logger.warning(f"No Sonarr client configured for library: {library_title}")
            continue

        # Group watched episodes by TVDB ID
        shows_by_tvdb = defaultdict(list)

        for item in media:
            if item.type == "episode":
                logger.debug(
                    f"{item.parent_title} - S{item.season_number:02d}E{item.episode_number:02d} - {item.title} (Last watched: {item.last_watched}) - {item.ids} - {item.files}"
                )

                # Extract TVDB ID from filepath
                tvdb_id = None
                for file_path in item.files:
                    tvdb_id = extract_tvdb_id_from_filepath(file_path)
                    if tvdb_id:
                        break

                # Also try from the IDs list
                if not tvdb_id:
                    for id_str in item.ids:
                        if id_str.startswith("tvdb://"):
                            tvdb_id = id_str.split("tvdb://")[-1]
                            break

                if tvdb_id:
                    shows_by_tvdb[tvdb_id].append(item)
                else:
                    logger.warning(f"Could not extract TVDB ID for: {item.parent_title} - {item.title}")
            else:
                logger.debug(
                    f"{item.parent_title} - {item.title} (Last watched: {item.last_watched}) - {item.ids} - {item.files}"
                )

        # Process each show
        episodes_to_unmonitor = []

        for tvdb_id, watched_episodes in shows_by_tvdb.items():
            try:
                logger.debug(f"Processing TVDB ID: {tvdb_id}")

                # Get series data from Sonarr
                series_data = client.get_series(tvdb_id)
                if not series_data:
                    show_name = watched_episodes[0].parent_title if watched_episodes else "Unknown"
                    logger.warning(f"No series found in Sonarr for TVDB ID: {tvdb_id} ({show_name})")
                    continue

                series_id = series_data[0]["id"] if isinstance(series_data, list) else series_data["id"]
                series_title = series_data[0]["title"] if isinstance(series_data, list) else series_data["title"]
                logger.debug(f"Found series: {series_title} (ID: {series_id})")

                # Get all episodes for this series
                episodes_data = client.get_episodes(series_id)

                # Create a lookup for episodes by season/episode number
                sonarr_episodes = {}
                for ep in episodes_data:
                    key = (ep["seasonNumber"], ep["episodeNumber"])
                    sonarr_episodes[key] = ep

                # Find matching episodes that are monitored
                for watched_ep in watched_episodes:
                    key = (watched_ep.season_number, watched_ep.episode_number)
                    if key in sonarr_episodes:
                        sonarr_ep = sonarr_episodes[key]
                        if sonarr_ep.get("monitored", False):
                            episodes_to_unmonitor.append(sonarr_ep["id"])
                            logger.info(
                                f"Will unmonitor: {series_title} - S{watched_ep.season_number:02d}E{watched_ep.episode_number:02d} - {watched_ep.title}"
                            )
                    else:
                        logger.warning(
                            f"Episode not found in Sonarr: {watched_ep.parent_title} S{watched_ep.season_number:02d}E{watched_ep.episode_number:02d}"
                        )

            except Exception as e:
                logger.error(f"Error processing TVDB ID {tvdb_id}: {e}")
                continue

        # Batch unmonitor episodes
        if episodes_to_unmonitor:
            if dry_run:
                logger.info(f"DRY RUN: Would unmonitor {len(episodes_to_unmonitor)} episodes in {library_title}")
            else:
                try:
                    client.set_episode_monitor(episodes_to_unmonitor, False)
                    logger.info(f"Successfully unmonitored {len(episodes_to_unmonitor)} episodes in {library_title}")
                except Exception as e:
                    logger.error(f"Failed to unmonitor episodes in {library_title}: {e}")
        else:
            logger.debug(f"No episodes to unmonitor in {library_title}")
