"""
seed_pg.py — Seed products and advertisements into PostgreSQL
using the image files already present in static/uploads/products/ and static/uploads/ads/

Usage:
    python seed_pg.py
"""

import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is not set")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# ── helpers ──────────────────────────────────────────────────────────────────

def img(filename):
    """Return the DB-stored thumbnail path for a product image."""
    return f"uploads/products/{filename}"

def ad_img(filename):
    """Return the DB-stored image path for an ad image."""
    return f"uploads/ads/{filename}"

# ── categories (already seeded by init_db) ───────────────────────────────────
# 1 Dresses & Gowns      5 Underwear & Nightwear
# 2 Tops & Shirts        6 Baby Suits & Rompers
# 3 Trousers & Shorts    7 Activewear
# 4 Jackets & Knitwear   8 Traditional Wear

# ── products ─────────────────────────────────────────────────────────────────
# (name, name_am, description, price, compare_price, cost, stock, cat_id, thumbnail, is_featured, is_new)

PRODUCTS = [
    # ── Traditional Wear (cat 8) ──────────────────────────────────────────
    ("Habesha Kemis", "ሀበሻ ቀሚስ",
     "እጅጉን የሚያምር ባህላዊ ሀበሻ ቀሚስ። ለሠርግ፣ ለፋሲካ እና ለሌሎች ክብረ-በዓላት ተስማሚ።",
     1850, 2200, 900, 25, 8, img("prod_01_habesha_kemis.jpg"), 1, 1),

    ("Ankara Dress", "አንካራ ቀሚስ",
     "ቀለማማ Ankara ጨርቅ ተጠቅሞ የተሰፋ ቀሚስ። ለዕለት ሥራ እና ለሠርግ ሁለቱም ይሆናል።",
     1450, 1800, 700, 30, 8, img("prod_02_ankara_dress.jpg"), 1, 1),

    ("Habesha Top", "ሀበሻ ቅምጥ",
     "ባህላዊ ጥልፍ ያለው ሀበሻ ቲሸርት/ቅምጥ። ከጂንስ ወይም ከሌሎች ሱሪዎች ጋር ይሠራል።",
     850, 1100, 420, 40, 8, img("prod_03_habesha_top.jpg"), 0, 1),

    ("Tilf Skirt", "ቲልፍ ቀሚስ",
     "ባህላዊ ጥልፍ ያለው ቲልፍ ቀሚስ። ለባህላዊ ዝግጅቶች ፍጹም ምርጫ።",
     1200, 1500, 600, 20, 8, img("product_tilf_skirt.jpg"), 1, 0),

    ("Tilf Dress", "ቲልፍ ልብስ",
     "ሙሉ ጥልፍ ያለው ረጅም ቲልፍ ቀሚስ። ለክብረ-በዓልና ሠርግ ተስማሚ።",
     2100, 2600, 1050, 15, 8, img("prod_08_tilf_dress.jpg"), 1, 0),

    ("Chiffon Kemis", "ሺፎን ቀሚስ",
     "ቀጭን ሺፎን ጨርቅ ተጠቅሞ የተሰፋ ሀበሻ ቀሚስ። ለበጋ ወቅት ተስማሚ።",
     1650, 2000, 800, 18, 8, img("prod_10_chiffon_kemis.jpg"), 1, 1),

    ("Habesha Dress", "ሀበሻ ቀሚስ (ዘመናዊ)",
     "ዘመናዊ ዲዛይን ያለው ሀበሻ ቀሚስ። ቀላል እና አምሮ ይታያሉ።",
     1750, 2100, 875, 22, 8, img("habesha_dress.jpg"), 0, 1),

    ("Gabi", "ጋቢ",
     "ባህላዊ ጋቢ — ለቀዝቃዛ ጊዜ እና ለሃይማኖታዊ ሥርዓቶች።",
     950, 1200, 475, 35, 8, img("product_gabi.jpg"), 0, 0),

    ("Netela", "ነጠላ",
     "ቀጭን ነጭ ነጠላ — ለቤተ ክርስቲያን እና ለሞቃት ቀናት ተስማሚ።",
     650, 850, 320, 50, 8, img("product_netela.jpg"), 0, 0),

    ("Kuta", "ኩታ",
     "ባህላዊ ኩታ — ለወንዶች ሃይማኖታዊ ሥርዓት ፍጹም ምርጫ።",
     1100, 1400, 550, 25, 8, img("product_kuta.jpg"), 0, 0),

    # ── Dresses & Gowns (cat 1) ───────────────────────────────────────────
    ("Bridal Gown", "የሠርግ ቀሚስ",
     "ውብ የሠርግ ቀሚስ። ለጋብቻ ቀን ፍጹም ምርጫ። ሙሉ ጌጦሽ ያለው።",
     8500, 12000, 4250, 5, 1, img("prod_04_bridal_gown.jpg"), 1, 0),

    ("Evening Gown", "የምሽት ቀሚስ",
     "ዘመናዊ የምሽት ቀሚስ። ለፓርቲ እና ለይፋዊ ዝግጅቶች ተስማሚ።",
     3200, 4000, 1600, 10, 1, img("evening_gown.jpg"), 1, 0),

    ("Evening Gown Premium", "ፕሪሚየም የምሽት ቀሚስ",
     "ፕሪሚየም የምሽት ቀሚስ። ከፍተኛ ጥራት ያለው ጨርቅ።",
     3800, 4800, 1900, 8, 1, img("product_evening_gown.jpg"), 1, 1),

    ("Luxury Dress", "ቅንጡ ቀሚስ",
     "ቅንጡ ሉክሸሪ ቀሚስ። ለፕሪሚየም ፓርቲ እና ኢቨንቶች ተስማሚ።",
     4500, 5500, 2250, 8, 1, img("luxury_dress.jpg"), 1, 1),

    ("Maxi Dress", "ማክሲ ቀሚስ",
     "ረዥም ማክሲ ቀሚስ። ምቹ እና አምሮ የሚታይ።",
     1800, 2200, 900, 20, 1, img("maxi_dress.jpg"), 0, 1),

    ("Floral Maxi Dress", "አበባ ማክሲ ቀሚስ",
     "አበባ ዲዛይን ያለው ረዥም ቀሚስ። ለበጋ ፍጹም ምርጫ።",
     1950, 2400, 975, 18, 1, img("product_floral_maxi.jpg"), 1, 1),

    ("Mini Dress", "ሚኒ ቀሚስ",
     "አጭር ሚኒ ቀሚስ። ዘመናዊ ዲዛይን ያለው።",
     1350, 1700, 675, 25, 1, img("mini_dress.jpg"), 0, 1),

    ("Girls Dress", "የልጃገረዶች ቀሚስ",
     "ለልጃገረዶች ቀሚስ — ቆንጆ ዲዛይን ያለው።",
     950, 1200, 475, 30, 1, img("girls_dress.jpg"), 0, 0),

    ("Prayer Dress", "የሰላት ቀሚስ",
     "ለሙስሊም ሴቶች የሰላት ቀሚስ — ምቹ እና ሙሉ ሽፋን ያለው።",
     1100, 1400, 550, 35, 1, img("prayer_dress.jpg"), 0, 0),

    # ── Tops & Shirts (cat 2) ─────────────────────────────────────────────
    ("Silk Blouse", "ሐር ጨርቅ ብሉዝ",
     "ሐር ጨርቅ ብሉዝ — ለቢሮ እና ለምሽት ዝግጅቶች ተስማሚ።",
     1250, 1600, 625, 30, 2, img("product_silk_blouse.jpg"), 1, 1),

    ("Ladies Shirt", "ሴቶች ሸሚዝ",
     "ክላሲክ ሴቶች ሸሚዝ — ፈሳሽ ቀለም ያለው ጨርቅ።",
     950, 1200, 475, 40, 2, img("ladies_shirt.jpg"), 0, 0),

    ("Blouse", "ብሉዝ",
     "ቀላል ብሉዝ — ለዕለት ሥራ ምቹ ምርጫ።",
     850, 1100, 425, 45, 2, img("blouse.jpg"), 0, 0),

    ("Printed Blouse", "ፕሪንትድ ብሉዝ",
     "ቀለም ያለው ፕሪንትድ ብሉዝ። ከሱሪ ወይም ቀሚስ ጋር ይሠራል።",
     950, 1200, 475, 35, 2, img("printed_blouse.jpg"), 0, 1),

    ("White Shirt", "ነጭ ሸሚዝ",
     "ፍጹም ነጭ ሸሚዝ — ለቢሮ ምርጥ ምርጫ።",
     850, 1100, 425, 50, 2, img("product_white_shirt.jpg"), 0, 0),

    ("Graphic T-Shirt", "ግራፊክ ቲሸርት",
     "ግራፊክ ዲዛይን ያለው ቲሸርት — ዘና ብሎ ለሚሄዱ።",
     650, 850, 325, 60, 2, img("product_graphic_tshirt.jpg"), 0, 1),

    ("T-Shirt", "ቲሸርት",
     "ቀላል ሊዘና ያለው ቲሸርት — ምቹ ዕለታዊ ምርጫ።",
     550, 750, 275, 70, 2, img("tshirt.jpg"), 0, 0),

    ("Hijab", "ሕጃብ",
     "ናሙና ሕጃብ — ለሙስሊም ሴቶች ምቹ ሽፋን።",
     450, 650, 225, 80, 2, img("hijab.jpg"), 0, 0),

    # ── Trousers & Shorts (cat 3) ─────────────────────────────────────────
    ("Jeans", "ጂንስ",
     "ክላሲክ ጂንስ ሱሪ — ለሁሉም ቦታ ምቹ።",
     1350, 1700, 675, 40, 3, img("jeans.jpg"), 1, 0),

    ("Casual Trousers", "ካዥዋል ሱሪ",
     "ካዥዋል ሱሪ — ምቹ እና ዘና ያለ ዲዛይን።",
     1100, 1400, 550, 35, 3, img("casual_trousers.jpg"), 0, 0),

    ("Linen Pants", "ሊነን ሱሪ",
     "ሊነን ሱሪ — ለሙቅ ወቅት ምቹ ምርጫ።",
     1200, 1500, 600, 30, 3, img("linen_pants.jpg"), 0, 1),

    ("Wide Leg Pants", "ዊድ-ሌግ ሱሪ",
     "ሰፊ ዊድ-ሌግ ሱሪ — ዘመናዊ ፋሽን ዲዛይን።",
     1350, 1700, 675, 25, 3, img("product_wide_leg.jpg"), 1, 1),

    ("Chinos", "ቺኖ ሱሪ",
     "ቺኖ ሱሪ — ለቢሮ እና ካዥዋል ሁለቱም ይሠራል።",
     1250, 1600, 625, 30, 3, img("product_chinos.jpg"), 0, 0),

    ("Denim Shorts", "ጂንስ ሾርት",
     "ጂንስ ሾርት — ለሙቅ ወቅት ምቹ ምርጫ።",
     850, 1100, 425, 35, 3, img("product_denim_shorts.jpg"), 0, 1),

    ("Leggings", "ሌጊንስ",
     "ሌጊንስ — ምቹ እና ዘምናዊ ዲዛይን ያለው።",
     750, 1000, 375, 50, 3, img("prod_07_leggings.jpg"), 0, 0),

    ("Leggings Classic", "ክላሲክ ሌጊንስ",
     "ክላሲክ ሌጊንስ — ስፖርት እና ዕለታዊ ሁለቱም ይሠራል።",
     750, 950, 375, 55, 3, img("product_leggings.jpg"), 0, 0),

    # ── Jackets & Knitwear (cat 4) ────────────────────────────────────────
    ("Blazer", "ብሌዘር",
     "ፎርማል ብሌዘር — ለቢሮ እና ሁለተኛ ዲዛይን።",
     2400, 3000, 1200, 15, 4, img("prod_06_blazer.jpg"), 1, 0),

    ("Denim Jacket", "ጂንስ ጃኬት",
     "ጂንስ ጃኬት — ዘመናዊ ዲዛይን ያለው።",
     1850, 2300, 925, 20, 4, img("denim_jacket.jpg"), 1, 1),

    ("Cardigan", "ካርዲጋን",
     "ካርዲጋን — ለቀዝቃዛ ቀናት ምቹ ምርጫ።",
     1400, 1800, 700, 25, 4, img("cardigan.jpg"), 0, 0),

    ("Cardigan Knit", "ኒት ካርዲጋን",
     "ክላሲክ ኒት ካርዲጋን — ለቤት እና ለቢሮ።",
     1350, 1700, 675, 28, 4, img("product_cardigan.jpg"), 0, 0),

    ("Leather Jacket", "የቆዳ ጃኬት",
     "የቆዳ ጃኬት — ቆዳ የሚመስል ጨርቅ። ዘና ያለ ዲዛይን።",
     3200, 4000, 1600, 10, 4, img("product_leather_jacket.jpg"), 1, 1),

    ("Hoodie", "ሁዲ",
     "ሁዲ — ምቹ እና ሙቅ ዲዛይን። ለካዥዋል ቀናት።",
     1250, 1600, 625, 30, 4, img("product_hoodie.jpg"), 0, 1),

    # ── Underwear & Nightwear (cat 5) ─────────────────────────────────────
    ("Pajama Set", "ፒጃማ",
     "ፒጃማ ሙሉ ስብስብ — ምቹ የሌሊት ልብስ።",
     950, 1250, 475, 40, 5, img("product_pajama.jpg"), 0, 0),

    # ── Baby Suits & Rompers (cat 6) ──────────────────────────────────────
    ("Baby Romper", "የህፃን ሮምፐር",
     "ለህፃናት ምቹ ሮምፐር — ለ0–12 ወር ህፃናት ተስማሚ።",
     650, 850, 325, 50, 6, img("prod_05_baby_romper.jpg"), 1, 1),

    ("Baby Romper Premium", "ፕሪሚየም የህፃን ሮምፐር",
     "ፕሪሚየም ህፃን ሮምፐር — ለ0–18 ወር ህፃናት።",
     750, 950, 375, 45, 6, img("product_baby_romper.jpg"), 0, 1),

    ("Baby Dress", "የህፃናት ቀሚስ",
     "ቆንጆ የህፃናት ቀሚስ — ለ6–24 ወር ህፃናት።",
     700, 900, 350, 35, 6, img("baby_dress.jpg"), 0, 0),

    ("Baby Winter Set", "የህፃን ክረምት ስብስብ",
     "የህፃናት ክረምት ስብስብ — ሙቅ እና ምቹ።",
     900, 1200, 450, 25, 6, img("product_baby_winter.jpg"), 0, 0),

    ("Kids Outfit", "የሕፃናት ልብስ",
     "ለሕፃናት ሙሉ ልብስ ስብስብ — ምቹ ዲዛይን ያለው።",
     850, 1100, 425, 30, 6, img("prod_09_kids_outfit.jpg"), 0, 0),

    # ── Activewear (cat 7) ────────────────────────────────────────────────
    ("Sportswear Set", "ስፖርት ልብስ",
     "ሙሉ ስፖርት ልብስ — ለጂም እና ለሩጫ ምቹ።",
     1450, 1800, 725, 30, 7, img("sportswear.jpg"), 1, 1),

    ("Yoga Pants", "ዮጋ ሱሪ",
     "ዮጋ ሱሪ — ለዮጋ እና ለሌሎች ብዝሃ-እንቅስቃሴ ምቹ።",
     1100, 1400, 550, 40, 7, img("yoga_pants.jpg"), 0, 1),
]

# ── advertisements ────────────────────────────────────────────────────────────
# advertisements schema: id, title, title_am, title_ar, description, description_am,
#   description_ar, image, media_url, link, sort_order, is_active, start_date, end_date, created_at
ADS = [
    # (title, title_am, description_am, image, link, sort_order)
    ("New Arrivals", "አዳዲስ ምርቶች",
     "አዳዲስ ምርቶቻችን ደርሰዋል — አሁን ይምረጡ!",
     ad_img("ad_new_arrivals.jpg"), "/products?filter=new", 1),

    ("Summer Sale", "የበጋ ቅናሽ",
     "እስከ 30% ቅናሽ — አሁን ይጠቀሙ!",
     ad_img("ad_summer.jpg"), "/products?filter=sale", 2),

    ("Traditional Wear", "ባህላዊ ልብሶች",
     "ሀበሻ ቀሚስ፣ ቲልፍ እና ሌሎች ባህላዊ ልብሶች",
     ad_img("ad_traditional.jpg"), "/products?category=8", 3),

    ("Holiday Collection", "የበዓል ስብስብ",
     "ለበዓላት ምርጥ ምርጦቻችን — ሁሉም ምርቶች ይገኛሉ",
     ad_img("ad_holiday.jpg"), "/products", 4),

    ("Special Sale", "ልዩ ቅናሽ",
     "ሁሉም ምርቶች ላይ ቅናሽ አለ — አሁን ይጠቀሙ!",
     ad_img("ad_sale.jpg"), "/products?filter=sale", 5),
]

# ── insert products ───────────────────────────────────────────────────────────

cur.execute("SELECT COUNT(*) FROM products")
existing = cur.fetchone()[0]
if existing > 0:
    print(f"⚠️  {existing} products already in DB — skipping product seed.")
else:
    print(f"Inserting {len(PRODUCTS)} products …")
    for p in PRODUCTS:
        name, name_am, desc, price, compare_price, cost, stock, cat_id, thumbnail, featured, is_new = p
        cur.execute("""
            INSERT INTO products
              (name, name_am, description, price, compare_price, cost,
               stock_quantity, category_id, thumbnail, is_active,
               is_featured, is_new)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s)
        """, (name, name_am, desc, price, compare_price, cost,
              stock, cat_id, thumbnail, featured, is_new))
    print(f"✅  {len(PRODUCTS)} products inserted.")

# ── insert ads ────────────────────────────────────────────────────────────────

cur.execute("SELECT COUNT(*) FROM advertisements")
existing_ads = cur.fetchone()[0]
if existing_ads > 0:
    print(f"⚠️  {existing_ads} ads already in DB — skipping ad seed.")
else:
    print(f"Inserting {len(ADS)} advertisements …")
    for a in ADS:
        title, title_am, description_am, image, link, sort_order = a
        cur.execute("""
            INSERT INTO advertisements
              (title, title_am, description_am, image, link, sort_order, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,1)
        """, (title, title_am, description_am, image, link, sort_order))
    print(f"✅  {len(ADS)} advertisements inserted.")

conn.commit()
cur.close()
conn.close()
print("\n🎉 Seed complete — refresh the homepage to see your products!")
