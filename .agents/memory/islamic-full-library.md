---
name: Islamic full library
description: Architecture for the complete Quran bilingual reader and full hadith library in the Islamic tab.
---

## Quran Tafsir Tab — Bilingual Reader

- Replaced 30-card library with a full 114-surah bilingual reader
- Surah grid reuses `/api/quran/surahs` endpoint (same as Quran tab); field is `arabic_name` NOT `arabic`
- Per-surah bilingual endpoint: `GET /api/quran/surah/<num>/bilingual`
  - Returns Arabic (from quran cache) + Amharic (fetched from `api.alquran.cloud/v1/surah/{n}/am.sadiq`)
  - Amharic is fetched on first open per surah and persisted to `database/quran_amharic_cache.json`
  - Loader: `database/quran_amharic_loader.py` → `get_surah_amharic(surah_num)`
- JS: `bilLoadSurahs()`, `bilOpenSurah(num)`, `bilFilter(q)`, `bilBack()`

## Hadith Tab — Full Paginated Collections

- Bukhari (~7580), Muslim (~7360): downloaded from fawazahmed0 CDN on first access
  - Arabic: `ara-bukhari.min.json`, English: `eng-bukhari.min.json` → merged by hadithnumber
  - Cached to `database/hadith_bukhari_ext.json` / `database/hadith_muslim_ext.json`
  - Downloader: `database/hadith_downloader.py` → `get_extended_collection(col_id)`
  - Extended hadiths have fields: `{number, arabic, text_en, grade, reference}`
- Nawawi40 (40), Riyad (20): served from local Amharic data in `database/hadith_collections.py`
  - Local hadiths have fields: `{number, arabic, text_am, narrator, source, grade, chapter_am}`
- Pagination: `GET /api/hadith/collection/<id>?page=N&per_page=50` (min=10, max=100)
  - page is clamped to [1, total_pages] in the route
  - Collections metadata: `GET /api/hadith/collections` shows `is_extended=True` for bukhari/muslim
- UI: `hcolOpen()` triggers download notice for large collections; `hlibPage(dir)` for pagination

**Why:**
- fawazahmed0 provides the only free, complete Arabic + English hadith CDN
- Nawawi40/Riyad have complete Amharic so local data is preferred; no Amharic for Bukhari/Muslim
- Quran Amharic from `am.sadiq` edition on alquran.cloud — verified real Amharic text, not just transliteration
