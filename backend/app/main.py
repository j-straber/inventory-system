# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""FastAPI application entry point for the Estate Inventory system.

- JWT‑based authentication
- Middleware registers AI guardrails, security headers, and audit logger
- Includes Swagger UI at /docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import items, users, payments, location_templates
from .audit.logger import audit_logger

app = FastAPI(title="Estate Inventory API", version=settings.app_version)

# CORS (allow front‑end origin – adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(location_templates.router, prefix="/api/v1/location-templates", tags=["location-templates"])

# Simple startup/shutdown hooks to init audit logger
@app.on_event("startup")
async def startup_event():
    await audit_logger.init()

@app.on_event("shutdown")
async def shutdown_event():
    await audit_logger.close()
