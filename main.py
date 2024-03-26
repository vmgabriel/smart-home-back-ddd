from typing import List, Callable, Dict

import inspect
import pathlib
import importlib.util

from app import lib
from app.lib import domain
from app.adapter import http, server, log


_SETTINGS = lib.SETTINGS
_LOG_PROVIDER = log.get(_SETTINGS.log_provider)(settings=_SETTINGS)
_HTTP_PROVIDER = http.get(_SETTINGS.http_provider)(log=_LOG_PROVIDER)
_SERVER_PROVIDER = server.get(_SETTINGS.server_provider)()


_PATH_DISCARD_APP: List[str] = ["lib", "adapter"]
_NAME_ENTRYPOINT_FILE = "entrypoint.py"
_NAME_COMMAND_FILE = "commands.py"


def get_apps() -> List[pathlib.Path]:
    discard_path = [_SETTINGS.app_path / path_discard for path_discard in _PATH_DISCARD_APP]
    app_path: pathlib.Path = _SETTINGS.app_path
    return [
        dir 
        for dir in app_path.iterdir() 
        if dir not in discard_path and dir.is_dir()
    ]


def get_module_for_app(entrypoint_file: str) -> List[pathlib.Path]:
    apps = get_apps()
    return [
        file 
        for app in apps 
        for file in app.iterdir() 
        if file.is_file() and file == app / entrypoint_file
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
    
    
def get_functions_of_module_path(file_module: pathlib.Path) -> List[object]:
    spec = importlib.util.spec_from_file_location("modulo", file_module.absolute())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [
        obj 
        for _, obj in inspect.getmembers(module) 
        if inspect.isfunction(obj)
    ]


def is_class_entrypoint(obj: object) -> bool:
    classes_entrypoints = [domain.CRUDEntrypointWeb, domain.EntrypointWeb]
    hierachies = obj.__bases__
    return any(hierachy in classes_entrypoints for hierachy in hierachies)


def get_parameters_of_function(fn: Callable) -> Dict[str, str]:
    signature = inspect.signature(fn)
    parameters = {}
    for nombre, parametro in signature.parameters.items():
        tipo = (
            parametro.annotation 
            if parametro.annotation != inspect.Parameter.empty else 
            None
        )
        parameters[nombre] = tipo
    return parameters


classes_entrypoint = [
    cl 
    for mod in get_module_for_app(_NAME_ENTRYPOINT_FILE)
    for cl in get_classes_of_module_path(mod)
    if is_class_entrypoint(cl)
]


functions_commands: Dict[object, Callable] = {
    type_parameter: fn
    for mod in get_module_for_app(_NAME_COMMAND_FILE)
    for fn in get_functions_of_module_path(mod)   
    for name_parameter, type_parameter in get_parameters_of_function(fn).items()
    if "cmd" == name_parameter
}


_HTTP_PROVIDER.set_functions_commands(functions_commands)
for class_entrypoint in classes_entrypoint:
    _HTTP_PROVIDER.add_route(class_entrypoint())


if __name__ == "__main__":
    app = _HTTP_PROVIDER.execute(settings=_SETTINGS)
    _SERVER_PROVIDER.execute(port=app, settings=_SETTINGS)
