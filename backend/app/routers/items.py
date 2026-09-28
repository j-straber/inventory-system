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
import io
import json

from ..config import settings
from ..audit.logger import audit_logger
from ..utils.barcode import generate_barcode, generate_qr
from ..schemas import ItemCreate, ItemUpdate, ItemInDB, LocationTemplate
from typing import Dict
from uuid import UUID

router = APIRouter()

# In‑memory stores (temporary prototype)
_fake_items: dict[int, ItemInDB] = {}
_next_item_id = 1

# Simple location template store – would be a DB table later
_template_store: dict[UUID, LocationTemplate] = {}

def _validate_location(template_id: UUID | None, location: Dict[str, str] | None):
    """Validate that required keys from the selected template are present.
    If `template_id` is None we allow any free‑form dict.
    """
    if not template_id:
        return
    tmpl = _template_store.get(template_id)
    if not tmpl:
        raise HTTPException(status_code=400, detail="Location template not found")
    missing = [seg.key for seg in tmpl.segments if seg.required and (location is None or seg.key not in location)]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required location fields: {', '.join(missing)}",
        )

@router.post("/", response_model=ItemInDB, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, user_id: int = Depends(lambda: 1)):
    global _next_item_id
    _validate_location(item.template_id, item.location)
    new_item = ItemInDB(id=_next_item_id, **item.dict())
    _fake_items[_next_item_id] = new_item
    _next_item_id += 1
    await audit_logger.log(user_id, "create_item", new_item.dict())
    return new_item

@router.get("/", response_model=list[ItemInDB])
async def list_items(user_id: int = Depends(lambda: 1)):
    await audit_logger.log(user_id, "list_items", {})
    return list(_fake_items.values())

@router.get("/{item_id}", response_model=ItemInDB)
async def get_item(item_id: int, user_id: int = Depends(lambda: 1)):
    item = _fake_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await audit_logger.log(user_id, "get_item", {"item_id": item_id})
    return item

@router.put("/{item_id}", response_model=ItemInDB)
async def update_item(item_id: int, updates: ItemUpdate, user_id: int = Depends(lambda: 1)):
    stored = _fake_items.get(item_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Item not found")
    # Validate location if template changes or location dict supplied
    if updates.template_id is not None or updates.location is not None:
        tmpl_id = updates.template_id if updates.template_id is not None else stored.template_id
        loc = updates.location if updates.location is not None else stored.location
        _validate_location(tmpl_id, loc)
    updated_data = stored.dict()
    for field, value in updates.dict(exclude_unset=True).items():
        updated_data[field] = value
    updated_item = ItemInDB(**updated_data)
    _fake_items[item_id] = updated_item
    await audit_logger.log(user_id, "update_item", {"item_id": item_id, "updates": updates.dict(exclude_unset=True)})
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, user_id: int = Depends(lambda: 1)):
    if item_id not in _fake_items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _fake_items[item_id]
    await audit_logger.log(user_id, "delete_item", {"item_id": item_id})
    return None

# ----- Barcode / QR endpoints -----

@router.get("/{item_id}/barcode", response_class=StreamingResponse)
async def get_item_barcode(item_id: int, user_id: int = Depends(lambda: 1)):
    """Return a Code128 barcode encoding the item ID and location string.
    Payload format: ``item:{id}|loc:{json_location}`` (location JSON may be empty).
    """
    item = _fake_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    loc_part = json.dumps(item.location) if item.location else ""
    payload = f"item:{item.id}|loc:{loc_part}"
    png_bytes = generate_barcode(payload)
    await audit_logger.log(user_id, "get_barcode", {"item_id": item_id})
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")

@router.get("/{item_id}/qr", response_class=StreamingResponse)
async def get_item_qr(item_id: int, user_id: int = Depends(lambda: 1)):
    """Return a QR code encoding JSON with item ID and location.
    Example payload: ``{"id": 12, "location": {...}}``
    """
    item = _fake_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    payload = {"id": item.id, "location": item.location}
    qr_bytes = generate_qr(json.dumps(payload))
    await audit_logger.log(user_id, "get_qr", {"item_id": item_id})
    return StreamingResponse(io.BytesIO(qr_bytes), media_type="image/png")
