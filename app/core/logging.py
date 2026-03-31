import logging
from logging.config import dictConfig


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(log_level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": LOG_FORMAT,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": log_level.upper(),
                "handlers": ["console"],
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
