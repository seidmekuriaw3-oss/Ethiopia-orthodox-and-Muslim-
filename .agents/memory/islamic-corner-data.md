---
name: Islamic Corner data layer
description: Covers the islamic_data.py module, new API endpoint, 6-card slider, and Mushaf layout changes.
---

## What was added

- **`database/islamic_data.py`** — 30-entry `QURAN_AMHARIC` list (daily Amharic verse + tafsir) and `HADITH_DAILY` list (authentic hadiths with narrator/source/grade). `get_today_quran_amharic()` and `get_today_hadith()` rotate by `day-of-month % 30`.
- **`/api/islamic/daily-content`** endpoint in `routes/islamic_routes.py` — returns both objects as JSON `{success, quran_am, hadith}`.

## Slider now has 6 cards

- `templates/customer/index.html`: `idcTotal = 6`, 6 dots. Cards 5 & 6 are `id="idc-card-quran-am"` and `id="idc-card-hadith"`. JS `loadIslamicDailyContent()` populates them on DOMContentLoaded.

## Mushaf layout (islamic.html)

- `.mushaf-block` CSS: `direction:rtl; text-align:justify; line-height:2.5rem; display:block` — all verses flow inline in one paragraph.
- `qRenderAyahs()` now outputs a `<p class="mushaf-block">` with inline `<span class="mushaf-inline">` verses and `<span class="ayah-num-badge">` numbers positioned AFTER each verse (RTL left-side naturally).
- `qFontAdj()` targets `.mushaf-block,.ayah-arabic` for font scaling.

## Font buttons

- `#btn-font-decrease` and `#btn-font-increase` IDs added to qfont-btn elements.
- DOMContentLoaded adds `addEventListener('click')` bindings in addition to existing onclick attrs.

## Inline audio strip

- `.qap-inline` div inserted inside `.qreader-title` (in qreader-header). Shows play/pause + surah name + elapsed time inline next to the surah metadata. Hidden by default; `qap-inline.visible` class added by `qPlayAudio()`, removed by `qStopAudio()`.
- `qTogglePlay()`, timeupdate, play, pause, ended events all sync `#qap-inline-play` button text and `#qap-inline-time`.

**Why:** Instructions required audio player near surah title metadata, font buttons with specific IDs and event listeners, and inline Mushaf flow with RTL text justify.
