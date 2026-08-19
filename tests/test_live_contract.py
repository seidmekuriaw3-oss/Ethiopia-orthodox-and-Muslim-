"""Regression tests for the current PostgreSQL Semira Fashion application."""

import os
import re

from database.db import get_db


def test_public_pages_load(client):
    for path in ("/", "/products", "/categories", "/cart/"):
        response = client.get(path)
        assert response.status_code == 200, path


def test_current_api_routes_use_the_live_contract(client):
    products = client.get("/api/products")
    assert products.status_code == 200
    product_data = products.get_json()
    assert product_data["success"] is True
    assert isinstance(product_data["products"], list)

    search = client.get("/api/products/search?q=shirt")
    assert search.status_code == 200
    assert search.get_json()["success"] is True

    empty_search = client.get("/api/products/search?q=")
    assert empty_search.status_code == 200
    assert empty_search.get_json()["products"] == []

    categories = client.get("/api/categories")
    assert categories.status_code == 200
    assert categories.get_json()["success"] is True


def test_customer_category_list_excludes_empty_categories(client, app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT c.id
            FROM categories c
            WHERE c.is_active = 1
              AND NOT EXISTS (
                  SELECT 1 FROM products p
                  WHERE p.category_id = c.id AND p.is_active = 1
              )
            LIMIT 1
            """
        )
        empty_category = cursor.fetchone()

    page = client.get("/categories").get_data(as_text=True)
    if empty_category:
        assert f'data-category="{empty_category["id"]}"' not in page


def test_cart_renders_a_loadable_product_image(client, app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, thumbnail
            FROM products
            WHERE is_active = 1 AND thumbnail IS NOT NULL AND thumbnail <> ''
            ORDER BY id
            LIMIT 1
            """
        )
        product = cursor.fetchone()
        assert product is not None

    with client.session_transaction() as session:
        session["cart"] = {str(product["id"]): 1}

    page = client.get("/cart/").get_data(as_text=True)
    image_urls = re.findall(r'<img[^>]+src="([^"]+)"', page)
    product_urls = [
        url for url in image_urls
        if "/uploads/products/" in url
    ]
    assert product_urls

    for url in product_urls:
        filename = url.split("/static/", 1)[-1]
        assert os.path.isfile(os.path.join("static", filename))


def test_all_active_product_thumbnails_exist(app):
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute(
            "SELECT id, thumbnail FROM products WHERE is_active = 1"
        )
        rows = cursor.fetchall()

    missing = []
    for row in rows:
        thumbnail = (row["thumbnail"] or "").strip()
        relative = thumbnail
        if relative.startswith("/static/"):
            relative = relative[8:]
        elif relative.startswith("static/"):
            relative = relative[7:]
        if not relative.startswith(("uploads/", "images/")):
            relative = "uploads/products/" + relative
        if not os.path.isfile(os.path.join("static", relative)):
            missing.append((row["id"], thumbnail))

    assert missing == []