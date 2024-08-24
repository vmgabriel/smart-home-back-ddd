from typing import Tuple

import psycopg

from app.adapter.uow import model


class PsycopgPersistence(model.Persistence):
    _session: psycopg.Cursor
    _connection: psycopg.Connection
    
    def commit(self) -> None:
        self._connection.commit()
    
    def rollback(self) -> None:
        self._connection.rollback()
        
    def flush(self) -> None:
        self._connection.flush()



class PsycopgUOW(model.UOW):
    con: psycopg.Connection
    
    def __init__(
        self, 
        log: model.log_model.LogAdapter,
        settings: model.lib_models.settings.Setting,
        persistence_creator: model.PersistenceCreator,
    ) -> None:
        super().__init__(log=log, settings=settings, persistence_creator=persistence_creator)
        self._conn_data = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
            dbname=self.settings.postgres_dbname, 
            user=self.settings.postgres_username, 
            password=self.settings.postgres_password,
            host=self.settings.postgres_host,
            port=self.settings.postgres_port,
        )
        
    def _open(self) -> Tuple[psycopg.Connection, psycopg.Cursor]:
        self.con = psycopg.connect(conninfo=self._conn_data)
        cur = self.con.cursor()
        self.log.info("Opening Session DB")
        return self.con, cur
    
    def _close(self, session: psycopg.Cursor) -> None:
        session.close()
        self.con.close()
        self.log.info("Closed Session DB")
        
