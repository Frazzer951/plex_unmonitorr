# Plex Unmonitorr

A Python application that automatically unmonitors watched media in Sonarr and Radarr based on viewing history from Plex Media Server.

## Overview

Plex Unmonitorr helps manage your media library by automatically unmonitoring episodes and movies that have already been watched in Plex. This prevents your *arr applications from continuing to search for and upgrade content you've already consumed, saving bandwidth and storage space.

## Features

- **Multi-Client Support**: Works with both Sonarr (TV shows) and Radarr (movies)
- **Library-Specific Configuration**: Configure different clients for different Plex libraries (e.g., separate Sonarr instances for TV shows and anime)
- **Time-Based Filtering**: Optionally filter by recently watched content (configurable days back)
- **Dry Run Mode**: Test configuration without making actual changes
- **Batch Processing**: Efficiently processes multiple episodes/movies at once
- **Comprehensive Logging**: Detailed logging with configurable levels and file rotation
- **Docker Support**: Ready-to-use Docker container with scheduled execution
- **Robust Error Handling**: Graceful handling of API errors and missing content

## How It Works

1. **Fetches Watched Content**: Queries Plex Media Server for watched episodes/movies in configured libraries
2. **Matches Media**: Uses TVDB IDs (for shows) and TMDB IDs (for movies) to match Plex content with Sonarr/Radarr entries
3. **Identifies Monitored Items**: Checks which watched items are still being monitored in the *arr applications
4. **Unmonitors Content**: Removes monitoring from watched episodes/movies to prevent further searches and upgrades

## Installation

### Requirements

- Python 3.13
- Access to Plex Media Server, Sonarr, and/or Radarr APIs

### Local Installation

1. Clone the repository:
   ```bash
   git clone &lt;repository-url&gt;
   cd plex_unmonitorr
   ```

2. Install dependencies:
   ```bash
   pip install -U pip uv
   uv pip install .
   ```

3. Copy and configure the example config:
   ```bash
   cp config.example.yaml config/config.yaml
   ```

4. Edit `config/config.yaml` with your server details and API keys

5. Run the application:
   ```bash
   python -m plex_unmonitorr.main
   ```

### Docker Installation

1. Build the image:
   ```bash
   docker build -t plex-unmonitorr .
   ```

2. Create a config directory and copy your configuration:
   ```bash
   mkdir -p ./config
   cp config.example.yaml ./config/config.yaml
   # Edit ./config/config.yaml with your settings
   ```

3. Run the container:
   ```bash
   docker run -v ./config:/plex_unmonitorr/config plex-unmonitorr
   ```

   Or with custom schedule (default is 1 hour):
   ```bash
   docker run -e SCHEDULE=7200 -v ./config:/plex_unmonitorr/config plex-unmonitorr
   ```

## Configuration

Create a `config/config.yaml` file based on the example:

```yaml
plex:
  url: "http://localhost:32400"
  token: "YOUR_PLEX_TOKEN_HERE"

libraries:
  "TV Shows": "sonarr_tv"        # Maps Plex library to client config
  "Movies": "radarr_movies"
  "Anime Shows": "sonarr_anime"
  "Anime Movies": "radarr_anime"

clients:
  sonarr_tv:
    type: sonarr
    url: "http://localhost:8989"
    api_key: "YOUR_SONARR_API_KEY_HERE"
  sonarr_anime:
    type: sonarr
    url: "http://localhost:9090"
    api_key: "YOUR_SONARR_ANIME_API_KEY_HERE"
  radarr_movies:
    type: radarr
    url: "http://localhost:7878"
    api_key: "YOUR_RADARR_API_KEY_HERE"
  radarr_anime:
    type: radarr
    url: "http://localhost:7979"
    api_key: "YOUR_RADARR_ANIME_API_KEY_HERE"

settings:
  # Number of days to look back for watched content (null = all time)
  days_back: null
  # Set to true to see what would be unmonitored without actually doing it
  dry_run: true
```

### Configuration Options

- **plex**: Plex Media Server connection details
  - `url`: Plex server URL
  - `token`: Plex authentication token
- **libraries**: Maps Plex library names to client configurations
- **clients**: Defines Sonarr/Radarr client connections
  - `type`: Either "sonarr" or "radarr"
  - `url`: Client URL
  - `api_key`: Client API key
- **settings**:
  - `days_back`: Filter to only recently watched content (null for all time)
  - `dry_run`: Preview mode without making changes

### Getting API Tokens

- **Plex Token**: See [Plex support documentation](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- **Sonarr API Key**: Settings -> General -> Security -> API Key
- **Radarr API Key**: Settings -> General -> Security -> API Key

## Logging

Logs are written to `config/logs/plex_unmonitorr.log` with automatic rotation. Console output level can be controlled with the `PU_LOG_LEVEL` environment variable:

```bash
export PU_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
python -m plex_unmonitorr.main
```

## Environment Variables

- `PU_LOG_LEVEL`: Console logging level (default: INFO)
- `SCHEDULE`: Docker container run interval in seconds (default: 3600)

## Requirements

Media in your Plex libraries must have proper metadata matching for the application to work:

- **TV Shows**: TVDB IDs are required (either in file paths as `{tvdb-123456}` or in Plex metadata)
- **Movies**: TMDB IDs are required (in Plex metadata as `tmdb://123456`)

## Troubleshooting

1. **No content found**: Ensure your Plex libraries have the correct metadata agents configured
2. **API errors**: Verify your API keys and URLs are correct
3. **Nothing unmonitored**: Check that content is actually watched in Plex and still monitored in Sonarr/Radarr
4. **TVDB/TMDB ID issues**: Ensure your media files have proper metadata matching

Enable debug logging for detailed troubleshooting:
```bash
export PU_LOG_LEVEL=DEBUG
```

## License

This project is open source. Please check the license file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.