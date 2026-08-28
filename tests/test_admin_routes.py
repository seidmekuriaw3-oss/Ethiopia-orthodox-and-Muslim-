from database.db import get_db
import pytest


pytestmark = pytest.mark.legacy


def test_admin_product_create_uses_name_en_for_display_name(client):
    with client.session_transaction() as session:
        session['admin'] = True
        session['_csrf_token'] = 'test-csrf-token'

    with client.application.app_context():
        cursor = get_db().cursor()
        cursor.execute("SELECT id FROM categories WHERE is_active = 1 ORDER BY id LIMIT 1")
        category = cursor.fetchone()
    assert category is not None, 'The PostgreSQL test database needs an active category'

    response = client.post('/admin/products/create', data={
        'name_am': 'ሙከራ ምርት',
        'name_en': 'Sample Product',
        'price': '120',
        'stock_quantity': '5',
        'category_id': str(category['id']),
        'csrf_token': 'test-csrf-token',
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.application.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, name_en FROM products WHERE name_en = %s ORDER BY id DESC LIMIT 1", ('Sample Product',))
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == 'Sample Product'
    assert row[1] == 'Sample Product'


def test_admin_ad_create_uses_ad_text_for_description(client):
    with client.session_transaction() as session:
        session['admin'] = True
        session['_csrf_token'] = 'test-csrf-token'

    response = client.post('/admin/ads/create', data={
        'ad_text': 'Spring offer for customers',
        'title': 'Spring Sale',
        'link': 'https://example.com',
        'csrf_token': 'test-csrf-token',
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.application.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, description FROM advertisements WHERE title = %s ORDER BY id DESC LIMIT 1", ('Spring Sale',))
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == 'Spring Sale'
    assert row[1] == 'Spring offer for customers'


def test_admin_settings_page_renders_for_authenticated_admin(client):
    with client.session_transaction() as sess:
        sess['admin'] = True

    response = client.get('/admin/settings')

    assert response.status_code == 200
    assert b'Admin Settings' in response.data
