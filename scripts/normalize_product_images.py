"""Download legacy external product thumbnails into local static storage.

Run once after importing a catalog that contains absolute image URLs:
    python scripts/normalize_product_images.py
"""

import hashlib
import os
import sys
from pathlib import Path

import requests
import psycopg2.extras

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database.db import _raw_connect


UPLOAD_DIR = ROOT / "static" / "uploads" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def main():
    conn = _raw_connect()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                "SELECT id, thumbnail FROM products "
                "WHERE thumbnail ILIKE 'http://%' OR thumbnail ILIKE 'https://%'"
            )
            rows = cur.fetchall()

        updated = 0
        for row in rows:
            source = row["thumbnail"].strip()
            digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
            filename = f"product_{digest}.jpg"
            destination = UPLOAD_DIR / filename
            relative = f"uploads/products/{filename}"

            if not destination.exists():
                response = requests.get(
                    source,
                    timeout=20,
                    headers={"User-Agent": "Semira-Fashion-image-import/1.0"},
                )
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if not content_type.startswith("image/"):
                    raise RuntimeError(f"Remote URL did not return an image: {source}")
                destination.write_bytes(response.content)

            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET thumbnail=%s, updated_at=NOW() WHERE id=%s",
                    (relative, row["id"]),
                )
            updated += 1

        conn.commit()
        print(f"Normalized {updated} product thumbnails.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()