from pydantic import BaseModel, Field
from src.type import vec2


class EnhancedCell(BaseModel):
    value: int = Field(..., ge=0, le=15)
    pos: vec2 = Field(...)

    @property
    def top(self):
        return bool(self.value & 1)

    @property
    def right(self):
        return bool((self.value >> 1) & 1)

    @property
    def bot(self):
        return bool((self.value >> 2) & 1)

    @property
    def left(self):
        return bool((self.value >> 3) & 1)
