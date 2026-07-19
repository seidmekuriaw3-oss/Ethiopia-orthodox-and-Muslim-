"""
SEMIRA FASHION - Database Seeder (PostgreSQL)
Seeds 20 fashion products with real photo URLs, 5 advertisements, and settings.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─── 20 realistic fashion products with real Unsplash photo URLs ───────────
PRODUCTS = [
    # (name_am, name_en, description_en, price, compare_price, stock, category_am, is_featured, image_url)
    (
        'ሉክስ 储ምሳሴ ቀሚስ',
        'Luxury Evening Gown',
        'Elegant floor-length evening gown with embroidered details. Perfect for weddings and formal events.',
        3200, 4500, 15, 'ቀሚሶች', True,
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop'
    ),
    (
        'ሞደርን ራፕ ቀሚስ',
        'Modern Wrap Dress',
        'Contemporary wrap dress in floral print. Flattering silhouette for all body types.',
        1800, 2400, 30, 'ቀሚሶች', True,
        'https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=600&auto=format&fit=crop'
    ),
    (
        'ክላሲክ ሚዲ ቀሚስ',
        'Classic Midi Dress',
        'Timeless midi dress in solid color. Versatile piece for office and casual outings.',
        1500, 2100, 25, 'ቀሚሶች', False,
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&auto=format&fit=crop'
    ),
    (
        'ሚኒ ፍሎራል ቀሚስ',
        'Mini Floral Dress',
        'Playful short dress with vibrant floral pattern. Ideal for summer outings.',
        1200, 1700, 40, 'ቀሚሶች', False,
        'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop'
    ),
    (
        'ቦሆ ማክሲ ቀሚስ',
        'Boho Maxi Dress',
        'Free-flowing bohemian maxi dress with elegant drape. Perfect for casual and beach events.',
        2000, 2800, 20, 'ቀሚሶች', True,
        'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'
    ),
    (
        'ሲልክ ብሉዝ',
        'Silk Blouse',
        'Luxurious silk blouse with V-neck design. Pairs beautifully with trousers or skirts.',
        1100, 1600, 35, 'ቶፖች እና ሸሚዞች', True,
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&auto=format&fit=crop'
    ),
    (
        'ፕሪንትድ ቲሸርት',
        'Printed Graphic T-Shirt',
        'Comfortable cotton t-shirt with artistic print. Casual everyday essential.',
        550, 800, 60, 'ቶፖች እና ሸሚዞች', False,
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop'
    ),
    (
        'ዴኒም ጃኬት',
        'Classic Denim Jacket',
        'Timeless denim jacket with button front. A wardrobe staple for all seasons.',
        2200, 3000, 20, 'ጃኬቶች እና ሹራቦች', True,
        'https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600&auto=format&fit=crop'
    ),
    (
        'ሴቶች ሱት ሴት',
        "Women's Blazer Suit Set",
        'Professional blazer and trouser set. Sharp look for business meetings and formal events.',
        3800, 5200, 10, 'ሱሪዎች እና ቁምጣዎች', True,
        'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&auto=format&fit=crop'
    ),
    (
        'ሃይ-ዌስት ትሮዘር',
        'High-Waist Tailored Trousers',
        'Elegant high-waist trousers with straight cut. Versatile for office and evening wear.',
        1400, 2000, 25, 'ሱሪዎች እና ቁምጣዎች', False,
        'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&auto=format&fit=crop'
    ),
    (
        'ስኪኒ ጂንስ',
        'Skinny Stretch Jeans',
        'High-quality stretch denim jeans. Comfortable fit with modern slim silhouette.',
        1600, 2200, 30, 'ሱሪዎች እና ቁምጣዎች', True,
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&auto=format&fit=crop'
    ),
    (
        'ሕፃናት ፓርቲ ቀሚስ',
        "Girls' Party Dress",
        'Beautiful tutu dress for little girls. Perfect for birthdays and celebrations.',
        750, 1100, 30, 'የሕፃናት ሙሉ ልብሶች', False,
        'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600&auto=format&fit=crop'
    ),
    (
        'ወንዶ ልጅ ሸሚዝ',
        "Boys' Oxford Shirt",
        'Classic Oxford shirt for boys. Comfortable and smart for school and events.',
        600, 850, 35, 'የሕፃናት ሙሉ ልብሶች', False,
        'https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=600&auto=format&fit=crop'
    ),
    (
        'ሳቲን ፓጃማ ሴት',
        'Satin Pajama Set',
        'Luxurious satin pajama set with lace trim. For a comfortable and elegant bedtime.',
        1000, 1400, 20, 'የውስጥ እና የሌሊት ልብሶች', False,
        'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop'
    ),
    (
        'ፍሉፊ ቤት ሮብ',
        'Fluffy Home Robe',
        'Ultra-soft plush robe for cozy home moments. Available in multiple colors.',
        900, 1300, 15, 'የውስጥ እና የሌሊት ልብሶች', False,
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'
    ),
    (
        'ትራክሱት ሴት',
        'Athletic Tracksuit Set',
        'Matching jacket and jogger set. Breathable fabric perfect for workouts and leisure.',
        1800, 2500, 25, 'ስፖርታዊ ልብሶች', True,
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&auto=format&fit=crop'
    ),
    (
        'ዮጋ ሊጊንስ ሴት',
        'Yoga Leggings & Top Set',
        'High-performance yoga set with moisture-wicking fabric. Stylish support for every pose.',
        1300, 1900, 20, 'ስፖርታዊ ልብሶች', False,
        'https://images.unsplash.com/photo-1518459031867-a89b944bffe4?w=600&auto=format&fit=crop'
    ),
    (
        'ሃበሻ ቀሚስ',
        'Traditional Habesha Kemis',
        'Authentic Ethiopian traditional dress with beautiful woven border (tilet). Handcrafted quality.',
        2500, 3500, 12, 'የባህል ልብሶች', True,
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'
    ),
    (
        'ፕሪሚየም ሂጃብ',
        'Premium Jersey Hijab',
        'Soft jersey hijab that stays in place all day. Breathable fabric in a range of colours.',
        450, 650, 60, 'ሃይማኖታዊ አልባሳት', True,
        'https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=600&auto=format&fit=crop'
    ),
    (
        'ሲልክ ስካርፍ',
        'Luxury Silk Scarf',
        'Versatile silk scarf that works as a hijab, head wrap, or neck accessory.',
        600, 900, 45, 'ሃይማኖታዊ አልባሳት', False,
        'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&auto=format&fit=crop'
    ),
]

# ─── 5 advertisements / promo banners ──────────────────────────────────────
ADS = [
    (
        '🔥 Summer Sale — Up to 50% Off!',
        '🔥 የበጋ ቅናሽ — እስከ 50% ቅናሽ!',
        'Shop our biggest sale of the year. Hundreds of styles marked down.',
        'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=800&auto=format&fit=crop',
        '/products', 1
    ),
    (
        '✨ New Collection Has Arrived',
        '✨ አዲስ ስብስብ ደርሷል!',
        'Fresh styles for every occasion. Be the first to shop the new arrivals.',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&auto=format&fit=crop',
        '/products', 2
    ),
    (
        '🚚 Free Shipping on Orders Over 5,000 ETB',
        '🚚 ከ5,000 ብር በላይ ትዕዛዝ ነጻ ማጓጓዣ!',
        'Order more, pay less. Free delivery right to your door.',
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop',
        '/cart', 3
    ),
    (
        '🎁 Buy 2 Get 1 Free — This Week Only',
        '🎁 2 ቢገዙ 1 ነጻ — ይህ ሳምንት ብቻ!',
        'Stock up and save! Add any three items to your cart to claim your free piece.',
        'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&auto=format&fit=crop',
        '/products', 4
    ),
    (
        '👗 Traditional Wear Festival Special',
        '👗 የባህል ልብስ የፌስቲቫል ቅናሽ!',
        'Celebrate in style with our authentic Ethiopian and Islamic fashion pieces.',
        'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=800&auto=format&fit=crop',
        '/products', 5
    ),
]


def seed_all(clear_existing=True):
    """Insert all sample data into PostgreSQL database."""
    try:
        from database.db import get_db
        conn = get_db()
        cursor = conn.cursor()

        print("\n" + "=" * 60)
        print("🌱 SEMIRA FASHION DATABASE SEEDER")
        print("=" * 60)

        # ══════════════════ CATEGORIES ══════════════════
        print("\n📁 Seeding categories...")
        category_defs = [
            ('ቀሚሶች',                'Dresses & Gowns',       'فساتين وعبايات'),
            ('ቶፖች እና ሸሚዞች',        'Tops & Shirts',          'قمصان وبلوزات'),
            ('ሱሪዎች እና ቁምጣዎች',      'Trousers & Shorts',      'بنطلونات'),
            ('ጃኬቶች እና ሹራቦች',       'Jackets & Knitwear',     'جاكيتات'),
            ('የውስጥ እና የሌሊት ልብሶች', 'Underwear & Nightwear',  'ملابس نوم'),
            ('የሕፃናት ሙሉ ልብሶች',      'Baby & Kids Wear',       'ملابس أطفال'),
            ('ስፖርታዊ ልብሶች',         'Activewear',             'ملابس رياضية'),
            ('የባህል ልብሶች',          'Traditional Wear',       'ملابس تقليدية'),
            ('ሃይማኖታዊ አልባሳት',      'Religious Wear',         'ملابس دينية'),
        ]
        cat_ids = {}
        for name_am, name_en, name_ar in category_defs:
            cursor.execute(
                "SELECT id FROM categories WHERE name = %s OR name_am = %s LIMIT 1",
                (name_en, name_am)
            )
            existing = cursor.fetchone()
            if existing:
                cat_ids[name_am] = existing[0]
            else:
                cursor.execute(
                    "INSERT INTO categories (name, name_am, name_ar, is_active) "
                    "VALUES (%s, %s, %s, 1) RETURNING id",
                    (name_en, name_am, name_ar)
                )
                row = cursor.fetchone()
                if row:
                    cat_ids[name_am] = row[0]
        conn.commit()
        print(f"   ✅ {len(cat_ids)} categories ready")

        # ══════════════════ PRODUCTS ══════════════════
        print("\n📦 Seeding 20 fashion products...")
        if clear_existing:
            cursor.execute(
                "DELETE FROM order_items WHERE product_id IN (SELECT id FROM products)"
            )
            cursor.execute(
                "DELETE FROM cart_items WHERE product_id IN (SELECT id FROM products)"
            )
            cursor.execute("DELETE FROM products")
            conn.commit()
            print("   ✓ Cleared existing products")

        def cid(name_am):
            return cat_ids.get(name_am) or (list(cat_ids.values())[0] if cat_ids else None)

        inserted = 0
        for (name_am, name_en, desc_en, price, compare_price,
             stock, cat_am, featured, image_url) in PRODUCTS:
            try:
                cursor.execute("""
                    INSERT INTO products
                        (name_am, name, description, price, compare_price,
                         stock_quantity, category_id, is_active, is_featured,
                         is_new, thumbnail, images, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, 1, %s, %s, %s)
                """, (
                    name_am, name_en, desc_en, price, compare_price,
                    stock, cid(cat_am), 1 if featured else 0,
                    image_url,
                    f'["{image_url}"]',
                    datetime.now()
                ))
                inserted += 1
            except Exception as e:
                print(f"   ⚠️  Could not insert '{name_en}': {e}")
                conn.rollback()
        conn.commit()
        print(f"   ✅ Inserted {inserted} products")

        # ══════════════════ ADVERTISEMENTS ══════════════════
        print("\n📢 Seeding 5 advertisements...")
        if clear_existing:
            cursor.execute("DELETE FROM advertisements")
            conn.commit()
            print("   ✓ Cleared existing advertisements")

        inserted_ads = 0
        for title_en, title_am, description, image_url, link, sort_order in ADS:
            try:
                cursor.execute("""
                    INSERT INTO advertisements
                        (title, title_am, description, image, link,
                         sort_order, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
                """, (
                    title_en, title_am, description, image_url, link,
                    sort_order, datetime.now()
                ))
                inserted_ads += 1
            except Exception as e:
                print(f"   ⚠️  Could not insert ad '{title_en}': {e}")
                conn.rollback()
        conn.commit()
        print(f"   ✅ Inserted {inserted_ads} advertisements")

        # ══════════════════ SETTINGS ══════════════════
        print("\n⚙️  Updating default settings...")
        settings = [
            ('site_name',               'SEMIRA FASHION'),
            ('site_name_am',            'ሰሚራ ፋሽን'),
            ('site_email',              'info@semirafashion.com'),
            ('site_phone',              '+251987957957'),
            ('admin_email',             'admin@semirafashion.com'),
            ('whatsapp_number',         '251987957957'),
            ('free_shipping_threshold', '5000'),
            ('shipping_cost',           '200'),
            ('currency',                'ETB'),
            ('currency_symbol',         'ETB'),
            ('default_language',        'am'),
            ('products_per_page',       '12'),
            ('maintenance_mode',        'false'),
            ('store_address',           'ወሎ ደሴ ኩታበር, Ethiopia'),
            ('last_seeded',             datetime.now().isoformat()),
        ]
        for key, value in settings:
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (%s, %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (key, value)
            )
        conn.commit()
        print(f"   ✅ Updated {len(settings)} settings")

        # ══════════════════ UPLOAD DIRECTORIES ══════════════════
        for directory in ['static/uploads', 'static/uploads/products', 'static/uploads/ads', 'logs']:
            os.makedirs(directory, exist_ok=True)

        # ══════════════════ SUMMARY ══════════════════
        cursor.execute("SELECT COUNT(*) FROM products")
        final_products = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM advertisements")
        final_ads = cursor.fetchone()[0]

        print("\n" + "=" * 60)
        print("📊 SEEDING SUMMARY")
        print("=" * 60)
        print(f"📦 Products:       {final_products}")
        print(f"📢 Advertisements: {final_ads}")
        print(f"⚙️  Settings:       {len(settings)}")
        print("=" * 60)
        print("✅ Database seeded successfully!")
        print(f"🌐 Website: http://localhost:5000")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Seeding error: {e}")
        import traceback
        traceback.print_exc()
        return False


def seed_products_only():
    """Seed only products without clearing existing data."""
    return seed_all(clear_existing=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Seed database for SEMIRA FASHION')
    parser.add_argument('--keep', action='store_true', help='Keep existing data')
    parser.add_argument('--products-only', action='store_true', help='Seed only products')
    args = parser.parse_args()

    from app import app
    with app.app_context():
        if args.products_only:
            seed_products_only()
        else:
            seed_all(clear_existing=not args.keep)
