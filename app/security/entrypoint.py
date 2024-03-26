from typing import Type
import pydantic

from app.lib import domain
from app.security import commands


class PP(pydantic.BaseModel):
    a: int = 1


class GetItems(domain.EntrypointWeb):
    route: str = "/item"
    name: str = "Get Items"
    summary: str = "Summary of get items"
    description: str = "Description of get items"
    command: Type[domain.Command] | None = commands.Cks
