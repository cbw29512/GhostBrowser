import reflex as rx
from sqlmodel import Field
from typing import Optional

class AdminProfile(rx.Model, table=True):
    """Stores the Master Admin credentials. Passwords are salted and hashed."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    salt: str

class VaultEntry(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identity_name: str = Field(index=True, default="My Main Identity")
    encrypted_payload: str = Field(default="") 

class GhostCard(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str
    target_url: str
    authorize_pii: bool = Field(default=False)
