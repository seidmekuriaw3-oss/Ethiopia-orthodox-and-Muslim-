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
(AWAIT_SEARCH, AWAIT_NAME, AWAIT_PHONE, AWAIT_ADDRESS, AWAIT_TRACK,
 AWAIT_ORDERS_PHONE, AWAIT_REG_NAME, AWAIT_REG_PHONE,
 AWAIT_REG_EMAIL, AWAIT_REG_PASS,
 AWAIT_EDIT_NAME, AWAIT_EDIT_PHONE, AWAIT_COUPON) = range(13)

# ───────────────────────── in-memory user state ─────────────────────────
# { telegram_user_id: { 'lang': 'am', 'cart': {}, 'order': {}, 'wishlist': [] } }
_user_state: dict = {}

def _get_state(uid: int) -> dict:
    if uid not in _user_state:
        _user_state[uid] = {'lang': 'am', 'cart': {}, 'order': {}, 'wishlist': []}
    s = _user_state[uid]
    s.setdefault('wishlist', [])
    return s

# ───────────────────────── translations ─────────────────────────
T = {
    'welcome': {
        'am': ('👗 *ወደ ሰሚራ ፋሽን እንኳን ደህና መጡ!*\n\n'
               'የኢትዮጵያ ምርጥ የሴቶችና ህጻናት ፋሽን መደብር።\n'
               'ምርቶቻችንን ይፈልጉ፣ ይዘዙ፣ ይከታተሉ።'),
        'en': ('👗 *Welcome to Semira Fashion!*\n\n'
               'Ethiopia\'s premier women & children fashion store.\n'
               'Browse, order and track your purchases with ease.'),
        'ar': ('👗 *مرحباً بكم في سميرا فاشن!*\n\n'
               'متجر الأزياء الأول للنساء والأطفال في إثيوبيا.\n'
               'تصفح، اطلب وتابع مشترياتك بكل سهولة.'),
    },
    'main_menu': {'am': '🏠 ዋና ምናሌ',    'en': '🏠 Main Menu',      'ar': '🏠 القائمة الرئيسية'},
    'products':  {'am': '🛍️ ምርቶች',      'en': '🛍️ Products',      'ar': '🛍️ المنتجات'},
    'categories':{'am': '🗂️ ምድቦች',      'en': '🗂️ Categories',    'ar': '🗂️ الفئات'},
    'new':       {'am': '🆕 አዲስ ምርቶች',  'en': '🆕 New Arrivals',  'ar': '🆕 وصل حديثاً'},
    'featured':  {'am': '⭐ ተወዳጅ',       'en': '⭐ Featured',       'ar': '⭐ مميز'},
    'search':    {'am': '🔍 ፈልግ',        'en': '🔍 Search',         'ar': '🔍 بحث'},
    'cart':      {'am': '🛒 ቅርጫቴ',      'en': '🛒 My Cart',        'ar': '🛒 سلتي'},
    'checkout':  {'am': '💳 ክፍያ',        'en': '💳 Checkout',       'ar': '💳 الدفع'},
    'track':     {'am': '📦 ትዕዛዝ ክትትል', 'en': '📦 Track Order',    'ar': '📦 تتبع الطلب'},
    'contact':   {'am': '📞 እውቂያ',       'en': '📞 Contact',        'ar': '📞 تواصل معنا'},
    'language':  {'am': '🌐 ቋንቋ',        'en': '🌐 Language',       'ar': '🌐 اللغة'},
    'back':      {'am': '◀️ ተመለስ',      'en': '◀️ Back',           'ar': '◀️ رجوع'},
    'price':     {'am': 'ዋጋ',            'en': 'Price',              'ar': 'السعر'},
    'stock':     {'am': 'ክምችት',          'en': 'Stock',              'ar': 'المخزون'},
    'add_cart':  {'am': '🛒 ወደ ቅርጫት ጨምር','en': '🛒 Add to Cart',  'ar': '🛒 أضف للسلة'},
    'remove':    {'am': '❌ አስወግድ',      'en': '❌ Remove',          'ar': '❌ إزالة'},
    'empty_cart':{'am': '🛒 ቅርጫቱ ባዶ ነው።','en': '🛒 Your cart is empty.','ar': '🛒 سلتك فارغة.'},
    'added':     {'am': '✅ ወደ ቅርጫት ተጨምሯል!','en': '✅ Added to cart!','ar': '✅ أضيف إلى السلة!'},
    'removed':   {'am': '✅ ከቅርጫት ተወግዷል!', 'en': '✅ Removed from cart!','ar': '✅ أزيل من السلة!'},
    'prev':      {'am': '◀ ቀዳሚ',         'en': '◀ Prev',            'ar': '◀ السابق'},
    'next':      {'am': 'ቀጣይ ▶',         'en': 'Next ▶',            'ar': 'التالي ▶'},
    'no_products':{'am': '😔 ምርቶች አልተገኙም።','en': '😔 No products found.','ar': '😔 لا توجد منتجات.'},
    'no_cats':   {'am': '😔 ምድቦች አልተገኙም።', 'en': '😔 No categories found.','ar': '😔 لا توجد فئات.'},
    'search_prompt':{'am': '🔍 የምርቱን ስም ይጻፉ...','en': '🔍 Type the product name...','ar': '🔍 اكتب اسم المنتج...'},
    'name_prompt':  {'am': '📝 ሙሉ ስምዎን ያስገቡ:','en': '📝 Enter your full name:','ar': '📝 أدخل اسمك الكامل:'},
    'phone_prompt': {'am': '📱 ስልክ ቁጥርዎን ያስገቡ:','en': '📱 Enter your phone number:','ar': '📱 أدخل رقم هاتفك:'},
    'addr_prompt':  {'am': '🏠 አድራሻዎን ያስገቡ:','en': '🏠 Enter your delivery address:','ar': '🏠 أدخل عنوان التوصيل:'},
    'track_prompt': {'am': '🔢 የትዕዛዝ ቁጥርዎን ያስገቡ:','en': '🔢 Enter your order number:','ar': '🔢 أدخل رقم طلبك:'},
    'order_ok':     {'am': '✅ ትዕዛዝዎ ተቀብሏል!\n\n📲 ቡድናችን ብዙም ሳይቆይ ያነጋግርዎታል።',
                     'en': '✅ Order received!\n\n📲 Our team will contact you shortly.',
                     'ar': '✅ تم استلام طلبك!\n\n📲 سيتواصل معك فريقنا قريباً.'},
    'order_err':    {'am': '❌ ትዕዛዝ ሲቀበል ስህተት ተፈጥሯል። እባክዎ ዳግም ሞክሩ።',
                     'en': '❌ Error placing order. Please try again.',
                     'ar': '❌ خطأ في تقديم الطلب. حاول مجدداً.'},
    'track_not_found':{'am': '❌ ትዕዛዝ አልተገኘም። ቁጥሩን ያረጋግጡ።',
                       'en': '❌ Order not found. Check the number.',
                       'ar': '❌ الطلب غير موجود. تحقق من الرقم.'},
    'cancel':    {'am': '❌ ተሰርዟል',    'en': '❌ Cancelled',         'ar': '❌ إلغاء'},
    'cancelled': {'am': '✅ ምርጫ ተሰርዟል። ከዋና ምናሌ ጀምሩ።',
                  'en': '✅ Cancelled. Start from the main menu.',
                  'ar': '✅ تم الإلغاء. ابدأ من القائمة الرئيسية.'},
    'subtotal':  {'am': 'ጠቅላላ',        'en': 'Subtotal',             'ar': 'المجموع الجزئي'},
    'shipping':  {'am': 'ማጓጓዣ',        'en': 'Shipping',             'ar': 'الشحن'},
    'free':      {'am': 'ነጻ',           'en': 'Free',                 'ar': 'مجاني'},
    'total':     {'am': 'ሁሉም ድምር',    'en': 'Grand Total',           'ar': 'الإجمالي'},
    'qty':       {'am': 'ቁጥር',         'en': 'Qty',                   'ar': 'الكمية'},
    'out_stock': {'am': '❌ ክምችት አልቋል','en': '❌ Out of stock',       'ar': '❌ نفد المخزون'},
    'desc':      {'am': 'መግለጫ',        'en': 'Description',           'ar': 'الوصف'},
    'size':      {'am': 'መጠን',         'en': 'Size',                  'ar': 'الحجم'},
    'color':     {'am': 'ቀለም',         'en': 'Color',                 'ar': 'اللون'},
    'contact_msg':{'am': ('📞 *ሰሚራ ፋሽን*\n\n'
                          '📱 WhatsApp: +{wa}\n'
                          '🕐 ሰዓት: ሰኞ–ቅዳሜ 9:00–7:00\n\n'
                          '🌐 ድረ-ገጽ: https://{site}'),
                   'en': ('📞 *Semira Fashion*\n\n'
                          '📱 WhatsApp: +{wa}\n'
                          '🕐 Hours: Mon–Sat 9 AM–7 PM\n\n'
                          '🌐 Website: https://{site}'),
                   'ar': ('📞 *سميرا فاشن*\n\n'
                          '📱 واتساب: +{wa}\n'
                          '🕐 المواعيد: الإثنين–السبت 9ص–7م\n\n'
                          '🌐 الموقع: https://{site}')},
    'status_labels': {
        'am': {'Pending':'⏳ በመጠባበቅ', 'Confirmed':'✅ ተረጋግጧል',
               'Processing':'🔄 በሂደት ላይ', 'Shipped':'🚚 ተልኳል',
               'Delivered':'📬 ደርሷል', 'Cancelled':'❌ ተሰርዟል'},
        'en': {'Pending':'⏳ Pending', 'Confirmed':'✅ Confirmed',
               'Processing':'🔄 Processing', 'Shipped':'🚚 Shipped',
               'Delivered':'📬 Delivered', 'Cancelled':'❌ Cancelled'},
        'ar': {'Pending':'⏳ قيد الانتظار', 'Confirmed':'✅ مؤكد',
               'Processing':'🔄 جاري المعالجة', 'Shipped':'🚚 تم الشحن',
               'Delivered':'📬 تم التسليم', 'Cancelled':'❌ ملغي'},
    },
    'increase': {'am': '➕', 'en': '➕', 'ar': '➕'},
    'decrease': {'am': '➖', 'en': '➖', 'ar': '➖'},
    # ── new features ──
    'orders':        {'am': '📦 ትዕዛዞቼ',      'en': '📦 My Orders',      'ar': '📦 طلباتي'},
    'wishlist':      {'am': '💝 ምኞቴ',         'en': '💝 Wishlist',        'ar': '💝 قائمة الأمنيات'},
    'branches':      {'am': '🏪 ቅርንጫፎቻችን',   'en': '🏪 Our Branches',   'ar': '🏪 فروعنا'},
    'account':       {'am': '👤 መለያዬ',        'en': '👤 My Account',      'ar': '👤 حسابي'},
    'orders_prompt': {'am': '📱 ትዕዛዞቹን ለማየት ስልክ ቁጥርዎን ያስገቡ:',
                      'en': '📱 Enter your phone number to view your orders:',
                      'ar': '📱 أدخل رقم هاتفك لعرض طلباتك:'},
    'no_orders':     {'am': '📦 ለዚህ ስልክ ቁጥር ትዕዛዝ አልተገኘም።',
                      'en': '📦 No orders found for this phone number.',
                      'ar': '📦 لا توجد طلبات لهذا الرقم.'},
    'no_branches':   {'am': '🏪 ቅርንጫፍ አልተገኘም።','en': '🏪 No branches found.','ar': '🏪 لا توجد فروع.'},
    'wish_add':      {'am': '❤️ ምኞቴ ጨምር',    'en': '❤️ Save to Wishlist',  'ar': '❤️ حفظ في الأمنيات'},
    'wish_remove':   {'am': '💔 ምኞቴ አስወግድ',  'en': '💔 Remove from Wishlist','ar': '💔 إزالة من الأمنيات'},
    'wish_added':    {'am': '❤️ ወደ ምኞቴ ተጨምሯል!','en': '❤️ Added to wishlist!','ar': '❤️ أضيف إلى الأمنيات!'},
    'wish_removed':  {'am': '💔 ከምኞቴ ተወግዷል!',  'en': '💔 Removed from wishlist!','ar': '💔 أزيل من الأمنيات!'},
    'empty_wish':    {'am': '💝 ምኞቴ ዝርዝር ባዶ ነው።\nምርቶቹን ሲያዩ ❤️ ይጫኑ።',
                      'en': '💝 Your wishlist is empty.\nTap ❤️ on any product to save it.',
                      'ar': '💝 قائمة الأمنيات فارغة.\nاضغط ❤️ على أي منتج لحفظه.'},
    'reg_intro':     {'am': ('👤 *ምዝገባ*\n\n'
                             'ሰሚራ ፋሽን ድረ-ገጽ ላይ ካለዎት መለያ *10% ቅናሽ* ያገኛሉ!\n\n'
                             'ምዝገባ ይፈልጋሉ?'),
                      'en': ('👤 *Register*\n\n'
                             'Get *10% discount* on every order with a Semira Fashion account!\n\n'
                             'Would you like to register?'),
                      'ar': ('👤 *التسجيل*\n\n'
                             'احصل على *خصم 10%* على كل طلب مع حساب سميرا فاشن!\n\n'
                             'هل تريد التسجيل؟')},
    'already_reg':   {'am': '✅ ቀደም ሲል ተመዝግበዋል! 10% ቅናሽ ይሰጥዎታል።',
                      'en': '✅ You already have an account! 10% discount applied.',
                      'ar': '✅ أنت مسجل بالفعل! سيتم تطبيق خصم 10%.'},
    'reg_name':      {'am': '📝 ሙሉ ስምዎን ያስገቡ:',          'en': '📝 Enter your full name:',           'ar': '📝 أدخل اسمك الكامل:'},
    'reg_phone':     {'am': '📱 ስልክ ቁጥርዎን ያስገቡ (+251...):', 'en': '📱 Enter your phone number (+251...):','ar': '📱 أدخل رقم هاتفك (+251...):'},
    'reg_email':     {'am': '📧 ኢሜልዎን ያስገቡ (ወይም "skip" ይጻፉ):','en': '📧 Enter your email (or type "skip"):','ar': '📧 أدخل بريدك الإلكتروني (أو اكتب "skip"):'},
    'reg_pass':      {'am': '🔐 ይለፍ ቃልዎን ያስገቡ (ቢያንስ 8 ፊደላት):','en': '🔐 Enter a password (min 8 chars):','ar': '🔐 أدخل كلمة مرور (8 أحرف على الأقل):'},
    'coupon_prompt': {'am': '🏷️ ኩፖን ካለዎት ያስገቡ (ወይም "skip" ይጻፉ):',
                      'en': '🏷️ Enter a coupon code (or type "skip"):',
                      'ar': '🏷️ أدخل رمز الكوبون (أو اكتب "skip"):'},
    'coupon_ok':     {'am': '✅ ኩፖን ተቀባይነት አለው! {pct}% ቅናሽ ተወስዷል።',
                      'en': '✅ Coupon applied! {pct}% discount.',
                      'ar': '✅ تم تطبيق الكوبون! خصم {pct}%.'},
    'coupon_bad':    {'am': '❌ ኩፖን ልክ አይደለም ወይም ጊዜው አልፏል።',
                      'en': '❌ Invalid or expired coupon code.',
                      'ar': '❌ رمز الكوبون غير صالح أو منتهي.'},
    'share':         {'am': '📤 አጋራ',          'en': '📤 Share',             'ar': '📤 مشاركة'},
    'cmd_branches':  {'am': '🏪 ቅርንጫፎቻችን',   'en': '🏪 Our Branches',      'ar': '🏪 فروعنا'},
    'reg_ok':        {'am': '✅ ምዝገባ ተሳክቷል! ከአሁን በኋላ 10% ቅናሽ ያገኛሉ።',
                      'en': '✅ Registered! You now get 10% off every order.',
                      'ar': '✅ تم التسجيل! ستحصل على خصم 10% على كل طلب.'},
    'reg_dup':       {'am': '⚠️ ይህ ስልክ ቁጥር ወይም ኢሜል ቀደም ሲል ተመዝግቧል።\nወደ ድህረ-ገጽ ያስገቡ።',
                      'en': '⚠️ This phone/email is already registered. Log in on the website.',
                      'ar': '⚠️ هذا الهاتف أو البريد مسجل بالفعل. سجّل الدخول من الموقع.'},
    'reg_err':       {'am': '❌ ምዝገባ አልተሳካም። እባክዎ ዳግም ሞክሩ።',
                      'en': '❌ Registration failed. Please try again.',
                      'ar': '❌ فشل التسجيل. حاول مجدداً.'},
    'reg_start_btn': {'am': '📝 ምዝገባ ጀምር',    'en': '📝 Start Registration', 'ar': '📝 بدء التسجيل'},
    # ── profile view / edit ──
    'prof_title':    {'am': '👤 *መለያዬ*',          'en': '👤 *My Account*',       'ar': '👤 *حسابي*'},
    'prof_name':     {'am': '📝 ስም',               'en': '📝 Name',               'ar': '📝 الاسم'},
    'prof_phone':    {'am': '📱 ስልክ',              'en': '📱 Phone',              'ar': '📱 الهاتف'},
    'prof_email':    {'am': '📧 ኢሜል',              'en': '📧 Email',              'ar': '📧 البريد الإلكتروني'},
    'prof_points':   {'am': '🌟 ነጥቦች',            'en': '🌟 Loyalty Points',     'ar': '🌟 نقاط الولاء'},
    'prof_orders':   {'am': '📦 ትዕዛዞች',           'en': '📦 Orders',             'ar': '📦 الطلبات'},
    'prof_discount': {'am': '🏷️ ቅናሽ',            'en': '🏷️ Discount',          'ar': '🏷️ الخصم'},
    'prof_since':    {'am': '📅 ተመዝግቦ',           'en': '📅 Member since',       'ar': '📅 عضو منذ'},
    'prof_edit_name':  {'am': '✏️ ስም አስተካክል',    'en': '✏️ Edit Name',         'ar': '✏️ تعديل الاسم'},
    'prof_edit_phone': {'am': '📱 ስልክ አስተካክል',   'en': '📱 Edit Phone',         'ar': '📱 تعديل الهاتف'},
    'prof_my_orders':  {'am': '📦 ትዕዛዞቼ ተመልከት', 'en': '📦 View My Orders',     'ar': '📦 عرض طلباتي'},
    'edit_name_prompt':  {'am': '✏️ አዲስ ስምዎን ያስገቡ:',  'en': '✏️ Enter your new full name:','ar': '✏️ أدخل اسمك الجديد:'},
    'edit_phone_prompt': {'am': '📱 አዲስ ስልክ ቁጥርዎን ያስገቡ:','en': '📱 Enter your new phone number:','ar': '📱 أدخل رقم هاتفك الجديد:'},
    'edit_saved':    {'am': '✅ ተቀምጧል!',          'en': '✅ Saved!',              'ar': '✅ تم الحفظ!'},
    'edit_err':      {'am': '❌ ለውጥ አልተሳካም።',   'en': '❌ Update failed. Please try again.','ar': '❌ فشل التحديث.'},
    'not_registered':{'am': ('👤 *መለያ አልተገኘም*\n\n'
                             'ምዝገባ ሲፈጽሙ:\n'
                             '• 10% ቅናሽ በሁሉም ትዕዛዞች\n'
                             '• የትዕዛዝ ታሪክ\n'
                             '• Loyalty ነጥቦች'),
                      'en': ('👤 *No Account Found*\n\n'
                             'Register to enjoy:\n'
                             '• 10% discount on every order\n'
                             '• Full order history\n'
                             '• Loyalty reward points'),
                      'ar': ('👤 *لم يتم العثور على حساب*\n\n'
                             'سجّل للاستمتاع بـ:\n'
                             '• خصم 10% على كل طلب\n'
                             '• سجل طلبات كامل\n'
                             '• نقاط مكافآت الولاء')},
    'link_account':  {'am': '🔗 ስልክ ቁጥር ይስጡ (መለያ ለማገናኘት):',
                      'en': '🔗 Enter your phone number to link your account:',
                      'ar': '🔗 أدخل رقم هاتفك لربط حسابك:'},
    'link_btn':      {'am': '🔗 ካለ መለያ አገናኝ',   'en': '🔗 Link Existing Account','ar': '🔗 ربط حساب موجود'},
    # ── extra UI strings ──
    'order_summary_title': {'am': 'የትዕዛዝ ማጠቃለያ',  'en': 'Order Summary',    'ar': 'ملخص الطلب'},
    'order_detail_title':  {'am': 'ትዕዛዝ ዝርዝር',    'en': 'Order Details',    'ar': 'تفاصيل الطلب'},
    'order_name':    {'am': 'ስም',    'en': 'Name',    'ar': 'الاسم'},
    'order_phone':   {'am': 'ስልክ',  'en': 'Phone',   'ar': 'الهاتف'},
    'order_address': {'am': 'አድራሻ', 'en': 'Address', 'ar': 'العنوان'},
    'order_items':   {'am': 'ምርቶች', 'en': 'Items',   'ar': 'المنتجات'},
    'order_discount':{'am': 'ቅናሽ',  'en': 'Discount','ar': 'الخصم'},
    'order_coupon':  {'am': 'ኩፖን',  'en': 'Coupon',  'ar': 'الكوبون'},
    'order_number_label': {'am': 'ቁጥር','en': 'Number','ar': 'الرقم'},
    'order_number_title': {'am': 'ትዕዛዝ ቁጥር','en': 'Order #','ar': 'رقم الطلب'},
    'order_status':  {'am': 'ሁኔታ',  'en': 'Status',  'ar': 'الحالة'},
    'order_total':   {'am': 'ጠቅላላ', 'en': 'Total',   'ar': 'الإجمالي'},
    'order_date':    {'am': 'ቀን',    'en': 'Date',    'ar': 'التاريخ'},
    'order_confirm': {'am': '✅ አረጋግጥ','en': '✅ Confirm Order','ar': '✅ تأكيد الطلب'},
    'order_cancel_btn':{'am': '❌ ሰርዝ','en': '❌ Cancel','ar': '❌ إلغاء'},
    'order_edit_btn':  {'am': '✏️ ቅርጫት አስተካክል','en': '✏️ Edit Cart','ar': '✏️ تعديل السلة'},
    'track_my_order':  {'am': '📦 ትዕዛዜን ክትትል','en': '📦 Track My Order','ar': '📦 تتبع طلبي'},
    'phone_invalid':   {'am': '❌ ልክ ያልሆነ ስልክ ቁጥር። ዳግም ይሞክሩ (ምሳሌ: 0911234567 ወይም +251911234567):',
                        'en': '❌ Invalid phone number. Try again (e.g. 0911234567 or +251911234567):',
                        'ar': '❌ رقم هاتف غير صحيح. حاول مجدداً (مثال: 0911234567 أو +251911234567):'},
    'name_too_short':  {'am': '❌ ስምዎ ቢያንስ 2 ፊደላት ሊኖሩት ይገባል። ዳግም ይሞክሩ:',
                        'en': '❌ Name must be at least 2 characters. Try again:',
                        'ar': '❌ يجب أن يحتوي الاسم على حرفين على الأقل. حاول مجدداً:'},
    'addr_too_short':  {'am': '❌ አድራሻ ቢያንስ 5 ፊደላት ሊኖሩት ይገባል። ዳግም ይሞክሩ:',
                        'en': '❌ Address must be at least 5 characters. Try again:',
                        'ar': '❌ يجب أن يحتوي العنوان على 5 أحرف على الأقل. حاول مجدداً:'},
    'open_website':    {'am': '🌐 ድህረ-ገጽ ክፈት','en': '🌐 Open Website','ar': '🌐 فتح الموقع'},
    'my_orders_title':{'am': 'ትዕዛዞቼ', 'en': 'My Orders','ar': 'طلباتي'},
    'branches_title': {'am': 'ቅርንጫፎቻችን','en': 'Our Branches','ar': 'فروعنا'},
    'wishlist_title': {'am': 'ምኞቴ ዝርዝር','en': 'My Wishlist','ar': 'قائمة أمنياتي'},
    'wishlist_hint':  {'am': 'ምርቱን ለማየት ስሙን ይጫኑ | 💔 ለማስወጣት',
                       'en': 'Tap name to view | 💔 to remove',
                       'ar': 'اضغط الاسم للعرض | 💔 للإزالة'},
    'products_hint':  {'am': 'ምርቱን ለማየት ከታች ያለውን አዝራር ይጫኑ 👇',
                       'en': 'Tap a product button below to view details 👇',
                       'ar': 'اضغط على زر المنتج أدناه للتفاصيل 👇'},
    'search_results': {'am': 'ውጤቶች',  'en': 'Results',  'ar': 'النتائج'},
    'products_count': {'am': 'ምርቶች',  'en': 'products', 'ar': 'منتجات'},
    'view_website':   {'am': '🌐 ድህረ-ገጽ ላይ እይ','en': '🌐 View on Website','ar': '🌐 عرض على الموقع'},
    'back_to_list':   {'am': '◀️ ዝርዝር ተመለስ',  'en': '◀️ Back to List',  'ar': '◀️ العودة للقائمة'},
    'account_linked': {'am': 'መለያ ተገናኝቷል! 10% ቅናሽ ይሰጥዎታል።',
                       'en': 'Account linked! 10% discount applied.',
                       'ar': 'تم ربط الحساب! سيتم تطبيق خصم 10%.'},
    'account_linked_icon': {'am': '✅', 'en': '✅', 'ar': '✅'},
    'unknown_cmd':    {'am': '❓ ያልታወቀ ትዕዛዝ። /start ይጠቀሙ።',
                       'en': '❓ Unknown command. Use /start.',
                       'ar': '❓ أمر غير معروف. استخدم /start.'},
}

def _(uid: int, key: str, **kwargs) -> str:
    lang = _get_state(uid).get('lang', 'am')
    entry = T.get(key, {})
    # Fallback chain: requested lang → en → am → raw key
    text = entry.get(lang) or entry.get('en') or entry.get('am') or key
    return text.format(**kwargs) if kwargs else text


def _p_name(p: dict, lang: str) -> str:
    """Return the localised product name for the given language."""
    if lang == 'am':
        return p.get('name_am') or p.get('name', '')
    return p.get('name', '')


def _status_label(lang: str, status: str) -> str:
    """Return a localised order-status label, falling back to en then am."""
    labels = T['status_labels']
    return (labels.get(lang) or labels.get('en') or labels.get('am') or {}).get(status, status)


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
         InlineKeyboardButton(t('orders'),     callback_data='menu:orders')],
        [InlineKeyboardButton(t('wishlist'),   callback_data='menu:wishlist'),
         InlineKeyboardButton(t('branches'),   callback_data='menu:branches')],
        [InlineKeyboardButton(t('account'),    callback_data='menu:account'),
         InlineKeyboardButton(t('contact'),    callback_data='menu:contact')],
        [InlineKeyboardButton(t('language'),   callback_data='menu:language')],
    ]
    # Add website button if URL is available
    site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL
    if site:
        rows.append([InlineKeyboardButton(t('open_website'), url=f'https://{site}')])
    return InlineKeyboardMarkup(rows)


def _back_account(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_(uid, 'account'), callback_data='menu:account')],
        [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
    ])

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

def _db_get_branches():
    from database.db import get_db
    db = get_db()
    return db.execute(
        "SELECT name, name_am, address, address_am, phone, working_hours "
        "FROM branches WHERE is_active=1 ORDER BY sort_order"
    ).fetchall()

def _db_get_orders_by_phone(phone: str):
    from database.db import get_db
    db = get_db()
    phone = phone.strip()
    rows = db.execute(
        "SELECT order_number, status, total, created_at "
        "FROM orders WHERE shipping_phone=%s OR shipping_phone=%s "
        "ORDER BY created_at DESC LIMIT 10",
        (phone, phone.replace('+', ''))
    ).fetchall()
    return rows

def _db_register_user(name: str, phone: str, email: str | None, password: str):
    """Create a customer account. Returns 'ok', 'dup', or 'err'."""
    from database.db import get_db, commit_or_rollback
    from werkzeug.security import generate_password_hash
    import random, string
    db = get_db()
    try:
        # Check duplicate phone or email
        phone = phone.strip()
        email = email.strip().lower() if email and email.lower() != 'skip' else None
        dup = db.execute(
            "SELECT id FROM users WHERE phone=%s" + (" OR email=%s" if email else ""),
            (phone, email) if email else (phone,)
        ).fetchone()
        if dup:
            return 'dup'
        username = 'tg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        pw_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, full_name, phone, email, password_hash, is_admin, is_active, created_at) "
            "VALUES (%s,%s,%s,%s,%s,0,1,NOW())",
            (username, name.strip(), phone, email or '', pw_hash)
        )
        commit_or_rollback(db)
        return 'ok'
    except Exception as e:
        log.error(f"[Register] {e}")
        return 'err'

def _db_user_exists_by_phone(phone: str) -> bool:
    from database.db import get_db
    db = get_db()
    row = db.execute(
        "SELECT id FROM users WHERE phone=%s AND is_admin=0", (phone.strip(),)
    ).fetchone()
    return row is not None

def _db_get_user_profile(phone: str) -> dict | None:
    """Return full profile dict for a customer by phone, including order stats."""
    from database.db import get_db
    db = get_db()
    phone = phone.strip()
    row = db.execute(
        "SELECT id, full_name, phone, email, loyalty_points, created_at, profile_photo "
        "FROM users WHERE (phone=%s OR phone=%s) AND is_admin=0 LIMIT 1",
        (phone, phone.lstrip('+'))
    ).fetchone()
    if not row:
        return None
    profile = dict(row)
    # order count
    try:
        cnt = db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=%s", (profile['id'],)
        ).fetchone()
        profile['order_count'] = int(cnt[0]) if cnt else 0
    except Exception:
        profile['order_count'] = 0
    return profile

def _db_update_user_field(phone: str, field: str, value: str) -> bool:
    """Update a single safe field on the users table by phone. Returns True on success."""
    allowed = {'full_name', 'phone'}
    if field not in allowed:
        return False
    from database.db import get_db, commit_or_rollback
    db = get_db()
    try:
        db.execute(
            f"UPDATE users SET {field}=%s, updated_at=NOW() WHERE phone=%s AND is_admin=0",
            (value.strip(), phone.strip())
        )
        commit_or_rollback(db)
        return True
    except Exception as e:
        log.error(f"[UpdateUser] {e}")
        return False

def _db_check_coupon(code: str) -> dict | None:
    """Validate a coupon code. Returns {'discount_percent': N, 'id': id} or None."""
    from database.db import get_db
    db = get_db()
    try:
        row = db.execute(
            """SELECT id, discount_percent FROM coupons
               WHERE code = %s AND is_active = 1
                 AND (expires_at IS NULL OR expires_at > NOW())
                 AND (max_uses IS NULL OR used_count < max_uses)
               LIMIT 1""",
            (code.strip().upper(),)
        ).fetchone()
        return dict(row) if row else None
    except Exception as e:
        log.warning(f"[Coupon] {e}")
        return None


def _db_get_user_by_phone_link(phone: str) -> dict | None:
    """Look up a user by phone for linking (same as get_profile but lighter)."""
    return _db_get_user_profile(phone)

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

        # Apply coupon discount if present
        coupon_pct   = int(user_data.get('coupon_discount', 0))
        discount_amt = round(subtotal * coupon_pct / 100, 2) if coupon_pct else 0.0
        discounted   = subtotal - discount_amt

        shipping = 0 if discounted >= FREE_SHIPPING else SHIPPING_COST
        total    = discounted + shipping

        coupon_note = ''
        if user_data.get('coupon_code'):
            coupon_note = f" | Coupon: {user_data['coupon_code']} (−{coupon_pct}%)"

        order_data = {
            'user_id': None,
            'customer_name': user_data.get('name', ''),
            'customer_phone': user_data.get('phone', ''),
            'customer_email': user_data.get('email', ''),
            'shipping_address': user_data.get('address', ''),
            'notes': f"Telegram Bot Order | @{user_data.get('username', 'N/A')}{coupon_note}",
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
    name = _p_name(p, lang)
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
            _(uid, 'prev'),
            callback_data=_prod_cb(pp['id'], kind, cat_id, idx - 1, prev_page)))
    if 0 <= idx < len(products) - 1:
        np_ = products[idx + 1]
        next_page = (idx + 1) // PRODUCTS_PER_PAGE
        nav.append(InlineKeyboardButton(
            _(uid, 'next'),
            callback_data=_prod_cb(np_['id'], kind, cat_id, idx + 1, next_page)))
    if nav:
        rows.append(nav)

    # ── Cart + Wishlist buttons ──────────────────────────────────────────────
    cart_lbl = _(uid, 'remove') if in_cart else _(uid, 'add_cart')
    cart_cb  = f'cart:remove:{pid}' if in_cart else f'cart:add:{pid}'
    wl = _get_state(uid).get('wishlist', [])
    in_wish = pid in wl
    wish_lbl = _(uid, 'wish_remove') if in_wish else _(uid, 'wish_add')
    rows.append([
        InlineKeyboardButton(cart_lbl, callback_data=cart_cb),
        InlineKeyboardButton(wish_lbl, callback_data=f'wish:toggle:{pid}'),
    ])

    # ── View on website + Share ──────────────────────────────────────────────
    if site:
        product_url = f'https://{site}/product/{pid}'
        rows.append([
            InlineKeyboardButton(_(uid, 'view_website'), url=product_url),
            InlineKeyboardButton(_(uid, 'share'), url=f'https://t.me/share/url?url={product_url}'),
        ])

    # ── Back to list + Cart ─────────────────────────────────────────────────
    rows.append([
        InlineKeyboardButton(_(uid, 'back_to_list'), callback_data=f'back_list:{kind}:{cat_id}:{page}'),
        InlineKeyboardButton('🛒 ' + _(uid, 'cart'), callback_data='menu:cart'),
    ])
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    return InlineKeyboardMarkup(rows)


def _cart_text(uid: int) -> str:
    state = _get_state(uid)
    cart = state.get('cart', {})
    if not cart:
        return _(uid, 'empty_cart')
    lang = state.get('lang', 'am')
    lines = [f"🛒 *{_(uid, 'cart')}*\n"]
    subtotal = 0.0
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if not p:
            continue
        price = float(p['price'])
        line_total = price * qty
        subtotal += line_total
        lines.append(f"• {_p_name(p, lang)} × {qty} = {_fmt_price(line_total)}")
    
    shipping = 0 if subtotal >= FREE_SHIPPING else SHIPPING_COST
    lines.append(f"\n{_(uid,'subtotal')}: {_fmt_price(subtotal)}")
    ship_label = _(uid, 'free') if shipping == 0 else _fmt_price(shipping)
    lines.append(f"{_(uid,'shipping')}: {ship_label}")
    lines.append(f"*{_(uid,'total')}: {_fmt_price(subtotal + shipping)}*")
    return '\n'.join(lines)


def _cart_keyboard(uid: int) -> InlineKeyboardMarkup:
    state = _get_state(uid)
    cart = state.get('cart', {})
    lang = state.get('lang', 'am')
    rows = []
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if not p:
            continue
        nm = _p_name(p, lang)
        name = (nm[:18] + '…') if len(nm) > 18 else nm
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
    cart  = state.get('cart', {})
    lang  = state.get('lang', 'am')

    items_lines = []
    subtotal = 0.0
    for pid_str, qty in cart.items():
        p = _db_get_product(int(pid_str))
        if p:
            price = float(p['price'])
            subtotal += price * qty
            items_lines.append(f"  • {_p_name(p, lang)} × {qty} — {_fmt_price(price * qty)}")

    # Coupon discount
    coupon_pct  = int(order.get('coupon_discount', 0))
    discount_amt = round(subtotal * coupon_pct / 100, 2) if coupon_pct else 0.0
    discounted   = subtotal - discount_amt

    shipping    = 0 if discounted >= FREE_SHIPPING else SHIPPING_COST
    total       = discounted + shipping
    ship_label  = _(uid, 'free') if shipping == 0 else _fmt_price(shipping)

    lines = [
        f"📋 *{_(uid, 'order_summary_title')}*\n",
        f"👤 {_(uid, 'order_name')}: {order.get('name','')}",
        f"📱 {_(uid, 'order_phone')}: {order.get('phone','')}",
        f"🏠 {_(uid, 'order_address')}: {order.get('address','')}",
        f"\n{_(uid, 'order_items')}:",
        *items_lines,
        f"\n{_(uid,'subtotal')}: {_fmt_price(subtotal)}",
    ]
    if coupon_pct:
        lines.append(f"🏷️ {_(uid, 'order_discount')} ({coupon_pct}%): −{_fmt_price(discount_amt)}")
    lines += [
        f"{_(uid,'shipping')}: {ship_label}",
        f"*{_(uid,'total')}: {_fmt_price(total)}*",
    ]
    if order.get('coupon_code'):
        lines.append(f"🎟️ {_(uid, 'order_coupon')}: `{order['coupon_code']}`")
    return '\n'.join(lines)


def _order_summary_keyboard(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_(uid, 'order_confirm'), callback_data='order:confirm')],
        [InlineKeyboardButton(_(uid, 'order_edit_btn'), callback_data='order:edit'),
         InlineKeyboardButton(_(uid, 'order_cancel_btn'), callback_data='order:cancel')],
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
def _user_profile_photo_url(profile: dict) -> str | None:
    """Convert a stored profile_photo path to a full HTTPS URL."""
    site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL
    if not site:
        return None
    photo = (profile.get('profile_photo') or '').strip()
    if not photo:
        return None
    if photo.startswith(('http://', 'https://')):
        return photo
    if photo.startswith('uploads/') or photo.startswith('images/'):
        return f"https://{site}/static/{photo}"
    return f"https://{site}/static/uploads/users/{photo}"


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = _get_state(uid)
    state['username'] = update.effective_user.username or str(uid)

    # Personalized greeting if the user already linked an account
    phone   = state.get('reg_phone', '')
    profile = _db_get_user_profile(phone) if phone else None
    lang    = state.get('lang', 'am')

    if profile:
        first_name = (profile.get('full_name') or '').split()[0]
        if lang == 'am':
            text = (f"👗 *እንኳን ደህና መጡ, {first_name}!*\n\n"
                    "ሰሚራ ፋሽን ላይ ምርቶቻችንን ይፈልጉ፣ ይዘዙ፣ ይከታተሉ።")
        elif lang == 'ar':
            text = (f"👗 *مرحباً بعودتك، {first_name}!*\n\n"
                    "تصفح، اطلب وتابع مشترياتك في سميرا فاشن.")
        else:
            text = (f"👗 *Welcome back, {first_name}!*\n\n"
                    "Browse, order and track your purchases with ease.")
    else:
        text = _(uid, 'welcome')

    # Try to show shop logo/banner with the greeting
    site = os.environ.get('REPLIT_DEV_DOMAIN', '') or SITE_URL
    logo_url = f"https://{site}/static/images/mylogo.png" if site else None
    if logo_url:
        try:
            await update.message.reply_photo(photo=logo_url, caption=text,
                                             parse_mode=ParseMode.MARKDOWN,
                                             reply_markup=_main_menu_keyboard(uid))
            return ConversationHandler.END
        except TelegramError:
            pass

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = _get_state(uid).get('lang', 'am')
    if lang == 'am':
        text = ('*🤖 ሰሚራ ፋሽን ቦት — ትዕዛዞች*\n\n'
                '🛍️ *ምርቶች*\n'
                '/products — ሁሉም ምርቶች\n'
                '/cart — ቅርጫቴ\n'
                '/track — ትዕዛዝ ክትትል\n\n'
                '👤 *መለያ*\n'
                '/account — የመለያ ዝርዝር\n'
                '/orders — ትዕዛዞቼ\n'
                '/wishlist — ምኞቴ\n\n'
                '📍 *ሌሎች*\n'
                '/branches — ቅርንጫፎቻችን\n'
                '/language — ቋንቋ ቀይር\n'
                '/cancel — ወቅታዊ ምርጫ ሰርዝ\n'
                '/start — ዋና ምናሌ')
    elif lang == 'ar':
        text = ('*🤖 بوت سميرا فاشن — الأوامر*\n\n'
                '🛍️ *التسوق*\n'
                '/products — تصفح المنتجات\n'
                '/cart — سلتي\n'
                '/track — تتبع طلب\n\n'
                '👤 *الحساب*\n'
                '/account — ملفي الشخصي\n'
                '/orders — طلباتي\n'
                '/wishlist — قائمة الأمنيات\n\n'
                '📍 *المزيد*\n'
                '/branches — فروعنا\n'
                '/language — تغيير اللغة\n'
                '/cancel — إلغاء الإجراء الحالي\n'
                '/start — القائمة الرئيسية')
    else:
        text = ('*🤖 Semira Fashion Bot — Commands*\n\n'
                '🛍️ *Shopping*\n'
                '/products — Browse products\n'
                '/cart — View my cart\n'
                '/track — Track an order\n\n'
                '👤 *Account*\n'
                '/account — My profile\n'
                '/orders — My orders\n'
                '/wishlist — My wishlist\n\n'
                '📍 *More*\n'
                '/branches — Our branches\n'
                '/language — Change language\n'
                '/cancel — Cancel current action\n'
                '/start — Main menu')
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

    elif data == 'menu:orders':
        await _safe_edit_text(query, _(uid, 'orders_prompt'),
                              reply_markup=_back_home(uid))
        return AWAIT_ORDERS_PHONE

    elif data == 'menu:wishlist':
        await _show_wishlist(query, uid)

    elif data == 'menu:branches':
        await _show_branches(query, uid)

    elif data == 'menu:account':
        await _show_account(query, uid)

    elif data == 'account:edit_name':
        await _safe_edit_text(query, _(uid, 'edit_name_prompt'), reply_markup=_back_home(uid))
        return AWAIT_EDIT_NAME

    elif data == 'account:edit_phone':
        await _safe_edit_text(query, _(uid, 'edit_phone_prompt'), reply_markup=_back_home(uid))
        return AWAIT_EDIT_PHONE

    elif data == 'account:orders':
        state = _get_state(uid)
        phone = state.get('reg_phone', '') or state.get('order', {}).get('phone', '')
        if phone:
            orders = _db_get_orders_by_phone(phone)
            lang = state.get('lang', 'am')
            if not orders:
                await _safe_edit_text(query, _(uid, 'no_orders'), reply_markup=_back_account(uid))
            else:
                lines = [f"📦 *{_(uid, 'my_orders_title')}* ({len(orders)})\n"]
                for o in orders:
                    num    = o.get('order_number', '')
                    status = o.get('status', '')
                    total  = _fmt_price(o.get('total', 0))
                    date   = o.get('created_at', '')
                    if date and hasattr(date, 'strftime'):
                        date = date.strftime('%Y-%m-%d')
                    status_lbl = _status_label(lang, status)
                    lines.append(f"🔢 `{num}` — {status_lbl}")
                    lines.append(f"   💰 {total}  |  🕐 {date}\n")
                await _safe_edit_text(query, '\n'.join(lines),
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=_back_account(uid))
        else:
            await _safe_edit_text(query, _(uid, 'orders_prompt'), reply_markup=_back_home(uid))
            return AWAIT_ORDERS_PHONE

    elif data == 'account:link':
        await _safe_edit_text(query, _(uid, 'link_account'), reply_markup=_back_home(uid))
        return AWAIT_ORDERS_PHONE   # re-use phone-input state; handler checks & links

    elif data == 'reg:start':
        await _safe_edit_text(query, _(uid, 'reg_name'), reply_markup=_back_home(uid))
        return AWAIT_REG_NAME

    # ── wishlist toggle ──
    elif data.startswith('wish:toggle:'):
        pid = int(data.split(':')[2])
        wl = _get_state(uid).setdefault('wishlist', [])
        if pid in wl:
            wl.remove(pid)
            await query.answer(_(uid, 'wish_removed'))
        else:
            wl.append(pid)
            await query.answer(_(uid, 'wish_added'))
        # Refresh the product detail to update the button label
        last = _get_state(uid).get('last_prod', {})
        await _edit_product_detail(query, uid, pid,
                                   kind=last.get('kind', 'all'),
                                   cat_id=last.get('cat_id', 0),
                                   idx=last.get('idx', -1),
                                   page=last.get('page', 0))

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

    # ── order flow (must come BEFORE the generic cart: catch-all) ──
    elif data == 'cart:checkout':
        cart = _get_state(uid).get('cart', {})
        if not cart:
            await _safe_edit_text(query, _(uid, 'empty_cart'),
                                  reply_markup=_back_home(uid))
            return ConversationHandler.END
        # Clear any stale order data before starting fresh
        _get_state(uid)['order'] = {}
        await _safe_edit_text(query, _(uid, 'name_prompt'),
                              reply_markup=_back_home(uid))
        return AWAIT_NAME

    elif data == 'order:confirm':
        return await _confirm_order(query, uid, ctx)

    elif data == 'order:cancel':
        await _safe_edit_text(query, _(uid, 'cancelled'),
                              reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END

    elif data == 'order:edit':
        # Let user go back to cart to edit before re-checking out
        await _safe_edit_text(query, _cart_text(uid), parse_mode=ParseMode.MARKDOWN,
                              reply_markup=_cart_keyboard(uid))
        return ConversationHandler.END

    # ── cart actions ──
    elif data.startswith('cart:'):
        await _handle_cart_action(query, uid, data, ctx)

    return ConversationHandler.END


# ── product list helpers ──
def _products_page_kb_and_text(uid: int, products: list, page: int,
                                kind: str, cat_id: int):
    """Return (text, keyboard, photo_url) for a product list page."""
    cid    = cat_id or 0
    prefix = f'{kind}:{cid}' if cid else kind
    lang   = _get_state(uid).get('lang', 'am')

    # Build items with full navigation context embedded in callback_data
    all_items = []
    for i, p in enumerate(products):
        nm = _p_name(p, lang)
        label_btn = (nm[:26] + '…') if len(nm) > 26 else nm
        all_items.append((label_btn, _prod_cb(p['id'], kind, cid, i, i // PRODUCTS_PER_PAGE)))

    title = {'all': '🛍️', 'new': '🆕', 'featured': '⭐', 'cat': '🗂️'}.get(kind, '🛍️')
    label = _(uid, kind if kind in T else 'products')
    total = len(products)
    pages = (total + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    pg_info = f'({page+1}/{pages})' if pages > 1 else ''

    # First product on this page — identify it in the caption so the cover photo makes sense
    start = page * PRODUCTS_PER_PAGE
    page_products = products[start:start + PRODUCTS_PER_PAGE]
    photo_url = None
    cover_name = ''
    for pp in page_products:
        url = _product_image_url(pp)
        if url:
            photo_url = url
            cover_name = _p_name(pp, lang)
            break

    hint = _(uid, 'products_hint')
    cover_line = f'📸 _{cover_name}_\n' if cover_name else ''
    text = f"{title} *{label}* {pg_info}\n{cover_line}_{total} {_(uid, 'products_count')}_\n{hint}"

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
    lang = _get_state(uid).get('lang', 'am')
    items = [((c.get('name_am') or c['name']) if lang == 'am' else c['name'],
              f'cat:{c["id"]}:page:0') for c in cats]
    kb = _paginated_keyboard(uid, items, page, 'catlist')
    await _safe_edit_text(query, _(uid, 'categories'),
                          parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def _show_language_menu(msg, uid: int):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🇪🇹 አማርኛ', callback_data='lang:am'),
         InlineKeyboardButton('🇬🇧 English', callback_data='lang:en'),
         InlineKeyboardButton('🇸🇦 العربية', callback_data='lang:ar')],
        [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
    ])
    await msg.reply_text('🌐 Language / ቋንቋ / اللغة', reply_markup=kb)


async def _edit_language_menu(query, uid: int):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🇪🇹 አማርኛ', callback_data='lang:am'),
         InlineKeyboardButton('🇬🇧 English', callback_data='lang:en'),
         InlineKeyboardButton('🇸🇦 العربية', callback_data='lang:ar')],
        [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
    ])
    await _safe_edit_text(query, '🌐 Language / ቋንቋ / اللغة', reply_markup=kb)


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
    items = []
    for i, p in enumerate(results):
        nm = _p_name(p, lang)
        label_btn = (nm[:26] + '…') if len(nm) > 26 else nm
        items.append((label_btn, _prod_cb(p['id'], 'all', 0, i, 0)))
    kb = _paginated_keyboard(uid, items, 0, 'search_res')
    text = f"🔍 {_(uid, 'search_results')} ({len(results)})"
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
    if len(name) < 2:
        await update.message.reply_text(_(uid, 'name_too_short'))
        return AWAIT_NAME
    _get_state(uid).setdefault('order', {})['name'] = name
    await update.message.reply_text(_(uid, 'phone_prompt'))
    return AWAIT_PHONE


def _is_valid_phone(phone: str) -> bool:
    """Accept Ethiopian-style phone numbers: 09xxxxxxxx, +251xxxxxxxxx, 251xxxxxxxxx."""
    import re
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(r'^(?:(?:\+251|251)[7-9]\d{8}|0[7-9]\d{8})
    uid  = update.effective_user.id
    text = update.message.text.strip()
    state = _get_state(uid)

    if text.lower() != 'skip' and text:
        coupon = _db_check_coupon(text)
        if coupon:
            pct = coupon.get('discount_percent', 0)
            state['order']['coupon_code']     = text.upper()
            state['order']['coupon_discount'] = pct
            await update.message.reply_text(_(uid, 'coupon_ok', pct=pct))
        else:
            await update.message.reply_text(_(uid, 'coupon_bad'))
            # Let them try again or skip — show summary anyway after bad coupon
    # Show order summary
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
    status_lbl = _status_label(lang, status_raw)
    items = _db_get_order_items(order['id'])
    items_lines = [f"  • {it.get('product_name', it.get('name','?'))} × {it.get('quantity',1)}"
                   for it in (items or [])]

    created = order.get('created_at', '')
    if created and hasattr(created, 'strftime'):
        created = created.strftime('%Y-%m-%d %H:%M')

    lines = [
        f"📦 *{_(uid, 'order_detail_title')}*\n",
        f"🔢 {_(uid, 'order_number_label')}: `{order.get('order_number','')}`",
        f"📊 {_(uid, 'order_status')}: {status_lbl}",
        f"💰 {_(uid, 'order_total')}: {_fmt_price(order.get('total', order.get('total_amount', 0)))}",
        f"🕐 {_(uid, 'order_date')}: {created}",
    ]
    if items_lines:
        lines.append(f"\n{_(uid, 'order_items')}:")
        lines.extend(items_lines)

    await update.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def _confirm_order(query, uid: int, ctx):
    state = _get_state(uid)
    cart = state.get('cart', {})
    if not cart:
        await _safe_edit_text(query, _(uid, 'empty_cart'),
                              reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END
    order_data = state.get('order', {})
    order_data['username'] = state.get('username', str(uid))

    order_number = _db_place_order(cart, order_data)
    if order_number:
        state['cart'] = {}   # clear cart
        state['order'] = {}  # clear order draft
        text = (_(uid, 'order_ok') +
                f"\n\n🔢 {_(uid, 'order_number_title')}: `{order_number}`\n\n"
                f"_{_(uid, 'track_prompt')}_")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(_(uid, 'track_my_order'), callback_data='menu:track')],
            [InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')],
        ])
        await _safe_edit_text(query, text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        # Notify admin
        await _notify_admin_new_order(ctx, uid, order_number, order_data, cart)
    else:
        await _safe_edit_text(query, _(uid, 'order_err'),
                              reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def _notify_admin_new_order(ctx, uid: int, order_number, order_data: dict, cart: dict):
    if not ADMIN_CHAT_ID:
        return
    try:
        bot = ctx.bot
        coupon = order_data.get('coupon_code', '')
        discount = order_data.get('coupon_discount', 0)
        lines = [
            f"🛍️ *New Telegram Order!*",
            f"📦 Order: `{order_number}`",
            f"👤 {order_data.get('name','')}",
            f"📱 {order_data.get('phone','')}",
            f"🏠 {order_data.get('address','')}",
            f"📲 @{order_data.get('username', uid)}",
        ]
        if coupon:
            lines.append(f"🏷️ Coupon: `{coupon}` (−{discount}%)")
        for pid_str, qty in cart.items():
            p = _db_get_product(int(pid_str))
            if p:
                lines.append(f"  • {p['name']} × {qty}")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='\n'.join(lines),
                               parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.warning(f"[TelegramBot] admin notify failed: {e}")


def _build_profile_text_kb(uid: int, profile: dict) -> tuple:
    """Build (text, keyboard) for a registered user's profile view."""
    name   = profile.get('full_name') or '—'
    ph     = profile.get('phone') or '—'
    email  = profile.get('email') or '—'
    points = int(profile.get('loyalty_points') or 0)
    orders = profile.get('order_count', 0)
    since  = profile.get('created_at', '')
    if since and hasattr(since, 'strftime'):
        since = since.strftime('%Y-%m-%d')

    lines = [
        f"{_(uid, 'prof_title')}\n",
        f"{_(uid, 'prof_name')}:  {name}",
        f"{_(uid, 'prof_phone')}:  `{ph}`",
        f"{_(uid, 'prof_email')}:  {email}",
        f"",
        f"{_(uid, 'prof_orders')}:  {orders}",
        f"{_(uid, 'prof_points')}:  {points}",
        f"{_(uid, 'prof_discount')}:  10% ✅",
    ]
    if since:
        lines.append(f"{_(uid, 'prof_since')}:  {since}")

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(_(uid, 'prof_edit_name'),  callback_data='account:edit_name'),
         InlineKeyboardButton(_(uid, 'prof_edit_phone'), callback_data='account:edit_phone')],
        [InlineKeyboardButton(_(uid, 'prof_my_orders'),  callback_data='account:orders')],
        [InlineKeyboardButton(_(uid, 'main_menu'),       callback_data='menu:home')],
    ])
    return '\n'.join(lines), kb


def _not_registered_kb(uid: int) -> tuple:
    """Build (text, keyboard) for an unregistered user's account view."""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(_(uid, 'reg_start_btn'), callback_data='reg:start')],
        [InlineKeyboardButton(_(uid, 'link_btn'),      callback_data='account:link')],
        [InlineKeyboardButton(_(uid, 'main_menu'),     callback_data='menu:home')],
    ])
    return _(uid, 'not_registered'), kb


# ── wishlist display ──
async def _show_account(query, uid: int):
    """Show full profile if registered, registration/link prompt if not."""
    state = _get_state(uid)
    phone = state.get('reg_phone', '') or state.get('order', {}).get('phone', '')
    profile = _db_get_user_profile(phone) if phone else None

    if profile:
        text, kb = _build_profile_text_kb(uid, profile)
        # Try to show profile photo
        photo_url = _user_profile_photo_url(profile)
        if photo_url:
            try:
                await query.message.reply_photo(photo=photo_url, caption=text,
                                                parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
                try:
                    await query.message.delete()
                except Exception:
                    pass
                return
            except TelegramError:
                pass
        await _safe_edit_text(query, text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    else:
        text, kb = _not_registered_kb(uid)
        await _safe_edit_text(query, text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def _show_account_from_msg(msg, uid: int):
    """Same as _show_account but responds to a plain command message."""
    state = _get_state(uid)
    phone = state.get('reg_phone', '') or state.get('order', {}).get('phone', '')
    profile = _db_get_user_profile(phone) if phone else None

    if profile:
        text, kb = _build_profile_text_kb(uid, profile)
        photo_url = _user_profile_photo_url(profile)
        if photo_url:
            try:
                await msg.reply_photo(photo=photo_url, caption=text,
                                      parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
                return
            except TelegramError:
                pass
        await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    else:
        text, kb = _not_registered_kb(uid)
        await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def _show_wishlist(query, uid: int):
    wl = _get_state(uid).get('wishlist', [])
    lang = _get_state(uid).get('lang', 'am')
    if not wl:
        await _safe_edit_text(query, _(uid, 'empty_wish'), reply_markup=_back_home(uid))
        return
    rows = []
    for pid in wl:
        p = _db_get_product(pid)
        if not p:
            continue
        nm = _p_name(p, lang)
        name = (nm[:24] + '…') if len(nm) > 24 else nm
        price = _fmt_price(p['price'])
        rows.append([
            InlineKeyboardButton(f"{name} — {price}",
                                 callback_data=_prod_cb(pid, 'all', 0, -1, 0)),
            InlineKeyboardButton('💔', callback_data=f'wish:toggle:{pid}'),
        ])
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    title = f"💝 *{_(uid, 'wishlist_title')}*"
    hint  = f"_{_(uid, 'wishlist_hint')}_"
    await _safe_edit_text(query, f"{title}\n{hint}", parse_mode=ParseMode.MARKDOWN,
                          reply_markup=InlineKeyboardMarkup(rows))


# ── branches display ──
def _branch_display_name(b: dict, lang: str) -> str:
    if lang == 'am':
        return b.get('name_am') or b.get('name') or ''
    return b.get('name') or b.get('name_am') or ''

def _branch_display_address(b: dict, lang: str) -> str:
    if lang == 'am':
        return b.get('address_am') or b.get('address') or ''
    return b.get('address') or b.get('address_am') or ''

async def _show_branches(query, uid: int):
    branches = _db_get_branches()
    lang = _get_state(uid).get('lang', 'am')
    if not branches:
        await _safe_edit_text(query, _(uid, 'no_branches'), reply_markup=_back_home(uid))
        return
    lines = [f"🏪 *{_(uid, 'branches_title')}*\n"]
    for b in branches:
        name    = _branch_display_name(b, lang)
        address = _branch_display_address(b, lang)
        phone   = b.get('phone') or ''
        hours   = b.get('working_hours') or ''
        lines.append(f"📍 *{name}*")
        if address: lines.append(f"🗺 {address}")
        if phone:   lines.append(f"📞 {phone}")
        if hours:   lines.append(f"🕐 {hours}")
        lines.append('')
    await _safe_edit_text(query, '\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                          reply_markup=_back_home(uid))


# ── new conversation handlers ──
async def on_orders_phone_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    phone = update.message.text.strip()
    lang  = _get_state(uid).get('lang', 'am')

    # If called from account:link — try to link the account first
    profile = _db_get_user_profile(phone)
    if profile:
        _get_state(uid)['reg_phone'] = phone
        await update.message.reply_text(
            f"✅ {_(uid, 'account_linked')}",
            reply_markup=_main_menu_keyboard(uid)
        )
        return ConversationHandler.END

    orders = _db_get_orders_by_phone(phone)
    if not orders:
        await update.message.reply_text(_(uid, 'no_orders'), reply_markup=_main_menu_keyboard(uid))
        return ConversationHandler.END
    lines = [f"📦 *{_(uid, 'my_orders_title')}* ({len(orders)})\n"]
    for o in orders:
        num    = o.get('order_number', '')
        status = o.get('status', '')
        total  = _fmt_price(o.get('total', 0))
        date   = o.get('created_at', '')
        if date and hasattr(date, 'strftime'):
            date = date.strftime('%Y-%m-%d')
        status_lbl = _status_label(lang, status)
        lines.append(f"🔢 `{num}` — {status_lbl}")
        lines.append(f"   💰 {total}  |  🕐 {date}\n")
    await update.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def on_edit_name_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text(_(uid, 'edit_name_prompt'))
        return AWAIT_EDIT_NAME
    phone = _get_state(uid).get('reg_phone', '') or _get_state(uid).get('order', {}).get('phone', '')
    if phone and _db_update_user_field(phone, 'full_name', name):
        await update.message.reply_text(_(uid, 'edit_saved'), reply_markup=_main_menu_keyboard(uid))
    else:
        await update.message.reply_text(_(uid, 'edit_err'), reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def on_edit_phone_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    new_ph   = update.message.text.strip()
    old_ph   = _get_state(uid).get('reg_phone', '') or _get_state(uid).get('order', {}).get('phone', '')
    if old_ph and _db_update_user_field(old_ph, 'phone', new_ph):
        _get_state(uid)['reg_phone'] = new_ph   # update local state too
        await update.message.reply_text(_(uid, 'edit_saved'), reply_markup=_main_menu_keyboard(uid))
    else:
        await update.message.reply_text(_(uid, 'edit_err'), reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


async def on_reg_name_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text(_(uid, 'reg_name'))
        return AWAIT_REG_NAME
    ctx.user_data['reg'] = {'name': name}
    await update.message.reply_text(_(uid, 'reg_phone'))
    return AWAIT_REG_PHONE


async def on_reg_phone_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    phone = update.message.text.strip()
    ctx.user_data.setdefault('reg', {})['phone'] = phone
    _get_state(uid)['reg_phone'] = phone
    await update.message.reply_text(_(uid, 'reg_email'))
    return AWAIT_REG_EMAIL


async def on_reg_email_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    email = update.message.text.strip()
    ctx.user_data.setdefault('reg', {})['email'] = email
    await update.message.reply_text(_(uid, 'reg_pass'))
    return AWAIT_REG_PASS


async def on_reg_pass_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    password = update.message.text.strip()
    if len(password) < 8:
        await update.message.reply_text(_(uid, 'reg_pass'))
        return AWAIT_REG_PASS
    reg = ctx.user_data.get('reg', {})
    result = _db_register_user(
        name=reg.get('name', ''),
        phone=reg.get('phone', ''),
        email=reg.get('email', ''),
        password=password,
    )
    if result == 'ok':
        await update.message.reply_text(_(uid, 'reg_ok'), reply_markup=_main_menu_keyboard(uid))
    elif result == 'dup':
        await update.message.reply_text(_(uid, 'reg_dup'), reply_markup=_main_menu_keyboard(uid))
    else:
        await update.message.reply_text(_(uid, 'reg_err'), reply_markup=_main_menu_keyboard(uid))
    ctx.user_data.pop('reg', None)
    return ConversationHandler.END


# ───────────────────────── new shortcut command handlers ─────────────────────────
async def cmd_account(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await _show_account_from_msg(update.message, uid)
    return ConversationHandler.END


async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    state = _get_state(uid)
    phone = state.get('reg_phone', '') or state.get('order', {}).get('phone', '')
    lang  = state.get('lang', 'am')
    if phone:
        orders = _db_get_orders_by_phone(phone)
        if not orders:
            await update.message.reply_text(_(uid, 'no_orders'), reply_markup=_main_menu_keyboard(uid))
        else:
            lines = [f"📦 *{_(uid, 'my_orders_title')}* ({len(orders)})\n"]
            for o in orders:
                num    = o.get('order_number', '')
                status = o.get('status', '')
                total  = _fmt_price(o.get('total', 0))
                date   = o.get('created_at', '')
                if date and hasattr(date, 'strftime'):
                    date = date.strftime('%Y-%m-%d')
                status_lbl = _status_label(lang, status)
                lines.append(f"🔢 `{num}` — {status_lbl}")
                lines.append(f"   💰 {total}  |  🕐 {date}\n")
            await update.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=_main_menu_keyboard(uid))
    else:
        await update.message.reply_text(_(uid, 'orders_prompt'), reply_markup=_back_home(uid))
        return AWAIT_ORDERS_PHONE
    return ConversationHandler.END


async def cmd_wishlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    lang = _get_state(uid).get('lang', 'am')
    wl   = _get_state(uid).get('wishlist', [])
    if not wl:
        await update.message.reply_text(_(uid, 'empty_wish'), reply_markup=_back_home(uid))
        return ConversationHandler.END
    rows = []
    for pid in wl:
        p = _db_get_product(pid)
        if not p:
            continue
        nm    = _p_name(p, lang)
        name  = (nm[:24] + '…') if len(nm) > 24 else nm
        price = _fmt_price(p['price'])
        rows.append([
            InlineKeyboardButton(f"{name} — {price}", callback_data=_prod_cb(pid, 'all', 0, -1, 0)),
            InlineKeyboardButton('💔', callback_data=f'wish:toggle:{pid}'),
        ])
    rows.append([InlineKeyboardButton(_(uid, 'main_menu'), callback_data='menu:home')])
    title = f"💝 *{_(uid, 'wishlist_title')}*"
    hint  = f"_{_(uid, 'wishlist_hint')}_"
    await update.message.reply_text(f"{title}\n{hint}", parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=InlineKeyboardMarkup(rows))
    return ConversationHandler.END


async def cmd_branches(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    branches = _db_get_branches()
    lang     = _get_state(uid).get('lang', 'am')
    if not branches:
        await update.message.reply_text(_(uid, 'no_branches'), reply_markup=_back_home(uid))
        return ConversationHandler.END
    lines = [f"🏪 *{_(uid, 'branches_title')}*\n"]
    for b in branches:
        name    = _branch_display_name(b, lang)
        address = _branch_display_address(b, lang)
        phone   = b.get('phone') or ''
        hours   = b.get('working_hours') or ''
        lines.append(f"📍 *{name}*")
        if address: lines.append(f"🗺 {address}")
        if phone:   lines.append(f"📞 {phone}")
        if hours:   lines.append(f"🕐 {hours}")
        lines.append('')
    await update.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=_back_home(uid))
    return ConversationHandler.END


# ── fallback for unexpected text ──
async def on_unknown_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(_(uid, 'unknown_cmd'), reply_markup=_main_menu_keyboard(uid))
    return ConversationHandler.END


# ───────────────────────── Application builder ─────────────────────────
def build_application() -> Application:
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start',    cmd_start),
            CommandHandler('help',     cmd_help),
            CommandHandler('products', cmd_products),
            CommandHandler('cart',     cmd_cart),
            CommandHandler('track',    cmd_track),
            CommandHandler('language', cmd_language),
            CommandHandler('cancel',   cmd_cancel),
            CommandHandler('account',  cmd_account),
            CommandHandler('orders',   cmd_orders),
            CommandHandler('wishlist', cmd_wishlist),
            CommandHandler('branches', cmd_branches),
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
            AWAIT_COUPON: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_coupon_input),
            ],
            AWAIT_TRACK: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_track_input),
            ],
            AWAIT_ORDERS_PHONE: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_orders_phone_input),
            ],
            AWAIT_REG_NAME: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_reg_name_input),
            ],
            AWAIT_REG_PHONE: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_reg_phone_input),
            ],
            AWAIT_REG_EMAIL: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_reg_email_input),
            ],
            AWAIT_REG_PASS: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_reg_pass_input),
            ],
            AWAIT_EDIT_NAME: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_edit_name_input),
            ],
            AWAIT_EDIT_PHONE: [
                CallbackQueryHandler(on_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_edit_phone_input),
            ],
        },
        fallbacks=[
            CommandHandler('cancel',   cmd_cancel),
            CommandHandler('start',    cmd_start),
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
