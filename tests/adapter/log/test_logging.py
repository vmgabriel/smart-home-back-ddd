import pytest
import pydantic
import unittest.mock as mock

from app.adapter.log import get as log_get, model
from app.lib import domain, model as lib_model
from app.lib.settings import Setting


@mock.patch("logging.Logger._log")
@pytest.mark.parametrize("port", ["FAKE", "LOGGING", "ERROR"])
def test_get_log(
    _log: mock.MagicMock,
    port: str,
) -> None:
    configuration = Setting()
    log = log_get(port)
    
    if port == "ERROR":
        assert not log
        return
    execution: model.LogAdapter | None = log(settings=configuration)
    
    assert execution
    
    execution.critical("critical")
    execution.error("Error")
    execution.warning("warning")
    execution.info("Execution with context")
    
    assert _log.call_count == 4