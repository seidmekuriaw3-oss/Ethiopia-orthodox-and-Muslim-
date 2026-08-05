---
name: Telegram bot order flow fixes
description: Critical bugs fixed in the Telegram bot checkout/order flow and overall project audit findings.
---

## cart:checkout Dead Code Bug
`cart:checkout` callback was never reached because `elif data.startswith('cart:')` came FIRST in `on_callback`. 
**Fix:** Moved `cart:checkout`, `order:confirm`, `order:cancel`, `order:edit` BEFORE the generic `cart:` handler.

## Order Summary Keyboard
Added "✏️ Edit Cart" (`order:edit`) button so users can go back to cart without full cancel.
`order:confirm` is now its own row for clarity.

## Phone Validation
`_is_valid_phone()` added — accepts `09xxxxxxxx`, `+251xxxxxxxxx`, `251xxxxxxxxx`.
`on_phone_input` re-prompts on invalid phone instead of accepting anything.

## Address Validation
`on_address_input` rejects addresses shorter than 5 characters.

## Name Validation
`on_name_input` rejects names shorter than 2 characters.

## Confirm Order Flow
`_confirm_order` now:
- Guards against empty cart
- Clears `state['order']` as well as `state['cart']` after success
- Shows "Track My Order" + "Main Menu" keyboard (not just main menu)
- Track prompt text shown as hint

## Website Button on Main Menu
`_main_menu_keyboard` adds `🌐 Open Website` URL button as last row when `SITE_URL` is set.

## Admin Notification
`_notify_admin_new_order` now shows itemized list with prices + subtotal + shipping + grand total.

## File Duplication (Danger)
The file was corrupted to 4113 lines (4× duplicate). Root cause: repeated Edit tool calls on sections with unterminated strings caused appending rather than replacing.
**Fix:** Python script to reconstruct: Part A (1-2244) + Part B (3011-3062) + Part C (2246-3010).
**Rule:** If telegram_bot.py ever grows above ~2200 lines, it likely has duplicates — run the deduplication check.

## telegram_bot.py Structure (clean)
After rebuild: ~3063 lines, 0 duplicates. Order of key functions:
`on_name_input` → `_is_valid_phone` → `on_phone_input` → `on_address_input` → `on_coupon_input` → `on_track_input` → profile/wishlist/branch helpers → cmd_* → `build_application` → background event loop.
