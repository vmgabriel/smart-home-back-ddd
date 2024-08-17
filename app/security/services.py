from app.security import domain


_INVALID_AUTHENTICATION = domain.AuthenticationResponse(
    message="Invalid Authentication",
    token=None,
    type=None,
)

_USER_HAS_ALREADY_EXISTS = domain.UserCreatedResponse(
    created=False,
    message="User has Already Created",
    user=None,
)


def _find_user_by_username(username: str, getter_repository: domain.UserFinderRepository) -> domain.User | None:
    return getter_repository.by_username(username=username)


def authenticate(getter_repository: domain.UserFinderRepository, username: str, password: str) -> domain.AuthenticationResponse:
    user = _find_user_by_username(username=username, getter_repository=getter_repository)
    if not user or not user.is_auth(password=password):
        return _INVALID_AUTHENTICATION
    return domain.AuthenticationResponse(
        status=True,
        message="Valid Authorization",
        type="Bearer",
        token="123213213213.123123123.1312312",
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
