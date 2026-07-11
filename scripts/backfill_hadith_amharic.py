"""
One-time backfill: machine-translate every Bukhari/Muslim hadith that lacks
a verified Amharic translation, using the same translate_to_amharic() helper
the live request-time fallback uses, so results are cached in exactly the
same place (database/hadith_{col}_ext.json).

Safe to interrupt and re-run — it skips any hadith that already has text_am.
Progress is saved to disk periodically so interruption never loses work.

Run manually: python scripts/backfill_hadith_amharic.py
"""
import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('backfill')

from database.hadith_downloader import get_extended_collection, _save_cache  # noqa: E402
from database.hadith_translator import translate_to_amharic, is_available  # noqa: E402

COLLECTIONS = ['bukhari', 'muslim']
WORKERS = 8
SAVE_EVERY = 100


def backfill(col_id: str):
    if not is_available():
        logger.error("Translator not available — aborting")
        return

    data = get_extended_collection(col_id)
    if not data:
        logger.error("No data for %s", col_id)
        return

    pending = [e for e in data if not e.get('text_am') and e.get('text_en', '').strip()]
    total_pending = len(pending)
    logger.info("[%s] %d/%d hadiths need translation", col_id, total_pending, len(data))

    done = 0
    failed = 0
    start_time = time.time()

    def work(entry):
        translated = translate_to_amharic(entry['text_en'])
        return entry, translated

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(work, e): e for e in pending}
        for fut in as_completed(futures):
            entry, translated = fut.result()
            if translated:
                entry['text_am'] = translated
                entry['am_auto'] = True
                done += 1
            else:
                failed += 1

            processed = done + failed
            if processed % SAVE_EVERY == 0:
                _save_cache(col_id, data)
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                remaining = total_pending - processed
                eta_min = (remaining / rate / 60) if rate > 0 else float('inf')
                logger.info("[%s] %d/%d done (%d failed) — %.1f/s — ETA %.1f min",
                            col_id, processed, total_pending, failed, rate, eta_min)

    _save_cache(col_id, data)
    logger.info("[%s] COMPLETE — %d translated, %d failed, %d total in collection",
                col_id, done, failed, len(data))


if __name__ == '__main__':
    for col in COLLECTIONS:
        backfill(col)
    logger.info("All collections backfilled.")
