# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Pydantic schemas shared across the backend.
Includes location‑template definitions and the extended Item models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID, uuid4

# ---------- Location Template ----------

class LocationSegment(BaseModel):
    """A single segment of a location hierarchy (e.g., garage, rack, shelf)."""
    key: str = Field(..., description="Internal identifier used in the stored dict")
    label: str = Field(..., description="Human‑readable label shown in the UI")
    required: bool = Field(False, description="Whether the user must fill this field")
    example: Optional[str] = Field(None, description="Example placeholder for the UI")

class LocationTemplateCreate(BaseModel):
    """Payload for creating a new location template."""
    name: str = Field(..., example="Large‑Vehicle Bay")
    segments: List[LocationSegment] = Field(..., description="Ordered list of hierarchy segments")

class LocationTemplate(LocationTemplateCreate):
    """Full representation of a persisted template, includes its UUID."""
    template_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the template")

# ---------- Item Schemas (extended) ----------

class ItemBase(BaseModel):
    name: str = Field(..., example="Antique silver pocket watch")
    description: Optional[str] = Field(None, example="Late 19th‑century pocket watch with engraved case.")
    category: Optional[str] = Field(None, example="Jewelry")
    price_usd: Optional[float] = Field(None, example=250.00)
    image_url: Optional[str] = Field(None, example="https://example.com/images/watch.jpg")
    status: Optional[str] = Field("draft", example="draft")  # draft, listed, sold, archived
    # NEW flexible location fields
    template_id: Optional[UUID] = Field(None, description="Reference to a LocationTemplate")
    location: Optional[Dict[str, str]] = Field(
        None, description="Dictionary of location key/value pairs matching the selected template"
    )

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    price_usd: Optional[float]
    image_url: Optional[str]
    status: Optional[str]
    template_id: Optional[UUID]
    location: Optional[Dict[str, str]]

class ItemInDB(ItemBase):
    id: int
