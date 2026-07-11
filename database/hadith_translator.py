"""
Automatic Amharic translation fallback for hadiths that don't have a
verified, hand-curated Amharic translation.

Uses Google Translate via the `deep-translator` library (free, no API key)
since no Groq/LLM key is configured in this environment and no complete
Amharic hadith dataset exists. Every translation produced here is machine
translation, not scholar-reviewed — callers must mark it as such
(`am_auto: True`) so the frontend can show provenance.

Results are meant to be cached permanently by the caller (see
`hadith_downloader.ensure_amharic`) so each hadith is only ever translated
once, the first time it is viewed.
"""

import re
import time
import logging

logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator
    _HAS_TRANSLATOR = True
except ImportError:
    GoogleTranslator = None
    _HAS_TRANSLATOR = False

# The free Google Translate web endpoint caps requests around ~5000 chars.
_MAX_CHUNK = 4000
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?\u06d4])\s+')


def is_available() -> bool:
    return _HAS_TRANSLATOR


def _split_text(text: str, max_len: int = _MAX_CHUNK):
    """Split long text into chunks under max_len, breaking at sentence
    boundaries where possible so translation quality isn't hurt by mid-
    sentence cuts."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ''
    for sentence in _SENTENCE_SPLIT_RE.split(text):
        candidate = f'{current} {sentence}'.strip() if current else sentence
        if len(candidate) > max_len and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current.strip())

    # Guard against a single sentence longer than max_len.
    final = []
    for c in chunks:
        if len(c) <= max_len:
            final.append(c)
        else:
            for i in range(0, len(c), max_len):
                final.append(c[i:i + max_len])
    return final or [text[:max_len]]


def translate_to_amharic(text: str, retries: int = 3):
    """Translate English text to Amharic. Returns the translated string, or
    None if translation is unavailable or fails after retries."""
    if not _HAS_TRANSLATOR or not text or not text.strip():
        return None

    chunks = _split_text(text.strip())
    translated_parts = []

    for chunk in chunks:
        result = None
        for attempt in range(retries):
            try:
                translator = GoogleTranslator(source='en', target='am')
                result = translator.translate(chunk)
                if result:
                    break
            except Exception as e:
                logger.warning("Amharic translation attempt %d/%d failed: %s", attempt + 1, retries, e)
                time.sleep(1.0 * (attempt + 1))
        if not result:
            return None
        translated_parts.append(result)

    return ' '.join(translated_parts)
