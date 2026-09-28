# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Compliance and guardrail documentation for the Estate Inventory SaaS prototype.
All sections map directly to code modules and CI checks.
"""

## 1️⃣ AI Guardrails
- **Google Vision** – confidence threshold `settings.vision_confidence_min` (default 0.90). Requests below this raise a `GuardrailViolation` and are not persisted.
- **Stripe OCR** – confidence threshold `settings.ocr_confidence_min` (default 0.92). Same behaviour as Vision.
- All AI calls are wrapped in `ai_guardrails.py` which logs request/response and enforces the thresholds.
- Offline fallback uses Tesseract (opens‑source) with the same confidence logic.

## 2️⃣ PCI‑DSS / Payment Compliance
- No raw card data is stored; only Stripe `payment_intent_id` or PayPal `order_id` tokens are saved.
- All payment events are written to the immutable audit log (`audit/logger.py`).
- HTTPS enforced by Fly.io/Render automatic certificates.
- CSP, HSTS, Referrer‑Policy headers are set in FastAPI middleware (future addition).

## 3️⃣ GDPR / CCPA
- Consent endpoint (`/api/v1/users/consent`) records `user_consent` with versioned text and timestamp.
- Right‑to‑erase endpoint (`DELETE /api/v1/users/{id}`) performs a soft delete then triggers an async job that purges all related rows and object storage references.
- Data minimisation – only fields explicitly required for inventory are stored.

## 4️⃣ Security Hardening (OWASP Top 10)
- Parameterised SQL via SQLAlchemy / asyncpg (placeholder in‑memory store now, DB layer will use ORM).
- CSRF protection via `fastapi.security` middleware (to be added).
- Rate limiting (`slowapi`) configured in `main.py`.
- CORS limited to allowed origins.
- Secrets stored in environment variables; no hard‑coded keys.

## 5️⃣ Auditability & Verifiability
- `audit/logger.py` writes JSON‑lines entries with HMAC‑SHA256 signatures using `AUDIT_HMAC_SECRET`.
- Entries include `timestamp`, `user_id`, `action`, `details`, and `hmac`.
- `audit_export` CLI (future) can generate a signed PDF/JSON report for regulators.

## 6️⃣ Hidden Watermark
- `build_watermark.py` injects a deterministic constant derived from the architect’s name/email into compiled assets (both backend and frontend). The constant can be extracted via the protected endpoint `/api/v1/meta/watermark` (admin‑only).

## 7️⃣ CI / Verification
- GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
  - `ruff`/`flake8` linting
  - `pytest` with coverage ≥ 85 %
  - `bandit` security scan
  - `npm audit` for frontend deps
  - Custom script `verify_compliance.py` that fails the pipeline if any required header, guardrail, or audit entry is missing.

---
*All sections are kept in sync with code; any change to thresholds or policies must be reflected in both the source and this markdown file.*
