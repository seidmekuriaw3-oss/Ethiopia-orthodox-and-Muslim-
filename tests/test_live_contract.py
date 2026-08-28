"""Regression tests for the current PostgreSQL Semira Fashion application."""

import os
import re
import uuid

import pytest

from database.db import get_db

pytestmark = pytest.mark.postgres


def test_public_pages_load(client):
    for path in ("/", "/products", "/categories", "/cart/"):
        response = client.get(path)
        assert response.status_code == 200, path


def test_products_page_uses_server_pagination_contract(client):
    response = client.get('/products?page=2&sort=price_desc&in_stock=1')
    assert response.status_code == 200
    assert b'id="productsGrid"' in response.data
    assert b'id="pagination"' in response.data


def test_protected_pages_require_authentication(client):
    admin_response = client.get('/admin/dashboard')
    assert admin_response.status_code == 302
    assert '/admin/login' in admin_response.location

    upload_response = client.post('/profile/upload-photo')
    assert upload_response.status_code == 302
    assert '/login' in upload_response.location


def test_checkout_empty_cart_redirects_to_home(client):
    with client.session_transaction() as session:
        session.pop('cart', None)
        session.pop('user_id', None)
    response = client.get('/cart/checkout')
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_cart_api_rejects_malformed_quantity(client):
    response = client.post('/api/cart/add', json={
        'product_id': 'not-an-id',
        'quantity': 'not-a-number',
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False


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


def test_state_changing_api_requires_csrf_token(client, app):
    original_testing = app.config.get('TESTING')
    app.config['TESTING'] = False
    try:
        with app.app_context():
            cursor = get_db().cursor()
            cursor.execute(
                "SELECT id FROM products WHERE is_active = 1 AND stock_quantity > 0 ORDER BY id LIMIT 1"
            )
            product = cursor.fetchone()
        assert product is not None, 'The live test database needs an in-stock product'
        product_id = product['id']

        missing_token = client.post('/api/cart/add', json={'product_id': product_id, 'quantity': 1})
        assert missing_token.status_code == 403

        client.get('/')
        with client.session_transaction() as session:
            token = session['_csrf_token']

        headers = {'X-CSRFToken': token}
        added = client.post(
            '/api/cart/add',
            json={'product_id': product_id, 'quantity': 1},
            headers=headers,
        )
        assert added.status_code == 200

        removed = client.post(
            '/api/cart/remove',
            json={'product_id': product_id},
            headers=headers,
        )
        assert removed.status_code == 200
    finally:
        app.config['TESTING'] = original_testing


def test_telegram_webhook_requires_secret_header(client, app, monkeypatch):
    monkeypatch.setenv('TELEGRAM_WEBHOOK_SECRET', 'test-telegram-webhook-secret')
    assert client.post('/telegram/webhook', json={}).status_code == 403
    assert client.post(
        '/telegram/webhook',
        json={},
        headers={'X-Telegram-Bot-Api-Secret-Token': 'wrong-secret'},
    ).status_code == 403
    assert client.post(
        '/telegram/webhook',
        json={},
        headers={'X-Telegram-Bot-Api-Secret-Token': 'test-telegram-webhook-secret'},
    ).status_code == 200
    assert client.post('/telegram/webhook/exposed-token', json={}).status_code == 404


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


def test_deleting_category_sets_product_category_to_null(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        marker = uuid.uuid4().hex
        cursor.execute(
            "INSERT INTO categories (name, name_am, sort_order, is_active) "
            "VALUES (%s, %s, 999, 1) RETURNING id",
            (f'Test Category {marker}', f'የሙከራ ምድብ {marker}'),
        )
        category_id = cursor.fetchone()['id']
        cursor.execute(
            "INSERT INTO products (name, name_en, price, category_id, sku) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (f'Test Product {marker}', f'Test Product {marker}', 1, category_id, marker),
        )
        product_id = cursor.fetchone()['id']
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        db.commit()

        cursor.execute("SELECT category_id FROM products WHERE id = %s", (product_id,))
        assert cursor.fetchone()['category_id'] is None
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()


def test_cart_upsert_keeps_one_row_per_user_product(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        user = cursor.fetchone()
        cursor.execute("SELECT id FROM products ORDER BY id LIMIT 1")
        product = cursor.fetchone()
        assert user is not None
        assert product is not None

        cursor.execute(
            "DELETE FROM cart_items WHERE user_id = %s AND product_id = %s",
            (user['id'], product['id']),
        )
        db.commit()

        cursor.execute(
            """INSERT INTO cart_items (user_id, product_id, quantity)
               VALUES (%s, %s, %s)
               ON CONFLICT (user_id, product_id)
               DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity""",
            (user['id'], product['id'], 1),
        )
        cursor.execute(
            """INSERT INTO cart_items (user_id, product_id, quantity)
               VALUES (%s, %s, %s)
               ON CONFLICT (user_id, product_id)
               DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity""",
            (user['id'], product['id'], 2),
        )
        db.commit()

        cursor.execute(
            "SELECT COUNT(*) AS count, SUM(quantity) AS quantity FROM cart_items "
            "WHERE user_id = %s AND product_id = %s",
            (user['id'], product['id']),
        )
        row = cursor.fetchone()
        assert row['count'] == 1
        assert row['quantity'] == 3

        cursor.execute(
            "DELETE FROM cart_items WHERE user_id = %s AND product_id = %s",
            (user['id'], product['id']),
        )
        db.commit()


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