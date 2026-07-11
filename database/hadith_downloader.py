"""
Download and cache complete Hadith collections from fawazahmed0/hadith-api.
Arabic and English editions are merged by hadith number and stored as local JSON files.
Supported: bukhari (7589), muslim (7563), nawawi40 (42).
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

try:
    import requests as _req
    _HAS_REQ = True
except ImportError:
    _HAS_REQ = False

_DIR = os.path.dirname(__file__)
_BASE = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{}.min.json'

_EDITIONS = {
    'bukhari':  ('ara-bukhari',  'eng-bukhari'),
    'muslim':   ('ara-muslim',   'eng-muslim'),
    'nawawi40': ('ara-nawawi',   'eng-nawawi'),
}

_mem: dict = {}


def _cache_path(col_id: str) -> str:
    return os.path.join(_DIR, f'hadith_{col_id}_ext.json')


def is_cached(col_id: str) -> bool:
    return col_id in _mem or os.path.exists(_cache_path(col_id))


def _save_cache(col_id: str, data: list) -> None:
    with open(_cache_path(col_id), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))


import re as _re

_DIACRITICS_RE = _re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06ED]')
_STRIP_RE      = _re.compile(r'[\s\u060C,.:؛"\'\u0640]')


def _normalize_ar(s: str) -> str:
    """Normalize Arabic text for robust content matching: strip diacritics,
    unify letter variants (alef/hamza forms, ta-marbuta, alef-maqsura), and
    remove whitespace/punctuation."""
    if not s:
        return ''
    s = _DIACRITICS_RE.sub('', s)
    s = s.translate(str.maketrans({'إ': 'ا', 'أ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}))
    s = _STRIP_RE.sub('', s)
    return s


def _curated_amharic_by_number(col_id: str, ara_hadiths: list) -> dict:
    """
    The curator's own hadith numbering in hadith_collections.py (e.g. 1..25
    for Bukhari) is just the order of their hand-picked list — it does NOT
    line up with the canonical hadithnumber used by the upstream extended
    dataset. Matching by number would silently attach the wrong Amharic
    translation to the wrong hadith, which is worse than no translation.

    Instead, match each curated hadith to its real counterpart by comparing
    normalized Arabic text (curated text is the matn only, so we check
    whether it appears as a substring of the full narration in the real
    dataset). Only confident matches are kept; everything else is skipped
    rather than guessed. No free complete Amharic dataset exists for
    Bukhari/Muslim, so this yields partial — but verified-correct —
    coverage by design.
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


def get_extended_collection(col_id: str):
    """
    Return merged list of hadiths: [{number, arabic, text_en, grades, reference}].
    Downloads from fawazahmed0 on first call (~10-30s for large collections).
    Cached to disk for instant subsequent access.
    Returns None if unavailable.
    """
    if col_id in _mem:
        return _mem[col_id]

    path = _cache_path(col_id)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _mem[col_id] = data
            logger.info("Loaded %d hadiths for '%s' from disk cache", len(data), col_id)
            return data
        except Exception as e:
            logger.error("Corrupt cache for '%s': %s — re-downloading", col_id, e)
            os.remove(path)

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

        merged = []
        skipped = 0
        for h in eng_hadiths:
            hnum = h['hadithnumber']
            arabic_txt = ara_by_num.get(hnum, '')
            english_txt = h.get('text', '')

            # Skip front-matter / chapter-intro stub entries that carry no
            # actual hadith text in either language (e.g. book-0 placeholders
            # in the upstream dataset). These render as empty cards otherwise.
            if not arabic_txt.strip() and not english_txt.strip():
                skipped += 1
                continue

            grades = h.get('grades', [])
            grade_str = grades[0].get('grade', '') if grades and isinstance(grades[0], dict) else ''
            ref = h.get('reference', {})
            entry = {
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
            logger.info("Skipped %d empty placeholder entries for '%s'", skipped, col_id)

        _save_cache(col_id, merged)

        _mem[col_id] = merged
        logger.info("Downloaded and cached %d hadiths for '%s'", len(merged), col_id)
        return merged

    except Exception as e:
        logger.error("Could not download '%s': %s", col_id, e)
        return None


def ensure_amharic(col_id: str, entries: list) -> int:
    """
    Fill in machine-translated Amharic text for any of the given entries
    that don't already have a (verified) `text_am`. Entries are the actual
    dict objects held in the in-memory collection (not copies), so mutating
    them here updates every future reference within this process. Persists
    the whole collection back to disk if anything changed, so translations
    are permanent — each hadith is machine-translated at most once, ever.

    Intended to be called with a single page's worth of entries (not an
    entire 7000+ collection) so a cold page load stays responsive.
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
