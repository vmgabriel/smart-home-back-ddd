from app.adapter.uow import model


_MIGRATION_TABLE = """
ALTER TABLE public.user 
ADD COLUMN permissions VARCHAR(250) NOT NULL DEFAULT '';
"""

_ROLLBACK = """
ALTER TABLE public.user 
DROP COLUMN permissions;
"""


migration = model.Migrator(
    up=_MIGRATION_TABLE,
    rollback=_ROLLBACK,
)