import pytest
import unittest.mock as mock

from app.adapter.enviroment_variable import get as envvar_get


@mock.patch("dotenv.DotEnv.all")
@pytest.mark.parametrize("port", ["FAKE", "DOTENV", "ERROR"])
def test_get_environment_ok(
    all: mock.MagicMock,
    port: str,
) -> None:
    expected_data = {"MODE": "dev", "DEBUG_LEVEL": "info"}
    all.return_value = expected_data
    enviroment = envvar_get(port)
    if port == "ERROR":
        assert not enviroment
        return
    adapter = enviroment()
    assert adapter.all() == {k.lower(): v for k,v in expected_data.items()}