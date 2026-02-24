import reflex as rx
from datetime import datetime
from typing import Optional
from sqlmodel import Field

class VaultEntry(rx.Model, table=True):
    """
    Data Schema for the Encrypted Vault.
    Stores the 'ghost' credentials for a specific site.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    site_name: str = Field(index=True)
    encrypted_payload: str  # Encrypted JSON blob
    nonce: str              # AES-GCM requirement
    salt: str               # Argon2 requirement
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GhostCard(rx.Model, table=True):
    """
    Data Schema for the UI Cards.
    Links the visual button to a target domain and vault entry.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str
    target_url: str
    icon_tag: str = "ghost"
    vault_id: Optional[int] = Field(default=None, foreign_key="vaultentry.id")
