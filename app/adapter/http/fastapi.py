import fastapi

from app import lib as lib_models
from app.adapter.http import model


_API: str = "/api"
_DOCUMENTATION: str = "/documentation"


class FastApiAdapter(model.HttpAdapter):
    def execute(self, settings: lib_models.settings.Setting) -> model.AppHttp:
        app = fastapi.FastAPI(
            debug=settings.has_debug,
            title=settings.title,
            summary=settings.summary,
            docs_url=_DOCUMENTATION,
            contact=settings.contact,
            root_path=_API,
        )
        return model.AppHttp(instance=app)