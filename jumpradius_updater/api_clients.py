import requests
from requests.exceptions import JSONDecodeError

from .constants import HTTPMethod
from .logs import logger
from .settings import (
    APP_NAME,
    IFCONFIG_CO_API_BASE,
    JUMPRADIUS_API_BASE,
    JUMPRADIUS_API_KEY,
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
    status_code = None
    try:
        response = requests.request(
            url=url,
            method=method,
            headers=headers,
            data=body if not json else None,
            json=body if json else None,
        )
        status_code = response.status_code
        retval = response.json()
        return retval
    except JSONDecodeError:
        retval = response.text
        return retval
    except Exception:
        logger.exception(
            f"{APP_NAME}.api_clients.send_api_request",
            host=base,
            path=path,
            url=url,
            status_code=status_code,
            body=body,
        )
        retval = None
        return retval
    finally:
        logger.debug(
            "{APP_NAME}.api_clients.send_api_request",
            host=base,
            path=path,
            url=url,
            status_code=status_code,
            body=body,
            response=retval,
        )


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
) -> None:
    """Get all radius servers from the API.

    Returns:
        dict: API response
    """
    body = {
        "name": name,
        "networkSourceIp": source_ip,
        "sharedSecret": secret,
    }
    send_api_request(
        method=HTTPMethod.PUT,
        base=JUMPRADIUS_API_BASE,
        path=f"radiusservers/{server_id}",
        json=True,
        body=body,
        headers={"x-api-key": JUMPRADIUS_API_KEY},
    )


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
        return response["ip"]

    return None
