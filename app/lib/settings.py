import pydantic

from app.lib import model as lib_models 


class Setting(pydantic.BaseModel):
    mode: lib_models.EnvironmentType = lib_models.EnvironmentType.PROD
    debug_level: lib_models.DebugLevelType = lib_models.DebugLevelType.INFO