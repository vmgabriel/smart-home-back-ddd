import pytest
import fastapi
import unittest.mock as mock

from app.adapter.server import get as get_server, uvicorn
from app.adapter.http import model
from app.lib.settings import Setting


@mock.patch("uvicorn.run")
@pytest.mark.parametrize("port", ["FAKE", "UVICORN", "ERROR"])
def test_get_uvicorn_ok(
    run: mock.MagicMock,
    port: str,
) -> None:
    configuration = Setting()
    http = get_server(port)
    app = model.AppHttp(instance=fastapi.FastAPI())
    
    if port == "ERROR":
        assert not http
        return
    adapter = uvicorn.UvicornAdapter()
    adapter.execute(port=app, settings=configuration)
    
    run.assert_called
    