"""PostgreSQL advertisement seeder compatibility entrypoint.

This replaces the retired SQLite advertisement script while preserving the
function names used by ``run.py``.
"""

import argparse

from database.db import get_db
from scripts.seed_sample_catalog import ADS


def seed_ads(with_media=False):
    """Seed the shared sample advertisements into PostgreSQL."""
    db = get_db()
    cursor = db.cursor()
    added = 0
    for title, title_am, description, image_file, sort_order in ADS:
        cursor.execute(
            "SELECT id FROM advertisements WHERE title = %s LIMIT 1",
            (title,),
        )
        if cursor.fetchone():
            continue
        image_path = f"uploads/ads/{image_file}" if with_media else ""
        cursor.execute(
            """
            INSERT INTO advertisements
                (title, title_am, description, image, sort_order, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
            """,
            (title, title_am, description, image_path, sort_order),
        )
        added += 1
    db.commit()
    print(f"PostgreSQL advertisements added: {added}")
    return added


def clear_ads():
    """Remove all advertisements from PostgreSQL."""
    db = get_db()
    db.execute("DELETE FROM advertisements")
    db.commit()
    print("PostgreSQL advertisements cleared.")
    return True


def show_ads():
    """Print a concise PostgreSQL advertisement summary."""
    rows = get_db().execute(
        "SELECT id, title, is_active FROM advertisements ORDER BY id DESC"
    ).fetchall()
    for row in rows:
        print(f"#{row['id']}: {row['title']} — active={row['is_active']}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Semira Fashion advertisements into PostgreSQL")
    parser.add_argument("--media", action="store_true", help="Store seeded media paths")
    parser.add_argument("--show", action="store_true", help="Show current advertisements")
    args = parser.parse_args()
    if args.show:
        show_ads()
    else:
        seed_ads(with_media=args.media)