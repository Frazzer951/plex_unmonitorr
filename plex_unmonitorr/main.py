from plex_unmonitorr.library_service import get_watched_content


def main():
    url = "http://10.10.20.20:32400"
    token = "WUHJRjQj6WtnfZQmtWcn"

    enabled_libraries = [
        "Anime Shows",
        "Anime Movies",
        "TV Shows",
        "Movies",
    ]

    days_back = 7

    print("Getting played media from Plex...")

    watched_media = get_watched_content(url, token, enabled_libraries, days_back)

    for library_title, media in watched_media.items():
        print(f"Library: {library_title}")
        for item in media:
            if item.type == "episode":
                print(
                    f"{item.parent_title} - S{item.season_number:02d}E{item.episode_number:02d} - {item.title} (Last watched: {item.last_watched})"
                )
            else:
                print(f"{item.parent_title} - {item.title} (Last watched: {item.last_watched})")


if __name__ == "__main__":
    main()
