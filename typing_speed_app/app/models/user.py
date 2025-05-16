from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    username: str
    password_hash: str
    is_validated: bool = False
    validation_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    code_created_at: datetime = Field(default_factory=datetime.utcnow)
    failed_attempts: int = 0
    lockout_until: Optional[datetime] = None
    temp_password_hash: Optional[str] = Field(default=None)
    temp_password_expiration: Optional[datetime] = Field(default=None)
    force_password_reset: bool = Field(default=False)

