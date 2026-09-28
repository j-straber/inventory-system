# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Location Template CRUD router.

Provides endpoints to manage flexible location templates that define the
segments required for an item's location string.  The router currently uses
an in‑memory store (`_template_store`).  Future iterations will replace this
with a persistent PostgreSQL model via SQLAlchemy.
"""

from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List

from ..schemas import LocationTemplateCreate, LocationTemplate

router = APIRouter()

# In‑memory store – maps template_id to LocationTemplate instances.
_template_store: Dict[UUID, LocationTemplate] = {}

@router.get("/", response_model=List[LocationTemplate])
def list_templates():
    """Return all location templates."""
    return list(_template_store.values())

@router.post(
    "/",
    response_model=LocationTemplate,
    status_code=status.HTTP_201_CREATED,
)
def create_template(template: LocationTemplateCreate):
    """Create a new location template.

    A fresh ``template_id`` (UUID) is generated and stored.
    """
    template_id = uuid4()
    new_template = LocationTemplate(template_id=template_id, **template.dict())
    _template_store[template_id] = new_template
    return new_template

@router.get("/{template_id}", response_model=LocationTemplate)
def get_template(template_id: UUID):
    """Retrieve a specific template by its UUID."""
    tmpl = _template_store.get(template_id)
    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location template {template_id} not found",
        )
    return tmpl

@router.put("/{template_id}", response_model=LocationTemplate)
def update_template(template_id: UUID, template: LocationTemplateCreate):
    """Replace an existing template with a new definition.

    The ``template_id`` stays unchanged; only the name and segments are
    overwritten.
    """
    if template_id not in _template_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location template {template_id} not found",
        )
    updated = LocationTemplate(template_id=template_id, **template.dict())
    _template_store[template_id] = updated
    return updated

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: UUID):
    """Delete a template.

    A ``204 No Content`` response signals successful deletion.  If the
    template does not exist a ``404`` is returned.
    """
    if template_id not in _template_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location template {template_id} not found",
        )
    del _template_store[template_id]
    return None
