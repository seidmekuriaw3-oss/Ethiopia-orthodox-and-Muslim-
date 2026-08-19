"""Read-only PostgreSQL catalog health check."""

from database.db import get_db


def check_data():
    """Print current product, category, and advertisement counts."""
    cursor = get_db().cursor()
    counts = {}
    for table in ("products", "categories", "advertisements"):
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        counts[table] = cursor.fetchone()["count"]
    print("SEMIRA FASHION PostgreSQL catalog status")
    for table, count in counts.items():
        print(f"  {table}: {count}")
    return counts


if __name__ == "__main__":
    check_data()