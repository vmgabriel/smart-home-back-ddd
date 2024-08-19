import uvicorn

from app import lib as lib_models
from app.adapter.http import model as http_model
from app.adapter.server import model


class UvicornAdapter(model.ServerAdapter):
    def execute(
        self, 
        port: http_model.AppHttp, 
        settings: lib_models.settings.Setting
    ) -> None:
        print(f"port.app - {port.instance}")
        uvicorn.run(
            app=port.instance, 
            host=settings.host,
            port=settings.port,
            reload=True,
            workers=1,
        )