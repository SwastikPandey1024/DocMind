import logging
import sys
from pathlib import Path

from app.core.settings import get_settings


def setup_logging() -> logging.Logger:
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("docuchat")
    logger.setLevel(log_level)

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    return logger
