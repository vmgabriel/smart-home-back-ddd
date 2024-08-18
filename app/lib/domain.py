from typing import Generator, List, Dict, Any, Type

import pydantic
import uuid

from app.lib import model


class CommandResponse(pydantic.BaseModel):
    """Command Response for Use and trace"""
    trace_id: str
    payload: Dict[str, Any] = pydantic.Field(default_factory=dict)
    errors: List[Dict[str, Any]] = pydantic.Field(default_factory=list)


class Command(pydantic.BaseModel):
    trace_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)


class ExampleResponse(pydantic.BaseModel):
    status_code: int
    description: str
    example_name: str
    content: Dict[str, Any] | List[Any]
    type: model.ResponseType = model.ResponseType.JSON


class EntrypointWeb(pydantic.BaseModel):
    route: str
    name: str
    summary: str
    description: str
    command: Type[Command] | None = None
    responses: List[ExampleResponse] = pydantic.Field(default_factory=list)
    tags: List[str] = pydantic.Field(default_factory=list)
    status_code: int = 200
    method: model.HttpStatusType = model.HttpStatusType.GET
    audiences: List[model.Audience] = pydantic.Field(default_factory=list)
    has_token: bool = True

    def get_str_audiencies(self) -> Generator[None, str, None]:
        for audience in self.audiences:
            yield str(audience)
    

class CRUDEntrypointWeb:
    get_all: EntrypointWeb
    get_one: EntrypointWeb
    create: EntrypointWeb
    update: EntrypointWeb
    delete: EntrypointWeb
    
    def __init__(self, route: str, has_token: bool = True) -> None:
        self.get_all = EntrypointWeb(
            route=route, 
            method=model.HttpStatusType.GET, 
            has_token=has_token
        )
        self.get_one = EntrypointWeb(
            route=route, 
            method=model.HttpStatusType.GET, 
            has_token=has_token
        )
        self.create = EntrypointWeb(
            route=route,
            method=model.HttpStatusType.POST,
            has_token=has_token,
        )
        self.update = EntrypointWeb(
            route=route,
            method=model.HttpStatusType.PUT,
            has_token=has_token,
        )
        self.delete = EntrypointWeb(
            route=route,
            method=model.HttpStatusType.DELETE,
            has_token=has_token,
        )

    def c(self) -> Generator:
        entrypoints: List[EntrypointWeb] = [
            self.get_all,
            self.get_one,
            self.create,
            self.update,
            self.delete,
        ]