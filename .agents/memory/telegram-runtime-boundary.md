---
name: Telegram runtime boundary
description: Separation between Telegram business handlers and the long-lived application runtime.
---

Telegram handler/business logic remains importable from `services.telegram_bot`, while application construction, asyncio loop ownership, webhook processing, and bot metadata calls live in `services.telegram_runtime`. Compatibility imports preserve existing Flask callers.

**Why:** Keeping the event-loop lifecycle beside thousands of lines of bot business logic made changes risky and encouraged duplicate wiring.

**How to apply:** Add or change Telegram handlers in `telegram_bot.py`; change lifecycle/webhook behavior in `telegram_runtime.py`. Keep the compatibility exports stable unless all Flask imports are updated together.