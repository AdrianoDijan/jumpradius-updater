from typing import Any

import requests
from requests.exceptions import HTTPError

from .constants import HTTPMethod
from .settings import (
    IFCONFIG_CO_API_BASE,
    JUMPRADIUS_API_BASE,
    JUMPRADIUS_API_KEY,
    logger,
)


def send_api_request(
    method: HTTPMethod,
    base: str,
    path: str,
    headers: dict = None,
    body: dict | str | None = None,
    json: bool = True,
) -> dict | str | list | None:
    """Wraps requests.

    Args:
        method (HTTPMethod): request method
        base (str): url base
        path (str): url path
        headers (dict): request headers
        body (dict | str, Optional): request body
        json (bool): True

    Returns:
        dict | str | int | bytes | None: response
    """
    url = f"{base}{path}"
    response = requests.request(
        url=url,
        method=method,
        headers=headers,
        data=body if not json else None,
        json=body if json else None,
    )

    try:
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        logger.error(
            "jumpradius.api_client.base_client", url=url, error=str(e)
        )
        return None
    except ValueError:
        return response.text


def get_radius_servers() -> dict | None:
    """Get all radius servers from the API.

    Returns:
        dict: API response
    """
    response = send_api_request(
        method=HTTPMethod.GET,
        base=JUMPRADIUS_API_BASE,
        path="radiusservers",
        headers={"x-api-key": JUMPRADIUS_API_KEY},
    )

    if response and isinstance(response, dict):
        return response

    return None


def update_server_ip(
    server_id: str, name: str, secret: str, source_ip: str
) -> Any:
    """Get all radius servers from the API.

    Returns:
        dict: API response
    """
    body = {
        "name": name,
        "networkSourceIp": source_ip,
        "sharedSecret": secret,
    }
    response = send_api_request(
        method=HTTPMethod.PUT,
        base=JUMPRADIUS_API_BASE,
        path=f"radiusservers/{server_id}",
        json=True,
        body=body,
        headers={"x-api-key": JUMPRADIUS_API_KEY},
    )

    if response:
        logger.info(
            "jumpradius_updater.api_clients.update_server_ip",
            status="success",
            response=response,
        )

    return response


def get_current_ip() -> str | None:
    """Get current IP using ifconfig.co.

    Returns:
        str: IP address
    """
    response = send_api_request(
        HTTPMethod.GET,
        base=IFCONFIG_CO_API_BASE,
        path="json",
    )

    if response and isinstance(response, dict):
        logger.info(
            "jumpradius_updater.api_clients.get_current_ip",
            status="success",
            response=response,
        )
        return response["ip"]

    return None
