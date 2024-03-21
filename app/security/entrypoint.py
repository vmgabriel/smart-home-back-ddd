from typing import Type
import pydantic

from app.lib import domain


class PP(pydantic.BaseModel):
    a: int = 1


class GetItems(domain.EntrypointWeb):
    route: str = "/item"
    name: str = "Get Items"
    summary: str = "Summary of get items"
    description: str = "Description of get items"
    response_model: Type[pydantic.BaseModel] | None = PP
