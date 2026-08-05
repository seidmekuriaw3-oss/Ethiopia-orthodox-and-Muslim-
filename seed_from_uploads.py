"""
SEMIRA FASHION — Seed all products & advertisements from static/uploads/
Reads every image/video in the uploads folder and inserts it into the DB.
Run:  python seed_from_uploads.py
"""
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────
# PRODUCT KNOWLEDGE BASE  (stem → name_am, name_en, desc, price, compare, stock, cat_id, featured)
# cat_id: 1=Dresses 2=Tops 3=Trousers 4=Jackets 5=Nightwear 6=Baby 7=Activewear 8=Traditional
# ─────────────────────────────────────────────────────────────────
NAMED = {
    # ── simple named files ──────────────────────────────────────
    "baby_dress":               ("የሕፃናት ቀሚስ",          "Baby Dress",               "Adorable baby dress in soft breathable fabric. Perfect for little ones.",                          680,  950,  25, 6, 0),
    "blouse":                   ("ብሉዝ",                 "Elegant Blouse",           "Stylish women's blouse with a flattering fit for any occasion.",                                  950, 1400,  30, 2, 1),
    "cardigan":                 ("ካርዲጋን",               "Knit Cardigan",            "Cozy fine-knit cardigan. Lightweight yet warm for layering.",                                    1400, 1900,  20, 4, 0),
    "casual_trousers":          ("ካዥዋል ሱሪ",             "Casual Trousers",          "Comfortable relaxed-fit casual trousers in breathable fabric.",                                 1200, 1700,  25, 3, 0),
    "denim_jacket":             ("ዴኒም ጃኬት",             "Denim Jacket",             "Classic button-front denim jacket. A wardrobe staple for all seasons.",                          2200, 3000,  18, 4, 1),
    "evening_gown":             ("ምሽት ቀሚስ",             "Evening Gown",             "Elegant floor-length evening gown with embroidered details. Perfect for weddings.",              3500, 5000,  10, 1, 1),
    "girls_dress":              ("የሕፃናት ቀሚስ",           "Girls' Dress",             "Beautiful party dress for girls with tulle skirt. Perfect for celebrations.",                    750, 1100,  30, 6, 0),
    "habesha_dress":            ("ሃበሻ ቀሚስ",             "Habesha Dress",            "Traditional Ethiopian habesha dress with hand-woven tilet border.",                             2800, 3800,  12, 8, 1),
    "hijab":                    ("ሂጃብ (ጀርሲ)",           "Jersey Hijab",             "Premium jersey hijab that stays in place all day. Breathable and comfortable.",                  450,  650,  60, 8, 1),
    "jeans":                    ("ጂንስ (ስትሬች)",          "Stretch Jeans",            "High-quality stretch denim with modern slim silhouette.",                                        1600, 2200,  30, 3, 1),
    "ladies_shirt":             ("የሴቶች ሸሚዝ",            "Ladies' Shirt",            "Classic ladies shirt in premium cotton. Versatile for office and outings.",                     1100, 1500,  35, 2, 0),
    "linen_pants":              ("ሊነን ሱሪ",               "Linen Pants",              "Breathable wide-leg linen pants. Ideal for warm weather.",                                      1300, 1800,  25, 3, 0),
    "luxury_dress":             ("ሉክስ ቀሚስ",             "Luxury Occasion Dress",    "Premium luxury dress with intricate detailing. Statement piece for special events.",              3800, 5500,   8, 1, 1),
    "maxi_dress":               ("ማክሲ ቀሚስ",             "Flowing Maxi Dress",       "Elegant floor-length maxi dress with a flowing silhouette.",                                    2200, 3100,  20, 1, 1),
    "mini_dress":               ("ሚኒ ቀሚስ",               "Chic Mini Dress",          "Trendy mini dress with clean lines. Perfect for casual and evening outings.",                   1400, 1900,  25, 1, 0),
    "prayer_dress":             ("ፀሎት ቀሚስ",              "Prayer Dress",             "Modest full-coverage prayer dress in lightweight breathable fabric.",                            1800, 2500,  20, 8, 0),
    "printed_blouse":           ("ፕሪንትድ ብሉዝ",           "Printed Blouse",           "Vibrant printed blouse with flutter sleeves. Eye-catching everyday piece.",                     1050, 1500,  30, 2, 0),
    "sportswear":               ("ስፖርታዊ ልብስ ሴት",        "Sportswear Set",           "Matching jacket and jogger sportswear set in breathable moisture-wicking fabric.",               1800, 2600,  22, 7, 1),
    "tshirt":                   ("ቲሸርት",                 "Cotton T-Shirt",           "Comfortable everyday cotton t-shirt. Essential casual wear.",                                     650,  900,  50, 2, 0),
    "yoga_pants":               ("ዮጋ ሱሪ",                "Yoga Pants",               "High-performance yoga pants with moisture-wicking fabric and flexible fit.",                    1100, 1600,  30, 7, 0),
    # ── prod_0N_* named files ────────────────────────────────────
    "prod_01_habesha_kemis":    ("ሃበሻ ቀሚስ (ፕሪሚየም)",     "Habesha Kemis Premium",    "Authentic handwoven habesha kemis with intricate silver tilet embroidery.",                    2800, 4000,  10, 8, 1),
    "prod_02_ankara_dress":     ("አንካራ ቀሚስ",             "Ankara Print Dress",       "Bold Ankara wax-print wrap dress. Celebrating African fashion heritage.",                       2000, 2800,  15, 1, 0),
    "prod_03_habesha_top":      ("ሃበሻ ቶፕ",               "Habesha Top",              "Traditional habesha top with hand-stitched embroidery on collar and cuffs.",                   1500, 2200,  20, 8, 0),
    "prod_04_bridal_gown":      ("ሙሽሪት ቀሚስ",             "Bridal Gown",              "Stunning bridal gown with cathedral train and lace bodice. Your dream wedding look.",           5500, 7500,   5, 1, 1),
    "prod_05_baby_romper":      ("ሕፃናት ሮምፐር",            "Baby Romper",              "Cute and comfortable cotton baby romper with snap buttons.",                                     580,  850,  35, 6, 0),
    "prod_06_blazer":           ("ብሌዘር (ሴቶች)",           "Women's Blazer",           "Sharp double-breasted women's blazer. Professional look for meetings and events.",               2800, 3900,  15, 4, 1),
    "prod_07_leggings":         ("ሊጊንስ (ሃይ-ዌስት)",        "High-Waist Leggings",      "Stretchy high-waist leggings. Seamless comfort for gym and everyday wear.",                     950, 1400,  40, 3, 0),
    "prod_08_tilf_dress":       ("ትልፍ ቀሚስ",              "Tilf Kemis",               "Elegant habesha dress with handwoven tilf embroidery on hem and sleeves.",                     3200, 4500,  10, 8, 1),
    "prod_09_kids_outfit":      ("የልጆች ልብስ ሴት",          "Kids' Outfit Set",         "Coordinated two-piece kids outfit in durable soft fabric.",                                      850, 1200,  25, 6, 0),
    "prod_10_chiffon_kemis":    ("ሺፎን ቀሚስ",              "Chiffon Kemis",            "Lightweight chiffon habesha kemis perfect for warmer occasions.",                               2600, 3600,  12, 1, 1),
    # ── product_* named files ────────────────────────────────────
    "product_baby_romper":      ("ሕፃናት ሮምፐር ሴት",         "Baby Romper Set",          "Soft cotton baby romper set with matching hat and socks.",                                      620,  900,  30, 6, 0),
    "product_baby_winter":      ("ሕፃናት ክረምት ልብስ",        "Baby Winter Wear",         "Warm quilted winter outfit for babies. Keeps little ones cosy in cold weather.",                 780, 1100,  20, 6, 0),
    "product_cardigan":         ("ካርዲጋን (ፕሪሚየም)",        "Premium Cardigan",         "Premium long-line knit cardigan in soft merino blend.",                                         1600, 2200,  18, 4, 1),
    "product_chinos":           ("ቺኖስ (ስሊም)",            "Slim-Fit Chinos",          "Smart slim-fit chinos in stretch cotton. Versatile for work and weekend.",                     1400, 1900,  25, 3, 0),
    "product_denim_shorts":     ("ዴኒም ቁምጣ",              "Denim Shorts",             "Classic raw-hem denim shorts. Summer essential.",                                                 900, 1300,  30, 3, 0),
    "product_evening_gown":     ("ምሽት ቀሚስ (ፕሪሚየም)",     "Evening Gown Premium",     "Premium floor-length gown with beaded bodice. Ideal for galas and weddings.",                  4200, 6000,   8, 1, 1),
    "product_floral_maxi":      ("ፍሎራል ማክሲ ቀሚስ",        "Floral Maxi Dress",        "Sweeping floral-print maxi dress with tiered skirt. Effortlessly feminine.",                   2300, 3200,  18, 1, 1),
    "product_gabi":             ("ጋቢ",                   "Ethiopian Gabi",           "Traditional Ethiopian hand-woven gabi. Perfect for cool evenings and ceremonies.",               1800, 2600,  15, 8, 1),
    "product_graphic_tshirt":   ("ግራፊክ ቲሸርት",           "Graphic T-Shirt",          "Trendy oversized graphic-print t-shirt in 100% organic cotton.",                                 750, 1100,  45, 2, 0),
    "product_habesha_kemis":    ("ሃበሻ ቀሚስ (ዴሉክስ)",       "Habesha Kemis Deluxe",     "Deluxe habesha kemis with gold tilet embroidery. Handcrafted masterpiece.",                    3500, 5000,   8, 8, 1),
    "product_hoodie":           ("ሁዲ",                   "Cosy Hoodie",              "Ultra-soft fleece-lined hoodie. Cosy comfort for all seasons.",                                 1700, 2300,  25, 4, 0),
    "product_kuta":             ("ኩታ",                   "Ethiopian Kuta",           "Traditional Ethiopian kuta draped wrap. Authentic cultural garment.",                            2200, 3200,  12, 8, 1),
    "product_leather_jacket":   ("ሌዘር ጃኬት",             "Leather Jacket",           "Premium faux-leather moto jacket with zip detail. Edgy and stylish.",                          3500, 5000,  10, 4, 1),
    "product_leggings":         ("ሊጊንስ (ኮምፎርት)",         "Comfort Leggings",         "Everyday comfort leggings in four-way stretch fabric.",                                          850, 1200,  45, 3, 0),
    "product_netela":           ("ነጠላ",                  "Ethiopian Netela",         "Fine hand-woven Ethiopian netela. Elegant for ceremonies and everyday use.",                    1500, 2200,  20, 8, 1),
    "product_pajama":           ("ፓጃማ (ሳቲን)",            "Satin Pajama Set",         "Luxurious satin pajama set with lace trim. Elegant bedtime comfort.",                           1200, 1700,  20, 5, 0),
    "product_silk_blouse":      ("ሲልክ ብሉዝ",              "Silk Blouse",              "Elegant pure-silk blouse with V-neck. Pairs beautifully with tailored trousers.",              2200, 3100,  15, 2, 1),
    "product_tilf_skirt":       ("ትልፍ ቀጭን",              "Tilf Embroidered Skirt",   "Traditional tilf-embroidered midi skirt. Pairs perfectly with habesha tops.",                  1800, 2600,  18, 8, 0),
    "product_white_shirt":      ("ነጭ ሸሚዝ",               "Classic White Shirt",      "Crisp poplin white shirt. Office staple that works from 9 to 9.",                               900, 1300,  35, 2, 0),
    "product_wide_leg":         ("ዋይድ ሌግ ሱሪ",            "Wide-Leg Trousers",        "Trendy wide-leg trousers with high waist and clean silhouette.",                               1600, 2300,  20, 3, 1),
}

# Auto-fill pool for generic / hash-named images (rotating)
_AUTO_POOL = [
    ("ፍሎራል ቀሚስ",       "Floral Summer Dress",     "Vibrant floral-print summer dress.",                           1600, 2200, 3, 1, 0),
    ("ሲልክ ብሉዝ ሴት",     "Silk Top & Skirt Set",    "Matching silk blouse and skirt set.",                          2800, 3800, 2, 1, 1),
    ("ካርጎ ሱሪ",          "Cargo Trousers",          "Utility cargo trousers with side pockets.",                    1400, 1900, 3, 0),
    ("ሆዲ ሴት",           "Matching Hoodie Set",     "Coordinated hoodie and jogger set.",                           2000, 2800, 4, 0),
    ("ቦሆ ቀሚስ",          "Boho Maxi Dress",         "Free-flowing bohemian maxi dress.",                            2100, 2900, 1, 1),
    ("ሴቶች ብሌዘር",        "Tailored Blazer",         "Structured double-breasted blazer.",                           3000, 4200, 4, 1),
    ("ሊነን ሸሚዝ",         "Linen Shirt",             "Relaxed linen shirt for warm days.",                           1050, 1500, 2, 0),
    ("ፓርቲ ቀሚስ",         "Party Dress",             "Sequin-accent party dress for celebrations.",                  2500, 3500, 1, 1),
    ("ራፕ ቀሚስ",          "Wrap Dress",              "Flattering wrap-style dress in floral print.",                 1800, 2600, 1, 0),
    ("ቀጭን ጂንስ",         "Skinny Jeans",            "Figure-hugging skinny jeans in stretch denim.",               1600, 2200, 3, 0),
    ("ሸሚዝ ቀሚስ",         "Shirt Dress",             "Relaxed button-down shirt dress.",                             1700, 2400, 1, 0),
    ("ስፖርት ቲሸርት",      "Sports T-Shirt",          "Moisture-wicking sports t-shirt.",                               850, 1200, 7, 0),
    ("ፕሪምሮዝ ቀሚስ",      "Primrose Midi Dress",     "Elegant primrose-coloured midi dress.",                        2000, 2800, 1, 1),
    ("አምሻ ቀሚስ",         "Evening Mini Dress",      "Chic embellished evening mini dress.",                         2200, 3100, 1, 1),
    ("ዘመናዊ አባያ",        "Modern Abaya",            "Contemporary abaya in lightweight crepe fabric.",              2800, 3900, 8, 1),
    ("ቡቲ ጃኬት",          "Utility Jacket",          "Functional utility jacket with multiple pockets.",             2400, 3300, 4, 0),
    ("ጂምዌር ሴት",         "Gym Wear Set",            "Coordinated sports bra and leggings gym set.",                1700, 2400, 7, 1),
    ("ሺፎን ብሉዝ",         "Chiffon Blouse",          "Floaty chiffon blouse with ruffled sleeves.",                  1300, 1800, 2, 0),
    ("ሃይ-ዌስት ሱሪ",       "High-Waist Tailored Trousers", "Elegant high-waist tailored trousers.",                  1500, 2100, 3, 1),
    ("ቤቢ ቀሚስ ሴት",      "Baby Dress & Headband Set", "Adorable baby dress with matching headband.",                  720,  980, 6, 0),
]

# Advertisement knowledge base
# Static JPG ads
AD_IMAGES = {
    "ad_holiday":       ("🎄 የበዓላት ቅናሽ!",         "Holiday Special Sale",       "Shop our holiday special — deep discounts on selected styles.",          "/products", 1),
    "ad_new_arrivals":  ("✨ አዲስ ምርቶች ደርሰዋል!",    "New Arrivals Are Here",      "Fresh styles just landed. Be the first to shop the new collection.",     "/products", 2),
    "ad_sale":          ("🔥 ታላቅ ቅናሽ — 50% ያነሰ!", "Big Sale — Up to 50% Off",  "Our biggest sale ever. Hundreds of styles marked down.",                  "/products", 3),
    "ad_summer":        ("☀️ የበጋ ወቅት ስብስብ",        "Summer Collection 2025",     "Beat the heat in style. Explore our breezy summer collection.",          "/products", 4),
    "ad_traditional":   ("👗 የባህል ልብሶች ፌስቲቫል",    "Traditional Wear Festival",  "Celebrate your heritage. Authentic Ethiopian and Islamic fashion pieces.","/products", 5),
}

# Video ad titles (rotating pool — content unknown from filename)
_VIDEO_TITLES = [
    ("🎥 አዲስ ፋሽን ቪዲዮ",     "New Fashion Video",          "Discover our latest fashion trends in this exclusive video."),
    ("🎬 ምርጥ ስብስብ",         "Premium Collection Reel",    "A visual journey through our premium collection."),
    ("✨ ስብስብ ቅድሞሽ",         "Collection Preview",         "Sneak peek at the newest arrivals."),
    ("👗 ፋሽን ትርዒት",          "Fashion Showcase",           "Watch our stylists put together stunning outfits."),
    ("🌟 ልዩ ቅናሽ ቪዲዮ",       "Exclusive Offer Video",      "Don't miss these limited-time exclusive deals."),
    ("🔥 ሞቅ ያሉ ምርቶች",       "Trending Products",          "Our hottest products as picked by our customers."),
    ("💃 ስታይል ጋይድ",          "Style Guide Reel",           "Get inspired with our seasonal style guide."),
    ("🎁 ልዩ ስጦታ ቀናቶች",     "Gift Season Special",        "Perfect gifts for every occasion — all in one place."),
    ("👑 ሉክስ ፋሽን",           "Luxury Fashion Reel",        "Experience luxury fashion Ethiopian style."),
    ("🌺 ፍሎራል ስብስብ",         "Floral Collection Reel",     "Our beautiful floral collection — perfect for spring."),
    ("🎨 ቀለማማ ፋሽን",          "Colourful Fashion Reel",     "Bold colours, bold looks — express yourself."),
    ("🕌 ሃይማኖታዊ ልብሶች",      "Modest Fashion Reel",        "Modest fashion that never compromises on style."),
    ("👶 ሕፃናት ፋሽን",          "Kids & Baby Fashion",        "Adorable fashion for the little ones."),
    ("💪 ስፖርታዊ ልብስ",         "Activewear Reel",            "Performance meets style in our activewear range."),
    ("🏆 ምርጥ ምርቶቻችን",        "Best Sellers Reel",          "Our all-time best-selling pieces — shop now."),
    ("🌙 ሌሊት ፋሽን",           "Evening Wear Reel",          "Stunning evening and occasion wear for every celebration."),
    ("🪡 ሃበሻ ፋሽን",            "Habesha Fashion Reel",       "Celebrating the beauty of Ethiopian traditional fashion."),
    ("💼 ሥራ ፋሽን",             "Work Fashion Reel",          "Professional looks for the modern working woman."),
    ("🌍 አፍሪካ ፋሽን",           "African Print Fashion",      "Bold and beautiful African print styles."),
    ("🛍️ ሶሺያል ሚዲያ ቪዲዮ",     "Social Media Fashion Reel",  "As seen on social — our most-loved pieces."),
]


def label(text):
    print(f"\n{'='*60}\n  {text}\n{'='*60}")


def seed_from_uploads():
    try:
        from database.db import get_db
        conn = get_db()
        cur = conn.cursor()

        label("🌱 SEMIRA — SEED FROM UPLOADS")

        # ── fetch category ids ──────────────────────────────────
        cur.execute("SELECT id, name_am, name FROM categories ORDER BY id")
        cats = cur.fetchall()
        cat_by_id   = {r[0]: r for r in cats}
        cat_by_name_am = {r[1]: r[0] for r in cats}
        cat_by_name    = {r[2]: r[0] for r in cats}

        # add Religious if missing
        if not any("Religious" in r[2] for r in cats):
            cur.execute(
                "INSERT INTO categories (name, name_am, name_ar, is_active) "
                "VALUES (%s,%s,%s,1) ON CONFLICT DO NOTHING RETURNING id",
                ("Religious Wear", "ሃይማኖታዊ አልባሳት", "ملابس دينية")
            )
            row = cur.fetchone()
            if row:
                cat_by_id[row[0]] = (row[0], "ሃይማኖታዊ አልባሳት", "Religious Wear")
                cat_by_name_am["ሃይማኖታዊ አልባሳት"] = row[0]
                cat_by_name["Religious Wear"] = row[0]
        conn.commit()

        def cid(n):
            """Return category id by numeric id (pass-through) or fallback."""
            return cat_by_id.get(n, list(cat_by_id.values())[0])[0] if n in cat_by_id else list(cat_by_id.keys())[0]

        # ── clear existing ──────────────────────────────────────
        print("🗑️  Clearing existing products & advertisements …")
        cur.execute("DELETE FROM order_items WHERE product_id IN (SELECT id FROM products)")
        cur.execute("DELETE FROM cart_items  WHERE product_id IN (SELECT id FROM products)")
        cur.execute("DELETE FROM products")
        cur.execute("DELETE FROM advertisements")
        conn.commit()
        print("   ✓ Cleared")

        # ════════════════════════════════════════════════════════
        # PRODUCTS
        # ════════════════════════════════════════════════════════
        print("\n📦 Scanning static/uploads/products …")
        prod_dir = "static/uploads/products"
        exts = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
        skip_stems = {"ad_01_banner", "ad_02_banner"}

        files = sorted(
            f for f in os.listdir(prod_dir)
            if os.path.splitext(f)[1].lower() in exts
               and os.path.splitext(f)[0] not in skip_stems
        )
        print(f"   Found {len(files)} product image files")

        auto_idx = 0
        inserted_products = 0
        skus_used = set()

        for i, fname in enumerate(files):
            stem = os.path.splitext(fname)[0]
            rel  = f"uploads/products/{fname}"

            if stem in NAMED:
                name_am, name_en, desc, price, compare, stock, cat_n, featured = NAMED[stem]
            else:
                # auto-assign from rotating pool
                pool_entry = _AUTO_POOL[auto_idx % len(_AUTO_POOL)]
                auto_idx += 1
                # pool entries may have 7 or 8 elements
                if len(pool_entry) == 8:
                    name_am, name_en, desc, price, compare, cat_n, _, featured = pool_entry
                else:
                    name_am, name_en, desc, price, compare, cat_n, featured = pool_entry
                # vary price slightly per index so duplicates aren't identical
                price   = int(price   * (1 + (auto_idx % 5) * 0.05))
                compare = int(compare * (1 + (auto_idx % 5) * 0.05))
                stock   = 15 + (auto_idx % 20)
                # append index to name to avoid exact duplicates
                name_am = f"{name_am} #{auto_idx}"
                name_en = f"{name_en} #{auto_idx}"

            # de-duplicate SKU
            base_sku = stem[:12].upper().replace("_", "")
            sku = base_sku
            suffix = 2
            while sku in skus_used:
                sku = f"{base_sku}{suffix}"
                suffix += 1
            skus_used.add(sku)

            category_id = cat_n if cat_n in cat_by_id else list(cat_by_id.keys())[0]
            is_featured = 1 if featured else 0
            is_new      = 1 if i < 30 else 0  # first 30 marked as new

            try:
                cur.execute("""
                    INSERT INTO products
                        (name_am, name, description, price, compare_price,
                         stock_quantity, low_stock_threshold, category_id,
                         is_active, is_featured, is_new,
                         thumbnail, images, sku, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s, 1,%s,%s, %s,%s,%s,%s)
                """, (
                    name_am, name_en, desc,
                    price, compare,
                    stock, 5,
                    category_id,
                    is_featured, is_new,
                    rel,
                    json.dumps([rel]),
                    sku,
                    datetime.now()
                ))
                inserted_products += 1
            except Exception as e:
                print(f"   ⚠️  Skipped {fname}: {e}")
                conn.rollback()

        conn.commit()
        print(f"   ✅ Inserted {inserted_products} products")

        # ════════════════════════════════════════════════════════
        # ADVERTISEMENTS
        # ════════════════════════════════════════════════════════
        print("\n📢 Scanning static/uploads/ads …")
        ads_dir = "static/uploads/ads"
        inserted_ads = 0
        sort_counter = 1

        # ── static JPG ads ──────────────────────────────────────
        for fname in sorted(os.listdir(ads_dir)):
            stem, ext = os.path.splitext(fname)
            if ext.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            if "_poster" in stem:
                continue  # posters used by video ads below

            rel_img = f"uploads/ads/{fname}"
            if stem in AD_IMAGES:
                title_am, title_en, desc, link, _ = AD_IMAGES[stem]
            else:
                title_am = f"ማስታወቂያ {sort_counter}"
                title_en = f"Advertisement {sort_counter}"
                desc     = "Special promotion — shop now."
                link     = "/products"

            try:
                cur.execute("""
                    INSERT INTO advertisements
                        (title, title_am, description, image, media_url,
                         link, sort_order, is_active, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,1,%s)
                """, (
                    title_en, title_am, desc,
                    rel_img, None,
                    link, sort_counter,
                    datetime.now()
                ))
                inserted_ads += 1
                sort_counter += 1
            except Exception as e:
                print(f"   ⚠️  Skipped ad {fname}: {e}")
                conn.rollback()

        conn.commit()

        # ── video MP4 ads ───────────────────────────────────────
        mp4_files = sorted(f for f in os.listdir(ads_dir) if f.lower().endswith(".mp4"))
        for v_idx, fname in enumerate(mp4_files):
            stem = os.path.splitext(fname)[0]
            poster_name = f"{stem}_poster.jpg"
            poster_path = os.path.join(ads_dir, poster_name)
            rel_video  = f"uploads/ads/{fname}"
            rel_poster = f"uploads/ads/{poster_name}" if os.path.exists(poster_path) else None

            t = _VIDEO_TITLES[v_idx % len(_VIDEO_TITLES)]
            title_am, title_en, desc = t

            try:
                cur.execute("""
                    INSERT INTO advertisements
                        (title, title_am, description, image, media_url,
                         link, sort_order, is_active, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,1,%s)
                """, (
                    title_en, title_am, desc,
                    rel_poster, rel_video,
                    "/products", sort_counter,
                    datetime.now()
                ))
                inserted_ads += 1
                sort_counter += 1
            except Exception as e:
                print(f"   ⚠️  Skipped video ad {fname}: {e}")
                conn.rollback()

        # ── banner images from products folder ──────────────────
        for fname in ["ad_01_banner.jpg", "ad_02_banner.jpg"]:
            fpath = os.path.join(prod_dir, fname)
            if not os.path.exists(fpath):
                continue
            rel = f"uploads/products/{fname}"
            idx = 1 if "01" in fname else 2
            titles = [
                ("🛍️ አዲስ ምርቶች ቀርበዋል", "New Products Banner", "Discover what's new in our store."),
                ("💥 ቅናሽ ሰፊ ምርቶች",     "Sale Banner",         "Great savings across the entire store."),
            ]
            tm = titles[idx - 1]
            try:
                cur.execute("""
                    INSERT INTO advertisements
                        (title, title_am, description, image, media_url,
                         link, sort_order, is_active, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,1,%s)
                """, (
                    tm[1], tm[0], tm[2],
                    rel, None,
                    "/products", sort_counter,
                    datetime.now()
                ))
                inserted_ads += 1
                sort_counter += 1
            except Exception as e:
                print(f"   ⚠️  Skipped banner {fname}: {e}")
                conn.rollback()

        conn.commit()
        print(f"   ✅ Inserted {inserted_ads} advertisements")

        # ── mark first 12 featured products & first 12 new ─────
        cur.execute("""
            UPDATE products SET is_featured = 1
            WHERE id IN (
                SELECT id FROM products ORDER BY id LIMIT 12
            )
        """)
        conn.commit()

        # ── summary ─────────────────────────────────────────────
        cur.execute("SELECT COUNT(*) FROM products")
        fp = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products WHERE is_featured=1")
        ff = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM advertisements")
        fa = cur.fetchone()[0]

        label("📊 SEED SUMMARY")
        print(f"  📦 Products total   : {fp}")
        print(f"  ⭐ Featured          : {ff}")
        print(f"  📢 Advertisements    : {fa}")
        print(f"  🌐 Visit             : http://localhost:5000")
        print("="*60)
        return True

    except Exception as e:
        import traceback
        print(f"\n❌ Seed error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed_from_uploads()
