import fastapi
from typing import Callable, Dict

from app import lib
from app.lib import domain, model as lib_model
from app.adapter.http import model


_API: str = "/api"
_DOCUMENTATION: str = "/documentation"


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
        for resp in route.responses:
            responses[resp.status_code] = {
                "description": resp.description, 
                "content": {responses_type[resp.type]: {"example": resp.content}}
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
        
        @decorator_router
        def callable_context() -> route.response_model:
            return route.response_model.model_validate({"a": 1, "b": 2})
        
        
    
    def execute(self, settings: lib.settings.Setting) -> model.AppHttp:
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