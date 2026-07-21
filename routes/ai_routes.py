"""
SEMIRA AI Agent — v3.0  (ጠንካራ፣ ሰራተኛ፣ ጎበዝ)
Powered by Groq llama-3.3-70b-versatile with comprehensive smart fallback.
Improvements: richer persona, cart context, discount badges, better history,
more Amharic keywords, model fallback, bulletproof error handling.
"""
import os
import re
import time
import logging
from flask import Blueprint, request, jsonify, session
from database.db import get_db
from routes.shared import WHATSAPP_NUMBER, FREE_SHIPPING_THRESHOLD, SHIPPING_COST, USER_DISCOUNT_RATE
from extensions import limiter

try:
    from groq import Groq as _GroqClient
    _GROQ_AVAILABLE = True
except ImportError:
    _GroqClient = None
    _GROQ_AVAILABLE = False

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

# ── Cache ────────────────────────────────────────────────────────────────────
_cache: dict = {}
_CACHE_TTL_SHORT = 120   # 2 min  — per-query product results
_CACHE_TTL_LONG  = 600   # 10 min — popular/category lists


def _cget(key: str):
    e = _cache.get(key)
    return e['v'] if e and (time.time() - e['t']) < e['ttl'] else None


def _cset(key: str, val, ttl: int = _CACHE_TTL_SHORT):
    _cache[key] = {'v': val, 't': time.time(), 'ttl': ttl}


# ── Amharic / English keyword → category/field mapping ───────────────────────
AMHARIC_CATEGORY_MAP = {
    # Dresses
    'ቀሚስ': 1, 'ቀሚሶች': 1, 'habesha': 1, 'ሀበሻ': 1, 'ሃበሻ': 1,
    'dress': 1, 'gown': 1, 'ምሽት ቀሚስ': 1, 'ጀለቢያ': 1, 'ሀበሻ ቀሚስ': 1,
    'habesha kemis': 1, 'ሃበሻ ቀሚስ': 1, 'kemis': 1,
    # Tops & Shirts
    'ሸሚዝ': 2, 'ብሎዝ': 2, 'ቲሸርት': 2, 'ቶፕ': 2,
    'shirt': 2, 'blouse': 2, 'top': 2, 't-shirt': 2, 'tshirt': 2,
    # Trousers & Shorts
    'ሱሪ': 3, 'ቁምጣ': 3, 'trouser': 3, 'pant': 3, 'short': 3,
    'jean': 3, 'denim': 3, 'chino': 3, 'legging': 3, 'ሌጊንስ': 3,
    # Jackets & Knitwear
    'ጃኬት': 4, 'ካርዲጋን': 4, 'ሹራብ': 4, 'jacket': 4, 'coat': 4,
    'cardigan': 4, 'knitwear': 4, 'sweater': 4, 'hoodie': 4,
    # Underwear & Nightwear
    'ፒጃማ': 5, 'ናይትዌር': 5, 'pajama': 5, 'nightwear': 5, 'underwear': 5, 'bra': 5,
    # Baby & Kids
    'ሕፃን': 6, 'ህፃን': 6, 'ልጅ': 6, 'baby': 6, 'kid': 6, 'child': 6,
    'romper': 6, 'ሮምፐር': 6, 'ህፃናት': 6, 'ሕፃናት': 6, 'ለልጆች': 6,
    # Activewear
    'ስፖርት': 7, 'ጂም': 7, 'sport': 7, 'gym': 7,
    'activewear': 7, 'workout': 7,
    # Traditional
    'ባህላዊ': 8, 'ነጠላ': 8, 'ጋቢ': 8, 'ኩታ': 8, 'ጥልፍ': 8,
    'netela': 8, 'gabi': 8, 'kuta': 8, 'traditional': 8, 'Ethiopian': 8,
    'ባህል': 8, 'ልብስ': 8,
}

AMHARIC_PRICE_WORDS = [
    'ዋጋ', 'ብር', 'etb', 'price', 'cost', 'ዋጋው', 'ምን ያህል', 'ስንት ብር',
    'cheap', 'affordable', 'ርካሽ', 'expensive', 'ውድ', 'ስንት ነው', 'ስንት ይዋጣል',
    'ዋጋ ስንት', 'how much', 'ምን ያህል ነው',
]

AMHARIC_ORDER_WORDS = [
    'ትዕዛዝ', 'ትዕዛዜ', 'order', 'ደረሰ', 'arrived', 'track',
    'ደረሰኝ', 'ተላከ', 'shipped', 'where is', 'order number', 'ትዕዛዝ ቁጥር',
    'ትዕዛዞቼ', 'my order', 'orders', 'ዘዝኩ', 'አዘዝኩ',
]

AMHARIC_SHIPPING_WORDS = [
    'ማጓጓዝ', 'ማድረስ', 'shipping', 'delivery', 'deliver', 'አድርስ',
    'free shipping', 'ነጻ ማጓጓዝ', 'ዋጋ ማጓጓዝ', 'ዲሊቨሪ', 'ምን ያህል ቀን',
    'how long', 'how many days', 'ስንት ቀን',
]

AMHARIC_RETURN_WORDS = [
    'መመለስ', 'ቅሬታ', 'refund', 'return', 'exchange', 'ልቀይር',
    'አልወደድኩም', 'ልቀይረው', 'ይቀየር', 'wrong', 'damaged', 'ተሳሳተ', 'ቀይር',
]

AMHARIC_SIZE_WORDS = [
    'ሳይዝ', 'መጠን', 'size', 'fit', 'large', 'small', 'medium',
    'xl', 'xxl', 'xs', 'ትልቅ', 'ትንሽ', 'ምን ሳይዝ', 'ሳይዝ ምን', 'what size',
    'size guide', 'sizing',
]

AMHARIC_GREETING_WORDS = [
    'ሰላም', 'selam', 'hello', 'hi', 'hey', 'good morning', 'good afternoon',
    'مرحبا', 'السلام', 'ጤና', 'እንደምን', 'what\'s up', 'wassup',
]

AMHARIC_PAYMENT_WORDS = [
    'ክፍያ', 'payment', 'pay', 'ከፍያ', 'cash', 'ካርድ', 'card',
    'telebirr', 'ቴሌብር', 'cbe', 'bank', 'ባንክ', 'እንዴት ይከፈላል', 'how to pay',
    'transfer', 'birr', 'online payment',
]

AMHARIC_CONTACT_WORDS = [
    'whatsapp', 'ስልክ', 'phone', 'call', 'contact', 'ደውል',
    'አድራሻ', 'address', 'location', 'ቦታ', 'ሱቅ', 'store',
    'ደሴ', 'dessie', 'wollo', 'ወሎ', 'ኩታቤር', 'kutaber', 'branch',
    'ቅርንጫፍ', 'ቅርንጫፎቻችን',
]

AMHARIC_DISCOUNT_WORDS = [
    'ቅናሽ', 'discount', 'sale', 'offer', 'promo', 'ልዩ', 'special',
    'ቀናሽ', 'reduced', 'percentage', 'percent', 'ፐርሰንት', 'off',
]

AMHARIC_CART_WORDS = [
    'ቅርጫት', 'cart', 'basket', 'bag', 'ቦርሳ', 'ያስቀመጥኩት', 'what\'s in my cart',
    'my cart', 'ካርት', 'shopping cart',
]

AMHARIC_WISHLIST_WORDS = [
    'wishlist', 'ምኞቴ', 'ወደዱ', 'favorite', 'ፈቀቅ', 'liked', 'saved',
]

# ── Order status labels ──────────────────────────────────────────────────────
STATUS_LABELS = {
    'pending':    {'am': '⏳ በመጠባበቅ ላይ',  'en': '⏳ Pending',    'ar': '⏳ قيد الانتظار'},
    'confirmed':  {'am': '✅ ተረጋግጧል',      'en': '✅ Confirmed',  'ar': '✅ مؤكد'},
    'processing': {'am': '🔧 በሂደት ላይ',     'en': '🔧 Processing', 'ar': '🔧 قيد المعالجة'},
    'shipped':    {'am': '🚚 ተላከ',          'en': '🚚 Shipped',    'ar': '🚚 تم الشحن'},
    'delivered':  {'am': '📦 ደረሰ',          'en': '📦 Delivered',  'ar': '📦 تم التسليم'},
    'cancelled':  {'am': '❌ ተሰርዟል',        'en': '❌ Cancelled',  'ar': '❌ ملغى'},
}

PAYMENT_LABELS = {
    'pending':  {'am': '⏳ ያልተከፈለ',  'en': '⏳ Unpaid',    'ar': '⏳ غير مدفوع'},
    'paid':     {'am': '✅ ተከፍሏል',    'en': '✅ Paid',      'ar': '✅ مدفوع'},
    'cod':      {'am': '💵 በደረሰ ጊዜ', 'en': '💵 Cash on Delivery', 'ar': '💵 الدفع عند الاستلام'},
    'refunded': {'am': '↩️ ተመልሷል',   'en': '↩️ Refunded',  'ar': '↩️ مسترد'},
}

# ── System prompt ─────────────────────────────────────────────────────────────
STORE_SYSTEM_PROMPT = """You are **SEMIRA** — the warm, knowledgeable AI shopping assistant for **SEMIRA FASHION**, Ethiopia's premier women's and children's clothing store. You are helpful, friendly, and deeply knowledgeable about Ethiopian fashion.

**Language Rule:** Always respond in the exact language the customer writes in. Amharic → Amharic, English → English, Arabic → Arabic. Never switch language unless the customer does first.

**Store Info:**
- Location: ወሎ፣ ደሴ፣ ኩታቤር — Wollo, Dessie, Kutaber, Ethiopia
- WhatsApp: {whatsapp} (wa.me/{whatsapp})
- Hours: Monday–Saturday 8AM–8PM EAT
- Payment: Cash on Delivery (COD) — pay when item arrives. No upfront payment needed.
- Shipping: FREE on orders ≥ {free_ship} ETB | {ship_cost} ETB flat fee otherwise | 2–5 business days
- Returns: 7 days, unused items with original tags | Contact WhatsApp for return instructions
- Discount: Logged-in customers get {discount_pct}% off every order automatically
- Sizes — Women: XS, S, M, L, XL, XXL, 3XL | Kids: newborn–14 years | Traditional: custom sizing available

**Products in database ({product_count} shown):**
{products}

**Customer Cart:**
{cart}

**Customer Orders:**
{orders}

**STRICT RULES — never break these:**
1. Only quote prices and products from the PRODUCTS list above. Never invent or guess prices.
2. If Orders shows "⚠️ not logged in" → tell customer to log in at /login. Never guess order status.
3. If Cart shows "empty" or "not logged in" → say cart is empty or ask them to log in.
4. If you don't know something → say "WhatsApp ያግኙን: wa.me/{whatsapp}" — never make up answers.
5. Always include product links (/products/ID) when mentioning specific products.
6. Keep responses concise and warm. Use at most 3 emojis per message.
7. For Amharic: use ኢትዮጵያዊ warmth — address customer as "እርስዎ" or "ደንበኛ"."""


def _extract_price_range(msg: str):
    """Extract min/max price hints from user message."""
    msg_clean = msg.lower().replace(',', '')
    under   = re.search(r'(?:under|below|ከ|less than|አነስ|ያነሰ|ያነሱ|ባነሰ)\s*(\d+)', msg_clean)
    over    = re.search(r'(?:above|over|ከ|more than|በላይ|ከ)\s*(\d+)\s*(?:በላይ|ብር)?', msg_clean)
    between = re.search(r'between\s*(\d+)\s*and\s*(\d+)', msg_clean)
    plain   = re.search(r'(\d{3,})', msg_clean)

    if between:
        return int(between.group(1)), int(between.group(2))
    if under:
        return 0, int(under.group(1))
    if over:
        return int(over.group(1)), 999999
    if plain:
        n = int(plain.group(1))
        if n >= 50:
            return 0, n
    return None, None


def _detect_category(msg: str) -> int | None:
    """Return category_id if message matches a known category keyword."""
    msg_l = msg.lower()
    for kw, cat_id in AMHARIC_CATEGORY_MAP.items():
        if kw in msg_l:
            return cat_id
    return None


def get_product_context(user_message: str, lang: str = 'am') -> tuple[str, int]:
    """
    Return (formatted_product_string, product_count).
    Searches by keyword + category + price range. Falls back to featured/popular items.
    """
    cache_key = f"prod:{lang}:{user_message[:80]}"
    cached = _cget(cache_key)
    if cached:
        return cached

    try:
        db = get_db()
        cursor = db.cursor()

        price_min, price_max = _extract_price_range(user_message)
        cat_id = _detect_category(user_message)
        search_term = f"%{user_message[:100]}%"

        if lang == 'ar':
            name_col = 'p.name_ar'
            desc_col = 'p.description_ar'
            cat_col  = 'c.name_ar'
        elif lang == 'en':
            name_col = 'p.name_en'
            desc_col = 'p.description_en'
            cat_col  = 'c.name'
        else:
            name_col = 'p.name_am'
            desc_col = 'p.description_am'
            cat_col  = 'c.name_am'

        base_conditions = "p.is_active = 1"
        params = []

        if cat_id:
            base_conditions += " AND p.category_id = %s"
            params.append(cat_id)

        if price_min is not None and price_max is not None and price_max < 999999:
            base_conditions += " AND p.price BETWEEN %s AND %s"
            params.extend([price_min, price_max])
        elif price_min is not None and price_min > 0:
            base_conditions += " AND p.price >= %s"
            params.append(price_min)
        elif price_max is not None and price_max < 999999:
            base_conditions += " AND p.price <= %s"
            params.append(price_max)

        kw_params = params + [search_term] * 7
        cursor.execute(f"""
            SELECT p.id, p.name_am, p.name_en, p.name_ar, p.price, p.compare_price,
                   p.stock_quantity, p.is_featured, p.is_new, p.material, p.color,
                   p.sizes, p.gender, {cat_col} as cat_name,
                   LEFT(COALESCE({desc_col}, p.description_am, p.description), 100) as desc_snippet
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE {base_conditions}
              AND (p.name_am ILIKE %s OR p.name_en ILIKE %s OR p.name_ar ILIKE %s
                   OR p.description_am ILIKE %s OR p.description_en ILIKE %s
                   OR c.name_am ILIKE %s OR p.material ILIKE %s)
            ORDER BY p.is_featured DESC, p.is_new DESC, p.sales_count DESC
            LIMIT 6
        """, kw_params)
        keyword_products = cursor.fetchall()

        # Popular products fallback (cached longer)
        pop_cache_key = f"pop:{lang}"
        popular = _cget(pop_cache_key)
        if popular is None:
            cursor.execute(f"""
                SELECT p.id, p.name_am, p.name_en, p.name_ar, p.price, p.compare_price,
                       p.stock_quantity, p.is_featured, p.is_new, p.sizes,
                       {cat_col} as cat_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
                ORDER BY p.is_featured DESC, p.is_new DESC, p.sales_count DESC
                LIMIT 6
            """)
            popular = cursor.fetchall()
            _cset(pop_cache_key, popular, ttl=_CACHE_TTL_LONG)

        # Merge, deduplicate — cap at 8 total
        seen_ids = set()
        all_products = []
        for p in list(keyword_products) + list(popular):
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                all_products.append(p)
            if len(all_products) >= 8:
                break

        if not all_products:
            result = "No products found in database."
            _cset(cache_key, (result, 0))
            return result, 0

        lines = []
        for p in all_products:
            if lang == 'am':
                name = p['name_am'] or p['name_en'] or 'Unknown'
            elif lang == 'ar':
                name = p['name_ar'] or p['name_en'] or 'Unknown'
            else:
                name = p['name_en'] or p['name_am'] or 'Unknown'

            price   = float(p['price'])
            compare = float(p['compare_price']) if p.get('compare_price') else None
            stock   = int(p['stock_quantity'] or 0)
            avail   = '✅ In Stock' if stock > 0 else '❌ Out of Stock'
            sizes   = p.get('sizes') or ''
            badges  = []
            if p.get('is_featured'): badges.append('⭐Featured')
            if p.get('is_new'):      badges.append('🆕New')

            line = f"• {name}: {price:,.0f} ETB"
            if compare and compare > price:
                pct = int((compare - price) / compare * 100)
                line += f" ~~{compare:,.0f}~~ ({pct}% off)"
            line += f" [{avail}]"
            if badges:  line += f" {' '.join(badges)}"
            if sizes:   line += f" | Sizes: {sizes}"
            line += f" → /products/{p['id']}"
            lines.append(line)

        result = "\n".join(lines)
        count = len(all_products)
        _cset(cache_key, (result, count), ttl=_CACHE_TTL_SHORT)
        return result, count

    except Exception as e:
        logger.error(f"AI product context error: {e}")
        return "Ethiopian women's and children's fashion available at /products", 0


def get_cart_context(user_id, lang: str = 'am') -> str:
    """Return a formatted summary of the logged-in user's current cart."""
    if not user_id:
        return {
            'am': "ወደ መለያ አልገቡም — cart ለማየት /login ይግቡ።",
            'en': "Not logged in — log in at /login to view your cart.",
            'ar': "غير مسجل الدخول — سجل الدخول على /login لعرض السلة.",
        }.get(lang, "Not logged in.")

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT ci.quantity, p.price, p.compare_price,
                   COALESCE(p.name_am, p.name_en, p.name) as name_am,
                   COALESCE(p.name_en, p.name_am, p.name) as name_en,
                   p.stock_quantity
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.user_id = %s AND p.is_active = 1
            ORDER BY ci.created_at DESC
        """, (user_id,))
        items = cursor.fetchall()

        if not items:
            return {
                'am': "Cart ባዶ ነው — /products ላይ ምርቶችን ይፈልጉ።",
                'en': "Cart is empty — browse products at /products",
                'ar': "السلة فارغة — تصفح المنتجات على /products",
            }.get(lang, "Cart is empty.")

        lines = []
        total = 0.0
        for it in items:
            name  = it['name_am'] if lang == 'am' else it['name_en']
            qty   = int(it['quantity'])
            price = float(it['price'])
            item_total = price * qty
            total += item_total
            lines.append(f"  • {name} × {qty} = {item_total:,.0f} ETB")

        discount = total * (1 - USER_DISCOUNT_RATE)
        final    = total - discount
        shipping = 0 if final >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST

        summary = "\n".join(lines)
        summary += f"\n  Subtotal: {total:,.0f} ETB"
        if discount > 0:
            summary += f" | Discount: -{discount:,.0f} ETB ({int((1-USER_DISCOUNT_RATE)*100)}%)"
        summary += f" | Shipping: {'FREE' if shipping == 0 else f'{shipping:,.0f} ETB'}"
        summary += f"\n  → TOTAL: {final + shipping:,.0f} ETB"
        return summary

    except Exception as e:
        logger.error(f"AI cart context error: {e}")
        return "Cart information unavailable."


def get_order_context(user_id, user_message: str, lang: str = 'am') -> str:
    """Fetch order history with item details for logged-in customers."""
    if not user_id:
        return {
            'ar': "⚠️ العميل غير مسجل الدخول. يجب تسجيل الدخول على /login لعرض الطلبات. لا تخترع أي معلومات.",
            'en': "⚠️ NOT LOGGED IN — customer must log in at /login to view orders. NEVER invent order status.",
            'am': "⚠️ ወደ ስርዓቱ አልገቡም። ትዕዛዝ ለማየት /login ላይ መግባት አለባቸው። ፍጹም ትዕዛዝ ሁኔታ አታስብ።",
        }.get(lang, "⚠️ NOT logged in — tell customer to log in at /login.")

    try:
        db = get_db()
        cursor = db.cursor()

        order_num_match = re.search(r'\b(\d{8}-[A-Z0-9]{6})\b', user_message.upper())
        specific_order_num = order_num_match.group(1) if order_num_match else None

        if specific_order_num:
            cursor.execute("""
                SELECT o.id, o.order_number, o.status, o.payment_status, o.total,
                       o.shipping_city, o.tracking_number, o.estimated_delivery,
                       o.created_at, o.notes
                FROM orders o
                WHERE o.user_id = %s AND UPPER(o.order_number) = %s
                LIMIT 1
            """, (user_id, specific_order_num))
        else:
            cursor.execute("""
                SELECT o.id, o.order_number, o.status, o.payment_status, o.total,
                       o.shipping_city, o.tracking_number, o.estimated_delivery,
                       o.created_at, o.notes
                FROM orders o
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
                LIMIT 5
            """, (user_id,))

        orders = cursor.fetchall()
        if not orders:
            return {
                'ar': "لا توجد طلبات بعد. تسوق الآن على /products",
                'en': "No orders yet. Start shopping at /products",
                'am': "ምንም ትዕዛዝ የለም። /products ላይ ይጀምሩ",
            }.get(lang, "No orders found.")

        lines = []
        for o in orders:
            cursor.execute("""
                SELECT oi.quantity, oi.price_at_time,
                       COALESCE(p.name_am, p.name_en, p.name) as product_name
                FROM order_items oi
                LEFT JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id = %s
                LIMIT 5
            """, (o['id'],))
            items = cursor.fetchall()

            status_raw = o['status'] or 'pending'
            pay_raw    = o['payment_status'] or 'pending'
            status_lbl = STATUS_LABELS.get(status_raw, {}).get(lang, status_raw)
            pay_lbl    = PAYMENT_LABELS.get(pay_raw, {}).get(lang, pay_raw)
            total      = float(o['total'] or 0)
            date_str   = o['created_at'].strftime('%Y-%m-%d') if o['created_at'] else '?'
            est_del    = o['estimated_delivery'].strftime('%Y-%m-%d') if o['estimated_delivery'] else 'N/A'
            city       = o['shipping_city'] or 'N/A'
            tracking   = o['tracking_number'] or 'Not assigned yet'

            items_str = ', '.join(
                f"{i['product_name']} ×{i['quantity']} ({float(i['price_at_time']):,.0f} ETB)"
                for i in items
            ) if items else 'N/A'

            lines.append(
                f"Order #{o['order_number']}\n"
                f"  Date: {date_str} | Status: {status_lbl} | Payment: {pay_lbl}\n"
                f"  Total: {total:,.0f} ETB | City: {city}\n"
                f"  Tracking: {tracking} | Est. Delivery: {est_del}\n"
                f"  Items: {items_str}"
            )

        return "\n\n".join(lines)

    except Exception as e:
        logger.error(f"AI order context error: {e}")
        return "Could not load order information at this time."


def smart_fallback(message: str, user_id=None, lang: str = 'am',
                   products_ctx: str = '', cart_ctx: str = '') -> str:
    """Comprehensive rule-based fallback — handles 25+ intent patterns."""
    msg = message.lower().strip()

    def _has(*words):
        return any(w in msg for w in words)

    # ── Greeting ──
    if _has(*AMHARIC_GREETING_WORDS) and len(msg) < 40:
        return {
            'am': ("ሰላም! 👗 እኔ ሰሚራ ነኝ — የ SEMIRA FASHION AI አስተናጋጅ።\n\n"
                   "ምን ልርዳዎ? ምርቶች፣ ዋጋ፣ ትዕዛዝ ሁኔታ፣ ሳይዝ፣ ማጓጓዝ — ሁሉ ልረዳ እችላለሁ! 🌸"),
            'en': ("Hello! 👗 I'm SEMIRA, your AI fashion assistant for SEMIRA FASHION.\n\n"
                   "I can help with products, prices, orders, sizing, shipping & more!"),
            'ar': ("أهلاً! 👗 أنا سيميرا، مساعدتك الذكية في SEMIRA FASHION.\n\n"
                   "يمكنني مساعدتك في المنتجات والأسعار والطلبات والمقاسات والشحن."),
        }.get(lang, "ሰላም! 👗 ምን ልርዳዎ?")

    # ── Cart inquiry ──
    if _has(*AMHARIC_CART_WORDS):
        if cart_ctx and 'Cart is empty' not in cart_ctx and 'not logged in' not in cart_ctx and len(cart_ctx) > 20:
            prefix = {'am': "🛒 የእርስዎ ቅርጫት:", 'en': "🛒 Your cart:", 'ar': "🛒 سلتك:"}.get(lang, "🛒 Cart:")
            return f"{prefix}\n{cart_ctx}\n\n→ /cart"
        elif not user_id:
            return {
                'am': f"🛒 ቅርጫት ለማየት ወደ /login ይግቡ፣ ወይም /products ላይ ይጀምሩ።",
                'en': f"🛒 Log in at /login to view your cart, or start shopping at /products.",
                'ar': f"🛒 سجل الدخول على /login لعرض سلتك، أو تسوق على /products.",
            }.get(lang, "Log in at /login to view cart.")
        else:
            return {
                'am': "🛒 ቅርጫትዎ ባዶ ነው። /products ላይ ምርቶችን ይፈልጉ!",
                'en': "🛒 Your cart is empty. Browse products at /products!",
                'ar': "🛒 سلتك فارغة. تصفح المنتجات على /products!",
            }.get(lang, "Cart is empty.")

    # ── Order tracking ──
    if _has(*AMHARIC_ORDER_WORDS):
        if user_id:
            order_info = get_order_context(user_id, message, lang)
            prefix = {'am': "📦 የትዕዛዝ ሁኔታዎ:", 'en': "📦 Your order details:", 'ar': "📦 تفاصيل طلبك:"}.get(lang, "📦 Order info:")
            suffix = {'am': "ሁሉም ትዕዛዞች → /orders", 'en': "View all orders → /orders", 'ar': "جميع الطلبات → /orders"}.get(lang, "→ /orders")
            return f"{prefix}\n\n{order_info}\n\n{suffix}"
        return {
            'am': f"📦 ትዕዛዝዎን ለማወቅ /login ይግቡ፣ ወይም WhatsApp ያግኙን: wa.me/{WHATSAPP_NUMBER}",
            'en': f"📦 Log in at /login to track your order, or WhatsApp: wa.me/{WHATSAPP_NUMBER}",
            'ar': f"📦 سجل الدخول على /login لتتبع طلبك، أو واتساب: wa.me/{WHATSAPP_NUMBER}",
        }.get(lang, f"Log in at /login or WhatsApp: wa.me/{WHATSAPP_NUMBER}")

    # ── Shipping ──
    if _has(*AMHARIC_SHIPPING_WORDS):
        return {
            'am': (f"🚚 **ማጓጓዣ ዝርዝር:**\n"
                   f"• ከ{FREE_SHIPPING_THRESHOLD:,} ብር በላይ → **ነጻ ማጓጓዝ!**\n"
                   f"• ከዚያ ያነሰ → {SHIPPING_COST:,} ብር ብቻ\n"
                   f"• ዲሊቨሪ: 2–5 የሥራ ቀናት\n"
                   f"• ክፍያ: COD (ምርቱ ሲደርስ ይከፍላሉ)"),
            'en': (f"🚚 **Shipping Info:**\n"
                   f"• Orders ≥ {FREE_SHIPPING_THRESHOLD:,} ETB → **FREE shipping!**\n"
                   f"• Below that → only {SHIPPING_COST:,} ETB\n"
                   f"• Delivery: 2–5 business days\n"
                   f"• Payment: COD (pay when order arrives)"),
            'ar': (f"🚚 **معلومات الشحن:**\n"
                   f"• طلبات ≥ {FREE_SHIPPING_THRESHOLD:,} بر → **شحن مجاني!**\n"
                   f"• أقل من ذلك → {SHIPPING_COST:,} بر فقط\n"
                   f"• التوصيل: 2–5 أيام عمل"),
        }.get(lang, f"Free shipping ≥ {FREE_SHIPPING_THRESHOLD:,} ETB. Standard: {SHIPPING_COST:,} ETB.")

    # ── Returns ──
    if _has(*AMHARIC_RETURN_WORDS):
        return {
            'am': (f"↩️ **ምርት መመለስ / መቀየር:**\n"
                   f"• ካልለበሱ ምርቶችን በ7 ቀን ውስጥ ይቀይሩ ወይም ይመልሱ\n"
                   f"• ዋናው Tag ያልተነቀለ መሆን አለበት\n"
                   f"• ለዝርዝር WhatsApp: wa.me/{WHATSAPP_NUMBER}"),
            'en': (f"↩️ **Returns & Exchanges:**\n"
                   f"• Unused items with original tags: 7 days\n"
                   f"• Contact WhatsApp to initiate: wa.me/{WHATSAPP_NUMBER}"),
            'ar': (f"↩️ **الإرجاع والاستبدال:**\n"
                   f"• المنتجات غير المستخدمة مع البطاقة الأصلية: 7 أيام\n"
                   f"• تواصل واتساب: wa.me/{WHATSAPP_NUMBER}"),
        }.get(lang, f"7-day return policy. WhatsApp: wa.me/{WHATSAPP_NUMBER}")

    # ── Size guide ──
    if _has(*AMHARIC_SIZE_WORDS):
        return {
            'am': (f"📏 **ሳይዝ መረጃ:**\n"
                   f"• ሴቶች: XS · S · M · L · XL · XXL · 3XL\n"
                   f"• ህፃናት: አዲስ የተወለደ – 14 ዓመት\n"
                   f"• ባህላዊ ልብስ: One Size / ካስቶም\n\n"
                   f"ለዝርዝር WhatsApp: wa.me/{WHATSAPP_NUMBER}"),
            'en': (f"📏 **Size Guide:**\n"
                   f"• Women: XS · S · M · L · XL · XXL · 3XL\n"
                   f"• Kids: Newborn – 14 years\n"
                   f"• Traditional: One Size / Custom\n\n"
                   f"For exact fit help: wa.me/{WHATSAPP_NUMBER}"),
            'ar': (f"📏 **دليل المقاسات:**\n"
                   f"• نساء: XS · S · M · L · XL · XXL · 3XL\n"
                   f"• أطفال: حديث الولادة – 14 سنة\n"
                   f"• التقليدية: مقاس واحد / مخصص"),
        }.get(lang, f"Women: XS–3XL. Kids: 0–14yr. WhatsApp: wa.me/{WHATSAPP_NUMBER}")

    # ── Payment ──
    if _has(*AMHARIC_PAYMENT_WORDS):
        return {
            'am': (f"💵 **ክፍያ ዘዴ:**\n"
                   f"• Cash on Delivery (COD) — ምርቱ ሲደርስ ብቻ ይከፍላሉ\n"
                   f"• አስቀድሞ ምንም ክፍያ አያስፈልጋትም!\n"
                   f"• ወደ መለያ ሲገቡ {int(USER_DISCOUNT_RATE * 100)}% ቅናሽ ያገኛሉ"),
            'en': (f"💵 **Payment Method:**\n"
                   f"• Cash on Delivery (COD) — pay only when your order arrives\n"
                   f"• No upfront payment required!\n"
                   f"• Log in for {int(USER_DISCOUNT_RATE * 100)}% discount on all orders"),
            'ar': (f"💵 **طريقة الدفع:**\n"
                   f"• الدفع عند الاستلام (COD) — ادفع فقط عند وصول طلبك\n"
                   f"• لا دفعة مقدمة!\n"
                   f"• سجل الدخول للحصول على خصم {int(USER_DISCOUNT_RATE * 100)}%"),
        }.get(lang, "Cash on Delivery. Log in for discount!")

    # ── Discount ──
    if _has(*AMHARIC_DISCOUNT_WORDS):
        return {
            'am': (f"🎉 **አሁን ያሉ ቅናሾች:**\n"
                   f"• ወደ መለያ ሲገቡ → {int(USER_DISCOUNT_RATE * 100)}% ቅናሽ\n"
                   f"• ከ{FREE_SHIPPING_THRESHOLD:,} ብር በላይ → ነጻ ማጓጓዝ\n"
                   f"• /products ላይ 'Sale' የምልክት ምርቶችን ይፈልጉ"),
            'en': (f"🎉 **Current Offers:**\n"
                   f"• Log in → {int(USER_DISCOUNT_RATE * 100)}% off every order\n"
                   f"• Orders ≥ {FREE_SHIPPING_THRESHOLD:,} ETB → FREE shipping\n"
                   f"• Check /products for sale items"),
            'ar': (f"🎉 **العروض الحالية:**\n"
                   f"• تسجيل الدخول → خصم {int(USER_DISCOUNT_RATE * 100)}%\n"
                   f"• طلبات ≥ {FREE_SHIPPING_THRESHOLD:,} بر → شحن مجاني"),
        }.get(lang, "Log in for discount!")

    # ── Contact / Location / Branches ──
    if _has(*AMHARIC_CONTACT_WORDS):
        return {
            'am': (f"📱 **ያግኙን:**\n"
                   f"• WhatsApp: wa.me/{WHATSAPP_NUMBER}\n"
                   f"• አድራሻ: ወሎ፣ ደሴ፣ ኩታቤር — ኢትዮጵያ\n"
                   f"• ሰዓት: ሰኞ–ቅዳሜ 8AM–8PM\n\n"
                   f"ቅርንጫፎቻችን → /branches"),
            'en': (f"📱 **Contact Us:**\n"
                   f"• WhatsApp: wa.me/{WHATSAPP_NUMBER}\n"
                   f"• Location: Wollo, Dessie, Kutaber — Ethiopia\n"
                   f"• Hours: Mon–Sat 8AM–8PM\n\n"
                   f"Our branches → /branches"),
            'ar': (f"📱 **تواصل معنا:**\n"
                   f"• واتساب: wa.me/{WHATSAPP_NUMBER}\n"
                   f"• العنوان: وولو، ديسي، كوتابر — إثيوبيا\n"
                   f"• الساعات: الإثنين–السبت 8ص–8م"),
        }.get(lang, f"WhatsApp: wa.me/{WHATSAPP_NUMBER} | Wollo, Dessie")

    # ── Wishlist ──
    if _has(*AMHARIC_WISHLIST_WORDS):
        login_note = "" if user_id else {
            'am': " (ለማየት /login ይግቡ)",
            'en': " (log in at /login to view)",
            'ar': " (سجل الدخول على /login لعرضها)",
        }.get(lang, "")
        return {
            'am': f"❤️ የምኞት ዝርዝርዎ{login_note} → /wishlist",
            'en': f"❤️ Your wishlist{login_note} → /wishlist",
            'ar': f"❤️ قائمة أمنياتك{login_note} → /wishlist",
        }.get(lang, f"Wishlist → /wishlist{login_note}")

    # ── Product/category query ──
    cat_id = _detect_category(msg)
    price_min, price_max = _extract_price_range(msg)
    is_product_query = cat_id or _has(*AMHARIC_PRICE_WORDS) or \
        any(w in msg for w in ('product', 'ምርት', 'ልብስ', 'ምን አለ', 'show me', 'አሳዩኝ', 'ምን ዓይነት'))

    if is_product_query and products_ctx and 'No products' not in products_ctx and len(products_ctx) > 20:
        intro = {'am': "👗 እነዚህ ምርቶች አሉ:", 'en': "👗 Here are our products:", 'ar': "👗 إليك منتجاتنا:"}.get(lang, "👗 Products:")
        browse_url = "/products"
        if cat_id:   browse_url += f"?category={cat_id}"
        if price_max and price_max < 999999:
            sep = '&' if '?' in browse_url else '?'
            browse_url += f"{sep}max_price={price_max}"
        footer = {'am': f"ሁሉም ምርቶች: {browse_url}", 'en': f"See all: {browse_url}", 'ar': f"عرض الكل: {browse_url}"}.get(lang, f"Browse: {browse_url}")
        return f"{intro}\n{products_ctx}\n\n{footer}"

    if is_product_query:
        base_url = "/products"
        if cat_id:   base_url += f"?category={cat_id}"
        if price_max and price_max < 999999:
            sep = '&' if '?' in base_url else '?'
            base_url += f"{sep}max_price={price_max}"
        return {
            'am': f"👗 ምርቶቻችንን ለማየት: {base_url}",
            'en': f"👗 Browse our products: {base_url}",
            'ar': f"👗 تصفح منتجاتنا: {base_url}",
        }.get(lang, f"Browse: {base_url}")

    # ── Default ──
    return {
        'am': (f"ሰሚራ AI ለማገልገል ዝግጁ ነኝ! 🌸\n"
               f"ስለ ምርቶች፣ ዋጋ፣ ቅርጫት፣ ትዕዛዝ ሁኔታ፣ ሳይዝ፣ ወይም ማጓጓዝ ይጠይቁ።"),
        'en': "I'm here to help! Ask about products, prices, cart, orders, sizes, or delivery. 🌸",
        'ar': "أنا هنا للمساعدة! اسألني عن المنتجات والأسعار والسلة وطلباتك والمقاسات. 🌸",
    }.get(lang, f"How can I help? WhatsApp: wa.me/{WHATSAPP_NUMBER}")


def _log_conversation(message: str, reply: str, source: str, lang: str,
                      user_id=None, user_name: str = None, ip: str = None):
    """Persist chat turn to ai_conversations table."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO ai_conversations
                (user_id, user_name, user_message, ai_reply, source, lang, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, user_name, message[:1000], reply[:3000], source, lang, ip))
        db.commit()
    except Exception as e:
        logger.debug(f"AI conversation log failed (non-fatal): {e}")


def _get_groq_api_key() -> str:
    """Get Groq API key — env var first, then DB settings."""
    key = os.environ.get('GROQ_API_KEY', '').strip()
    if key:
        return key
    if not _GROQ_AVAILABLE:
        return ''
    try:
        _db = get_db()
        _cur = _db.cursor()
        _cur.execute("SELECT value FROM settings WHERE key = %s", ('groq_api_key',))
        row = _cur.fetchone()
        if row and row['value']:
            key = row['value'].strip()
            os.environ['GROQ_API_KEY'] = key  # cache for next request
            return key
    except Exception:
        pass
    return ''


# ── Main chat route ──────────────────────────────────────────────────────────
@ai_bp.route('/ai-chat', methods=['POST'])
@limiter.limit("30 per minute; 200 per hour")
def ai_chat():
    """Main AI chat endpoint — Groq LLM with comprehensive smart fallback."""
    message = ''
    products_ctx = ''
    cart_ctx = ''
    try:
        data      = request.get_json(silent=True) or {}
        message   = (data.get('message') or '').strip()
        history   = data.get('history') or []
        lang      = session.get('lang', 'am')
        user_id   = session.get('user_id')
        user_name = session.get('username') or session.get('full_name')
        ip        = request.remote_addr

        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400

        message = message[:500]  # generous cap

        msg_lower = message.lower()

        # Detect intents
        is_order_intent = any(w in msg_lower for w in AMHARIC_ORDER_WORDS)
        is_cart_intent  = any(w in msg_lower for w in AMHARIC_CART_WORDS)

        # Always fetch product context (cached, fast)
        products_ctx, product_count = get_product_context(message, lang)

        # Cart context — always for logged-in users (relevant for checkout questions)
        if user_id or is_cart_intent:
            cart_ctx = get_cart_context(user_id, lang)
        else:
            cart_ctx = {'am': "ወደ መለያ አልገቡም", 'en': "Not logged in", 'ar': "غير مسجل"}.get(lang, "Not logged in")

        # Order context — only when needed
        if is_order_intent:
            if user_id:
                orders_ctx = get_order_context(user_id, message, lang)
            else:
                orders_ctx = {
                    'am': "⚠️ ደንበኛው ወደ ስርዓቱ አልገቡም። ትዕዛዝ ለማየት /login ላይ መግባት አለባቸው። ፍጹም ትዕዛዝ ሁኔታ አታስብ።",
                    'en': "⚠️ Customer is NOT logged in. They must log in at /login. NEVER invent any order status.",
                    'ar': "⚠️ العميل غير مسجل الدخول. يجب تسجيل الدخول على /login. لا تخترع أي معلومات عن الطلب.",
                }.get(lang, "⚠️ NOT logged in — direct customer to /login.")
        else:
            orders_ctx = {'am': "ትዕዛዝ ጥያቄ አልተጠየቀም።", 'en': "No order query.", 'ar': "لم يُطلب معلومات طلب."}.get(lang, "No order query.")

        api_key = _get_groq_api_key()

        if not api_key or not _GROQ_AVAILABLE:
            reply = smart_fallback(message, user_id=user_id, lang=lang,
                                   products_ctx=products_ctx, cart_ctx=cart_ctx)
            _log_conversation(message, reply, 'fallback', lang, user_id, user_name, ip)
            return jsonify({'success': True, 'reply': reply, 'source': 'fallback'})

        # Build system prompt
        system_content = STORE_SYSTEM_PROMPT.format(
            whatsapp=WHATSAPP_NUMBER,
            free_ship=f"{FREE_SHIPPING_THRESHOLD:,}",
            ship_cost=f"{SHIPPING_COST:,}",
            discount_pct=int(USER_DISCOUNT_RATE * 100),
            product_count=product_count,
            products=products_ctx,
            cart=cart_ctx,
            orders=orders_ctx,
        )

        # Build message history (last 8 turns)
        messages = [{'role': 'system', 'content': system_content}]
        for h in history[-8:]:
            role    = h.get('role', 'user')
            content = h.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': str(content)[:300]})
        messages.append({'role': 'user', 'content': message})

        # Try primary model, fallback to smaller model on failure
        models = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']
        reply = None
        for model in models:
            try:
                client = _GroqClient(api_key=api_key, timeout=18.0)
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=600,
                    temperature=0.3,
                    top_p=0.92,
                )
                reply = completion.choices[0].message.content.strip()
                source = f'groq:{model.split("-")[1]}'
                break
            except Exception as model_err:
                logger.warning(f"AI model {model} failed: {model_err}")
                continue

        if not reply:
            reply = smart_fallback(message, user_id=user_id, lang=lang,
                                   products_ctx=products_ctx, cart_ctx=cart_ctx)
            source = 'fallback'

        _log_conversation(message, reply, source, lang, user_id, user_name, ip)
        return jsonify({'success': True, 'reply': reply, 'source': source})

    except Exception as e:
        logger.error(f"AI chat error: {e}")
        _lang    = session.get('lang', 'am')
        _uid     = session.get('user_id')
        _name    = session.get('username') or session.get('full_name')
        _ip      = request.remote_addr
        fallback = smart_fallback(message or '', user_id=_uid, lang=_lang,
                                  products_ctx=products_ctx, cart_ctx=cart_ctx)
        _log_conversation(message or '', fallback, 'error', _lang, _uid, _name, _ip)
        return jsonify({'success': True, 'reply': fallback, 'source': 'fallback'})


# ── Suggestions route ─────────────────────────────────────────────────────────
@ai_bp.route('/ai-chat/suggestions', methods=['GET'])
def ai_suggestions():
    """Return smart suggestion chips based on language + login state."""
    lang      = session.get('lang', 'am')
    logged_in = bool(session.get('user_id'))

    base = {
        'am': {
            True: [
                "የእኔ ትዕዛዝ ሁኔታ ምንድን ነው?",
                "ቅርጫቴ ምን አለ?",
                "ለ2000 ብር ቀሚሶች አሳዩኝ",
                "ሀበሻ ቀሚስ ዋጋ ስንት ነው?",
            ],
            False: [
                "ለ1500 ብር ምን ቀሚሶች አሉ?",
                "ሀበሻ ቀሚስ አለ?",
                "ለህፃናት ምን ምርቶች አሉ?",
                "ነጻ ማጓጓዝ መቼ ነው?",
            ],
        },
        'en': {
            True: [
                "Where is my order?",
                "What's in my cart?",
                "Show dresses under 2000 ETB",
                "What sizes are available?",
            ],
            False: [
                "Show dresses under 2000 ETB",
                "Do you have Habesha Kemis?",
                "What kids clothing is available?",
                "How does shipping work?",
            ],
        },
        'ar': {
            True: [
                "ما حالة طلبي؟",
                "ما الموجود في سلتي؟",
                "أريد فستاناً بأقل من 2000 بر",
                "ما هي المقاسات المتاحة؟",
            ],
            False: [
                "أريد فستاناً بأقل من 2000 بر",
                "هل يوجد هبشا كيميس؟",
                "ملابس الأطفال المتوفرة",
                "معلومات الشحن والتوصيل",
            ],
        },
    }

    lang_data   = base.get(lang, base['am'])
    suggestions = lang_data.get(logged_in, lang_data[False])
    return jsonify({'success': True, 'suggestions': suggestions})
