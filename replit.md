# SEMIRA FASHION

## Overview

A multi-language e-commerce platform for an Ethiopian women's and children's fashion store. Features a customer storefront, admin dashboard, WhatsApp integration, and a full Telegram shopping bot (@semirafashionBot). Supports Amharic, English, and Arabic.

## Stack

- **Backend**: Python 3.11 + Flask 2.3.3
- **Database**: PostgreSQL (via psycopg2-binary, Replit managed)
- **Frontend**: HTML/Jinja2 templates + vanilla JavaScript + CSS
- **Server**: Flask dev server (development), Gunicorn (production)
- **Auth**: Custom session-based (admin password + customer email/password)
- **Extras**: Flask-Limiter, Flask-Session, Flask-Caching, APScheduler, Pillow, python-telegram-bot

## How to Run

The `Start application` workflow runs the app. It starts automatically. The app is served at port 5000.

- `python app.py` — start dev server on port 5000
- `python run.py --init-db` — re-initialize database schema
- `python run.py --seed` — seed sample products and ads

## Environment Variables

Managed via Replit Secrets / Env Vars panel (not the `.env` file):

- `SESSION_SECRET` — Flask session signing key (already set ✓)
- `DATABASE_URL` — PostgreSQL connection string (Replit managed, auto-injected ✓)
- `ADMIN_PASSWORD` — Admin login password
- `WHATSAPP_NUMBER` — Store WhatsApp number (default: `251987957957`)
- `FREE_SHIPPING_THRESHOLD` — Min order for free shipping in ETB (default: 5000)
- `SHIPPING_COST` — Standard shipping cost in ETB (default: 200)
- `TELEGRAM_BOT_TOKEN` — Token from @BotFather for @semirafashionBot (set ✓)
- `TELEGRAM_ADMIN_CHAT_ID` — (Optional) Admin Telegram chat ID for new-order alerts

## Admin Access

Visit `/admin` and log in with username `admin` and the `ADMIN_PASSWORD` value.

## Telegram Bot

- Bot: **@semirafashionBot**
- Webhook auto-registers on every app start via `REPLIT_DEV_DOMAIN`
- Admin setup page: `/admin/telegram/setup` (must be logged in as admin)
- Commands: `/start`, `/products`, `/cart`, `/track`, `/language`, `/help`, `/cancel`
- Features: browse categories & products, search, cart, place orders, track orders, contact
- Admin notifications: set `TELEGRAM_ADMIN_CHAT_ID` to receive new-order alerts
- Bot files: `services/telegram_bot.py`, `routes/telegram_routes.py`

## Replit Setup (completed)

The following were configured to get this project running on Replit:

1. **Dependencies** — all packages in `requirements.txt` installed via `pip install -r requirements.txt`. The `scripts/post-merge.sh` runs this automatically after every merge.
2. **Database** — Replit's managed PostgreSQL is used. `DATABASE_URL` is injected automatically; no manual configuration needed. Schema is initialized by `init_db()` on first startup.
3. **Secrets** — `SESSION_SECRET` and `ADMIN_PASSWORD` are set in Replit Secrets. `DATABASE_URL` is runtime-managed by Replit.
4. **Workflow** — the `Start application` workflow runs `python app.py` on port 5000 with auto-restart.

## User Preferences

- App runs on port 5000 in development
- Deployment uses Gunicorn on port 8080
- All SQL uses `%s` placeholders (PostgreSQL / psycopg2, never `?`)
- NUMERIC(12,2) for all price columns — no DOUBLE PRECISION
- Decimal values from DB must be wrapped with `float()` before arithmetic
