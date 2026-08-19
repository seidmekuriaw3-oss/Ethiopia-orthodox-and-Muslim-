"""Safe PostgreSQL catalog maintenance commands.

This replaces the retired SQLite cleanup utility. Destructive commands require
an explicit confirmation unless ``--force`` is supplied.
"""

import argparse

from database.db import get_db


def _delete(table, where=None):
    db = get_db()
    cursor = db.cursor()
    query = f"DELETE FROM {table}"
    if where:
        query += f" WHERE {where}"
    cursor.execute(query)
    count = cursor.rowcount
    db.commit()
    return count


def view_counts():
    cursor = get_db().cursor()
    counts = {}
    for table in ("products", "advertisements", "orders", "categories"):
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        counts[table] = cursor.fetchone()["count"]
    for table, count in counts.items():
        print(f"{table}: {count}")
    return counts


def clear_products_only(confirm=True):
    if confirm and input("Clear all products and dependent cart/order rows? (yes/no): ").lower() != "yes":
        print("Cancelled.")
        return False
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM order_items WHERE product_id IN (SELECT id FROM products)")
    cursor.execute("DELETE FROM cart_items WHERE product_id IN (SELECT id FROM products)")
    cursor.execute("DELETE FROM products")
    db.commit()
    print("Products cleared from PostgreSQL.")
    return True


def clear_ads_only(confirm=True):
    if confirm and input("Clear all advertisements? (yes/no): ").lower() != "yes":
        print("Cancelled.")
        return False
    print(f"Advertisements cleared: {_delete('advertisements')}")
    return True


def clear_orders_only(confirm=True):
    if confirm and input("Clear all orders? (yes/no): ").lower() != "yes":
        print("Cancelled.")
        return False
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    db.commit()
    print("Orders cleared from PostgreSQL.")
    return True


def clear_all_data(confirm=True):
    if confirm and input("Clear products, advertisements, and orders? (yes/no): ").lower() != "yes":
        print("Cancelled.")
        return False
    clear_orders_only(confirm=False)
    clear_products_only(confirm=False)
    clear_ads_only(confirm=False)
    return True


def clear_and_seed_demo():
    clear_all_data(confirm=True)
    from seed_all import seed_all
    return seed_all(clear_existing=False)


def backup_before_clear():
    print("Database backups are managed by PostgreSQL/Replit; no local SQLite backup is created.")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintain the Semira Fashion PostgreSQL catalog")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--products", action="store_true")
    parser.add_argument("--ads", action="store_true")
    parser.add_argument("--orders", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--counts", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    confirm = not args.force
    if args.all:
        clear_all_data(confirm=confirm)
    elif args.products:
        clear_products_only(confirm=confirm)
    elif args.ads:
        clear_ads_only(confirm=confirm)
    elif args.orders:
        clear_orders_only(confirm=confirm)
    elif args.reset:
        clear_and_seed_demo()
    elif args.backup:
        backup_before_clear()
    else:
        view_counts()