---
name: Bot order persistence boundary
description: Durable constraint for saving orders from the Telegram background runtime.
---

Telegram background handlers must persist orders through a dedicated database connection and the exact PostgreSQL orders schema. Do not call Flask-context model helpers that assume request-scoped database state, and do not translate order fields by incompatible names.

**Why:** The bot's order flow runs outside Flask request context; the previous path used a helper expecting `shipping_fee` and `total` while supplying different keys, so final checkout failed after coupon entry.

**How to apply:** Keep bot order insertion, order-item insertion, stock updates, commit, rollback, and connection close within one explicit transaction. Preserve `Skip` as no coupon (`None`/zero discount).