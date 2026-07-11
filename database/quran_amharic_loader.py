"""
Fetch and cache the full Amharic Quran from api.alquran.cloud (am.sadiq edition).
Per-surah lazy loading — each surah is fetched once on first request and persisted
in database/quran_amharic_cache.json for instant subsequent access.
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

_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'quran_amharic_cache.json')
_API_URL = 'https://api.alquran.cloud/v1/surah/{}/am.sadiq'

_mem_cache: dict = None


def _load_disk_cache() -> dict:
    global _mem_cache
    if _mem_cache is not None:
        return _mem_cache
    if os.path.exists(_CACHE_PATH):
        try:
            with open(_CACHE_PATH, 'r', encoding='utf-8') as f:
                _mem_cache = json.load(f)
            return _mem_cache
        except Exception:
            pass
    _mem_cache = {}
    return _mem_cache


def _save_disk_cache() -> None:
    try:
        with open(_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(_mem_cache, f, ensure_ascii=False, separators=(',', ':'))
    except Exception as e:
        logger.error("Could not save Amharic Quran cache: %s", e)


def get_surah_amharic(surah_num: int):
    """
    Return list of {'number': int, 'text': str} for each ayah (Amharic translation).
    Fetches from alquran.cloud on first call and persists to disk cache.
    Returns None if network unavailable and not cached.
    """
    cache = _load_disk_cache()
    key = str(surah_num)
    if key in cache:
        return cache[key]
    if not _HAS_REQ:
        return None
    try:
        resp = _req.get(_API_URL.format(surah_num), timeout=25)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        ayahs = [
            {'number': a['numberInSurah'], 'text': a['text']}
            for a in data.get('ayahs', [])
        ]
        if ayahs:
            cache[key] = ayahs
            _save_disk_cache()
        return ayahs if ayahs else None
    except Exception as e:
        logger.warning("Could not fetch Amharic Surah %d: %s", surah_num, e)
        return None


def get_cached_surah_count() -> int:
    """Return how many surahs are already in the local cache."""
    return len(_load_disk_cache())
