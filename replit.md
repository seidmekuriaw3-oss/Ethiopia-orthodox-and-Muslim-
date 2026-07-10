# SEMIRA FASHION

## Overview

A multi-language e-commerce platform for an Ethiopian women's and children's fashion store. Features a customer storefront, admin dashboard, and WhatsApp integration. Supports Amharic, English, and Arabic.

## Stack

- **Backend**: Python 3.11 + Flask 2.3.3
- **Database**: PostgreSQL (via psycopg2-binary, Replit managed)
- **Frontend**: HTML/Jinja2 templates + vanilla JavaScript + CSS
- **Server**: Flask dev server (development), Gunicorn (production)
- **Auth**: Custom session-based (admin password + customer email/password)
- **Extras**: Flask-Limiter, Flask-Session, Flask-Caching, APScheduler, Pillow

## How to Run

The `Start application` workflow runs the app. It starts automatically. The app is served at port 5000.

- `python app.py` — start dev server on port 5000
- `python run.py --init-db` — re-initialize database schema
- `python run.py --seed` — seed sample products and ads

## Environment Variables

Managed via Replit Secrets / Env Vars panel (not the `.env` file):

- `SESSION_SECRET` — Flask session signing key (already set ✓)
- `DATABASE_URL` — PostgreSQL connection string (Replit managed, auto-injected ✓)
- `ADMIN_PASSWORD` — Admin login password (default from `.env` seed: `Semira2026!`)
- `WHATSAPP_NUMBER` — Store WhatsApp number (default: `251987957957`)
- `FREE_SHIPPING_THRESHOLD` — Min order for free shipping in ETB (default: 5000)
- `SHIPPING_COST` — Standard shipping cost in ETB (default: 200)

## Admin Access

Visit `/admin` and log in with username `admin` and the `ADMIN_PASSWORD` value.

## User Preferences

- App runs on port 5000 in development
- Deployment uses Gunicorn on port 8080
- All SQL uses `%s` placeholders (PostgreSQL / psycopg2, never `?`)
- NUMERIC(12,2) for all price columns — no DOUBLE PRECISION
- Decimal values from DB must be wrapped with `float()` before arithmetic
