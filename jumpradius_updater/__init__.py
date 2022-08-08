__version__ = "0.1.3"

from time import sleep

from .api_clients import get_current_ip
from .logs import logger
from .models import RadiusServer, ServerFilters
from .settings import (
    APP_NAME,
    IP_REFRESH_RATE_SEC,
    RADIUS_SERVER_IDS,
    RADIUS_SERVER_NAMES,
    SERVERS_REFRESH_MULTIPLIER,
)


def _get_current_ip() -> str:
    """Retry getting current IP until successful.

    Returns:
        str: current IP address
    """
    while not (current_ip := get_current_ip()):
        logger.error(f"{APP_NAME}.get_initial_ip", delay=IP_REFRESH_RATE_SEC)
        sleep(IP_REFRESH_RATE_SEC)

    return current_ip


def loop():
    """Run updater in daemon mode."""
    servers = RadiusServer.from_api(
        filters=ServerFilters(ids=RADIUS_SERVER_IDS, names=RADIUS_SERVER_NAMES)
        if any((RADIUS_SERVER_IDS, RADIUS_SERVER_NAMES))
        else None
    )

    while True:
        for _ in range(SERVERS_REFRESH_MULTIPLIER):
            current_ip = _get_current_ip()
            for server in servers:
                if current_ip != server.source_ip:
                    logger.info(
                        f"{APP_NAME}.updater.ip_change",
                        current_ip=server.source_ip,
                        new_ip=current_ip,
                    )
                    server.update_ip(current_ip)

            sleep(IP_REFRESH_RATE_SEC)
