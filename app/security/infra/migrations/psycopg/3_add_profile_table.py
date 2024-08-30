from app.adapter.uow import model


_MIGRATION_TABLE = """
CREATE TABLE public.profile (
    id INTEGER NOT NULL PRIMARY KEY,
    actived BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    icon_url TEXT NULL
);
"""

_ROLLBACK = """
DROP TABLE public.profile;
"""


migration = model.Migrator(
    up=_MIGRATION_TABLE,
    rollback=_ROLLBACK,
)