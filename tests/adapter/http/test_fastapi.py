import pytest
import pydantic
import unittest.mock as mock

from app.adapter.http import get as http_get, model
from app.lib import domain, model as lib_model
from app.lib.settings import Setting
from app.adapter.log import get as log_get


@pytest.mark.parametrize("port", ["FAKE", "FASTAPI", "ERROR"])
def test_get_fastapi_ok(
    port: str,
) -> None:
    configuration = Setting()
    log = log_get("LOGGING")
    http = http_get(port)
    
    if port == "ERROR":
        assert not http
        return
    execution: model.AppHttp | None = http(log=log).execute(settings=configuration)
    
    assert execution
    assert execution.instance
    
 
@mock.patch("fastapi.FastAPI.get")
def test_add_route_fastapi(get: mock.MagicMock) -> None:
    configuration = Setting()
    log = log_get("LOGGING")
    http = http_get("FASTAPI")(log=log)
    
    class Val(pydantic.BaseModel):
        a: int
        b: int

    entrypoint = domain.EntrypointWeb(
        route="/items",
        name="Get Items",
        tags=["backend", "api", "items"],
        method=lib_model.HttpStatusType.GET,
        summary="""Get Items""",
        has_token=False,
        response_model=Val,
        description="""Esto es un demonio\n nosotros tenemos todo un proceso""",
        responses=[
            domain.ExampleResponse(
                status_code=200, 
                description="Success Data of Items", 
                content={"a": 1, "b": 2}, 
                type=lib_model.ResponseType.JSON
            ),
            domain.ExampleResponse(
                status_code=400, 
                description="Invalid Content", 
                content={"errors": []}, 
                type=lib_model.ResponseType.JSON
            )
        ]
    )
    
    http.add_route(entrypoint)
    execution: model.AppHttp | None = http.execute(settings=configuration)
    
    get.assert_called()