"""
Runtime settings module.

Provides a single access point for environment-aware application settings.
All settings can be overridden via environment variables.
"""

import os
import sys
import logging
from pathlib import Path
from config import get_config

# Setup structured logging for Azure App Service (streaming stdout logs)
def configure_logging():
    log_level_str = os.getenv("KOSVIO_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence verbose Streamlit info logs
    logging.getLogger("streamlit").setLevel(logging.WARNING)

configure_logging()
logger = logging.getLogger(__name__)

# Load core base config
try:
    _CONFIG = get_config()
    BASE_DIR = str(_CONFIG.base_dir)
except Exception as e:
    logger.error("Failed to load base configuration: %s", str(e))
    BASE_DIR = str(Path(__file__).resolve().parent)

# Application Identity
APP_NAME = os.getenv("KOSVIO_APP_NAME", getattr(_CONFIG, "app_name", "Kosvio"))

# Runtime flags
DEBUG = os.getenv("KOSVIO_DEBUG", os.getenv("INSIGHTFLOW_DEBUG", str(getattr(_CONFIG, "debug", False)))).lower() in {
    "1",
    "true",
    "yes",
}

# Configurable Paths & Storage Directories
DATA_DIR = os.getenv("KOSVIO_DATA_DIR", os.path.join(BASE_DIR, "data"))
DOCS_DIR = os.getenv("KOSVIO_DOCS_DIR", os.path.join(BASE_DIR, "docs"))

# Specific File Upload Dir
UPLOAD_DIR = os.getenv("KOSVIO_UPLOAD_DIR", os.path.join(DATA_DIR, "uploads"))

# Ensure paths exist on load (lazy directory initialization with graceful error handling)
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception as e:
    logger.warning("Could not create storage directories automatically: %s. Relying on transient path configurations.", str(e))
