from app import lib
from app.adapter import http, server


_SETTINGS = lib.SETTINGS
_HTTP_PROVIDER = http.get(_SETTINGS.http_provider)()
_SERVER_PROVIDER = server.get(_SETTINGS.server_provider)()


if __name__ == "__main__":
    app = _HTTP_PROVIDER.execute(settings=_SETTINGS)
    _SERVER_PROVIDER.execute(port=app, settings=_SETTINGS)
