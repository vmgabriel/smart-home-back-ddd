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