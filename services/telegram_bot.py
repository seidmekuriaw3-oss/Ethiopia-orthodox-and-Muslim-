"""
SemiraFashionBot — Full-featured Telegram shopping bot
Supports Amharic (primary) and English.
Uses python-telegram-bot v20+ with a background asyncio loop for Flask compatibility.
"""

import os
import json
import logging
import asyncio
import threading
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, Bot
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

log = logging.getLogger(__name__)

# ───────────────────────── configuration ─────────────────────────
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '')
SITE_URL = os.environ.get('REPLIT_DEV_DOMAIN', '')
WHATSAPP = os.environ.get('WHATSAPP_NUMBER', '251987957957')
CURRENCY = 'ETB'
SHIPPING_COST = int(os.environ.get('SHIPPING_COST', 200))
FREE_SHIPPING = int(os.environ.get('FREE_SHIPPING_THRESHOLD', 5000))
PRODUCTS_PER_PAGE = 6

# ───────────────────────── conversation states ─────────────────────────
(AWAIT_SEARCH, AWAIT_NAME, AWAIT_PHONE, AWAIT_ADDRESS, AWAIT_TRACK) = range(5)

# ───────────────────────── in-memory user state ─────────────────────────
# { telegram_user_id: { 'lang': 'am', 'cart': {product_id: qty}, 'order': {} } }
_user_state: dict = {}

def _get_state(uid: int) -> dict:
    if uid not in _user_state:
        _user_state[uid] = {'lang': 'am', 'cart': {}, 'order': {}}
    return _user_state[uid]

# ───────────────────────── translations ─────────────────────────
T = {
    'welcome': {
        'am': ('👗 *ወደ ሰሚራ ፋሽን እንኳን ደህና መጡ!*\n\n'
               'የኢትዮጵያ ምርጥ የሴቶችና ህጻናት ፋሽን መደብር።\n'
               'ምርቶቻችንን ይፈልጉ፣ ይዘዙ፣ ይከታተሉ።'),
        'en': ('👗 *Welcome to Semira Fashion!*\n\n'
               'Ethiopia\'s premier women & children fashion store.\n'
               'Browse, order and track your purchases with ease.'),
    },
    'main_menu': {'am': '🏠 ዋና ምናሌ', 'en': '🏠 Main Menu'},
    'products':  {'am': '🛍️ ምርቶች',   'en': '🛍️ Products'},
    'categories':{'am': '🗂️ ምድቦች',   'en': '🗂️ Categories'},
    'new':       {'am': '🆕 አዲስ ምርቶች','en': '🆕 New Arrivals'},
    'featured':  {'am': '⭐ ተወዳጅ',    'en': '⭐ Featured'},
    'search':    {'am': '🔍 ፈልግ',     'en': '🔍 Search'},
    'cart':      {'am': '🛒 ቅርጫቴ',   'en': '🛒 My Cart'},
    'checkout':  {'am': '💳 ክፍያ',     'en': '💳 Checkout'},
    'track':     {'am': '📦 ትዕዛዝ ክትትል','en': '📦 Track Order'},
    'contact':   {'am': '📞 እውቂያ',    'en': '📞 Contact'},
    'language':  {'am': '🌐 ቋንቋ',     'en': '🌐 Language'},
    'back':      {'am': '◀️ ተመለስ',   'en': '◀️ Back'},
    'price':     {'am': 'ዋጋ',         'en': 'Price'},
    'stock':     {'am': 'ክምችት',       'en': 'Stock'},
    'add_cart':  {'am': '🛒 ወደ ቅርጫት ጨምር', 'en': '🛒 Add to Cart'},
    'remove':    {'am': '❌ አስወግድ',   'en': '❌ Remove'},
    'empty_cart':{'am': '🛒 ቅርጫቱ ባዶ ነው።', 'en': '🛒 Your cart is empty.'},
    'added':     {'am': '✅ ወደ ቅርጫት ተጨምሯል!', 'en': '✅ Added to cart!'},
    'removed':   {'am': '✅ ከቅርጫት ተወግዷል!', 'en': '✅ Removed from cart!'},
    'prev':      {'am': '◀ ቀዳሚ',     'en': '◀ Prev'},
    'next':      {'am': 'ቀጣይ ▶',    'en': 'Next ▶'},
    'no_products':{'am': '😔 ምርቶች አልተገኙም።', 'en': '😔 No products found.'},
    'no_cats':   {'am': '😔 ምድቦች አልተገኙም።', 'en': '😔 No categories found.'},
    'search_prompt':{'am': '🔍 የምርቱን ስም ይጻፉ...', 'en': '🔍 Type the product name...'},
    'name_prompt':  {'am': '📝 ሙሉ ስምዎን ያስገቡ:', 'en': '📝 Enter your full name:'},
    'phone_prompt': {'am': '📱 ስልክ ቁጥርዎን ያስገቡ:', 'en': '📱 Enter your phone number:'},
    'addr_prompt':  {'am': '🏠 አድራሻዎን ያስገቡ:', 'en': '🏠 Enter your delivery address:'},
    'track_prompt': {'am': '🔢 የትዕዛዝ ቁጥርዎን ያስገቡ:', 'en': '🔢 Enter your order number:'},
    'order_ok':     {'am': '✅ ትዕዛዝዎ ተቀብሏል!\n\n📲 ቡድናችን ብዙም ሳይቆይ ያነጋግርዎታል።',
                     'en': '✅ Order received!\n\n📲 Our team will contact you shortly.'},
    'order_err':    {'am': '❌ ትዕዛዝ ሲቀበል ስህተት ተፈጥሯል። እባክዎ ዳግም ሞክሩ።',
                     'en': '❌ Error placing order. Please try again.'},
    'track_not_found':{'am': '❌ ትዕዛዝ አልተገኘም። ቁጥሩን ያረጋግጡ።',
                       'en': '❌ Order not found. Check the number.'},
    'cancel':    {'am': '❌ ተሰርዟል', 'en': '❌ Cancelled'},
    'cancelled': {'am': '✅ ምርጫ ተሰርዟል። ከዋና ምናሌ ጀምሩ።',
                  'en': '✅ Cancelled. Start from the main menu.'},
    'subtotal':  {'am': 'ጠቅላላ', 'en': 'Subtotal'},
    'shipping':  {'am': 'ማጓጓዣ', 'en': 'Shipping'},
    'free':      {'am': 'ነጻ',   'en': 'Free'},
    'total':     {'am': 'ሁሉም ድምር', 'en': 'Grand Total'},
    'qty':       {'am': 'ቁጥር', 'en': 'Qty'},
    'out_stock': {'am': '❌ ክምችት አልቋል', 'en': '❌ Out of stock'},
    'desc':      {'am': 'መግለጫ', 'en': 'Description'},
    'size':      {'am': 'መጠን',  'en': 'Size'},
    'color':     {'am': 'ቀለም',  'en': 'Color'},
    'contact_msg':{'am': ('📞 *ሰሚራ ፋሽን*\n\n'
                          '📱 WhatsApp: +{wa}\n'
                          '🕐 ሰዓት: ሰኞ–ቅዳሜ 9:00–7:00\n\n'
                          '🌐 ድረ-ገጽ: https://{site}'),
                   'en': ('📞 *Semira Fashion*\n\n'
                          '📱 WhatsApp: +{wa}\n'
                          '🕐 Hours: Mon–Sat 9 AM–7 PM\n\n'
                          '🌐 Website: https://{site}')},
    'status_labels': {
        'am': {'Pending':'⏳ በመጠባበቅ', 'Confirmed':'✅ ተረጋግጧል',
               'Processing':'🔄 በሂደት ላይ', 'Shipped':'🚚 ተልኳል',
               'Delivered':'📬 ደርሷል', 'Cancelled':'❌ ተሰርዟል'},
        'en': {'Pending':'⏳ Pending', 'Confirmed':'✅ Confirmed',
               'Processing':'🔄 Processing', 'Shipped':'🚚 Shipped',
               'Delivered':'📬 Delivered', 'Cancelled':'❌ Cancelled'},
    },
    'increase': {'am': '➕', 'en': '➕'},
    'decrease': {'am': '➖', 'en': '➖'},
}

def _(uid: int, key: str, **kwargs) -> str:
    lang = _get_state(uid).get('lang', 'am')
    text = T.get(key, {}).get(lang, T.get(key, {}).get('am', key))
    return text.format(**kwargs) if kwargs else text


# ───────────────────────── helpers ─────────────────────────
def _product_image_url(product) -> str | None:
    """Return the first product image as a full URL, or None."""
    site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL
    if not site:
        return None
    try:
        # Prefer thumbnail; fall back to first entry in images JSON
        thumb = product.get('thumbnail') or ''
        imgs  = product.get('images', '[]') or '[]'
        if isinstance(imgs, str):
            try:
                imgs = json.loads(imgs)
            except (json.JSONDecodeError, ValueError):
                # plain path string stored directly — wrap it
                imgs = [imgs] if imgs else []
        path = thumb or (imgs[0] if imgs else '')
        if not path:
            return None
        if path.startswith(('http://', 'https://')):
            return path
        # Normalise: paths may be "uploads/...", "images/...", or bare filename
        if path.startswith('static/'):
            pass                                      # already correct
        elif path.startswith(('uploads/', 'images/')):
            path = f"static/{path}"                  # prepend static/ only
        else:
            path = f"static/uploads/products/{path}" # bare filename
        return f"https://{site}/{path}"
    except Exception:
        pass
    return None


def _fmt_price(price) -> str:
    try:
        return f"{float(price):,.2f} {CURRENCY}"
    except Exception:
        return f"{price} {CURRENCY}"


def _main_menu_keyboard(uid: int) -> InlineKeyboardMarkup:
    lang = _get_state(uid).get('lang', 'am')
    def t(k): return _(uid, k)
    rows = [
        [InlineKeyboardButton(t('products'),   callback_data='menu:products'),
         InlineKeyboardButton(t('categories'), callback_data='menu:categories')],
        [InlineKeyboardButton(t('new'),        callback_data='menu:new'),
         InlineKeyboardButton(t('featured'),   callback_data='menu:featured')],
        [InlineKeyboardButton(t('search'),     callback_data='menu:search'),
         InlineKeyboardButton(t('cart'),       callback_data='menu:cart')],
        [InlineKeyboardButton(t('track'),      callback_data='menu:track'),
         InlineKeyboardButton(t('contact'),    callback_data='menu:contact')],
        [InlineKeyboardButton(t('language'),   callback_data='menu:language')],
    ]
    return InlineKeyboardMarkup(rows)


def _back_home(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')
    ]])


# ── product navigation helpers ──────────────────────────────────────────────
def _prod_cb(pid: int, kind: str, cat_id: int, idx: int, page: int) -> str:
    """Compact callback_data for a product (always < 64 bytes)."""
    return f'prod:{pid}:{kind}:{cat_id}:{idx}:{page}'


def _parse_prod_cb(data: str):
    """Return (pid, kind, cat_id, idx, page) from a prod: callback string."""
    parts = data.split(':')
    pid    = int(parts[1])
    kind   = parts[2] if len(parts) > 2 else 'all'
    cat_id = int(parts[3]) if len(parts) > 3 else 0
    idx    = int(parts[4]) if len(parts) > 4 else -1
    page   = int(parts[5]) if len(parts) > 5 else 0
    return pid, kind, cat_id, idx, page


def _paginated_keyboard(uid: int, items, page: int, prefix: str,
                        extra_rows=None) -> InlineKeyboardMarkup:
    """Build a paginated inline keyboard for a list of (label, data) items."""
    start = page * PRODUCTS_PER_PAGE
    chunk = items[start:start + PRODUCTS_PER_PAGE]
    rows = []
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(chunk[i][0], callback_data=chunk[i][1])]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(chunk[i+1][0], callback_data=chunk[i+1][1]))
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(_(uid, 'prev'), callback_data=f'{prefix}:page:{page-1}'))
    if start + PRODUCTS_PER_PAGE < len(items):
        nav.append(InlineKeyboardButton(_(uid, 'next'), callback_data=f'{prefix}:page:{page+1}'))
    if nav:
        rows.append(nav)
    if extra_rows:
        rows.extend(extra_rows)
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    return InlineKeyboardMarkup(rows)


# ───────────────────────── DB helpers (called inside Flask app context) ─────────────────────────
def _db_get_categories():
    from database.models import Category
    return Category.get_all()

def _db_get_products_all(limit=60):
    from database.db import get_db
    db = get_db()
    return db.execute(
        "SELECT * FROM products WHERE is_active=1 ORDER BY id DESC LIMIT %s", (limit,)
    ).fetchall()

def _db_get_products_by_category(cid):
    from database.models import Product
    return Product.get_by_category(cid)

def _db_get_product(pid):
    from database.models import Product
    return Product.get_by_id(pid)

def _db_get_featured(limit=20):
    from database.models import Product
    return Product.get_featured(limit)

def _db_get_new(limit=20):
    from database.models import Product
    return Product.get_new(limit)

def _db_search(query):
    from database.models import Product
    return Product.search(query)

def _db_track_order(order_number):
    from database.models import Order
    return Order.get_by_order_number(order_number.strip())

def _db_get_order_items(order_id):
    from database.models import Order
    return Order.get_items(order_id)

def _db_place_order(cart: dict, user_data: dict) -> str | None:
    """Place an order, return order number or None on failure."""
    try:
        from database.models import Order, Product
        from database.db import commit_or_rollback
        import random

        items_data = []
        subtotal = 0.0
        for pid_str, qty in cart.items():
            p = Product.get_by_id(int(pid_str))
            if not p:
                continue
            price = float(p['price'])
            items_data.append({'product_id': int(pid_str), 'qty': qty,
                                'price': price, 'name': p['name']})
            subtotal += price * qty

        if not items_data:
            return None

        shipping = 0 if subtotal >= FREE_SHIPPING else SHIPPING_COST
        total = subtotal + shipping

        order_data = {
            'user_id': None,
            'customer_name': user_data.get('name', ''),
            'customer_phone': user_data.get('phone', ''),
            'customer_email': user_data.get('email', ''),
            'shipping_address': user_data.get('address', ''),
            'notes': f"Telegram Bot Order | @{user_data.get('username', 'N/A')}",
            'items': items_data,
            'subtotal': subtotal,
            'shipping_cost': shipping,
            'total_amount': total,
            'payment_method': 'Cash on Delivery',
            'status': 'Pending',
            'payment_status': 'Unpaid',
        }
        order = Order.create(order_data)
        if order:
            return order.get('order_number') or order.get('id')
        return None
    except Exception as e:
        log.error(f"[TelegramBot] place_order error: {e}")
        return None


# ───────────────────────── message builders ─────────────────────────
def _product_text(uid: int, p) -> str:
    lang = _get_state(uid).get('lang', 'am')
    name = p['name']
    price = _fmt_price(p['price'])
    compare = p.get('compare_price')
    stock = p.get('stock_quantity', 0)
    desc = (p.get('description') or '')[:200]
    
    lines = [f"*{name}*", f"💰 {_(uid,'price')}: {price}"]
    if compare and float(compare) > float(p['price']):
        lines.append(f"~~{_fmt_price(compare)}~~")
    if stock and int(stock) > 0:
        lines.append(f"📦 {_(uid,'stock')}: {stock}")
    else:
        lines.append(_(uid, 'out_stock'))
    if desc:
        lines.append(f"\n📝 {desc}")
    return '\n'.join(lines)


def _product_keyboard(uid: int, pid: int, in_cart: bool = False,
                      kind: str = 'all', cat_id: int = 0,
                      idx: int = -1, page: int = 0,
                      products: list = None) -> InlineKeyboardMarkup:
    lang = _get_state(uid).get('lang', 'am')
    site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL
    rows = []

    # ── Prev / Next navigation ──────────────────────────────────────────────
    products = products or []
    nav = []
    if idx > 0:
        pp = products[idx - 1]
        prev_page = (idx - 1) // PRODUCTS_PER_PAGE
        nav.append(InlineKeyboardButton(
            '◀️ ቀዳሚ' if lang == 'am' else '◀️ Prev',
            callback_data=_prod_cb(pp['id'], kind, cat_id, idx - 1, prev_page)))
    if 0 <= idx < len(products) - 1:
        np_ = products[idx + 1]
        next_page = (idx + 1) // PRODUCTS_PER_PAGE
        nav.append(InlineKeyboardButton(
            'ቀጣይ ▶️' if lang == 'am' else 'Next ▶️',
            callback_data=_prod_cb(np_['id'], kind, cat_id, idx + 1, next_page)))
    if nav:
        rows.append(nav)

    # ── Cart button ─────────────────────────────────────────────────────────
    cart_lbl = _(uid, 'remove') if in_cart else _(uid, 'add_cart')
    cart_cb  = f'cart:remove:{pid}' if in_cart else f'cart:add:{pid}'
    rows.append([InlineKeyboardButton(cart_lbl, callback_data=cart_cb)])

    # ── View on website ─────────────────────────────────────────────────────
    if site:
        view_lbl = '🌐 ድህረ-ገጽ ላይ እይ' if lang == 'am' else '🌐 View on Website'
        rows.append([InlineKeyboardButton(view_lbl, url=f'https://{site}/product/{pid}')])

    # ── Back to list + Cart ─────────────────────────────────────────────────
    back_lbl = '◀️ ዝርዝር ተመለስ' if lang == 'am' else '◀️ Back to List'
    rows.append([
        InlineKeyboardButton(back_lbl, callback_data=f'back_list:{kind}:{cat_id}:{page}'),
        InlineKeyboardButton('🛒 ' + _(uid, 'cart'), callback_data='menu:cart'),
    ])
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    return InlineKeyboardMarkup(rows)


def _cart_text(uid: int) -> str:
    state = _get_state(uid)
    cart = state.get('cart', {})
    if not cart:
        return _(uid, 'empty_cart')
    
    lines = [f"🛒 *{_(uid, 'cart')}*\n"]
    subtotal = 0.0
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if not p:
            continue
        price = float(p['price'])
        line_total = price * qty
        subtotal += line_total
        lines.append(f"• {p['name']} × {qty} = {_fmt_price(line_total)}")
    
    shipping = 0 if subtotal >= FREE_SHIPPING else SHIPPING_COST
    lines.append(f"\n{_(uid,'subtotal')}: {_fmt_price(subtotal)}")
    ship_label = _(uid, 'free') if shipping == 0 else _fmt_price(shipping)
    lines.append(f"{_(uid,'shipping')}: {ship_label}")
    lines.append(f"*{_(uid,'total')}: {_fmt_price(subtotal + shipping)}*")
    return '\n'.join(lines)


def _cart_keyboard(uid: int) -> InlineKeyboardMarkup:
    state = _get_state(uid)
    cart = state.get('cart', {})
    rows = []
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if not p:
            continue
        name = (p['name'][:18] + '…') if len(p['name']) > 18 else p['name']
        rows.append([
            InlineKeyboardButton(f"➖", callback_data=f'cart:dec:{pid_str}'),
            InlineKeyboardButton(f"{name} ({qty})", callback_data=f'prod:{pid_str}'),
            InlineKeyboardButton(f"➕", callback_data=f'cart:inc:{pid_str}'),
        ])
        rows.append([
            InlineKeyboardButton(_(uid, 'remove'), callback_data=f'cart:remove:{pid_str}'),
        ])
    if cart:
        rows.append([InlineKeyboardButton(_(uid, 'checkout'), callback_data='cart:checkout')])
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    return InlineKeyboardMarkup(rows)


def _order_summary_text(uid: int) -> str:
    state = _get_state(uid)
    order = state.get('order', {})
    cart = state.get('cart', {})
    
    lang = state.get('lang', 'am')
    items_lines = []
    subtotal = 0.0
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if p:
            price = float(p['price'])
            subtotal += price * qty
            items_lines.append(f"  • {p['name']} × {qty} — {_fmt_price(price * qty)}")
    
    shipping = 0 if subtotal >= FREE_SHIPPING else SHIPPING_COST
    total = subtotal + shipping
    ship_label = _(uid, 'free') if shipping == 0 else _fmt_price(shipping)
    
    lines = [
        f"📋 *{'የትዕዛዝ ማጠቃለያ' if lang=='am' else 'Order Summary'}*\n",
        f"👤 {'ስም' if lang=='am' else 'Name'}: {order.get('name','')}",
        f"📱 {'ስልክ' if lang=='am' else 'Phone'}: {order.get('phone','')}",
        f"🏠 {'አድራሻ' if lang=='am' else 'Address'}: {order.get('address','')}",
        f"\n{'ምርቶች' if lang=='am' else 'Items'}:",
        *items_lines,
        f"\n{_(uid,'subtotal')}: {_fmt_price(subtotal)}",
        f"{_(uid,'shipping')}: {ship_label}",
        f"*{_(uid,'total')}: {_fmt_price(total)}*",
    ]
    return '\n'.join(lines)


def _order_summary_keyboard(uid: int) -> InlineKeyboardMarkup:
    lang = _get_state(uid).get('lang', 'am')
    confirm = '✅ አረጋግጥ' if lang == 'am' else '✅ Confirm Order'
    cancel  = '❌ ሰርዝ'  if lang == 'am' else '❌ Cancel'
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(confirm, callback_data='order:confirm'),
         InlineKeyboardButton(cancel,  callback_data='order:cancel')],
    ])


# ───────────────────────── safe edit helper ─────────────────────────
async def _safe_edit_text(query, text: str, parse_mode=None, reply_markup=None):
    """
    Edit the current message as text.
    If the current message is a photo (cannot edit text on it), reply with a new
    text message and delete the old photo message instead.
    """
    try:
        await query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except TelegramError:
        try:
            await query.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
            try:
                await query.message.delete()
            except Exception:
                pass
        except Exception:
            pass


# ───────────────────────── handlers ─────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = _get_state(uid)
    # Store username for order notes
    state['username'] = update.effective_user.username or str(uid)
    text = _(uid, 'welcome')
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = _get_state(uid).get('lang', 'am')
    if lang == 'am':
        text = ('*ሰሚራ ፋሽን ቦት ምናሌ*\n\n'
                '/start — ዋና ምናሌ\n'
                '/products — ምርቶችን ይፈልጉ\n'
                '/cart — ቅርጫቴን ይመልከቱ\n'
                '/track — ትዕዛዝ ይከታተሉ\n'
                '/language — ቋንቋ ይቀይሩ\n'
                '/cancel — ወቅታዊ ምርጫ ሰርዝ')
    else:
        text = ('*Semira Fashion Bot Help*\n\n'
                '/start — Main menu\n'
                '/products — Browse products\n'
                '/cart — View my cart\n'
                '/track — Track an order\n'
                '/language — Change language\n'
                '/cancel — Cancel current action')
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_back_home(uid))
    return ConversationHandler.END


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(_(uid, 'cancelled'),
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def cmd_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await _show_products_page(update.message, uid, 0, 'all')
    return ConversationHandler.END


async def cmd_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(_cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_cart_keyboard(uid))
    return ConversationHandler.END


async def cmd_track(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(_(uid, 'track_prompt'),
                                    reply_markup=_back_home(uid))
    return AWAIT_TRACK


async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await _show_language_menu(update.message, uid)
    return ConversationHandler.END


# ── inline button dispatcher ──
async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    data = query.data

    # ── menu navigation ──
    if data == 'menu:home':
        await _safe_edit_text(query, _(uid, 'welcome'), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END

    elif data == 'menu:products':
        await _edit_products_page(query, uid, 0, 'all')

    elif data == 'menu:categories':
        await _edit_categories(query, uid)

    elif data == 'menu:new':
        await _edit_products_page(query, uid, 0, 'new')

    elif data == 'menu:featured':
        await _edit_products_page(query, uid, 0, 'featured')

    elif data == 'menu:cart':
        await _safe_edit_text(query, _cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_cart_keyboard(uid))

    elif data == 'menu:contact':
        site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL or 'semira.fashion'
        text = _(uid, 'contact_msg', wa=WHATSAPP, site=site)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP}'),
            InlineKeyboardButton('🌐 Website', url=f'https://{site}'),
        ], [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')]])
        await _safe_edit_text(query, text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

    elif data == 'menu:language':
        await _edit_language_menu(query, uid)

    elif data == 'menu:search':
        await _safe_edit_text(query, _(uid, 'search_prompt'),
                              reply_markup=_back_home(uid))
        ctx.user_data['awaiting'] = 'search'
        return AWAIT_SEARCH

    elif data == 'menu:track':
        await _safe_edit_text(query, _(uid, 'track_prompt'),
                              reply_markup=_back_home(uid))
        ctx.user_data['awaiting'] = 'track'
        return AWAIT_TRACK

    # ── language selection ──
    elif data.startswith('lang:'):
        lang = data.split(':')[1]
        _get_state(uid)['lang'] = lang
        await _safe_edit_text(query, _(uid, 'welcome'), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_main_menu_keyboard(uid))

    # ── category drill-down ──
    elif data.startswith('cat:'):
        parts = data.split(':')
        cid = int(parts[1])
        page = int(parts[3]) if len(parts) > 3 else 0
        await _edit_products_page(query, uid, page, 'cat', cat_id=cid)

    # ── product list page ──
    elif (data.startswith('all:page:') or data.startswith('products:page:') or
          data.startswith('new:page:') or data.startswith('featured:page:')):
        parts = data.split(':')
        raw_kind = parts[0]
        kind = 'all' if raw_kind == 'products' else raw_kind   # normalise legacy prefix
        page = int(parts[2])
        await _edit_products_page(query, uid, page, kind)

    # ── category list pagination ──
    elif data.startswith('catlist:page:'):
        page = int(data.split(':')[2])
        await _edit_categories(query, uid, page)

    # ── single product (with full nav context) ──
    elif data.startswith('prod:'):
        pid, kind, cat_id, idx, page = _parse_prod_cb(data)
        await _edit_product_detail(query, uid, pid,
                                   kind=kind, cat_id=cat_id, idx=idx, page=page)

    # ── back to product list ──
    elif data.startswith('back_list:'):
        parts = data.split(':')
        kind   = parts[1]
        cat_id = int(parts[2])
        page   = int(parts[3])
        await _edit_products_page(query, uid, page, kind,
                                  cat_id=cat_id if cat_id else None)

    # ── cart actions ──
    elif data.startswith('cart:'):
        await _handle_cart_action(query, uid, data, ctx)

    # ── order flow ──
    elif data == 'cart:checkout':
        cart = _get_state(uid).get('cart', {})
        if not cart:
            await _safe_edit_text(query, _(uid, 'empty_cart'),
                                  reply_markup=_back_home(uid))
            return ConversationHandler.END
        await _safe_edit_text(query, _(uid, 'name_prompt'),
                              reply_markup=_back_home(uid))
        return AWAIT_NAME

    elif data == 'order:confirm':
        return await _confirm_order(query, uid)

    elif data == 'order:cancel':
        await _safe_edit_text(query, _(uid, 'cancelled'),
                              reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END

    return ConversationHandler.END


# ── product list helpers ──
def _products_page_kb_and_text(uid: int, products: list, page: int,
                                kind: str, cat_id: int):
    """Return (text, keyboard, photo_url) for a product list page."""
    cid    = cat_id or 0
    prefix = f'{kind}:{cid}' if cid else kind
    lang   = _get_state(uid).get('lang', 'am')

    # Build items with full navigation context embedded in callback_data
    all_items = [
        (
            (p['name'][:26] + '…') if len(p['name']) > 26 else p['name'],
            _prod_cb(p['id'], kind, cid, i, i // PRODUCTS_PER_PAGE)
        )
        for i, p in enumerate(products)
    ]

    title = {'all': '🛍️', 'new': '🆕', 'featured': '⭐', 'cat': '🗂️'}.get(kind, '🛍️')
    label = _(uid, kind if kind in T else 'products')
    total = len(products)
    pages = (total + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    pg_info = f'({page+1}/{pages})' if pages > 1 else ''

    # First product on this page — identify it in the caption so the cover photo makes sense
    start = page * PRODUCTS_PER_PAGE
    page_products = products[start:start + PRODUCTS_PER_PAGE]
    first_p = page_products[0] if page_products else None
    photo_url = None
    cover_name = ''
    for pp in page_products:
        url = _product_image_url(pp)
        if url:
            photo_url = url
            cover_name = pp.get('name', '')
            break

    if lang == 'am':
        hint = 'ምርቱን ለማየት ከታች ያለውን አዝራር ይጫኑ 👇'
    else:
        hint = 'Tap a product button below to view details 👇'

    cover_line = f'📸 _{cover_name}_\n' if cover_name else ''
    text = f"{title} *{label}* {pg_info}\n{cover_line}_{total} {'ምርቶች' if lang=='am' else 'products'}_\n{hint}"

    kb = _paginated_keyboard(uid, all_items, page, prefix)

    return text, kb, photo_url


async def _edit_products_page(query, uid: int, page: int, kind: str, cat_id=None):
    products = _get_products_for_kind(kind, cat_id)
    if not products:
        await _safe_edit_text(query, _(uid, 'no_products'), reply_markup=_back_home(uid))
        return
    text, kb, photo_url = _products_page_kb_and_text(uid, products, page, kind, cat_id or 0)
    try:
        if photo_url:
            await query.message.reply_photo(photo=photo_url, caption=text,
                                            parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
            try:
                await query.message.delete()
            except Exception:
                pass
        else:
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    except TelegramError:
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        except Exception:
            pass


async def _show_products_page(msg, uid: int, page: int, kind: str, cat_id=None):
    products = _get_products_for_kind(kind, cat_id)
    if not products:
        await msg.reply_text(_(uid, 'no_products'), reply_markup=_back_home(uid))
        return
    text, kb, photo_url = _products_page_kb_and_text(uid, products, page, kind, cat_id or 0)
    try:
        if photo_url:
            await msg.reply_photo(photo=photo_url, caption=text,
                                  parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        else:
            await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    except TelegramError:
        await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


def _get_products_for_kind(kind: str, cat_id=None):
    if kind == 'featured':
        return _db_get_featured()
    elif kind == 'new':
        return _db_get_new()
    elif kind == 'cat' and cat_id:
        return _db_get_products_by_category(cat_id)
    else:
        return _db_get_products_all()


async def _edit_product_detail(query, uid: int, pid: int,
                               kind: str = 'all', cat_id: int = 0,
                               idx: int = -1, page: int = 0):
    p = _db_get_product(pid)
    if not p:
        await _safe_edit_text(query, _(uid, 'no_products'), reply_markup=_back_home(uid))
        return
    products = _get_products_for_kind(kind, cat_id or None)
    # Resolve idx if unknown
    if idx < 0:
        for i, prod in enumerate(products):
            if prod['id'] == pid:
                idx = i
                break
    # Save nav context so cart actions can restore it
    _get_state(uid)['last_prod'] = {'kind': kind, 'cat_id': cat_id, 'idx': idx, 'page': page}
    cart = _get_state(uid).get('cart', {})
    in_cart = str(pid) in cart
    text = _product_text(uid, p)
    kb = _product_keyboard(uid, pid, in_cart,
                           kind=kind, cat_id=cat_id,
                           idx=idx, page=page, products=products)
    img_url = _product_image_url(p)
    try:
        if img_url:
            await query.message.reply_photo(photo=img_url, caption=text,
                                            parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
            try:
                await query.message.delete()
            except Exception:
                pass
        else:
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    except TelegramError as e:
        log.warning(f"[ProductDetail] TelegramError: {e}")
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        except Exception:
            pass


async def _edit_categories(query, uid: int, page: int = 0):
    cats = _db_get_categories()
    if not cats:
        await _safe_edit_text(query, _(uid, 'no_cats'), reply_markup=_back_home(uid))
        return
    items = [(c['name'], f'cat:{c["id"]}:page:0') for c in cats]
    kb = _paginated_keyboard(uid, items, page, 'catlist')
    await _safe_edit_text(query, _(uid, 'categories'),
                          parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def _show_language_menu(msg, uid: int):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🇪🇹 አማርኛ', callback_data='lang:am'),
         InlineKeyboardButton('🇬🇧 English', callback_data='lang:en')],
        [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
    ])
    await msg.reply_text('🌐 Language / ቋንቋ', reply_markup=kb)


async def _edit_language_menu(query, uid: int):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🇪🇹 አማርኛ', callback_data='lang:am'),
         InlineKeyboardButton('🇬🇧 English', callback_data='lang:en')],
        [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
    ])
    await _safe_edit_text(query, '🌐 Language / ቋንቋ', reply_markup=kb)


async def _handle_cart_action(query, uid: int, data: str, ctx):
    parts = data.split(':')
    action = parts[1]
    pid_str = parts[2] if len(parts) > 2 else ''
    cart = _get_state(uid).setdefault('cart', {})

    if action == 'add' and pid_str:
        p = _db_get_product(int(pid_str))
        stock = int(p.get('stock_quantity', 0)) if p else 0
        current_qty = cart.get(pid_str, 0)
        if not p or stock == 0:
            await query.answer(_(uid, 'out_stock'), show_alert=True)
            return
        if current_qty >= stock:
            await query.answer(_(uid, 'out_stock'), show_alert=True)
            return
        cart[pid_str] = current_qty + 1
        await query.answer(_(uid, 'added'))
        # Refresh product view — restore nav context from user state
        nav = _get_state(uid).get('last_prod', {})
        await _edit_product_detail(query, uid, int(pid_str),
                                   kind=nav.get('kind', 'all'),
                                   cat_id=nav.get('cat_id', 0),
                                   idx=nav.get('idx', -1),
                                   page=nav.get('page', 0))

    elif action == 'remove' and pid_str:
        cart.pop(pid_str, None)
        await query.answer(_(uid, 'removed'))
        await _safe_edit_text(query, _cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_cart_keyboard(uid))

    elif action == 'inc' and pid_str:
        p = _db_get_product(int(pid_str))
        stock = int(p.get('stock_quantity', 0)) if p else 0
        if cart.get(pid_str, 0) >= stock:
            await query.answer(_(uid, 'out_stock'), show_alert=True)
        else:
            cart[pid_str] = cart.get(pid_str, 0) + 1
        await _safe_edit_text(query, _cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_cart_keyboard(uid))

    elif action == 'dec' and pid_str:
        qty = cart.get(pid_str, 0) - 1
        if qty <= 0:
            cart.pop(pid_str, None)
        else:
            cart[pid_str] = qty
        await _safe_edit_text(query, _cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_cart_keyboard(uid))

    elif action == 'checkout':
        # This branch is handled in on_callback directly to return proper state
        pass


# ── conversation input handlers ──
async def on_search_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    query_text = update.message.text.strip()
    results = _db_search(query_text)
    if not results:
        await update.message.reply_text(_(uid, 'no_products'), reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END
    lang = _get_state(uid).get('lang', 'am')
    # Embed full context in search results so Prev/Next works
    items = [
        (
            (p['name'][:26] + '…') if len(p['name']) > 26 else p['name'],
            _prod_cb(p['id'], 'all', 0, i, 0)
        )
        for i, p in enumerate(results)
    ]
    kb = _paginated_keyboard(uid, items, 0, 'search_res')
    text = f"🔍 {'ውጤቶች' if lang=='am' else 'Results'} ({len(results)})"
    # Show first result's photo alongside the list
    photo_url = _product_image_url(results[0]) if results else None
    try:
        if photo_url:
            await update.message.reply_photo(photo=photo_url, caption=text,
                                             parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    except TelegramError:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    return ConversationHandler.END


async def on_name_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.message.text.strip()
    _get_state(uid).setdefault('order', {})['name'] = name
    await update.message.reply_text(_(uid, 'phone_prompt'))
    return AWAIT_PHONE


async def on_phone_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    phone = update.message.text.strip()
    _get_state(uid).setdefault('order', {})['phone'] = phone
    await update.message.reply_text(_(uid, 'addr_prompt'))
    return AWAIT_ADDRESS


async def on_address_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    address = update.message.text.strip()
    state = _get_state(uid)
    state.setdefault('order', {})['address'] = address
    state['order']['username'] = state.get('username', str(uid))
    # Show summary
    summary = _order_summary_text(uid)
    await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_order_summary_keyboard(uid))
    return ConversationHandler.END  # confirmation via callback


async def on_track_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    order_number = update.message.text.strip()
    order = _db_track_order(order_number)
    if not order:
        await update.message.reply_text(_(uid, 'track_not_found'),
                                        reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END

    lang = _get_state(uid).get('lang', 'am')
    status_raw = order.get('status', 'Pending')
    status_label = T['status_labels'][lang].get(status_raw, status_raw)
    items = _db_get_order_items(order['id'])
    items_lines = [f"  • {it.get('product_name', it.get('name','?'))} × {it.get('quantity',1)}"
                   for it in (items or [])]
    
    created = order.get('created_at', '')
    if created and hasattr(created, 'strftime'):
        created = created.strftime('%Y-%m-%d %H:%M')

    lines = [
        f"📦 *{'ትዕዛዝ ዝርዝር' if lang=='am' else 'Order Details'}*\n",
        f"🔢 {'ቁጥር' if lang=='am' else 'Number'}: `{order.get('order_number','')}`",
        f"📊 {'ሁኔታ' if lang=='am' else 'Status'}: {status_label}",
        f"💰 {'ጠቅላላ' if lang=='am' else 'Total'}: {_fmt_price(order.get('total_amount',0))}",
        f"🕐 {'ቀን' if lang=='am' else 'Date'}: {created}",
    ]
    if items_lines:
        lines.append(f"\n{'ምርቶች' if lang=='am' else 'Items'}:")
        lines.extend(items_lines)

    await update.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def _confirm_order(query, uid: int):
    state = _get_state(uid)
    cart = state.get('cart', {})
    order_data = state.get('order', {})
    order_data['username'] = state.get('username', str(uid))

    order_number = _db_place_order(cart, order_data)
    if order_number:
        state['cart'] = {}  # clear cart
        lang = state.get('lang', 'am')
        text = (_(uid, 'order_ok') +
                f"\n\n🔢 {'ትዕዛዝ ቁጥር' if lang=='am' else 'Order #'}: `{order_number}`")
        await _safe_edit_text(query, text, parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_main_menu_keyboard(uid))
        # Notify admin
        await _notify_admin_new_order(query, uid, order_number, order_data, cart)
    else:
        await _safe_edit_text(query, _(uid, 'order_err'),
                              reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def _notify_admin_new_order(query, uid: int, order_number, order_data: dict, cart: dict):
    if not ADMIN_CHAT_ID:
        return
    try:
        bot = query.get_bot()
        lines = [
            f"🛍️ *New Telegram Order!*",
            f"📦 Order: `{order_number}`",
            f"👤 {order_data.get('name','')}",
            f"📱 {order_data.get('phone','')}",
            f"🏠 {order_data.get('address','')}",
            f"📲 @{order_data.get('username',uid)}",
        ]
        for pid_str, qty in cart.items():
            p = _db_get_product(int(pid_str))
            if p:
                lines.append(f"  • {p['name']} × {qty}")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='\n'.join(lines),
                               parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.warning(f"[TelegramBot] admin notify failed: {e}")


# ── fallback for unexpected text ──
async def on_unknown_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = _get_state(uid).get('lang', 'am')
    hint = '❓ ያልታወቀ ትዕዛዝ። /start ይጠቀሙ።' if lang == 'am' else '❓ Unknown command. Use /start.'
    await update.message.reply_text(hint, reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


# ───────────────────────── Application builder ─────────────────────────
def build_application() -> Application:
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', cmd_start),
            CommandHandler('help',  cmd_help),
            CommandHandler('products', cmd_products),
            CommandHandler('cart',  cmd_cart),
            CommandHandler('track', cmd_track),
            CommandHandler('language', cmd_language),
            CommandHandler('cancel', cmd_cancel),
            CallbackQueryHandler(on_callback),
        ],
        states={
            AWAIT_SEARCH: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_search_input),
            ],
            AWAIT_NAME: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_name_input),
            ],
            AWAIT_PHONE: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_phone_input),
            ],
            AWAIT_ADDRESS: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_address_input),
            ],
            AWAIT_TRACK: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_track_input),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cmd_cancel),
            CommandHandler('start',  cmd_start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, on_unknown_text),
        ],
        allow_reentry=True,
        per_chat=True,
        per_user=True,
    )

    app.add_handler(conv)
    return app


# ───────────────────────── background event loop ─────────────────────────
_loop: asyncio.AbstractEventLoop | None = None
_application: Application | None = None
_lock = threading.Lock()


def _start_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _get_or_create_app() -> tuple[Application, asyncio.AbstractEventLoop]:
    global _loop, _application
    with _lock:
        if _loop is None or not _loop.is_running():
            _loop = asyncio.new_event_loop()
            t = threading.Thread(target=_start_loop, args=(_loop,), daemon=True)
            t.start()
        if _application is None:
            _application = build_application()
            future = asyncio.run_coroutine_threadsafe(_application.initialize(), _loop)
            future.result(timeout=30)
    return _application, _loop


def process_update_sync(update_data: dict):
    """Called from the Flask webhook route — processes one Telegram update."""
    if not TOKEN:
        return
    try:
        app, loop = _get_or_create_app()
        update = Update.de_json(update_data, app.bot)
        future = asyncio.run_coroutine_threadsafe(app.process_update(update), loop)
        future.result(timeout=25)
    except Exception as e:
        log.error(f"[TelegramBot] process_update error: {e}")


async def _set_webhook_async(webhook_url: str) -> dict:
    if not TOKEN:
        return {'ok': False, 'description': 'TELEGRAM_BOT_TOKEN not set'}
    bot = Bot(token=TOKEN)
    async with bot:
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
    if not TOKEN:
        return False
    bot = Bot(token=TOKEN)
    async with bot:
        return await bot.delete_webhook(drop_pending_updates=True)


def delete_webhook_sync() -> bool:
    return asyncio.run(_delete_webhook_async())


async def _get_me_async():
    if not TOKEN:
        return None
    bot = Bot(token=TOKEN)
    async with bot:
        return await bot.get_me()


def get_bot_info():
    try:
        return asyncio.run(_get_me_async())
    except Exception:
        return None
