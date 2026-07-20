"""
Telegram SSO — Magic-Link Auto-Login Route
==========================================
Users who click "Open Website" in the Telegram bot are sent to:
  /auth/telegram?tg_id=<telegram_user_id>&token=<one-time-token>

Policy (Registration-First):
  1. Look up user by telegram_id.
  2. If the user does not exist OR is_registered != 1 → flash a bilingual
     message and redirect to /login. No session is created.
  3. Verify the one-time token (15-min window, single-use).
  4. On success: create Flask session (same keys as normal login) → redirect /.
  5. On any failure: flash + redirect to /login.
"""
import logging
import secrets
from datetime import datetime

from flask import Blueprint, request, redirect, session, flash, url_for
from database.db import get_db, commit_or_rollback

log = logging.getLogger(__name__)

tg_auth_bp = Blueprint('tg_auth', __name__)

_NOT_REGISTERED_MSG = (
    "የቴሌግራም ምዝገባዎን ስላላጠናቀቁ እባክዎን በድረ-ገጹ ይመዝገቡ ወይም ይግቡ / "
    "Please complete your Telegram bot registration first, "
    "or login / register on the website."
)


@tg_auth_bp.route('/auth/telegram')
def telegram_login():
    tg_id = request.args.get('tg_id', '').strip()
    token = request.args.get('token', '').strip()

    if not tg_id or not token:
        flash(_NOT_REGISTERED_MSG, 'warning')
        return redirect('/login')

    try:
        db = get_db()

        # ── 1. Look up user by telegram_id ──────────────────────────────
        row = db.execute(
            """SELECT id, full_name, email, phone, profile_photo,
                      loyalty_points, is_registered,
                      telegram_token, telegram_token_expires
               FROM users
               WHERE telegram_id = %s AND is_active = 1
               LIMIT 1""",
            (tg_id,)
        ).fetchone()

        # ── 2. Registration-First gate ───────────────────────────────────
        if not row or not row['is_registered']:
            log.info(
                "[TgSSO] tg_id=%s not found or not registered (is_registered=%s)",
                tg_id, row['is_registered'] if row else 'no row'
            )
            flash(_NOT_REGISTERED_MSG, 'warning')
            return redirect('/login')

        user = dict(row)

        # ── 3. Verify one-time token ─────────────────────────────────────
        stored  = user.get('telegram_token') or ''
        expires = user.get('telegram_token_expires')

        token_ok = (
            stored
            and secrets.compare_digest(stored, token)
            and expires is not None
            and datetime.utcnow() < expires
        )

        if not token_ok:
            log.warning("[TgSSO] Invalid or expired token for tg_id=%s", tg_id)
            flash(_NOT_REGISTERED_MSG, 'warning')
            return redirect('/login')

        # ── 4. Invalidate token (one-time use) ───────────────────────────
        db.execute(
            """UPDATE users
               SET telegram_token = NULL,
                   telegram_token_expires = NULL,
                   last_login = NOW()
               WHERE id = %s""",
            (user['id'],)
        )
        commit_or_rollback(db)

        # ── 5. Create Flask session (same keys as normal login) ──────────
        session.permanent = True
        session['user_id']    = user['id']
        session['user_name']  = user.get('full_name') or 'Semira Customer'
        session['user_email'] = user.get('email') or ''
        session['user_phone'] = user.get('phone') or ''
        session['user_photo'] = user.get('profile_photo') or ''

        log.info("[TgSSO] Auto-logged in user id=%s via Telegram", user['id'])
        return redirect('/')

    except Exception as exc:
        log.error("[TgSSO] Error during telegram login: %s", exc)
        flash(_NOT_REGISTERED_MSG, 'warning')
        return redirect('/login')
