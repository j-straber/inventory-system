# Inventory Management System

**Project name:** Estate Inventory SaaS (prototype)

## Overview

A cross‑platform, offline‑first inventory management system for estate executors, facilitators, families, and liquidators. It supports multiple intake methods (barcode scanner, phone camera, document scanner, keyboard), advanced AI‑powered recognition (Google Vision, Stripe OCR), and a secure public storefront with Stripe and PayPal payment processing.

The architecture consists of:
- **Backend:** FastAPI (Python) exposing REST endpoints, JWT auth, audit logging, AI guardrails, payment adapters.
- **Frontend:** React (Vite) with a themable dark‑mode UI, offline storage (IndexedDB) and sync service.
- **Database:** PostgreSQL (Fly.io free tier).
- **Search:** Typesense (optional) for faceted search.
- **Deploy:** Fly.io (API) + Vercel/Netlify (static frontend). All components run within free tiers.

## Key Features
- Offline intake and local storage with later cloud sync.
- AI guardrails around Vision/OCR confidence.
- PCI‑DSS compliant payment handling (no raw card data stored).
- GDPR/CCPA‑ready consent flow and right‑to‑erase.
- Auditable immutable logs with HMAC signatures.
- MIT‑licensed open‑source core with hidden watermark for provenance.

## Getting Started (local development)
```bash
# Clone the repo (once created)
git clone <REPO_URL>
cd inventory-system

# Backend (Python 3.12)
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend/app/main:app --reload

# Frontend (Node 20)
cd frontend
npm install
npm run dev
```

## Deployment
- Build Docker images with `docker-compose build`.
- Deploy API to Fly.io (`flyctl launch`).
- Deploy frontend to Vercel/Netlify (point to `frontend/dist`).

## License
MIT – see `LICENSE`.

---

*Generated scaffold – further development will follow the roadmap.*
