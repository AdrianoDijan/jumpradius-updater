__version__ = "0.1.0"

from time import sleep

from .api_clients import get_current_ip
from .models import RadiusServer, ServerFilters
from .settings import RADIUS_SERVER_IDS, RADIUS_SERVER_NAMES, REFRESH_RATE_SEC


def loop():
    """Run updater in daemon mode."""
    servers = RadiusServer.from_api(
        filters=ServerFilters(ids=RADIUS_SERVER_IDS, names=RADIUS_SERVER_NAMES)
    )

    while True:
        current_ip = get_current_ip()
        for server in servers:
            if current_ip != server.source_ip:
                server.update_ip(current_ip)

        sleep(REFRESH_RATE_SEC)
