from enum import Enum, unique


@unique
class HTTPMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
