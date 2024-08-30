from typing import Optional, Dict, Any
import abc
import hashlib
import pydantic
import datetime
from app.adapter.uow import model, generics
from app.lib import model as lib_model


_AUD_CLIENT = str(lib_model.Role.CLIENT)


def _encrypt_password(password) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class User(model.RepositoryData):
    name: str
    last_name: str
    username: str
    password: str
    permissions: str

    @staticmethod
    def create(name: str, last_name: str, username: str, password: str) -> "User":
        return User(
            id="",
            name=name,
            last_name=last_name,
            username=username,
            password=_encrypt_password(password),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            permissions=_AUD_CLIENT,
            actived=True,
            deleted_at=None,
        )

    def is_auth(self, password: str) -> bool:
        return _encrypt_password(password) == self.password


class Profile(model.RepositoryData):
    email: str
    phone: str
    icon_url: Optional[str] = ""


class PreCreationUser(pydantic.BaseModel):
    name: str
    last_name: str
    username: str
    password: str

    def to_user(self) -> User:
        return User.create(**self.dict())


class UserCreatorRepository(generics.AlterGeneric):
    ...


class UserFinderRepository(generics.Getter):
    @abc.abstractmethod
    def by_username(self, username: str) -> User | None:
        raise NotImplementedError()


class ProfileFinderRepository(generics.Getter):
    ...


class AuthenticationResponse(pydantic.BaseModel):
    status: bool = False
    message: str
    type: str | None
    access_token: str | None
    refresh_token: str | None
    generation_datetime: datetime.datetime | None
    expiration_datetime: datetime.datetime | None


class UserCreatedResponse(pydantic.BaseModel):
    created: bool = True
    message: str
    user: Optional[Dict[str, Any]]