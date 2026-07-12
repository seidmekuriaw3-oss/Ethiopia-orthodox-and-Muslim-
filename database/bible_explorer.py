"""
Bible Explorer — serves the full Amharic Bible (66 books) from the local
amharic_bible.json. Keyed as { "GEN": { "1": [{number, text}, ...] } }.
"""
import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), 'amharic_bible.json')
_bible_data = None


def _load():
    global _bible_data
    if _bible_data is None:
        with open(_DATA_PATH, encoding='utf-8') as f:
            _bible_data = json.load(f)
    return _bible_data


# Full metadata: code → Amharic name, English name, testament, canonical order
BOOK_META = {
    "GEN": {"am": "ዘፍጥረት",    "en": "Genesis",          "testament": "OT", "order": 1},
    "EXO": {"am": "ዘጸአት",     "en": "Exodus",           "testament": "OT", "order": 2},
    "LEV": {"am": "ዘሌዋዊያን",   "en": "Leviticus",        "testament": "OT", "order": 3},
    "NUM": {"am": "ዘኁልቁ",     "en": "Numbers",          "testament": "OT", "order": 4},
    "DEU": {"am": "ዘዳግም",     "en": "Deuteronomy",      "testament": "OT", "order": 5},
    "JOS": {"am": "ኢያሱ",      "en": "Joshua",           "testament": "OT", "order": 6},
    "JDG": {"am": "መሳፍንት",    "en": "Judges",           "testament": "OT", "order": 7},
    "RUT": {"am": "ሩት",       "en": "Ruth",             "testament": "OT", "order": 8},
    "1SA": {"am": "1ሳሙኤል",   "en": "1 Samuel",         "testament": "OT", "order": 9},
    "2SA": {"am": "2ሳሙኤል",   "en": "2 Samuel",         "testament": "OT", "order": 10},
    "1KI": {"am": "1ነገሥት",   "en": "1 Kings",          "testament": "OT", "order": 11},
    "2KI": {"am": "2ነገሥት",   "en": "2 Kings",          "testament": "OT", "order": 12},
    "1CH": {"am": "1ዜና",     "en": "1 Chronicles",     "testament": "OT", "order": 13},
    "2CH": {"am": "2ዜና",     "en": "2 Chronicles",     "testament": "OT", "order": 14},
    "EZR": {"am": "ዕዝራ",     "en": "Ezra",             "testament": "OT", "order": 15},
    "NEH": {"am": "ነህምያ",    "en": "Nehemiah",         "testament": "OT", "order": 16},
    "EST": {"am": "አስቴር",    "en": "Esther",           "testament": "OT", "order": 17},
    "JOB": {"am": "ኢዮብ",     "en": "Job",              "testament": "OT", "order": 18},
    "PSA": {"am": "መዝሙር",    "en": "Psalms",           "testament": "OT", "order": 19},
    "PRO": {"am": "ምሳሌ",     "en": "Proverbs",         "testament": "OT", "order": 20},
    "ECC": {"am": "መክብብ",    "en": "Ecclesiastes",     "testament": "OT", "order": 21},
    "SON": {"am": "መኃልይ",    "en": "Song of Songs",    "testament": "OT", "order": 22},
    "ISA": {"am": "ኢሳይያስ",   "en": "Isaiah",           "testament": "OT", "order": 23},
    "JER": {"am": "ኤርምያስ",   "en": "Jeremiah",         "testament": "OT", "order": 24},
    "LAM": {"am": "ሰቆቃወ",    "en": "Lamentations",     "testament": "OT", "order": 25},
    "EZE": {"am": "ሕዝቅኤል",   "en": "Ezekiel",          "testament": "OT", "order": 26},
    "DAN": {"am": "ዳንኤል",    "en": "Daniel",           "testament": "OT", "order": 27},
    "HOS": {"am": "ሆሴዕ",     "en": "Hosea",            "testament": "OT", "order": 28},
    "JOE": {"am": "ዮኤል",     "en": "Joel",             "testament": "OT", "order": 29},
    "AMO": {"am": "አሞጽ",     "en": "Amos",             "testament": "OT", "order": 30},
    "OBA": {"am": "ዓብድዩ",    "en": "Obadiah",          "testament": "OT", "order": 31},
    "JON": {"am": "ዮናስ",     "en": "Jonah",            "testament": "OT", "order": 32},
    "MIC": {"am": "ሚክያስ",    "en": "Micah",            "testament": "OT", "order": 33},
    "NAH": {"am": "ናሆም",     "en": "Nahum",            "testament": "OT", "order": 34},
    "HAB": {"am": "ዕንባቆም",   "en": "Habakkuk",         "testament": "OT", "order": 35},
    "ZEP": {"am": "ሶፎንያስ",   "en": "Zephaniah",        "testament": "OT", "order": 36},
    "HAG": {"am": "ሐጌ",      "en": "Haggai",           "testament": "OT", "order": 37},
    "ZEC": {"am": "ዘካርያስ",   "en": "Zechariah",        "testament": "OT", "order": 38},
    "MAL": {"am": "ሚልክያስ",   "en": "Malachi",          "testament": "OT", "order": 39},
    "MAT": {"am": "ማቴዎስ",    "en": "Matthew",          "testament": "NT", "order": 40},
    "MAR": {"am": "ማርቆስ",    "en": "Mark",             "testament": "NT", "order": 41},
    "LUK": {"am": "ሉቃስ",     "en": "Luke",             "testament": "NT", "order": 42},
    "JOH": {"am": "ዮሐንስ",    "en": "John",             "testament": "NT", "order": 43},
    "ACT": {"am": "ሐዋርያት",   "en": "Acts",             "testament": "NT", "order": 44},
    "ROM": {"am": "ሮሜ",      "en": "Romans",           "testament": "NT", "order": 45},
    "1CO": {"am": "1ቆሮንቶስ",  "en": "1 Corinthians",   "testament": "NT", "order": 46},
    "2CO": {"am": "2ቆሮንቶስ",  "en": "2 Corinthians",   "testament": "NT", "order": 47},
    "GAL": {"am": "ገላትያ",    "en": "Galatians",        "testament": "NT", "order": 48},
    "EPH": {"am": "ኤፌሶን",    "en": "Ephesians",        "testament": "NT", "order": 49},
    "PHI": {"am": "ፊልጵስዩስ",  "en": "Philippians",      "testament": "NT", "order": 50},
    "COL": {"am": "ቆላስይስ",   "en": "Colossians",       "testament": "NT", "order": 51},
    "1TH": {"am": "1ተሰሎ",   "en": "1 Thessalonians",  "testament": "NT", "order": 52},
    "2TH": {"am": "2ተሰሎ",   "en": "2 Thessalonians",  "testament": "NT", "order": 53},
    "1TI": {"am": "1ጢሞቴዎስ",  "en": "1 Timothy",        "testament": "NT", "order": 54},
    "2TI": {"am": "2ጢሞቴዎስ",  "en": "2 Timothy",        "testament": "NT", "order": 55},
    "TIT": {"am": "ቲቶ",      "en": "Titus",            "testament": "NT", "order": 56},
    "PHM": {"am": "ፊልሞና",    "en": "Philemon",         "testament": "NT", "order": 57},
    "HEB": {"am": "ዕብራዊያን",  "en": "Hebrews",          "testament": "NT", "order": 58},
    "JAM": {"am": "ያዕቆብ",    "en": "James",            "testament": "NT", "order": 59},
    "1PE": {"am": "1ጴጥሮስ",   "en": "1 Peter",          "testament": "NT", "order": 60},
    "2PE": {"am": "2ጴጥሮስ",   "en": "2 Peter",          "testament": "NT", "order": 61},
    "1JO": {"am": "1ዮሐንስ",   "en": "1 John",           "testament": "NT", "order": 62},
    "2JO": {"am": "2ዮሐንስ",   "en": "2 John",           "testament": "NT", "order": 63},
    "3JO": {"am": "3ዮሐንስ",   "en": "3 John",           "testament": "NT", "order": 64},
    "JUD": {"am": "ይሁዳ",     "en": "Jude",             "testament": "NT", "order": 65},
    "REV": {"am": "ራዕይ",     "en": "Revelation",       "testament": "NT", "order": 66},
}


def get_books_index() -> dict:
    """Return OT and NT book lists sorted canonically."""
    data = _load()
    ot, nt = [], []
    for code, meta in sorted(BOOK_META.items(), key=lambda x: x[1]["order"]):
        if code not in data:
            continue
        chapters = data[code]
        entry = {
            "code":     code,
            "am":       meta["am"],
            "en":       meta["en"],
            "chapters": len(chapters),
        }
        (ot if meta["testament"] == "OT" else nt).append(entry)
    return {"OT": ot, "NT": nt}


def get_chapter_verses(code: str, chapter_num: int) -> dict | None:
    """Return all verses for a given book code + chapter number."""
    data = _load()
    book = data.get(code.upper())
    if not book:
        return None
    chap = book.get(str(chapter_num))
    if not chap:
        return None
    meta = BOOK_META.get(code.upper(), {})
    total_chapters = len(book)
    prev_chap = chapter_num - 1 if chapter_num > 1 else None
    next_chap = chapter_num + 1 if chapter_num < total_chapters else None
    return {
        "book_code":      code.upper(),
        "book_am":        meta.get("am", code),
        "book_en":        meta.get("en", code),
        "testament":      meta.get("testament", "OT"),
        "chapter":        chapter_num,
        "total_chapters": total_chapters,
        "total_verses":   len(chap),
        "verses":         chap,
        "prev_chapter":   prev_chap,
        "next_chapter":   next_chap,
    }
