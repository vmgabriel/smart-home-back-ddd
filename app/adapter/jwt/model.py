from typing import Optional, List
import abc
import pydantic
import enum
import datetime

from app import lib as lib_models
from app.adapter.log import model as log_model


class StatusType(enum.StrEnum):
    OK = enum.auto()
    NOT_PERMISSIONS = enum.auto()
    EXPIRED = enum.auto()
    NOT_COMPLETE = enum.auto()
    NOT_AUTHORIZED = enum.auto()


class AuthUser(pydantic.BaseModel):
    id: str
    name: str
    last_name: str
    username: str


class EncodedJWT(pydantic.BaseModel):
    type: str
    access_token: str
    refresh_token: str
    generation: datetime.datetime
    expiration: datetime.datetime


class JWTData(pydantic.BaseModel):
    user: AuthUser
    aud: List[str]
    gen: datetime.datetime
    exp: datetime.datetime


class RefreshAuthUser(pydantic.BaseModel):
    id: str
    gen: datetime.datetime
    exp: datetime.datetime


class StatusCheckJWT(pydantic.BaseModel):
    message: str
    status: bool = False
    type: StatusType = StatusType.OK
    data: Optional[JWTData | RefreshAuthUser] = None


class AuthJWT(abc.ABC):
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter

    def __init__(self, settings: lib_models.settings.Setting, log: log_model.LogAdapter) -> None:
        self.settings = settings
        self.log = log

    @abc.abstractmethod
    def encode(self, user: AuthUser, auth: List[str], expiration: Optional[datetime.timedelta] = None) -> EncodedJWT:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_and_decode(self, token: str, allowed_aud: List[str]) -> StatusCheckJWT:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_refresh_and_decode(self, token: str) -> StatusCheckJWT:
        raise NotImplementedError()