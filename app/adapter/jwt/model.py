from typing import Optional, List, Dict, Any
import abc
import pydantic
import enum
import datetime

from app import lib as lib_models
from app.lib import model as model_lib
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

    def has_permission(self, auds: List[str]) -> bool:
        role = list(filter(lambda aud: aud.startswith("role:"), self.aud))[0]
        all_auds_with_role = model_lib.ROLE_PERMISSIONS[model_lib.Role(role)]
        current_user_auds = [
            model_lib.Audience(aud)
            for aud in self.aud
            if model_lib.Audience.exists(aud)
        ] + all_auds_with_role
        return any(model_lib.Audience(aud) in current_user_auds for aud in auds)

    def dict(self) -> Dict[str, Any]:
        return {
            "user": self.user.dict(),
            "aud": self.aud,
            "gen": self.gen.timestamp(),
            "exp": self.exp.timestamp(),
        }


class RefreshAuthUser(pydantic.BaseModel):
    id: str
    gen: datetime.datetime
    exp: datetime.datetime

    def dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "gen": self.gen.timestamp(),
            "exp": self.exp.timestamp(),
        }


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
    def encode(self, user: AuthUser, aud: List[str], expiration: Optional[datetime.timedelta] = None) -> EncodedJWT:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_and_decode(self, token: str, allowed_aud: List[str]) -> StatusCheckJWT:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_refresh_and_decode(self, token: str) -> StatusCheckJWT:
        raise NotImplementedError()