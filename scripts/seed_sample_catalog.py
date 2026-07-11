"""
One-off seeder: adds 20 real-photo sample products (across all 8 categories)
and 5 advertisements to the PostgreSQL database.

Images were sourced from real product photography on the web and saved to
static/uploads/products/ and static/uploads/ads/.
Safe to re-run: skips rows that already exist (matched by name + category).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db

PRODUCTS = [
    # name_en, name_am, category_id, price, compare_price, stock, image_file, is_featured, gender
    ("Habesha Kemis", "ሀበሻ ቀሚስ", 8, 3800, 5200, 18, "habesha_kemis.jpg", 1, "women"),
    ("Modern Abaya", "ዘመናዊ አባያ", 8, 2600, 3400, 22, "modern_abaya.jpg", 0, "women"),
    ("Ethiopian Netela Gabi", "የኢትዮጵያ ነጠላ ጋቢ", 8, 2200, 2900, 25, "ethiopian_gabi.jpg", 0, "unisex"),
    ("Elegant Evening Gown", "ውብ የምሽት ቀሚስ", 1, 4200, 5800, 10, "evening_gown.jpg", 1, "women"),
    ("Luxury Floral Dress", "የአበባ ንድፍ ቀሚስ", 1, 2100, 2900, 20, "floral_dress.jpg", 1, "women"),
    ("Casual Maxi Dress", "ካዥዋል ማክሲ ቀሚስ", 1, 1650, 2200, 28, "maxi_dress.jpg", 0, "women"),
    ("Classic Polo Shirt", "ክላሲክ ፖሎ ሸሚዝ", 2, 900, 1300, 40, "polo_shirt.jpg", 0, "men"),
    ("Men's Formal Shirt", "የወንዶች መደበኛ ሸሚዝ", 2, 1100, 1500, 35, "formal_shirt.jpg", 0, "men"),
    ("Floral Crop Top", "የአበባ ክሮፕ ቶፕ", 2, 650, 950, 45, "crop_top.jpg", 1, "women"),
    ("High Waist Jeans", "ከፍ ያለ ወገብ ጂንስ", 3, 1500, 2100, 30, "jeans.jpg", 1, "women"),
    ("Slim Fit Chinos", "ስሊም ፊት ቺኖስ", 3, 1300, 1800, 26, "chinos.jpg", 0, "men"),
    ("Cargo Shorts", "ካርጎ ቁምጣ", 3, 850, 1200, 32, "cargo_shorts.jpg", 0, "men"),
    ("Denim Jacket", "ጂንስ ጃኬት", 4, 2000, 2700, 18, "denim_jacket.jpg", 1, "unisex"),
    ("Knit Cardigan", "ሹራብ ካርዲጋን", 4, 1400, 1900, 24, "cardigan.jpg", 0, "women"),
    ("Leather Biker Jacket", "የቆዳ ባይከር ጃኬት", 4, 3200, 4300, 12, "biker_jacket.jpg", 1, "unisex"),
    ("Silk Pajama Set", "የሐር ፒጃማ ስብስብ", 5, 1200, 1650, 20, "pajama.jpg", 0, "women"),
    ("Cotton Underwear Set", "የጥጥ የውስጥ ልብስ ስብስብ", 5, 550, 800, 50, "underwear.jpg", 0, "women"),
    ("Baby Onesie Set", "የሕፃናት ልብስ ስብስብ", 6, 750, 1050, 30, "baby_onesie.jpg", 1, "baby"),
    ("Running Sports Set", "የስፖርት ስብስብ", 7, 1350, 1850, 22, "sports_set.jpg", 1, "unisex"),
    ("Yoga Leggings", "የዮጋ ሌጊንስ", 7, 800, 1100, 38, "leggings.jpg", 0, "women"),
]

ADS = [
    ("Season Sale", "የወቅት ቅናሽ", "Up to 30% off across the store", "ad_sale_photo.jpg", 1),
    ("New Arrivals", "አዳዲስ ስብስቦች", "Fresh styles just landed", "ad_new_arrivals_photo.jpg", 2),
    ("Summer Collection", "የበጋ ስብስብ", "Light, bright looks for the season", "ad_summer_photo.jpg", 3),
    ("Holiday Elegance", "የበዓል ውበት", "Dress up for the celebrations", "ad_holiday_photo.jpg", 4),
    ("Traditional Ethiopian Wear", "የኢትዮጵያ ባህላዊ አልባሳት", "Handwoven heritage pieces", "ad_traditional_photo.jpg", 5),
]


def seed():
    conn = get_db()
    cur = conn.cursor()

    print("Seeding products...")
    added_p = 0
    for name_en, name_am, cat_id, price, compare, stock, img, featured, gender in PRODUCTS:
        cur.execute("SELECT id FROM products WHERE name = %s AND category_id = %s", (name_en, cat_id))
        if cur.fetchone():
            print(f"  - skip (exists): {name_en}")
            continue
        image_path = f"uploads/products/{img}"
        cur.execute(
            """
            INSERT INTO products
                (name, name_am, name_en, price, compare_price, stock_quantity,
                 category_id, images, thumbnail, is_active, is_featured, is_new, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, 1, %s)
            """,
            (name_en, name_am, name_en, price, compare, stock, cat_id,
             image_path, image_path, featured, gender)
        )
        added_p += 1
        print(f"  + added: {name_en}")
    conn.commit()
    print(f"Products added: {added_p}")

    print("\nSeeding advertisements...")
    added_a = 0
    for title, title_am, description, img, sort_order in ADS:
        cur.execute("SELECT id FROM advertisements WHERE title = %s", (title,))
        if cur.fetchone():
            print(f"  - skip (exists): {title}")
            continue
        image_path = f"uploads/ads/{img}"
        cur.execute(
            """
            INSERT INTO advertisements
                (title, title_am, description, image, sort_order, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
            """,
            (title, title_am, description, image_path, sort_order)
        )
        added_a += 1
        print(f"  + added: {title}")
    conn.commit()
    print(f"Advertisements added: {added_a}")

    cur.execute("SELECT COUNT(*) FROM products")
    total_p = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM advertisements")
    total_a = cur.fetchone()[0]
    print(f"\nTotals -> products: {total_p}, advertisements: {total_a}")


if __name__ == "__main__":
    seed()
