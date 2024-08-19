from app.adapter.uow import model


_MIGRATION_TABLE = """
ALTER TABLE user 
ADD COLUMN permissions TEXT NOT NULL DEFAULT '';
"""

_ROLLBACK = """
"""


migration = model.Migrator(
    up=_MIGRATION_TABLE,
    rollback=_ROLLBACK,
)