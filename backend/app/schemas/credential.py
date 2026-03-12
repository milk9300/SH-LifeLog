from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CredentialBase(BaseModel):
    name: str
    category: Optional[str] = None
    username: Optional[str] = None
    project_id: Optional[int] = None
    encrypted_data: str

class CredentialCreate(CredentialBase):
    pass

class CredentialUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    username: Optional[str] = None
    project_id: Optional[int] = None
    encrypted_data: Optional[str] = None

class Credential(CredentialBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
