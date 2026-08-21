"""Telegram application construction and webhook runtime.

Handler/business logic stays in telegram_bot.py; this module owns the
long-lived asyncio loop and Telegram application lifecycle.
"""

import asyncio
import logging
import threading

from telegram import Bot, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

log = logging.getLogger(__name__)

_loop: asyncio.AbstractEventLoop | None = None
_application: Application | None = None
_lock = threading.Lock()


def build_application() -> Application:
    """Build the Telegram application using handlers from telegram_bot."""
    from services import telegram_bot as botmod

    app = Application.builder().token(botmod._get_token()).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', botmod.cmd_start),
            CommandHandler('help', botmod.cmd_help),
            CommandHandler('products', botmod.cmd_products),
            CommandHandler('cart', botmod.cmd_cart),
            CommandHandler('track', botmod.cmd_track),
            CommandHandler('language', botmod.cmd_language),
            CommandHandler('cancel', botmod.cmd_cancel),
            CommandHandler('account', botmod.cmd_account),
            CommandHandler('orders', botmod.cmd_orders),
            CommandHandler('wishlist', botmod.cmd_wishlist),
            CommandHandler('branches', botmod.cmd_branches),
            CallbackQueryHandler(botmod.on_callback),
        ],
        states={
            botmod.AWAIT_SEARCH: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_search_input),
            ],
            botmod.AWAIT_NAME: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_name_input),
            ],
            botmod.AWAIT_PHONE: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_phone_input),
            ],
            botmod.AWAIT_ADDRESS: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_address_input),
            ],
            botmod.AWAIT_COUPON: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_coupon_input),
            ],
            botmod.AWAIT_TRACK: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_track_input),
            ],
            botmod.AWAIT_ORDERS_PHONE: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.CONTACT, botmod.on_link_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_orders_phone_input),
            ],
            botmod.AWAIT_CONTACT: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.CONTACT, botmod.on_link_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_orders_phone_input),
            ],
            botmod.AWAIT_REG_NAME: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_reg_name_input),
            ],
            botmod.AWAIT_REG_PHONE: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_reg_phone_input),
            ],
            botmod.AWAIT_REG_EMAIL: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_reg_email_input),
            ],
            botmod.AWAIT_REG_PASS: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_reg_pass_input),
            ],
            botmod.AWAIT_EDIT_NAME: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_edit_name_input),
            ],
            botmod.AWAIT_EDIT_PHONE: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_edit_phone_input),
            ],
            botmod.AWAIT_RECEIPT: [
                CallbackQueryHandler(botmod.on_callback),
                MessageHandler(filters.PHOTO, botmod.on_receipt_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_unknown_text),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', botmod.cmd_cancel),
            CommandHandler('start', botmod.cmd_start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, botmod.on_unknown_text),
        ],
        allow_reentry=True,
        per_chat=True,
        per_user=True,
    )
    app.add_handler(conv)
    return app


def _start_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _get_or_create_app() -> tuple[Application, asyncio.AbstractEventLoop]:
    global _loop, _application
    with _lock:
        if _loop is None or not _loop.is_running():
            _loop = asyncio.new_event_loop()
            threading.Thread(target=_start_loop, args=(_loop,), daemon=True).start()
        if _application is None:
            _application = build_application()
            future = asyncio.run_coroutine_threadsafe(_application.initialize(), _loop)
            future.result(timeout=30)
    return _application, _loop


def reset_application():
    global _application
    with _lock:
        if _application is None:
            return
        try:
            future = asyncio.run_coroutine_threadsafe(_application.shutdown(), _loop)
            future.result(timeout=15)
        except Exception as exc:
            log.warning("[TelegramBot] reset_application shutdown error: %s", exc)
        finally:
            _application = None


def process_update_sync(update_data: dict):
    """Process a webhook update from a synchronous Flask request."""
    from services import telegram_bot as botmod

    if not botmod._get_token():
        return
    try:
        app, loop = _get_or_create_app()
        update = Update.de_json(update_data, app.bot)
        future = asyncio.run_coroutine_threadsafe(app.process_update(update), loop)
        future.result(timeout=25)
    except Exception as exc:
        log.error("[TelegramBot] process_update error: %s", exc)


async def _set_webhook_async(webhook_url: str) -> dict:
    from services import telegram_bot as botmod

    token = botmod._get_token()
    if not token:
        return {'ok': False, 'description': 'TELEGRAM_BOT_TOKEN not set'}
    async with Bot(token=token) as bot:
        result = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        info = await bot.get_webhook_info()
        return {
            'ok': result,
            'webhook_url': info.url,
            'pending_updates': info.pending_update_count,
        }


def set_webhook_sync(webhook_url: str) -> dict:
    return asyncio.run(_set_webhook_async(webhook_url))


async def _delete_webhook_async():
    from services import telegram_bot as botmod

    token = botmod._get_token()
    if not token:
        return False
    async with Bot(token=token) as bot:
        return await bot.delete_webhook(drop_pending_updates=True)


def delete_webhook_sync() -> bool:
    return asyncio.run(_delete_webhook_async())


async def _get_me_async():
    from services import telegram_bot as botmod

    token = botmod._get_token()
    if not token:
        return None
    async with Bot(token=token) as bot:
        return await bot.get_me()


def get_bot_info():
    try:
        return asyncio.run(_get_me_async())
    except Exception:
        return None