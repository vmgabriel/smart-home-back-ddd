from typing import List

import inspect
import pathlib
import importlib.util

from app import lib
from app.lib import domain
from app.adapter import http, server


_SETTINGS = lib.SETTINGS
_HTTP_PROVIDER = http.get(_SETTINGS.http_provider)()
_SERVER_PROVIDER = server.get(_SETTINGS.server_provider)()


def get_apps() -> List[pathlib.Path]:
    discard_path = [_SETTINGS.app_path / "lib", _SETTINGS.app_path / "adapter"]
    app_path: pathlib.Path = _SETTINGS.app_path
    return [
        dir 
        for dir in app_path.iterdir() 
        if dir not in discard_path and dir.is_dir()
    ]


def get_entrypoint_for_app() -> List[pathlib.Path]:
    apps = get_apps()
    name_entrypoint_file = "entrypoint.py"
    return [
        file 
        for app in apps 
        for file in app.iterdir() 
        if file.is_file() and file == app / name_entrypoint_file
    ]
    

def get_classes_of_module_path(file_module: pathlib.Path) -> List[object]:
    spec = importlib.util.spec_from_file_location("modulo", file_module.absolute())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [
        obj 
        for _, obj in inspect.getmembers(module) 
        if inspect.isclass(obj)
    ]


def is_class_entrypoint(obj: object) -> bool:
    classes_entrypoints = [domain.CRUDEntrypointWeb, domain.EntrypointWeb]
    hierachies = obj.__bases__
    return any(hierachy in classes_entrypoints for hierachy in hierachies)


classes_entrypoint = [
    cl 
    for mod in get_entrypoint_for_app() 
    for cl in get_classes_of_module_path(mod)
    if is_class_entrypoint(cl)
]


for class_entrypoint in classes_entrypoint:
    _HTTP_PROVIDER.add_route(class_entrypoint())

if __name__ == "__main__":
    app = _HTTP_PROVIDER.execute(settings=_SETTINGS)
    _SERVER_PROVIDER.execute(port=app, settings=_SETTINGS)
