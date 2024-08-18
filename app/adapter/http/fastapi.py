from typing import Callable, Dict, Optional, Any

import inspect
import fastapi
import itertools

from app import lib
from app.adapter.http import model
from app.lib import domain, model as lib_model
from app.adapter.uow import model as uow_model
from app.adapter.jwt import model as jwt_model


_API: str = "/api"
_DOCUMENTATION: str = "/docs"
_403_NOT_COMPLETE_DOCUMENTATION: Dict[str, Any] = {
    "payload": {},
    "errors": [
        {
            "message": "Not Complete Information in Token",
            "type": "not_complete"
        }
    ]
}
_403_NOT_FOUND_DOCUMENTATION: Dict[str, str] = {
  "detail": "Not authenticated"
}


oauth2_scheme = fastapi.security.APIKeyHeader(name="Authorization")


class FastApiAdapter(model.HttpAdapter):
    authorization_name_attribute: str
    auth_type: str

    def _to_route(self, app: object, route: domain.EntrypointWeb) -> None:
        app: fastapi.FastAPI = app
        status_callable: Dict[lib_model.HttpStatusType, Callable] = {
            lib_model.HttpStatusType.GET: app.get,
            lib_model.HttpStatusType.POST: app.post,
            lib_model.HttpStatusType.PUT: app.put,
            lib_model.HttpStatusType.PATCH: app.patch,
            lib_model.HttpStatusType.DELETE: app.delete,
        }
        
        responses_type: Dict[lib_model.ResponseType, str] = {
            lib_model.ResponseType.JSON: "application/json",
            lib_model.ResponseType.WS: "application/ws",
        }
        
        responses = {}
        for status_code, responses_group in itertools.groupby(route.responses, key=lambda x: x.status_code):
            resp = ...
            examples_responses = {}
            for x in responses_group:
                examples_responses[x.example_name] = {"value": x.content}
                resp = x
            responses[resp.status_code] = {
                "description": resp.description,
                "content": {
                    responses_type[resp.type]: {
                        "examples": examples_responses
                    }
                }
            }

        if route.has_token:
            responses[403] = {
                "description": "Not Allowed Authorization",
                "content": {
                    "application/json": { "examples": {
                        "Token not Valid": { "value": _403_NOT_COMPLETE_DOCUMENTATION },
                        "Token not found": { "value": _403_NOT_FOUND_DOCUMENTATION },
                    } }
                }
            }
        
        decorator_router = status_callable[route.method](
            route.route, 
            name=route.name,
            status_code=route.status_code,
            tags=route.tags,
            summary=route.summary,
            responses=responses,
            description=route.description,
        )
        
        command_function = None
        if route.command:
            command_function = self.functions_commands[route.command.__name__]
            
        if not command_function:
            return
        
        self.log.info(f"Adding Command [{route.command.__name__}]")

        command_execution_request = {
            "user": ...,
            "uow": self.uow,
            "request": fastapi.Request,
        }
        function_required_parameters = inspect.signature(command_function).parameters
        parameters = {
            a: command_execution_request[a] 
            for a, _ in function_required_parameters.items() 
            if a in command_execution_request
        }

        def check_authentication(token: str) -> fastapi.responses.JSONResponse | None:
            print(f"token {token}")
            if not token.startswith(f"{self.auth_type} "):
                return fastapi.responses.JSONResponse(
                    content={"payload": {}, "errors": [{"message": "Not Authentication"}]}, 
                    status_code=401
                )
            response = self.jwt.check_and_decode(
                token=token.split(" ")[1],
                allowed_aud=list(route.get_str_audiencies())
            )
            if not response.status:
                return fastapi.responses.JSONResponse(
                    content={"payload": {}, "errors": [{"message": response.message, "type": response.type.value}]}, 
                    status_code=403
                )
            if "user" in parameters:
                parameters["user"] = response.data

        if inspect.iscoroutinefunction(command_function):
            @decorator_router
            async def callable_context(
                payload: route.command,
                token: Optional[str] = fastapi.Depends(oauth2_scheme) if route.has_token else None,
            ) -> domain.CommandResponse:
                if route.has_token:
                    fail = check_authentication(token=token)
                    if fail:
                        return fail
                return await command_function(**parameters, cmd=payload)
        else:
            @decorator_router
            def callable_context(
                payload: route.command,
                token: Optional[str] = fastapi.Depends(oauth2_scheme) if route.has_token else None,
            ) -> domain.CommandResponse:
                if route.has_token:
                    fail = check_authentication(token=token)
                    if fail:
                        return fail
                return command_function(**parameters, cmd=payload)
        
    def execute(
        self, 
        settings: lib.settings.Setting, 
        uow: uow_model.UOW,
        jwt: jwt_model.AuthJWT,
    ) -> model.AppHttp:
        self.uow = uow
        self.jwt = jwt
        self.authorization_name_attribute = settings.authorization_name_attribute
        self.auth_type=settings.auth_type
        app = fastapi.FastAPI(
            debug=settings.has_debug,
            title=settings.title,
            summary=settings.summary,
            docs_url=_DOCUMENTATION,
            contact=settings.contact,
            root_path=_API,
        )
        
        for route in self.routes:
            self._to_route(app, route)
        
        return model.AppHttp(instance=app)