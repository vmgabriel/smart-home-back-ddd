from typing import List, Callable, Dict, Tuple

import inspect
import pathlib
import importlib.util

from app import lib
from app.lib import domain
from app.adapter import http, server, log, uow
from app.adapter.uow import model as uow_model


_SETTINGS = lib.SETTINGS
_LOG_PROVIDER = log.get(_SETTINGS.log_provider)(settings=_SETTINGS)
_HTTP_PROVIDER = http.get(_SETTINGS.http_provider)(log=_LOG_PROVIDER)
_SERVER_PROVIDER = server.get(_SETTINGS.server_provider)()
_UOW_MIGRATION = uow.migration_get(_SETTINGS.migration_provider)(log=_LOG_PROVIDER, settings=_SETTINGS)


_PATH_DISCARD_APP: List[str] = ["lib", "adapter"]
_NAME_ENTRYPOINT_FILE = "entrypoint.py"
_NAME_COMMAND_FILE = "commands.py"
_PATH_APP = pathlib.Path() / "app"


class NotFoundMigration(Exception):
    message: str = "Migration not Found"


def get_files_of_dir(dir_path: pathlib.Path, discards: List[str] = ["__init__.py"]) -> List[pathlib.Path]:
    return [
        dir_path / fil.name 
        for fil in dir_path.iterdir() 
        if fil.is_file() and fil.name not in discards
    ]


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
    
    
def get_migration_of_module_path(file_module: pathlib.Path) -> object:
    spec = importlib.util.spec_from_file_location("modulo", file_module.absolute())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return getattr(module, "migration", None)


def get_repositories_and_migrations_by_domain(file_module: pathlib.Path) -> Tuple[object, object]:
    path_migrations: pathlib.Path = pathlib.Path(file_module / "infra" / "migrations")
    path_repositories: pathlib.Path = pathlib.Path(file_module / "infra" / "repositories")

    migrations = get_files_of_dir(path_migrations)
    migrations.sort(key=lambda file: file.name.split("_")[0])
    repositories = get_files_of_dir(path_repositories)
    
    return migrations, repositories 
    
    
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


def _get_migrations() -> Dict[str, object | None]:
    path = pathlib.Path(_SETTINGS.route_path_migrations)
    files = [
        file for file in path.iterdir() 
        if file.is_file() and file.name != "__init__.py"
    ]
    files.sort(key=lambda file: file.name.split("_")[0])
    return { 
        file.name.split(".")[0]: get_migration_of_module_path(file)
        for file in files
    }


def _migrate(name: str, to_migrate: object | None) -> None:
    _LOG_PROVIDER.info(f"Including Migration {name}")
    if not to_migrate:
        raise NotFoundMigration(message=f"Migration {name} Not Found")
    _UOW_MIGRATION.add_migrator(uow_model.MigrateContext(name=name, migrator=to_migrate))
    


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


migrators = _get_migrations()
for name_migration, migrator in migrators.items():
    _migrate(name_migration, migrator)


repositories = []

# Get Domains
for domain in _SETTINGS.domains:
    _LOG_PROVIDER.info(f"Getting From Domain {domain} - Repositories | Migrations")
    migrations, repositories = get_repositories_and_migrations_by_domain(_PATH_APP / domain)
    print(f"migrations {migrations}")
    for migration in migrations:
        _migrate(
            f"{domain}_{(migrations[0].name).split('.')[:-1][0]}", 
            get_migration_of_module_path(migration)
        )

    # TODO: Include in UOW
    print(f"repositories {repositories}")
    # TODO: Get Repositories and Inject
    ...


_UOW_MIGRATION.migrate()


if __name__ == "__main__":
    app = _HTTP_PROVIDER.execute(settings=_SETTINGS)
    _SERVER_PROVIDER.execute(port=app, settings=_SETTINGS)
