#!/usr/bin/env python3
"""
Download the christos-c Amharic Bible corpus XML and convert it to
database/amharic_bible.json  →  { "GEN": { "1": [{"number":1,"text":"..."}] } }

Run once:  python3 scripts/build_amharic_bible.py
"""
import json
import re
import sys
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

URL = "https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/Amharic.xml"
OUT = Path(__file__).parent.parent / "database" / "amharic_bible.json"

def main():
    print("Downloading Amharic Bible corpus …", flush=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    print(f"Downloaded {len(raw):,} bytes. Parsing …", flush=True)

    root = ET.fromstring(raw)
    # Namespace-free parsing — strip any namespace prefix
    bible = {}  # { "GEN": { "1": [ {"number":1,"text":"..."} ] } }

    for book_div in root.iter():
        if book_div.get("type") != "book":
            continue
        bid_raw = book_div.get("id", "")          # e.g. "b.GEN"
        bid = bid_raw.split(".")[-1].upper()       # "GEN"
        bible[bid] = {}

        for ch_div in book_div:
            if ch_div.get("type") != "chapter":
                continue
            cid_raw = ch_div.get("id", "")        # "b.GEN.1"
            parts = cid_raw.split(".")
            ch_num = parts[-1]                     # "1"
            verses = []
            for seg in ch_div:
                if seg.get("type") != "verse":
                    continue
                vid_raw = seg.get("id", "")        # "b.GEN.1.1"
                v_parts = vid_raw.split(".")
                v_num = int(v_parts[-1]) if v_parts[-1].isdigit() else len(verses) + 1
                text = (seg.text or "").strip()
                if text:
                    verses.append({"number": v_num, "text": text})
            bible[bid][ch_num] = verses

    books = len(bible)
    chapters = sum(len(v) for v in bible.values())
    print(f"Parsed {books} books, {chapters} chapters.", flush=True)
    print(f"Writing to {OUT} …", flush=True)
    OUT.write_text(json.dumps(bible, ensure_ascii=False), encoding="utf-8")
    print("Done ✓", flush=True)


if __name__ == "__main__":
    main()
