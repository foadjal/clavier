from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Score(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    wpm: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
