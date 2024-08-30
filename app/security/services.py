import jwt

from app.security import domain
from app.adapter.jwt import model as jwt_model
from app.adapter.uow import model as uow_model


_INVALID_AUTHENTICATION = domain.AuthenticationResponse(
    access_token=None,
    refresh_token=None,
    generation_datetime=None,
    expiration_datetime=None,
    message="Invalid Authentication",
    token=None,
    type=None,
)

_INVALID_REFRESH_AUTHENTICATION = domain.AuthenticationResponse(
    access_token=None,
    refresh_token=None,
    generation_datetime=None,
    expiration_datetime=None,
    message="Invalid Refresh",
    token=None,
    type=None,
)

_USER_HAS_ALREADY_EXISTS = domain.UserCreatedResponse(
    created=False,
    message="User has Already Created",
    user=None,
)


def _find_user_by_id(id: str, getter_repository: domain.UserFinderRepository) -> domain.User | None:
    return getter_repository.get_by_id(id=id)


def _find_profile_by_id(id: str, getter_repository: domain.ProfileFinderRepository) -> domain.Profile | None:
    try:
        return getter_repository.get_by_id(id=id)
    except uow_model.RepositoryNotFoundError:
        return None


def _find_user_by_username(username: str, getter_repository: domain.UserFinderRepository) -> domain.User | None:
    return getter_repository.by_username(username=username)


def authenticate(
    jwt: jwt_model.AuthJWT,
    getter_repository: domain.UserFinderRepository,
    username: str,
    password: str,
) -> domain.AuthenticationResponse:
    user = _find_user_by_username(username=username, getter_repository=getter_repository)
    if not user or not user.is_auth(password=password):
        return _INVALID_AUTHENTICATION

    auth_user = jwt_model.AuthUser(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        username=user.username,
    )

    encoded = jwt.encode(user=auth_user, aud=user.permissions.split(","))

    return domain.AuthenticationResponse(
        status=True,
        message="Valid Authorization",
        type=encoded.type,
        access_token=encoded.access_token,
        refresh_token=encoded.refresh_token,
        generation_datetime=encoded.generation,
        expiration_datetime=encoded.expiration,
    )


def refresh(
    jwt: jwt_model.AuthJWT,
    getter_repository: domain.UserFinderRepository,
    refresh_token: str,
) -> domain.AuthenticationResponse:
    user_refresh = jwt.check_refresh_and_decode(token=refresh_token)
    if not user_refresh.status:
        return _INVALID_REFRESH_AUTHENTICATION
    
    user = _find_user_by_id(id=user_refresh.data.id, getter_repository=getter_repository)
    if not user:
        return _INVALID_REFRESH_AUTHENTICATION

    user_auth = jwt_model.AuthUser(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        username=user.username,
    )

    encoded = jwt.encode(user=user_auth, aud=user.permissions.split(","))

    return domain.AuthenticationResponse(
        status=True,
        message="Valid Authorization",
        type=encoded.type,
        access_token=encoded.access_token,
        refresh_token=encoded.refresh_token,
        generation_datetime=encoded.generation,
        expiration_datetime=encoded.expiration,
    )



def create_a_new_user(
    getter_repository: domain.UserFinderRepository, 
    persistence_repository: domain.UserCreatorRepository, 
    user: domain.PreCreationUser
) -> domain.UserCreatedResponse:
    user_to_find = _find_user_by_username(username=user.username, getter_repository=getter_repository)
    if user_to_find:
        return _USER_HAS_ALREADY_EXISTS
    
    new_user = persistence_repository.create(new=user.to_user())
    data_new_user = new_user.dict()
    del data_new_user["password"]
    
    return domain.UserCreatedResponse(
        created=True,
        message="Created Correctly",
        user=data_new_user,
    )


def get_user_information(id: str, getter_repository: domain.ProfileFinderRepository) -> domain.Profile | None:
    return _find_profile_by_id(id=id, getter_repository=getter_repository)


def upsert_user_information(
    id: str,
    getter_repository: domain.ProfileFinderRepository,
    persistence_repository: domain.ProfileCreatorRepository, 
    profile_data: domain.PreUpdateProfile,
) -> domain.ProfileUpdatedResponse:
    profile = _find_profile_by_id(id=id, getter_repository=getter_repository)
    if profile:
        profile = persistence_repository.update(id=id, to_update=profile.update(profile_data))
    else:
        profile = persistence_repository.create(new=profile_data.to_profile(id=id))
    
    return domain.ProfileUpdatedResponse(
        message="Updated Correctly",
        profile=profile,
    )
