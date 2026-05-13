import logging
from typing import Any

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def log_service_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    fields.setdefault("service", settings.service_name)
    logger.info("%s %s", event, " ".join(_format_field(key, value) for key, value in fields.items()))


def _format_field(key: str, value: Any) -> str:
    text = str(value).replace("\n", "\\n").replace(" ", "_")
    return f"{key}={text}"
