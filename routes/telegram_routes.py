"""
Telegram webhook + admin routes for SemiraFashionBot.
"""

import os
import logging
from flask import Blueprint, request, jsonify, render_template_string, abort, current_app

log = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)


def _token():
    """Read token at request time, not import time."""
    return os.environ.get('TELEGRAM_BOT_TOKEN', '')


def _site_url():
    return os.environ.get('REPLIT_DEV_DOMAIN', '')


# ─────────────────────────────────────────────────────────────
# Webhook endpoint  — Telegram POSTs every update here
# ─────────────────────────────────────────────────────────────
@telegram_bp.route('/telegram/webhook/<string:token>', methods=['POST'])
def webhook(token: str):
    """Receive updates from Telegram."""
    expected = _token()
    if not expected or token != expected:
        log.warning(f"[TelegramWebhook] 403 — token mismatch (got {token[:10]}...)")
        abort(403)
    update_data = request.get_json(force=True, silent=True) or {}
    # Process inside Flask app context so DB helpers work
    app = current_app._get_current_object()
    from services.telegram_bot import process_update_sync
    with app.app_context():
        process_update_sync(update_data)
    return 'ok', 200


# ─────────────────────────────────────────────────────────────
# Admin helper — register / remove webhook
# ─────────────────────────────────────────────────────────────
@telegram_bp.route('/admin/telegram/setup', methods=['GET', 'POST'])
def telegram_setup():
    """Admin page: register or delete the Telegram webhook."""
    from flask import session
    if not session.get('admin'):
        abort(403)

    tok  = _token()
    site = _site_url()
    from services.telegram_bot import set_webhook_sync, delete_webhook_sync, get_bot_info

    result = None
    bot_info = get_bot_info()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'set':
            webhook_url = f"https://{site}/telegram/webhook/{tok}"
            result = set_webhook_sync(webhook_url)
        elif action == 'delete':
            ok = delete_webhook_sync()
            result = {'ok': ok, 'webhook_url': '(removed)'}

    return render_template_string(_SETUP_TEMPLATE,
                                  bot_info=bot_info,
                                  result=result,
                                  site_url=site,
                                  token_set=bool(tok))


# ─────────────────────────────────────────────────────────────
# Status endpoint — quick health check
# ─────────────────────────────────────────────────────────────
@telegram_bp.route('/telegram/status', methods=['GET'])
def telegram_status():
    configured = bool(_token())
    info = None
    if configured:
        try:
            from services.telegram_bot import get_bot_info
            me = get_bot_info()
            info = {'username': me.username, 'name': me.first_name} if me else None
        except Exception:
            pass
    return jsonify({'configured': configured, 'bot': info})


# ─────────────────────────────────────────────────────────────
# Admin setup template
# ─────────────────────────────────────────────────────────────
_SETUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Telegram Bot Setup — Semira Fashion</title>
<style>
  body { font-family: sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; }
  h1 { color: #1b4332; }
  .card { background:#f9f9f9; border:1px solid #ddd; border-radius:8px; padding:20px; margin:20px 0; }
  .badge { display:inline-block; padding:4px 10px; border-radius:12px; font-size:.85em; }
  .ok   { background:#d4edda; color:#155724; }
  .warn { background:#fff3cd; color:#856404; }
  .err  { background:#f8d7da; color:#721c24; }
  button { padding:10px 20px; border:none; border-radius:6px; cursor:pointer; font-size:1em; margin:5px; }
  .btn-green  { background:#1b4332; color:#fff; }
  .btn-red    { background:#c0392b; color:#fff; }
  pre { background:#f4f4f4; padding:12px; border-radius:6px; overflow-x:auto; }
  a.back { color:#1b4332; text-decoration:none; }
</style>
</head>
<body>
<a class="back" href="/admin">← Admin Dashboard</a>
<h1>🤖 SemiraFashionBot Setup</h1>

<div class="card">
  <h2>Bot Status</h2>
  {% if not token_set %}
    <span class="badge err">⚠️ TELEGRAM_BOT_TOKEN not set</span>
    <p>Add <strong>TELEGRAM_BOT_TOKEN</strong> in Replit Secrets and restart the app.</p>
  {% elif bot_info %}
    <span class="badge ok">✅ Connected</span>
    <p><strong>@{{ bot_info.username }}</strong> ({{ bot_info.first_name }})</p>
  {% else %}
    <span class="badge warn">⚠️ Token set but bot unreachable</span>
  {% endif %}
</div>

{% if token_set and site_url %}
<div class="card">
  <h2>Webhook</h2>
  <p><strong>Webhook URL:</strong></p>
  <pre>https://{{ site_url }}/telegram/webhook/&lt;token&gt;</pre>
  <form method="POST">
    <button class="btn-green" name="action" value="set">▶ Register Webhook</button>
    <button class="btn-red"   name="action" value="delete">✕ Remove Webhook</button>
  </form>
  {% if result %}
  <h3>Result</h3>
  <pre>{{ result }}</pre>
  {% endif %}
</div>
{% endif %}

<div class="card">
  <h2>Commands (set via BotFather)</h2>
  <pre>start - ዋና ምናሌ / Main menu
help - ማስፈቻ / Help
products - ምርቶች / Products
cart - ቅርጫቴ / My cart
track - ትዕዛዝ ክትትል / Track order
account - መለያዬ / My account
orders - ትዕዛዞቼ / My orders
wishlist - ምኞቴ / My wishlist
branches - ቅርንጫፎቻችን / Our branches
language - ቋንቋ / Language
cancel - ሰርዝ / Cancel</pre>
</div>

<div class="card">
  <h2>Admin Notifications</h2>
  <p>Set <strong>TELEGRAM_ADMIN_CHAT_ID</strong> in Replit Secrets to receive new-order alerts.</p>
  <p>Find your Chat ID by messaging <a href="https://t.me/userinfobot" target="_blank">@userinfobot</a>.</p>
</div>
</body>
</html>
"""
