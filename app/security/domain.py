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


class PreCreationUser(pydantic.BaseModel):
    name: str
    last_name: str
    username: str
    password: str

    def to_user(self) -> User:
        return User.create(**self.dict())


class Profile(model.RepositoryData):
    email: str
    phone: str
    icon_url: Optional[str] = ""

    @staticmethod
    def create(id: str, email: str, phone: str, icon_url: str = "") -> "Profile":
        return Profile(
            id=id,
            email=email,
            phone=phone,
            icon_url=icon_url,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            actived=True,
            deleted_at=None,
        )

    def update(self, profile_data: "PreUpdateProfile") -> None:
        self.email = profile_data.email
        self.phone = profile_data.phone
        self.icon_url = profile_data.icon_url


class PreUpdateProfile(pydantic.BaseModel):
    email: str
    phone: str
    icon_url: Optional[str] = ""

    def to_profile(self, id: str) -> Profile:
        return Profile.create(id=id, **self.dict())


class UserCreatorRepository(generics.AlterGeneric):
    ...


class UserFinderRepository(generics.Getter):
    @abc.abstractmethod
    def by_username(self, username: str) -> User | None:
        raise NotImplementedError()


class ProfileCreatorRepository(generics.AlterGeneric):
    ...


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


class ProfileUpdatedResponse(pydantic.BaseModel):
    updated: bool = True
    message: str
    profile: Profile
