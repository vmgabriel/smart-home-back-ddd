from app.lib import domain
from app.security import services


class Cks(domain.Command):
    ...
    
    
class Crm(domain.Command):
    ...
    
    
async def get_items(cmd: Cks) -> domain.CommandResponse:
    return domain.CommandResponse(payload={"a": 1}, trace_id=str(cmd.trace_id))


async def get_context(cmd: Crm) -> domain.CommandResponse:
    return domain.CommandResponse(payload={"b": 1}, trace_id=str(cmd.trace_id))


def generate_process(a: int = 1) -> int:
    return 1
