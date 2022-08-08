from time import time

import structlog
import structlog_pretty
from structlog.stdlib import _NAME_TO_LEVEL

from .settings import APP_NAME, LOG_FOR


def get_logger(
    app_name, process_name=None, log_level="notset", log_for=""
) -> structlog.stdlib.BoundLogger:
    """Configure and return logger."""
    configure_structlog(app_name, process_name, log_level, log_for)
    return structlog.get_logger()


def configure_structlog(
    app_name, process_name=None, log_level="notset", log_for=""
):
    """Add processors."""
    processors = [
        filter_by_level(log_level),
        structlog.stdlib.add_log_level,
        add_process_info(process_name),
        add_app_name(app_name),
    ]

    test_processors = [drop_all_logs]

    non_human_processors = [
        structlog.stdlib.PositionalArgumentsFormatter(),
        unix_timestamper,
        structlog_pretty.NumericRounder(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    human_processors = [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog_pretty.NumericRounder(),
        structlog.processors.TimeStamper("iso"),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(pad_event=25),
    ]

    if log_for == "test":
        processors = test_processors
    elif log_for == "human":
        processors.extend(human_processors)
    else:
        processors.extend(non_human_processors)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )


def unix_timestamper(_, __, event_dict):
    """Add timestamp."""
    event_dict["timestamp"] = time()
    return event_dict


def add_process_info(process_name):
    """Add process info."""

    def wrapper(_, __, event_dict):
        if process_name:
            event_dict["process"] = process_name

        return event_dict

    return wrapper


def add_app_name(app_name):
    """Add app name."""

    def wrapper(_, __, event_dict):
        event_dict["app"] = app_name
        return event_dict

    return wrapper


def filter_by_level(log_level):
    """Filter by level."""
    current_log_level = _NAME_TO_LEVEL.get(log_level, 0)

    def wrapper(_, level, event_dict):
        if _NAME_TO_LEVEL.get(level, 0) >= current_log_level:
            return event_dict

        raise structlog.DropEvent

    return wrapper


def drop_all_logs(*args, **kwargs):
    """Drop all logs."""
    raise structlog.DropEvent


logger = get_logger(APP_NAME, log_for=LOG_FOR)
