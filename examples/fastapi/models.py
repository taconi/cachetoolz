from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int]
