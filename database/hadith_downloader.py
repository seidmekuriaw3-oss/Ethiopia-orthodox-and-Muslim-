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

        merged = []
        for h in eng_hadiths:
            hnum = h['hadithnumber']
            grades = h.get('grades', [])
            grade_str = grades[0].get('grade', '') if grades and isinstance(grades[0], dict) else ''
            ref = h.get('reference', {})
            merged.append({
                'number':    hnum,
                'arabic':    ara_by_num.get(hnum, ''),
                'text_en':   h.get('text', ''),
                'grade':     grade_str,
                'reference': ref,
            })

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, separators=(',', ':'))

        _mem[col_id] = merged
        logger.info("Downloaded and cached %d hadiths for '%s'", len(merged), col_id)
        return merged

    except Exception as e:
        logger.error("Could not download '%s': %s", col_id, e)
        return None
