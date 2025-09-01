import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging():
    log_level_env = os.getenv("PU_LOG_LEVEL", "INFO").upper()
    console_level = getattr(logging, log_level_env, logging.INFO)

    logs_dir = Path("config/logs")
    logs_dir.mkdir(exist_ok=True, parents=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "plex_unmonitorr.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug(f"Logging initialized - Console level: {logging.getLevelName(console_level)}, File level: DEBUG")
