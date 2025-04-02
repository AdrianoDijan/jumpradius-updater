from __future__ import annotations

__version__ = "0.1.3"

import re
from time import sleep

from .api_clients import get_current_ip
from .logs import logger
from .models import RadiusServer, ServerFilters
from .settings import (
    APP_NAME,
    IP_FILTER_PATTERN,
    IP_REFRESH_RATE_SEC,
    RADIUS_SERVER_IDS,
    RADIUS_SERVER_NAMES,
    SERVERS_REFRESH_MULTIPLIER,
)


def _is_ip_allowed(ip_address: str | None) -> bool:
    """Check if IP is allowed.

    Args:
        ip_address (str | None): IP address

    Returns:
        bool: True if allowed, False otherwise
    """
    if not ip_address:
        return False

    if not IP_FILTER_PATTERN:
        return True

    pattern = re.compile(IP_FILTER_PATTERN)
    if not pattern.match(ip_address):
        logger.error(f"{APP_NAME}.ip_not_allowed", address=ip_address)
        return False

    return True


def _get_current_ip() -> str | None:
    """Retry getting current IP until successful.

    Returns:
        str: current IP address
    """
    while not (current_ip := get_current_ip()) or not _is_ip_allowed(
        current_ip
    ):
        logger.error(f"{APP_NAME}.get_initial_ip", delay=IP_REFRESH_RATE_SEC)
        sleep(IP_REFRESH_RATE_SEC)

    return current_ip


def loop():
    """Run updater in daemon mode."""
    while True:
        servers = RadiusServer.from_api(
            filters=(
                ServerFilters(ids=RADIUS_SERVER_IDS, names=RADIUS_SERVER_NAMES)
                if any((RADIUS_SERVER_IDS, RADIUS_SERVER_NAMES))
                else None
            )
        )
        for _ in range(SERVERS_REFRESH_MULTIPLIER):
            current_ip = _get_current_ip()
            for server in servers:
                if current_ip and current_ip != server.source_ip:
                    logger.info(
                        f"{APP_NAME}.updater.ip_change",
                        current_ip=server.source_ip,
                        new_ip=current_ip,
                    )
                    server.update_ip(current_ip)

            sleep(IP_REFRESH_RATE_SEC)
