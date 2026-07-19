"""
Telegram SSO — Magic-Link Auto-Login Route
==========================================
Users who click the "Open Website" button in the Telegram bot are sent to
  /auth/telegram?tg_id=<telegram_user_id>&token=<one-time-token>

This route:
1. Looks up the user by telegram_id
2. Verifies the one-time token (15-min window, single-use)
3. Creates a Flask session identical to a normal login
4. Redirects to the home page as a fully authenticated customer

If the token is invalid / expired the user is sent to / unauthenticated
(they can still log in the normal way).
"""
import logging
import secrets
from datetime import datetime

from flask import Blueprint, request, redirect, session
from database.db import get_db, commit_or_rollback

log = logging.getLogger(__name__)

tg_auth_bp = Blueprint('tg_auth', __name__)


@tg_auth_bp.route('/auth/telegram')
def telegram_login():
    tg_id = request.args.get('tg_id', '').strip()
    token = request.args.get('token', '').strip()

    if not tg_id or not token:
        return redirect('/')

    try:
        db = get_db()

        # ── 1. Look up user by telegram_id ──────────────────────────
        row = db.execute(
            """SELECT id, full_name, email, phone, profile_photo,
                      loyalty_points, telegram_token, telegram_token_expires
               FROM users
               WHERE telegram_id = %s AND is_active = 1
               LIMIT 1""",
            (tg_id,)
        ).fetchone()

        if not row:
            log.warning("[TgSSO] No user found for tg_id=%s", tg_id)
            return redirect('/')

        user = dict(row)

        # ── 2. Verify token ──────────────────────────────────────────
        stored  = user.get('telegram_token') or ''
        expires = user.get('telegram_token_expires')

        token_ok = (
            stored
            and secrets.compare_digest(stored, token)
            and expires is not None
            and datetime.utcnow() < expires
        )

        if not token_ok:
            log.warning("[TgSSO] Invalid/expired token for tg_id=%s", tg_id)
            return redirect('/')

        # ── 3. One-time use — invalidate token immediately ───────────
        db.execute(
            """UPDATE users
               SET telegram_token = NULL,
                   telegram_token_expires = NULL,
                   last_login = NOW()
               WHERE id = %s""",
            (user['id'],)
        )
        commit_or_rollback(db)

        # ── 4. Create Flask session (same keys as normal login) ──────
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
        return redirect('/')
