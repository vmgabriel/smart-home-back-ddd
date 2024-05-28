from typing import List, Dict, Any, Type, Generator

import contextlib
import abc
import pydantic
import enum

from app import lib as lib_models
from app.adapter.log import model as log_model


# Migration

class MigrationFailedError(Exception):
    message = "Migration not completed"
    
    
class MigrationsNotCompletedError(Exception):
    message = "Migrations Not complated"


class Migrator(pydantic.BaseModel):
    up: str
    rollback: str
    
    
class MigrateContext(pydantic.BaseModel):
    name: str
    migrator: Migrator
    has_migrated: bool = False


class Migration(abc.ABC):
    migrations: List[MigrateContext]
    log : log_model.LogAdapter
    settings: lib_models.settings.Setting
    
    def __init__(self, log: log_model.LogAdapter, settings: lib_models.settings.Setting) -> None:
        self.migrations = []
        self.log = log
        self.settings = settings
        
    def add_migrator(self, migrator: MigrateContext) -> None:
        self.migrations.append(migrator)
        
    def migrate(self) -> None:
        with self:
            for to_migrate in self.migrations:
                if not self._is_migrated(to_migrate):
                    try:
                        self.log.info(f"Making Migration {to_migrate.name}")
                        self._migrate_unique(to_migrate)
                        self._mark_migrated(to_migrate)
                    except MigrationFailedError as exc:
                        self.log.error(f"Migration Error - {exc}")
                        self.log.warning(f"Making Rollback {to_migrate.name}")
                        self._rollback_unique(to_migrate)
                        raise MigrationsNotCompletedError(message=str(exc))
            if all(not migration.has_migrated for migration in self.migrations):
                self.log.info("Not Require Migrations")
                
    def __enter__(self) -> None:
        self._open()
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        self._close(exc_type, exc_value, exc_tb)
                
    @abc.abstractmethod
    def _open(self) -> None:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def _close(self) -> None:
        raise NotImplementedError()
            
    @abc.abstractmethod
    def _is_migrated(self, to_migrate: MigrateContext) -> bool:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _mark_migrated(sel, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _rollback_unique(self, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _migrate_unique(self, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()


# Persistence - Repository - UOW

class PersistenceType(enum.StrEnum):
    PERSISTENCE = enum.auto()


class RepositoryHasAlreadyExistsError(Exception):
    message: str = "Repository has Already Exists"


class RepositoryNotFoundError(Exception):
    message: str = "Repository Not Found"
    
    
class PersistenceTypeNotFoundError(Exception):
    message: str = "Persistence Not Found"


class Repository(abc.ABC):
    _session: object
    
    def __init__(self, _session: object) -> None:
        self._session = _session    
    
    @staticmethod
    def serialize(**kwargs) -> "Repository":
        raise NotImplementedError
        
    def dict(self) -> Dict[str, Any]:
        raise NotImplementedError()
        
    def repository_name(self) -> str:
        return self.__class__.__name__


class Persistence(abc.ABC):
    repositories: Dict[Type[Repository], Repository | Type[Repository]]
    log: log_model.LogAdapter
    settings: lib_models.settings.Setting
    _session: object
    
    def __init__(
        self,
        _session: object,
        log: log_model.LogAdapter, 
        settings: lib_models.settings.Setting,
    ) -> None:
        super().__init__()
        self.repositories = {}
        self.log = log
        self.settings = settings
        self._session = _session
    
    def add_repository(self, repository_type: Type[Repository]) -> None:
        if repository_type in self.repositories:
            raise RepositoryHasAlreadyExistsError()
        self.repositories[repository_type] = repository_type
        
    def get_repository(self, repository_type: Type[Repository]) -> Repository | Type[Repository] | None:
        repository = self.repositories.get(repository_type)
        if not repository:
            return None
        if isinstance(repository, Repository):
            return repository
        new_repository = repository(_session=self._session)
        self.repositories[repository_type] = new_repository
        return new_repository
        
    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def flush(self) -> None:
        raise NotImplementedError()


class PersistenceCreator:
    kwargs: Any
    repositories: List[Type[Repository]]
    
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.repositories = []
        
    def add_repository(self, repository_type: Type[Repository]) -> None:
        self.repositories.append(repository_type)
        
    def build(self, _session: object) -> Persistence:
        persistence = Persistence(**self.kwargs, _session=_session)
        for repository in self.repositories:
            try:
                persistence.add_repository(repository)
            except RepositoryHasAlreadyExistsError:
                pass
        return persistence
        
    
class UOW(abc.ABC):
    log: log_model.LogAdapter
    settings: lib_models.settings.Setting
    
    # Creators
    persistence_creator: PersistenceCreator
    
    def __init__(
        self, 
        log: log_model.LogAdapter,
        settings: lib_models.settings.Setting,
        persistence_creator: PersistenceCreator,
    ) -> None:
        super().__init__()
        self.log = log
        self.settings = settings
        self.persistence_creator = persistence_creator
    
    @contextlib.contextmanager
    def session(self, type: PersistenceType) -> Generator[None, Persistence, None]:
        _session = self._open()
        try:
            match type:
                case PersistenceType.PERSISTENCE:
                    yield self.persistence_creator.build(_session=_session)
                case _:
                    raise PersistenceTypeNotFoundError()
        finally:
            self._close(session=_session)
        
    @abc.abstractmethod
    def _open(self) -> object:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _close(self, session: object) -> None:
        raise NotImplementedError()