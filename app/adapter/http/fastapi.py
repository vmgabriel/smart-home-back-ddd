import inspect
import fastapi
import itertools

from typing import Callable, Dict

from app import lib
from app.lib import domain, model as lib_model
from app.adapter.http import model
from app.adapter.uow import model as uow_model


_API: str = "/api"
_DOCUMENTATION: str = "/docs"


class FastApiAdapter(model.HttpAdapter):
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
            "uow": self.uow,
            "request": fastapi.Request,
        }
        function_required_parameters = inspect.signature(command_function).parameters
        parameters = {
            a: command_execution_request[a] 
            for a, _ in function_required_parameters.items() 
            if a in command_execution_request
        }

        if inspect.iscoroutinefunction(command_function):
            @decorator_router
            async def callable_context(payload: route.command) -> domain.CommandResponse:
                return await command_function(**parameters, cmd=payload)
        else:
            @decorator_router
            def callable_context(payload: route.command) -> domain.CommandResponse:
                return command_function(**parameters, cmd=payload)
        
    def execute(self, settings: lib.settings.Setting, uow: uow_model.UOW) -> model.AppHttp:
        self.uow = uow
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