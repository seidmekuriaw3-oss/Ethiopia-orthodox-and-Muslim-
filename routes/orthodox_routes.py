"""
Orthodox Tewahedo Routes — SEMIRA FASHION
/orthodox  — main page
/api/orthodox/today  — today's data (JSON)
"""
from flask import Blueprint, render_template, request, jsonify
from routes.shared import get_lang
import datetime
import math

from database.orthodox_data import (
    SAINTS_BY_DAY, ANNUAL_FEASTS, FASTING_SEASONS, WEEKLY_FAST_DAYS,
    PRAYER_HOURS, WUDASE_MARIAM, BIBLE_81_BOOKS, DAILY_PSALM_PLAN,
    ETH_MONTHS, ETH_DAYS
)

orthodox_bp = Blueprint('orthodox', __name__)


# ────────────────────────────────────────────────────────────────
#  Ethiopian calendar conversion helpers
# ────────────────────────────────────────────────────────────────

def gregorian_to_ethiopian(year, month, day):
    """Convert Gregorian date to Ethiopian (Ge'ez) calendar date.

    The Ethiopian leap year is the year whose (year % 4) == 3, so in every
    4-year block the pattern is: 365, 365, 366, 365 days.
    Epoch: Meskerem 1, 1 EC = JDN 1724221.
    """
    # Julian Day Number (proleptic Gregorian)
    a   = (14 - month) // 12
    y   = year + 4800 - a
    m   = month + 12 * a - 3
    jdn = (day + (153 * m + 2) // 5 + 365 * y
           + y // 4 - y // 100 + y // 400 - 32045)

    ETH_EPOCH = 1724221          # JDN of Meskerem 1, 1 EC
    r         = jdn - ETH_EPOCH

    # Each 4-year cycle = 1461 days (3×365 + 1×366).
    # The leap year is the THIRD year of each cycle (year%4 == 3).
    # Cycle layout relative to cycle-start (base year B where B%4 == 1):
    #   year B   : days  0 – 364   (365 days)
    #   year B+1 : days 365 – 729   (365 days)
    #   year B+2 : days 730 – 1095  (366 days, leap)
    #   year B+3 : days 1096 – 1460 (365 days)
    cycle      = r // 1461
    n          = r % 1461
    base_year  = 4 * cycle + 1   # first year of this 4-year cycle

    if n <= 364:
        eth_year     = base_year
        day_of_year  = n
    elif n <= 729:
        eth_year     = base_year + 1
        day_of_year  = n - 365
    elif n <= 1095:
        eth_year     = base_year + 2
        day_of_year  = n - 730
    else:
        eth_year     = base_year + 3
        day_of_year  = n - 1096

    eth_month = day_of_year // 30 + 1
    eth_day   = day_of_year % 30 + 1

    return eth_year, eth_month, eth_day


def _eth_year_start_jdn(eth_year):
    """Return the Julian Day Number of Meskerem 1 for the given Ethiopian year."""
    ETH_EPOCH = 1724221
    return ETH_EPOCH + (eth_year - 1) * 365 + (eth_year - 1) // 4


def is_fasting_day(greg_date):
    """Return a fasting label if today is a weekly or seasonal fast."""
    weekday = greg_date.weekday()   # Mon=0 … Sun=6
    if weekday == 2:
        return "ረቡዕ ጾም (Wednesday Fast)"
    if weekday == 4:
        return "ዓርብ ጾም (Friday Fast)"
    return None


def get_todays_data(greg_date=None):
    """Return a dict with all context for today's Orthodox corner."""
    if greg_date is None:
        greg_date = datetime.date.today()

    eth_year, eth_month, eth_day = gregorian_to_ethiopian(
        greg_date.year, greg_date.month, greg_date.day
    )

    eth_month_name = ETH_MONTHS[eth_month - 1] if 1 <= eth_month <= 13 else "ጷጉሜ"
    eth_day_name   = ETH_DAYS[greg_date.weekday() % 7]   # weekday → Sun=6 adjusted below
    # Python weekday: Mon=0 Sun=6; Ethiopian week starts Sunday
    py_wd = greg_date.weekday()
    # convert to Sun=0 … Sat=6
    eth_wd = (py_wd + 1) % 7

    # Saints of the day
    day_key   = eth_day if 1 <= eth_day <= 30 else 1
    day_saints = SAINTS_BY_DAY.get(day_key, SAINTS_BY_DAY[1])

    # Annual feast for today?
    annual_feast = next(
        (f for f in ANNUAL_FEASTS if f["month"] == eth_month and f["day"] == eth_day),
        None
    )

    # Fasting
    fasting = is_fasting_day(greg_date)

    # Wudase Mariam for today
    wudase = WUDASE_MARIAM.get(py_wd, WUDASE_MARIAM[0])

    # Current prayer hour
    now_hour = datetime.datetime.now().hour
    current_prayer = None
    next_prayer    = None
    for i, ph in enumerate(PRAYER_HOURS):
        if ph["int_hour"] <= now_hour < (PRAYER_HOURS[i + 1]["int_hour"] if i + 1 < len(PRAYER_HOURS) else 24):
            current_prayer = ph
            next_prayer    = PRAYER_HOURS[i + 1] if i + 1 < len(PRAYER_HOURS) else PRAYER_HOURS[0]
            break
    if current_prayer is None:
        current_prayer = PRAYER_HOURS[-1]
        next_prayer    = PRAYER_HOURS[0]

    # Psalm of the day
    psalm_num = DAILY_PSALM_PLAN.get(eth_day, 1)

    return {
        "eth_year":      eth_year,
        "eth_month":     eth_month,
        "eth_month_name": eth_month_name,
        "eth_day":       eth_day,
        "eth_day_name":  ETH_DAYS[eth_wd],
        "greg_date":     greg_date.strftime("%Y-%m-%d"),
        "day_saints":    day_saints,
        "annual_feast":  annual_feast,
        "fasting":       fasting,
        "wudase":        wudase,
        "current_prayer": current_prayer,
        "next_prayer":   next_prayer,
        "psalm_num":     psalm_num,
    }


# ────────────────────────────────────────────────────────────────
#  Routes
# ────────────────────────────────────────────────────────────────

@orthodox_bp.route('/orthodox')
def orthodox_home():
    lang   = get_lang()
    today  = get_todays_data()
    return render_template(
        'customer/orthodox.html',
        lang          = lang,
        today         = today,
        prayer_hours  = PRAYER_HOURS,
        saints_by_day = SAINTS_BY_DAY,
        annual_feasts = ANNUAL_FEASTS,
        bible_books   = BIBLE_81_BOOKS,
        wudase_all    = WUDASE_MARIAM,
        eth_months    = ETH_MONTHS,
        fasting_seasons = FASTING_SEASONS,
    )


@orthodox_bp.route('/api/orthodox/today')
def orthodox_today_api():
    data = get_todays_data()
    return jsonify(data)


@orthodox_bp.route('/api/orthodox/saints/<int:day>')
def orthodox_saints_api(day):
    if day < 1 or day > 30:
        return jsonify({"error": "Day must be 1–30"}), 400
    return jsonify(SAINTS_BY_DAY.get(day, {}))
