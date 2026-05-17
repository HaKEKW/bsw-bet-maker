import logging

from app import app
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

logger.info(
    "Application `%s` started (environment=%s, debug=%s)",
    app.title,
    settings.environment,
    settings.debug,
)
