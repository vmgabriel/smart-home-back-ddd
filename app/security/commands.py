from app.lib import domain
from app.security import services, domain as security_domain
from app.adapter.uow import model as uow_model
from app.adapter.jwt import model as jwt_model


class AuthenticateUser(domain.Command):
    username: str
    password: str


class CreateUser(domain.Command):
    user: security_domain.PreCreationUser


class RefreshAuthenticate(domain.Command):
    refresh_token:  str


async def authenticate_user(cmd: AuthenticateUser, uow: uow_model.UOW, jwt: jwt_model.AuthJWT) -> domain.CommandResponse:
    with uow.session(type=uow_model.PersistenceType.PERSISTENCE) as session:
        getter_user = session.get_repository(security_domain.UserFinderRepository)
        authentication_response = services.authenticate(
            jwt=jwt,
            getter_repository=getter_user,
            username=cmd.username, 
            password=cmd.password
        )
    return domain.CommandResponse(
        payload=authentication_response.dict() if authentication_response.status else {},
        trace_id=str(cmd.trace_id),
        errors=[authentication_response.dict()] if not authentication_response.status else [],
    )


async def refresh_authenticate_user(cmd: RefreshAuthenticate, uow: uow_model.UOW, jwt: jwt_model.AuthJWT) -> domain.CommandResponse:
    with uow.session(type=uow_model.PersistenceType.PERSISTENCE) as session:
        getter_user = session.get_repository(security_domain.UserFinderRepository)
        authentication_response = services.refresh(
            jwt=jwt,
            getter_repository=getter_user,
            refresh_token=cmd.refresh_token,
        )
    return domain.CommandResponse(
        payload=authentication_response.dict() if authentication_response.status else {},
        trace_id=str(cmd.trace_id),
        errors=[authentication_response.dict()] if not authentication_response.status else [],
    )


async def create_new_user(cmd: CreateUser, uow: uow_model.UOW) -> domain.CommandResponse:
    with uow.session(type=uow_model.PersistenceType.PERSISTENCE) as session:
        persistence_repository = session.get_repository(security_domain.UserCreatorRepository)
        getter_user = session.get_repository(security_domain.UserFinderRepository)
        response = services.create_a_new_user(
            getter_repository=getter_user,
            persistence_repository=persistence_repository,
            user=cmd.user
        )
        session.commit()
    return domain.CommandResponse(
        payload=response.dict() if response.created else {},
        trace_id=str(cmd.trace_id),
        errors=[response.dict()] if not response.created else [],
    )