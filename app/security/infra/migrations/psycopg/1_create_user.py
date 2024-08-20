from app.adapter.uow import model


_MIGRATION_TABLE = """
CREATE TABLE public.user (
    id SERIAL NOT NULL PRIMARY KEY,
    actived BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(150) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);
"""

_ROLLBACK = """
DROP TABLE public.user;
"""


migration = model.Migrator(
    up=_MIGRATION_TABLE,
    rollback=_ROLLBACK,
)