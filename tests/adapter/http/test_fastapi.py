import pytest
import unittest.mock as mock

from app.adapter.http import get as http_get, model
from app.lib.settings import Setting


@pytest.mark.parametrize("port", ["FAKE", "FASTAPI", "ERROR"])
def test_get_fastapi_ok(
    port: str,
) -> None:
    configuration = Setting()
    http = http_get(port)
    
    if port == "ERROR":
        assert not http
        return
    execution: model.AppHttp | None = http().execute(settings=configuration)
    
    assert execution
    assert execution.instance