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

## Full library already exists — don't confuse with the 30-entry daily rotator

- The 30-entry `QURAN_AMHARIC`/`HADITH_DAILY` above is ONLY the homepage "verse/hadith of the day" widget. The actual `/islamic` Qur'an + Hadith library is a separate, already-complete system:
  - **Qur'an**: `database/quran_surahs.py` has all 114 surahs metadata; `database/quran_amharic_loader.py` lazy-fetches full per-ayah Amharic translation from `api.alquran.cloud` (am.sadiq edition), cached to `database/quran_amharic_cache.json`. Arabic text loads from a GitHub-hosted full quran.json cached to `database/quran_cache.json`. `/api/quran/surah/<n>/bilingual` returns every ayah of any of the 114 surahs with Arabic + Amharic side by side.
  - **Hadith**: `database/hadith_downloader.py` lazy-downloads the COMPLETE Bukhari (7,589) and Muslim (7,563) collections in Arabic + English from the fawazahmed0/hadith-api CDN, cached to `database/hadith_<id>_ext.json`. Nawawi's 40 is fully hand-translated to Amharic in `database/hadith_collections.py`.
  - No public dataset provides a complete Amharic translation of the full Bukhari/Muslim (only Nawawi's 40 has full Amharic) — full Bukhari/Muslim are Arabic+English only. Mention this constraint if asked to make them full-Amharic too.
- Riyad as-Saliheen intentionally stays a small curated Amharic subset (no extended downloader wired for it).

## Extended Bukhari/Muslim: blank-card + wrong-translation pitfalls

- The fawazahmed0 CDN dataset contains "book:0" placeholder entries with empty Arabic AND English text (9 in Bukhari, 203 in Muslim) — these render as blank cards unless filtered out at merge time in `database/hadith_downloader.py`. Real totals after filtering: Bukhari 7580, Muslim 7360 (not 7589/7563).
- **Never merge the curated Amharic hadiths (hadith_collections.py, numbered 1..25/1..20) into the extended dataset by matching on `number`.** The curator's numbering is just hand-pick order — it does NOT correspond to the canonical hadithnumber in the extended dataset. Verified example: curated Bukhari "#1" (revelation-began-with-dreams, Aisha) is actually canonical hadith #3; canonical #1 is the "actions are by intentions" hadith. Matching by number silently attaches the wrong Amharic translation to the wrong hadith — worse than showing none.
- **Why it matters:** mislabeling a hadith's translation is a religious-content correctness issue, not a cosmetic bug.
- **How to apply:** to attach curated Amharic to the correct extended-collection hadith, match by normalized Arabic *content* (strip diacritics/letter variants, check if the curated matn is a substring of the real narration) and only keep confident matches — this found genuine matches for only ~9/25 Bukhari and ~11/20 curated entries; the rest are legitimately unmatched and should be left without Amharic rather than guessed.

## Full Amharic coverage via machine-translation fallback

- No Groq/OpenAI key was configured and user declined to add one, so full Amharic coverage for extended Bukhari/Muslim (~14,940 hadiths) uses `deep-translator`'s free `GoogleTranslator` (no API key) as the translation backend, in `database/hadith_translator.py`.
- Translations are permanently cached into the same `database/hadith_{col}_ext.json` file (via `hadith_downloader.ensure_amharic()`), marked with `am_auto: True` so the frontend can show a subtle "machine translated" label distinct from the 9/11 scholar-verified entries (which have `text_am` but no `am_auto` flag).
- Live request-time fallback in `routes/islamic_routes.py` translates only the current page's missing entries (bounded to per_page ≤100) so a cold page load stays responsive (~1-2s per hadith); already-translated entries are instant.
- **`nohup ... &` backgrounded shell commands do NOT survive past the ShellExec call that started them in this environment** — the process was gone on the next call even though nohup should protect it. To run a long one-time batch job (here: pre-translating ~15k hadiths, ~35 min total), run it in the foreground repeatedly with `timeout <N>s python3 script.py`, where the script itself persists progress to disk and skips already-done items on each re-invocation, until a run reports 0 pending.
