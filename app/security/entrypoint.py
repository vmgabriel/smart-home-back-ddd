from typing import Type, List
import pydantic

from app.lib import domain, model
from app.security import commands


class Authenticate(domain.EntrypointWeb):
    method: model.HttpStatusType = model.HttpStatusType.POST
    route: str = "/auth"
    name: str = "Authenticate a User"
    summary: str = "Autenticate a User for generate a Valid Token"
    description: str = (
        "Based in username and password, generate a valid token or generate an error"
    )
    command: Type[domain.Command] | None = commands.AuthenticateUser
    has_token: bool = False
    responses: List[domain.ExampleResponse] = [
        domain.ExampleResponse(
            status_code=200,
            example_name="valid authentication",
            description="Valid Authentication and generate valid token",
            content={
                "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payload": {
                    "status": True,
                    "message": "Valid Authorization",
                    "type": "Bearer",
                    "token": "123213213213.123123123.1312312",
                },
                "errors": [],
            },
        ),
        domain.ExampleResponse(
            status_code=200,
            example_name="invalid authentication",
            description="Not Valid Authentication",
            content={
                "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payload": {},
                "errors": [
                    {
                        "status": False,
                        "message": "Invalid Authentication",
                        "type": None,
                        "token": None,
                    }
                ],
            },
        ),
    ]


class RefreshAuthenticate(domain.EntrypointWeb):
    method: model.HttpStatusType = model.HttpStatusType.POST
    route: str = "/auth/refresh"
    name: str = "Refresh Authenticate a User"
    summary: str = "Refresh Autenticate a User for generate a Valid Token"
    description: str = (
        "Based in username and password, generate a valid refresh token or generate an error"
    )
    command: Type[domain.Command] | None = commands.RefreshAuthenticate
    has_token: bool = False
    responses: List[domain.ExampleResponse] = [
        domain.ExampleResponse(
            status_code=200,
            example_name="valid refresh authentication",
            description="Valid Refresh Authentication and generate valid token",
            content={
                "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payload": {
                    "status": True,
                    "message": "Valid Authorization",
                    "type": "Bearer",
                    "access_token": "1111",
                    "refresh_token": "11111",
                    "generation_datetime": "2024-08-19T20:00:04.020555Z",
                    "expiration_datetime": "2024-08-19T22:00:04.020555Z",
                },
                "errors": [],
            },
        )
    ]


class CreateUser(domain.EntrypointWeb):
    method: model.HttpStatusType = model.HttpStatusType.PUT
    route: str = "/users/new"
    name: str = "Create a New User"
    summary: str = "Create a New User"
    description: str = "Based in info getted create a new user"
    command: Type[domain.Command] | None = commands.CreateUser
    status_code: int = 201
    has_token: bool = True
    responses: List[domain.ExampleResponse] = [
        domain.ExampleResponse(
            status_code=201,
            example_name="created correctly",
            description="User Created Correctly",
            content={
                "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payload": {
                    "created": True,
                    "message": "Created Correctly",
                    "user": {
                        "id": "",
                        "actived": True,
                        "created_at": "2024-08-16T22:46:35.777071",
                        "updated_at": "2024-08-16T22:46:35.777076",
                        "deleted_at": None,
                        "name": "Daissi",
                        "last_name": "Gonzalez",
                        "username": "timdx",
                    },
                },
                "errors": [],
            },
        ),
        domain.ExampleResponse(
            status_code=201,
            example_name="user has already exist",
            description="User Has Already Created",
            content={
                "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "payload": {},
                "errors": [
                    {
                        "created": False,
                        "message": "User has Already Created",
                        "user": None,
                    }
                ],
            },
        ),
    ]
