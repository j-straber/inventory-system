# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Application configuration using Pydantic BaseSettings.
All settings can be overridden via environment variables or a .env file.
"""

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    app_name: str = "Estate Inventory API"
    app_version: str = "1.2.0"
    secret_key: str = Field(..., env="SECRET_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    # AI guardrail thresholds
    vision_confidence_min: float = 0.90
    ocr_confidence_min: float = 0.92
    # Payment gateway keys (optional, can be empty for dev)
    stripe_secret_key: str | None = None
    paypal_client_id: str | None = None
    paypal_secret: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
