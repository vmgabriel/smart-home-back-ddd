import enum


class EnvironmentType(enum.StrEnum):
    DEV = enum.auto()
    PROD = enum.auto()


class DebugLevelType(enum.StrEnum):
    CRITICAL = enum.auto()
    ERROR = enum.auto()
    WARNING = enum.auto()
    INFO = enum.auto()