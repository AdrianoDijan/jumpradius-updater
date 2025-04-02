from envparse import env

env.read_envfile()

APP_NAME = "jumpradius_updater"

JUMPRADIUS_API_BASE = env.str(
    "JUMPRADIUS_API_BASE", default="https://console.jumpcloud.com/api/"
)
JUMPRADIUS_API_KEY = env.str("JUMPRADIUS_API_KEY")
IFCONFIG_CO_API_BASE = env.str(
    "IFCONFIG_CO_API_BASE", default="https://ifconfig.co/"
)

IP_FILTER_PATTERN = env.str("IP_FILTER_PATTERN", default="")
IP_REFRESH_RATE_SEC = env.int("IP_REFRESH_RATE_SEC", default=10)

# refresh servers data every x IP refreshes
SERVERS_REFRESH_MULTIPLIER = env.int("SERVERS_REFRESH_MULTIPLIER", default=6)

RADIUS_SERVER_NAMES = env.list("RADIUS_SERVER_NAMES", default=[])
RADIUS_SERVER_IDS = env.list("RADIUS_SERVER_IDS", default=[])

LOG_FOR = env.str("LOG_FOR", default="")
