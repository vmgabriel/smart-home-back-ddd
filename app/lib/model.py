from typing import Dict, List
import enum


class EnvironmentType(enum.StrEnum):
    DEV = enum.auto()
    PROD = enum.auto()


class DebugLevelType(enum.StrEnum):
    CRITICAL = enum.auto()
    ERROR = enum.auto()
    WARNING = enum.auto()
    INFO = enum.auto()
    NONE = enum.auto()


class HttpStatusType(enum.StrEnum):
    GET = enum.auto()
    POST = enum.auto()
    PUT = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()
    
    
class ResponseType(enum.StrEnum):
    JSON = enum.auto()
    WS = enum.auto()


class Role(enum.StrEnum):
    CLIENT = "role:client"
    ADMIN = "role:admin"

class Audience(enum.StrEnum):
    GET_PROFILE = "profile:get"

    @staticmethod
    def exists(name: str) -> bool:
        try:
            Audience(name)
        except ValueError:
            return False
        return True



ROLE_PERMISSIONS: Dict[Role, List[Audience]] = {
    Role.ADMIN: [
        Audience.GET_PROFILE,
    ],
    Role.CLIENT: [
        Audience.GET_PROFILE,
    ],
}