from app.lib import domain
from app.security import services, domain as security_domain
from app.adapter.uow import model as uow_model


class Cks(domain.Command):
    ...
    
    
class Crm(domain.Command):
    ...
    
    
async def get_items(cmd: Cks, uow: uow_model.UOW) -> domain.CommandResponse:
    with uow.session(type=uow_model.PersistenceType.PERSISTENCE) as session:
        print(f"session {session}")
        print(f"session repositories {session.get_repository(security_domain.UserCreatorRepository)}")
        session.commit()
    return domain.CommandResponse(payload={"a": 1}, trace_id=str(cmd.trace_id))


async def get_context(cmd: Crm) -> domain.CommandResponse:
    return domain.CommandResponse(payload={"b": 1}, trace_id=str(cmd.trace_id))


def generate_process(a: int = 1) -> int:
    return 1
