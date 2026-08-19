"""PostgreSQL product seeder compatibility entrypoint.

The original version of this script wrote to a retired SQLite database.
Keep the command name used by ``run.py``, but use the current PostgreSQL
schema and the shared sample catalog instead.
"""

import argparse

from database.db import get_db
from scripts.seed_sample_catalog import PRODUCTS


def seed_products(clear_existing=True, add_images=False):
    """Seed the shared sample products into PostgreSQL."""
    db = get_db()
    cursor = db.cursor()
    if clear_existing:
        cursor.execute("DELETE FROM order_items WHERE product_id IN (SELECT id FROM products)")
        cursor.execute("DELETE FROM cart_items WHERE product_id IN (SELECT id FROM products)")
        cursor.execute("DELETE FROM products")

    added = 0
    for name_en, name_am, category_id, price, compare_price, stock, image_file, featured, gender in PRODUCTS:
        cursor.execute(
            "SELECT id FROM products WHERE name = %s AND category_id = %s",
            (name_en, category_id),
        )
        if cursor.fetchone():
            continue
        image_path = f"uploads/products/{image_file}"
        cursor.execute(
            """
            INSERT INTO products
                (name, name_am, name_en, price, compare_price, stock_quantity,
                 category_id, images, thumbnail, is_active, is_featured, is_new, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, 1, %s)
            """,
            (
                name_en, name_am, name_en, price, compare_price, stock,
                category_id, image_path, image_path, featured, gender,
            ),
        )
        added += 1
    db.commit()
    print(f"PostgreSQL products added: {added}")
    return added


def clear_products():
    """Remove products and dependent cart/order rows from PostgreSQL."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM order_items WHERE product_id IN (SELECT id FROM products)")
    cursor.execute("DELETE FROM cart_items WHERE product_id IN (SELECT id FROM products)")
    cursor.execute("DELETE FROM products")
    db.commit()
    print("PostgreSQL products cleared.")
    return True


def show_products():
    """Print a concise PostgreSQL product summary."""
    rows = get_db().execute(
        "SELECT id, name, price, stock_quantity FROM products ORDER BY id DESC"
    ).fetchall()
    for row in rows:
        print(f"#{row['id']}: {row['name']} — {row['price']} ETB — stock {row['stock_quantity']}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Semira Fashion products into PostgreSQL")
    parser.add_argument("--append", action="store_true", help="Keep existing products")
    parser.add_argument("--show", action="store_true", help="Show current products")
    args = parser.parse_args()
    if args.show:
        show_products()
    else:
        seed_products(clear_existing=not args.append)