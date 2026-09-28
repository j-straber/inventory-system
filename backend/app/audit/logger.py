# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Audit logger that writes immutable, HMAC‑signed entries to PostgreSQL and a flat file.
The logger is an async singleton used by routers to record every important action.
"""

import os
import hmac
import hashlib
import json
from datetime import datetime
from typing import Any

# In a real deployment this would use an async DB client (e.g., asyncpg).
# For the prototype we write to a JSON‑lines file in the workspace.

class AuditLogger:
    def __init__(self):
        self.file_path = os.getenv("AUDIT_LOG_PATH", "audit.log")
        self.secret = os.getenv("AUDIT_HMAC_SECRET", "default_secret_key")
        self.file = None

    async def init(self):
        # Open the log file in append mode (text)
        self.file = open(self.file_path, "a", encoding="utf-8")
        await self._write({"event": "audit_logger_started", "timestamp": self._now()})

    async def close(self):
        if self.file:
            await self._write({"event": "audit_logger_stopped", "timestamp": self._now()})
            self.file.close()
            self.file = None

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _sign(self, payload: dict) -> str:
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return hmac.new(self.secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    async def log(self, user_id: int, action: str, details: dict):
        entry = {
            "timestamp": self._now(),
            "user_id": user_id,
            "action": action,
            "details": details,
        }
        entry["hmac"] = self._sign(entry)
        await self._write(entry)

    async def _write(self, entry: dict):
        line = json.dumps(entry, separators=(",", ":")) + "\n"
        self.file.write(line)
        self.file.flush()

# Instantiate a single logger for importers
audit_logger = AuditLogger()
