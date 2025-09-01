from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from plex_unmonitorr.plex_client import MEDIA_TYPE, PlexClient


@dataclass
class Library:
    id: str
    title: str
    type: str


@dataclass
class Media:
    guid: str
    parent_title: str
    title: str
    type: str
    watched: bool
    view_count: int
    last_watched: int | None
    files: list[str]
    ids: list[str]
    season_number: int | None = None
    episode_number: int | None = None


def parse_libraries(data: dict, enabled_libraries: list[str]) -> list[Library]:
    libraries = []
    for item in data.get("MediaContainer", {}).get("Directory", []):
        if item.get("title", "") not in enabled_libraries:
            continue
        library = Library(
            id=item.get("key", ""),
            title=item.get("title", ""),
            type=item.get("type", ""),
        )
        libraries.append(library)
    return libraries


def parse_library_content(data: dict) -> list[Media]:
    content = data.get("MediaContainer", {}).get("Metadata", [])
    media_items = []

    for item in content:
        media = Media(
            guid=item.get("guid", ""),
            parent_title=item.get("grandparentTitle", ""),
            title=item.get("title", ""),
            type=item.get("type", ""),
            view_count=item.get("viewCount", 0),
            watched=item.get("viewCount", 0) > 0,
            last_watched=item.get("lastViewedAt", 0),
            files=[],
            ids=[g.get("id") for g in item.get("Guid", []) if (g.get("id") is not None)],
            season_number=item.get("parentIndex") if item.get("type") == "episode" else None,
            episode_number=item.get("index") if item.get("type") == "episode" else None,
        )
        for m in item.get("Media", []):
            for p in m.get("Part", []):
                if file := p.get("file"):
                    media.files.append(file)

        media_items.append(media)

    return media_items


def get_watched_content(
    plex_url: str, plex_token: str, enabled_libraries: list[str], days_back: int | None = None
) -> dict[str, list[Media]]:
    """
    Get all watched content from specified Plex libraries.

    Args:
        plex_url: Plex server URL
        plex_token: Plex authentication token
        enabled_libraries: List of library names to process
        days_back: Optional number of days to look back for watched content

    Returns:
        Dictionary mapping library names to lists of watched media items
    """
    last_watched_cutoff = None
    if days_back is not None:
        last_watched_cutoff = int((datetime.now(UTC) - timedelta(days=days_back)).timestamp())

    with PlexClient(plex_url, plex_token) as plex:
        libraries = parse_libraries(plex.get_libraries(), enabled_libraries)
        watched_media = {}

        for library in libraries:
            if library.type == "show":
                media_type = MEDIA_TYPE.EPISODE
            elif library.type == "movie":
                media_type = MEDIA_TYPE.MOVIE
            else:
                raise ValueError(f"Unsupported library type: {library.type}")

            content = plex.get_library_content(library.id, media_type)
            media = parse_library_content(content)

            watched_media[library.title] = [
                m for m in media if m.watched and (last_watched_cutoff is None or m.last_watched > last_watched_cutoff)
            ]

    return watched_media
