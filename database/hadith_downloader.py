"""
Download and cache complete Hadith collections.

fawazahmed0/hadith-api CDN → Bukhari (~7589), Muslim (~7563), Nawawi40 (42)
sunnah.com API             → Riyad as-Saliheen (1895)

All collections are merged Arabic + English and cached as local JSON files.
"""

import os
import json
import logging
import re as _re
import time as _time

logger = logging.getLogger(__name__)

try:
    import requests as _req
    _HAS_REQ = True
except ImportError:
    _HAS_REQ = False

_DIR  = os.path.dirname(__file__)
_BASE = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{}.min.json'

_EDITIONS = {
    'bukhari':  ('ara-bukhari',  'eng-bukhari'),
    'muslim':   ('ara-muslim',   'eng-muslim'),
    'nawawi40': ('ara-nawawi',   'eng-nawawi'),
}

# sunnah.com — Riyad as-Saliheen
_SUNNAH_BASE     = 'https://api.sunnah.com/v1'
_SUNNAH_DEMO_KEY = 'SqD712P3E82xnwOAEOkGd5JZH8s9wRR24TqNFzjk'
_RIYAD_BOOKS     = [
    'introduction',
    '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
]

_mem: dict = {}

# ── helpers ──────────────────────────────────────────────────────────────────

_HTML_TAG_RE  = _re.compile(r'<[^>]+>')
_MULTI_WS_RE  = _re.compile(r'\n{3,}')
_DIACRITICS_RE = _re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06ED]')
_STRIP_RE      = _re.compile(r'[\s\u060C,.:؛"\'\u0640]')


def _strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    if not text:
        return ''
    text = _re.sub(r'<br\s*/?>', '\n', text, flags=_re.IGNORECASE)
    text = _re.sub(r'</p>', '\n', text, flags=_re.IGNORECASE)
    text = _re.sub(r'<p[^>]*>', '', text, flags=_re.IGNORECASE)
    text = _HTML_TAG_RE.sub('', text)
    text = _MULTI_WS_RE.sub('\n\n', text)
    return text.strip()


def _normalize_ar(s: str) -> str:
    """Normalize Arabic text for robust content matching."""
    if not s:
        return ''
    s = _DIACRITICS_RE.sub('', s)
    s = s.translate(str.maketrans({'إ': 'ا', 'أ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}))
    s = _STRIP_RE.sub('', s)
    return s


def _cache_path(col_id: str) -> str:
    return os.path.join(_DIR, f'hadith_{col_id}_ext.json')


def is_cached(col_id: str) -> bool:
    return col_id in _mem or os.path.exists(_cache_path(col_id))


def _save_cache(col_id: str, data: list) -> None:
    with open(_cache_path(col_id), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))


def _load_cache(col_id: str):
    path = _cache_path(col_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _mem[col_id] = data
        logger.info("Loaded %d hadiths for '%s' from disk cache", len(data), col_id)
        return data
    except Exception as e:
        logger.error("Corrupt cache for '%s': %s — will re-download", col_id, e)
        os.remove(path)
        return None


# ── curated Amharic matching ──────────────────────────────────────────────────

def _curated_amharic_by_number(col_id: str, ara_hadiths: list) -> dict:
    """
    Match curated local Amharic translations to the full extended dataset by
    comparing normalized Arabic text (substring match). Only confident matches
    are kept; no guessing.
    """
    try:
        from database.hadith_collections import HADITH_COLLECTIONS
        curated = None
        for c in HADITH_COLLECTIONS:
            if c['id'] == col_id:
                curated = c.get('hadiths', [])
                break
        if not curated:
            return {}

        real_norm = [(h['hadithnumber'], _normalize_ar(h.get('text', ''))) for h in ara_hadiths]

        mapping = {}
        for cur in curated:
            am = cur.get('text_am')
            ar = cur.get('arabic')
            if not am or not ar:
                continue
            anchor = _normalize_ar(ar)[:30]
            if len(anchor) < 15:
                continue
            for real_num, real_txt in real_norm:
                if anchor in real_txt:
                    mapping[real_num] = am
                    break
        return mapping
    except Exception as e:
        logger.warning("Could not match curated Amharic for '%s': %s", col_id, e)
        return {}


# ── Riyad as-Saliheen via sunnah.com ─────────────────────────────────────────

def _sunnah_api_key() -> str:
    return os.environ.get('SUNNAH_API_KEY', _SUNNAH_DEMO_KEY)


def get_riyad_collection():
    """
    Download complete Riyad as-Saliheen (1895 hadiths) from sunnah.com API.
    Iterates through all 20 books, paginating at 100 per request.
    Caches to database/hadith_riyad_ext.json for instant subsequent access.
    Returns list of {number, arabic, text_en, chapter_en, chapter_ar, book_number, grade}.
    """
    col_id = 'riyad'
    if col_id in _mem:
        return _mem[col_id]

    cached = _load_cache(col_id)
    if cached is not None:
        return cached

    if not _HAS_REQ:
        return None

    api_key = _sunnah_api_key()
    headers = {'X-API-Key': api_key}
    all_hadiths = []

    logger.info("Downloading Riyad as-Saliheen from sunnah.com (%d books)…", len(_RIYAD_BOOKS))

    for book_num in _RIYAD_BOOKS:
        page = 1
        book_total = 0
        while True:
            url = (
                f'{_SUNNAH_BASE}/collections/riyadussalihin/books/'
                f'{book_num}/hadiths?limit=100&page={page}'
            )
            retries = 0
            max_retries = 5
            while retries <= max_retries:
                try:
                    resp = _req.get(url, headers=headers, timeout=30)
                    if resp.status_code == 429:
                        wait = 2 ** retries  # 1, 2, 4, 8, 16 seconds
                        logger.warning("Rate limited on book=%s page=%d — waiting %ds", book_num, page, wait)
                        _time.sleep(wait)
                        retries += 1
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    break
                except Exception as e:
                    logger.error("Failed Riyad book=%s page=%d attempt=%d: %s", book_num, page, retries, e)
                    retries += 1
                    if retries > max_retries:
                        data = None
                    else:
                        _time.sleep(2 ** retries)
            else:
                data = None

            if data is None:
                break

            items = data.get('data', [])
            if not items:
                break

            for item in items:
                h_num = item.get('hadithNumber', '')
                hadith_langs = item.get('hadith', [])

                arabic    = ''
                english   = ''
                chapter_en = ''
                chapter_ar = ''

                for lang_entry in hadith_langs:
                    lang = lang_entry.get('lang', '')
                    body = _strip_html(lang_entry.get('body', ''))
                    ctitle = lang_entry.get('chapterTitle', '')
                    if lang == 'ar':
                        arabic     = body
                        chapter_ar = _strip_html(ctitle)
                    elif lang == 'en':
                        english    = body
                        chapter_en = _strip_html(ctitle)

                if not arabic.strip() and not english.strip():
                    continue

                try:
                    num = int(h_num)
                except (ValueError, TypeError):
                    num = h_num

                all_hadiths.append({
                    'number':      num,
                    'arabic':      arabic,
                    'text_en':     english,
                    'chapter_en':  chapter_en,
                    'chapter_ar':  chapter_ar,
                    'book_number': book_num,
                    'grade':       '',
                })
                book_total += 1

            next_page = data.get('next')
            if next_page is None:
                break
            page += 1
            _time.sleep(0.4)  # polite pacing between pages

        logger.info("  Book %-15s → %d hadiths", book_num, book_total)
        _time.sleep(0.8)  # polite pacing between books

    if not all_hadiths:
        logger.error("Riyad download yielded 0 hadiths — aborting")
        return None

    # Sort by hadith number (numeric)
    all_hadiths.sort(key=lambda h: int(h['number']) if isinstance(h['number'], int) else 0)

    _save_cache(col_id, all_hadiths)
    _mem[col_id] = all_hadiths
    logger.info("Riyad as-Saliheen: downloaded and cached %d hadiths", len(all_hadiths))
    return all_hadiths


# ── fawazahmed0 collections (Bukhari / Muslim / Nawawi40) ────────────────────

def get_extended_collection(col_id: str):
    """
    Return merged list of hadiths for a collection.
    • 'riyad'   → sunnah.com API  → {number, arabic, text_en, chapter_en, chapter_ar, book_number, grade}
    • others    → fawazahmed0 CDN → {number, arabic, text_en, grade, reference}
    Downloads on first call (~10-60 s); instant on subsequent calls from disk.
    Returns None if unavailable.
    """
    # Riyad uses its own downloader
    if col_id == 'riyad':
        return get_riyad_collection()

    if col_id in _mem:
        return _mem[col_id]

    cached = _load_cache(col_id)
    if cached is not None:
        return cached

    if not _HAS_REQ or col_id not in _EDITIONS:
        return None

    ara_ed, eng_ed = _EDITIONS[col_id]
    try:
        logger.info("Downloading hadith collection '%s' (Arabic + English)…", col_id)

        ara_resp = _req.get(_BASE.format(ara_ed), timeout=90)
        ara_resp.raise_for_status()
        ara_hadiths = ara_resp.json()['hadiths']

        eng_resp = _req.get(_BASE.format(eng_ed), timeout=90)
        eng_resp.raise_for_status()
        eng_hadiths = eng_resp.json()['hadiths']

        ara_by_num = {h['hadithnumber']: h.get('text', '') for h in ara_hadiths}
        am_by_num  = _curated_amharic_by_number(col_id, ara_hadiths)

        merged  = []
        skipped = 0
        for h in eng_hadiths:
            hnum       = h['hadithnumber']
            arabic_txt = ara_by_num.get(hnum, '')
            english_txt = h.get('text', '')

            if not arabic_txt.strip() and not english_txt.strip():
                skipped += 1
                continue

            grades    = h.get('grades', [])
            grade_str = grades[0].get('grade', '') if grades and isinstance(grades[0], dict) else ''
            ref       = h.get('reference', {})
            entry     = {
                'number':    hnum,
                'arabic':    arabic_txt,
                'text_en':   english_txt,
                'grade':     grade_str,
                'reference': ref,
            }
            if hnum in am_by_num:
                entry['text_am'] = am_by_num[hnum]
            merged.append(entry)

        if skipped:
            logger.info("Skipped %d empty entries for '%s'", skipped, col_id)

        _save_cache(col_id, merged)
        _mem[col_id] = merged
        logger.info("Downloaded and cached %d hadiths for '%s'", len(merged), col_id)
        return merged

    except Exception as e:
        logger.error("Could not download '%s': %s", col_id, e)
        return None


def ensure_amharic(col_id: str, entries: list) -> int:
    """
    Fill in machine-translated Amharic for entries that don't already have text_am.
    Mutates entries in-place and persists back to cache if anything changed.
    """
    from database.hadith_translator import translate_to_amharic, is_available

    if not is_available():
        return 0

    changed = 0
    for entry in entries:
        if entry.get('text_am'):
            continue
        source_text = entry.get('text_en', '')
        if not source_text.strip():
            continue
        translated = translate_to_amharic(source_text)
        if translated:
            entry['text_am'] = translated
            entry['am_auto'] = True
            changed += 1
        else:
            logger.warning("Auto-translation failed for %s #%s", col_id, entry.get('number'))

    if changed and col_id in _mem:
        _save_cache(col_id, _mem[col_id])
        logger.info("Auto-translated %d hadith(s) to Amharic for '%s' (cached)", changed, col_id)

    return changed
