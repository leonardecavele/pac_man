from pydantic import BaseModel, Field


class Config(BaseModel):
    lives: int = Field(..., ge=1)
    points_per_pacgum: int = Field(..., ge=0)
    points_per_super_pacgum: int = Field(..., ge=0)
    points_per_ghost: int = Field(..., ge=0)
    level_max_time: int = Field(..., ge=1)
