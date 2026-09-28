# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Router handling CRUD operations for inventory items.
Each item includes optional image URLs, provenance data, pricing, location, and status.
All endpoints are protected by JWT authentication (middleware not shown).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import io
import json

from ..config import settings
from ..audit.logger import audit_logger
from ..utils.barcode import generate_barcode, generate_qr

router = APIRouter()

class ItemBase(BaseModel):
    name: str = Field(..., example="Antique silver pocket watch")
    description: Optional[str] = Field(None, example="Late 19th‑century pocket watch with engraved case.")
    category: Optional[str] = Field(None, example="Jewelry")
    price_usd: Optional[float] = Field(None, example=250.00)
    image_url: Optional[str] = Field(None, example="https://example.com/images/watch.jpg")
    status: Optional[str] = Field("draft", example="draft")  # draft, listed, sold, archived
    location: Optional[str] = Field(None, example="House 2, Room 3, Rack A, Shelf 1")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    price_usd: Optional[float]
    image_url: Optional[str]
    status: Optional[str]
    location: Optional[str]

class ItemInDB(ItemBase):
    id: int

# Placeholder in‑memory store – replace with real DB calls later
_fake_db: dict[int, ItemInDB] = {}
_next_id = 1

@router.post("/", response_model=ItemInDB, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, user_id: int = Depends(lambda: 1)):
    global _next_id
    new_item = ItemInDB(id=_next_id, **item.dict())
    _fake_db[_next_id] = new_item
    _next_id += 1
    await audit_logger.log(user_id, "create_item", new_item.dict())
    return new_item

@router.get("/", response_model=List[ItemInDB])
async def list_items(user_id: int = Depends(lambda: 1)):
    await audit_logger.log(user_id, "list_items", {})
    return list(_fake_db.values())

@router.get("/{item_id}", response_model=ItemInDB)
async def get_item(item_id: int, user_id: int = Depends(lambda: 1)):
    item = _fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await audit_logger.log(user_id, "get_item", {"item_id": item_id})
    return item

@router.put("/{item_id}", response_model=ItemInDB)
async def update_item(item_id: int, updates: ItemUpdate, user_id: int = Depends(lambda: 1)):
    stored = _fake_db.get(item_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_data = stored.dict()
    for field, value in updates.dict(exclude_unset=True).items():
        updated_data[field] = value
    updated_item = ItemInDB(**updated_data)
    _fake_db[item_id] = updated_item
    await audit_logger.log(user_id, "update_item", {"item_id": item_id, "updates": updates.dict(exclude_unset=True)})
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, user_id: int = Depends(lambda: 1)):
    if item_id not in _fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del _fake_db[item_id]
    await audit_logger.log(user_id, "delete_item", {"item_id": item_id})
    return None

# ----- Barcode / QR endpoints -----

@router.get("/{item_id}/barcode", response_class=StreamingResponse)
async def get_item_barcode(item_id: int, user_id: int = Depends(lambda: 1)):
    """Return a Code128 barcode encoding the item ID and location string.
    Payload format: ``item:{id}|loc:{location}`` (location may be empty).
    """
    item = _fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    payload = f"item:{item.id}|loc:{item.location or ''}"
    png_bytes = generate_barcode(payload)
    await audit_logger.log(user_id, "get_barcode", {"item_id": item_id})
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")

@router.get("/{item_id}/qr", response_class=StreamingResponse)
async def get_item_qr(item_id: int, user_id: int = Depends(lambda: 1)):
    """Return a QR code encoding JSON with item ID and location.
    Example payload: ``{"id": 12, "location": "House 2, Room 3"}``
    """
    item = _fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    payload = {"id": item.id, "location": item.location}
    qr_bytes = generate_qr(json.dumps(payload))
    await audit_logger.log(user_id, "get_qr", {"item_id": item_id})
    return StreamingResponse(io.BytesIO(qr_bytes), media_type="image/png")
