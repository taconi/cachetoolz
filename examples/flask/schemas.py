from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HeroUpdate(BaseModel):
    name: Optional[str]
    secret_name: Optional[str]
    age: Optional[int]


class Filter(HeroUpdate):
    id: Optional[UUID]
