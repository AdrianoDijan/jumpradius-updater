from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from .api_clients import get_radius_servers, update_server_ip
from .logs import logger
from .settings import APP_NAME


@dataclass
class ServerFilters:
    ids: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)


@dataclass
class RadiusServer:
    id: str
    name: str
    source_ip: str
    shared_secret: str

    @classmethod
    def from_api(
        cls: type[RadiusServer], filters: ServerFilters | None = None
    ) -> list[RadiusServer]:
        """Load RadiusServer object from the API.

        Args:
            filters (ServerFilters, optional): filter based on this, don't filter if None

        Returns:
            list[RadiusServer]: filtered server objects
        """
        response = get_radius_servers()
        if not response:
            raise ValueError

        servers = cls.parse_api_response(response)
        if filters:
            servers = [
                server
                for server in servers
                if server.name in filters.names or server.id in filters.ids
            ]
            logger.debug(
                f"{APP_NAME}.models.radius_server.filter",
                count=len(servers),
                servers=[dataclasses.asdict(server) for server in servers],
            )

        return servers

    @classmethod
    def parse_api_response(
        cls: type[RadiusServer], body: dict
    ) -> list[RadiusServer]:
        """Parse API response.

        Args:
            body (dict): API response body

        .. code-block:: json
           :caption: Example API response

            {
                "totalCount": 1,
                "results": [
                    {
                        "_id": "3819d8503481f3f842131c53",
                        "id": "3819d8503481f3f842131c53",
                        "mfa": "DISABLED",
                        "name": "radius",
                        "networkSourceIp": "192.2.0.12",
                        "organization": "8a91g20af6c12g1232321376",
                        "sharedSecret": "secret",
                        "userLockoutAction": "REMOVE",
                        "userPasswordExpirationAction": "REMOVE",
                    }
                ]
            }


        Returns:
            list[RadiusServer]: object
        """
        return [
            cls(
                id=result["id"],
                name=result["name"],
                source_ip=result["networkSourceIp"],
                shared_secret=result["sharedSecret"],
            )
            for result in body["results"]
        ]

    def update_ip(self, source_ip: str) -> None:
        """Update radius server attributes.

        Args:
            source_ip (str): new source IP

        Returns:
            RadiusServer: self
        """
        self.source_ip = source_ip
        update_server_ip(
            server_id=self.id,
            name=self.name,
            secret=self.shared_secret,
            source_ip=self.source_ip,
        )
