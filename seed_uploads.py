"""
seed_uploads.py — imports every file in static/uploads/products/ and
static/uploads/ads/ into the PostgreSQL database.

Run: python seed_uploads.py
"""

import os, sys, json, uuid
from database.db import _get_database_url
import psycopg2

DATABASE_URL = _get_database_url()
conn = psycopg2.connect(DATABASE_URL)
cur  = conn.cursor()

# ── helpers ──────────────────────────────────────────────────────────────────
def insert_product(name, name_am, price, compare_price, category_id,
                   thumbnail, stock=30, is_featured=0, is_new=0,
                   description="", description_am=""):
    sku = "SKU-" + uuid.uuid4().hex[:8].upper()
    cur.execute("""
        INSERT INTO products
            (name, name_am, name_en, price, compare_price, category_id,
             thumbnail, images, stock_quantity, is_active, is_featured, is_new,
             description, description_am, sku)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s,%s,%s,%s)
        ON CONFLICT (sku) DO NOTHING
    """, (name, name_am, name, price, compare_price, category_id,
          thumbnail, json.dumps([thumbnail]),
          stock, is_featured, is_new,
          description or name, description_am or name_am, sku))

def insert_ad(title, title_am, image=None, media_url=None, sort_order=0,
              description="", description_am=""):
    cur.execute("""
        INSERT INTO advertisements
            (title, title_am, description, description_am,
             image, media_url, is_active, sort_order)
        VALUES (%s,%s,%s,%s,%s,%s,1,%s)
    """, (title, title_am, description, description_am,
          image, media_url, sort_order))

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS
# category ids: 1=Dresses  2=Tops  3=Trousers  4=Jackets
#               5=Nightwear  6=Baby  7=Activewear  8=Traditional
# ─────────────────────────────────────────────────────────────────────────────

P = "uploads/products/"   # prefix stored in DB

named_products = [
    # ── Dresses ──────────────────────────────────────────────────────────────
    ("Floral Maxi Dress",   "የአበባ ማክሲ ቀሚስ",      1_200, 1_500, 1, P+"product_floral_maxi.jpg",    25, 1, 1),
    ("Elegant Evening Gown","ኤሌጋንት 储ምሽት ቀሚስ",    2_500, 3_200, 1, P+"product_evening_gown.jpg",   15, 1, 0),
    ("Evening Gown",        "ምሽት ቀሚስ",            2_200, 2_800, 1, P+"evening_gown.jpg",           18, 1, 0),
    ("Maxi Dress",          "ማክሲ ቀሚስ",             980,  1_200, 1, P+"maxi_dress.jpg",             30, 0, 1),
    ("Mini Dress",          "ሚኒ ቀሚስ",              750,    950, 1, P+"mini_dress.jpg",             30, 0, 1),
    ("Luxury Dress",        "ሉክሸሪ ቀሚስ",           3_000, 3_800, 1, P+"luxury_dress.jpg",          12, 1, 0),
    ("Ankara Dress",        "አንካራ ቀሚስ",           1_100, 1_400, 1, P+"prod_02_ankara_dress.jpg",   20, 1, 1),
    ("Bridal Gown",         "የሙሽሪት ቀሚስ",          4_500, 5_500, 1, P+"prod_04_bridal_gown.jpg",    8, 1, 0),
    ("Girls Dress",         "የልጃገረድ ቀሚስ",          650,    850, 1, P+"girls_dress.jpg",            25, 0, 1),

    # ── Tops & Shirts ────────────────────────────────────────────────────────
    ("White Formal Shirt",  "ነጭ ፎርማል ሸሚዝ",        550,    700, 2, P+"product_white_shirt.jpg",    40, 0, 1),
    ("Silk Blouse",         "ሲልክ ብሉዝ",             780,    980, 2, P+"product_silk_blouse.jpg",    30, 1, 1),
    ("Graphic T-Shirt",     "ግራፊክ ቲሸርት",           450,    600, 2, P+"product_graphic_tshirt.jpg", 50, 0, 1),
    ("Ladies Shirt",        "የሴቶች ሸሚዝ",             480,    620, 2, P+"ladies_shirt.jpg",          35, 0, 0),
    ("Printed Blouse",      "ፕሪንትድ ብሉዝ",           620,    800, 2, P+"printed_blouse.jpg",         28, 0, 1),
    ("Blouse",              "ብሉዝ",                  520,    680, 2, P+"blouse.jpg",                 30, 0, 0),
    ("Classic T-Shirt",     "ክላሲክ ቲሸርት",           380,    500, 2, P+"tshirt.jpg",                45, 0, 0),
    ("Habesha Top",         "የሀበሻ ቶፕ",              680,    880, 2, P+"prod_03_habesha_top.jpg",   20, 1, 0),
    ("Hijab",               "ሂጃብ",                  350,    450, 2, P+"hijab.jpg",                 60, 0, 0),

    # ── Trousers & Shorts ────────────────────────────────────────────────────
    ("Chino Trousers",      "ቺኖ ሱሪ",               720,    900, 3, P+"product_chinos.jpg",        30, 0, 1),
    ("Wide-Leg Pants",      "ወይድ ሌግ ሱሪ",           850,  1_050, 3, P+"product_wide_leg.jpg",      25, 1, 1),
    ("Denim Shorts",        "ዴኒም ሾርት",             560,    720, 3, P+"product_denim_shorts.jpg",  35, 0, 1),
    ("Leggings",            "ሌጊንስ",                 380,    500, 3, P+"product_leggings.jpg",      50, 0, 0),
    ("Classic Jeans",       "ክላሲክ ጂንስ",             780,    980, 3, P+"jeans.jpg",                30, 1, 0),
    ("Linen Pants",         "ሊነን ሱሪ",               650,    820, 3, P+"linen_pants.jpg",          28, 0, 1),
    ("Casual Trousers",     "ካዥዋል ሱሪ",              580,    750, 3, P+"casual_trousers.jpg",      35, 0, 0),
    ("Workout Leggings",    "ስፖርት ሌጊንስ",            420,    550, 3, P+"prod_07_leggings.jpg",     40, 0, 1),

    # ── Jackets & Knitwear ───────────────────────────────────────────────────
    ("Hoodie",              "ሁዲ",                   880,  1_100, 4, P+"product_hoodie.jpg",        30, 1, 1),
    ("Cardigan",            "ካርዲጋን",                750,    950, 4, P+"product_cardigan.jpg",      25, 0, 1),
    ("Leather Jacket",      "ሌዘር ጃኬት",            1_400,  1_800, 4, P+"product_leather_jacket.jpg",18, 1, 0),
    ("Classic Cardigan",    "ክላሲክ ካርዲጋን",           720,    900, 4, P+"cardigan.jpg",             28, 0, 0),
    ("Denim Jacket",        "ዴኒም ጃኬት",              980,  1_250, 4, P+"denim_jacket.jpg",         22, 1, 1),
    ("Blazer",              "ብሌዘር",                1_200,  1_500, 4, P+"prod_06_blazer.jpg",       15, 1, 0),

    # ── Underwear & Nightwear ─────────────────────────────────────────────────
    ("Pajama Set",          "ፓጃማ ሴት",              650,    820, 5, P+"product_pajama.jpg",        30, 0, 0),
    ("Prayer Dress",        "የጸሎት ልብስ",             720,    900, 5, P+"prayer_dress.jpg",         25, 0, 0),

    # ── Baby Suits & Rompers ─────────────────────────────────────────────────
    ("Baby Romper",         "የሕፃን ሮምፐር",            420,    550, 6, P+"product_baby_romper.jpg",  35, 1, 1),
    ("Baby Winter Suit",    "የሕፃን ክረምት ልብስ",        580,    750, 6, P+"product_baby_winter.jpg",  28, 0, 1),
    ("Baby Dress",          "የሕፃን ቀሚስ",             380,    500, 6, P+"baby_dress.jpg",           30, 0, 1),
    ("Baby Romper Set",     "የሕፃን ሮምፐር ሴት",         450,    580, 6, P+"prod_05_baby_romper.jpg",  30, 1, 1),
    ("Kids Outfit",         "የልጆች ልብስ ሴት",          520,    680, 6, P+"prod_09_kids_outfit.jpg",  25, 0, 1),

    # ── Activewear ───────────────────────────────────────────────────────────
    ("Sportswear Set",      "ስፖርት ልብስ ሴት",          780,    980, 7, P+"sportswear.jpg",           30, 1, 1),
    ("Yoga Pants",          "ዮጋ ሱሪ",                480,    620, 7, P+"yoga_pants.jpg",           35, 0, 1),

    # ── Traditional Wear ─────────────────────────────────────────────────────
    ("Habesha Kemis",       "ሀበሻ ቀሚስ",            1_200,  1_500, 8, P+"product_habesha_kemis.jpg", 20, 1, 0),
    ("Kuta",                "ኩታ",                    850,  1_100, 8, P+"product_kuta.jpg",          18, 1, 0),
    ("Netela",              "ነጠላ",                    680,    880, 8, P+"product_netela.jpg",        22, 0, 0),
    ("Gabi",                "ጋቢ",                     750,    950, 8, P+"product_gabi.jpg",          20, 0, 0),
    ("Tilf Skirt",          "ቲልፍ ቀሚስ",              920,  1_180, 8, P+"product_tilf_skirt.jpg",    15, 1, 0),
    ("Habesha Kemis Classic","ሀበሻ ቀሚስ ክላሲክ",       1_100,  1_400, 8, P+"prod_01_habesha_kemis.jpg", 18, 1, 0),
    ("Chiffon Kemis",       "ሺፎን ቀሚስ",             1_050,  1_350, 8, P+"prod_10_chiffon_kemis.jpg", 15, 1, 1),
    ("Tilf Traditional Dress","ቲልፍ ባህላዊ ቀሚስ",      980,  1_250, 8, P+"prod_08_tilf_dress.jpg",   18, 1, 0),
    ("Habesha Dress",       "ሀበሻ ቀሚስ ልዩ",          1_150,  1_450, 8, P+"habesha_dress.jpg",       20, 1, 0),
]

# Numbered product files — distribute across all 8 categories
numbered_files = [f"product_{str(i).zfill(3)}.jpg" for i in range(2, 22)]
num_categories = [
    (1,"Dress Collection","ቀሚስ ስብስብ",         1_050, 1_350),
    (2,"Fashion Top","ፋሽን ቶፕ",                  520,   680),
    (3,"Trouser Style","ሱሪ ስታይል",               680,   880),
    (4,"Jacket Style","ጃኬት ስታይል",               920, 1_180),
    (5,"Sleepwear","ሌሊት ልብስ",                    580,   750),
    (6,"Kids Wear","የልጆች ልብስ",                   450,   580),
    (7,"Active Set","ስፖርት ሴት",                   680,   880),
    (8,"Traditional Piece","ባህላዊ ልብስ",           850, 1_100),
    (1,"Gown Style","ጋውን ስታይል",               1_200, 1_550),
    (2,"Blouse Style","ብሉዝ ስታይል",                480,   620),
    (3,"Pants Style","ሱሪ ስታይል ሁለት",             720,   920),
    (4,"Knitwear","ኒትዌር",                         780, 1_000),
    (5,"Night Set","የሌሊት ሴት",                    620,   800),
    (6,"Baby Outfit","የሕፃን ልብስ",                 480,   620),
    (7,"Gym Wear","ጂም ልብስ",                       550,   720),
    (8,"Kemis Design","ቀሚስ ዲዛይን",             1_000, 1_300),
    (1,"Casual Dress","ካዥዋል ቀሚስ",               850, 1_050),
    (2,"Summer Top","ሰመር ቶፕ",                    450,   580),
    (3,"Slim Pants","ስሊም ሱሪ",                    680,   870),
    (7,"Sports Top","ስፖርት ቶፕ",                   480,   620),
]

# Hash-named product files — distribute evenly
hash_files = [
    "product_09aa2f97.jpg","product_0afa5c1a.jpg","product_15068dbe.jpg",
    "product_255e2a78.jpg","product_25d1c722.jpg","product_291aa2d0.jpg",
    "product_2defcf58.jpg","product_31289c3e.jpg","product_3f939a0a.jpg",
    "product_4857da26.jpg","product_4fb9c9e4.jpg","product_55179410.jpg",
    "product_58edd888.jpg","product_5bf257d5.jpg","product_63c03e17.jpg",
    "product_67da8649.jpg","product_6abfe72f.jpg","product_6b34dd2a.jpg",
    "product_70a82523.jpg","product_712ccf0f.jpg","product_731f63d7.jpg",
    "product_7e98064f.jpg","product_7fc6a24c.jpg","product_802b81af.jpg",
    "product_840589d7.jpg","product_8b88f74a.jpg","product_91402ba3.jpg",
    "product_91dc9d9c.jpg","product_966eb2c9.jpg","product_9ec9424a.jpg",
    "product_ad65ee90.jpg","product_b525bdb3.jpg","product_b56f53ce.jpg",
    "product_b6f3c896.jpg","product_b9acd553.jpg","product_beaad39c.jpg",
    "product_f80a9c80.jpg","product_fe957026.jpg",
]
hash_meta = [
    (1,"Fashion Dress","ፋሽን ቀሚስ",           1_100,1_400),
    (2,"Fashion Top","ፋሽን ቶፕ",               500,  650),
    (3,"Fashion Pants","ፋሽን ሱሪ",             700,  900),
    (4,"Fashion Jacket","ፋሽን ጃኬት",           950,1_200),
    (5,"Lounge Wear","ላውንጅ ልብስ",             600,  780),
    (6,"Baby Fashion","የሕፃን ፋሽን",            450,  580),
    (7,"Active Wear","አክቲቭ ልብስ",             600,  780),
    (8,"Cultural Dress","ባህላዊ ቀሚስ",          900,1_150),
    (1,"Elegant Gown","ኤሌጋንት ጋውን",         1_300,1_650),
    (2,"Casual Top","ካዥዋል ቶፕ",               460,  600),
    (3,"Modern Pants","ዘመናዊ ሱሪ",             720,  920),
    (4,"Classic Jacket","ክላሲክ ጃኬት",          900,1_150),
    (5,"Nightwear Set","ናይትዌር ሴት",           650,  840),
    (6,"Kids Fashion","የልጆች ፋሽን",            420,  550),
    (7,"Yoga Set","ዮጋ ሴት",                    540,  700),
    (8,"Habesha Style","ሀበሻ ስታይል",         1_050,1_350),
    (1,"Summer Dress","ሰመር ቀሚስ",             900,1_150),
    (2,"Office Shirt","ኦፊስ ሸሚዝ",             560,  720),
    (3,"Jogger Pants","ጆገር ሱሪ",              640,  820),
    (4,"Winter Jacket","ዊንተር ጃኬት",         1_100,1_400),
    (5,"Silk Nightwear","ሲልክ ናይትዌር",         700,  900),
    (6,"Romper Set","ሮምፐር ሴት",               440,  570),
    (7,"Running Set","ሩኒንግ ሴት",              580,  750),
    (8,"Tibeb Dress","ጥበብ ቀሚስ",           1_200,1_500),
    (1,"Party Dress","ፓርቲ ቀሚስ",           1_050,1_350),
    (2,"Trendy Top","ትሬንዲ ቶፕ",               490,  640),
    (3,"Wide Trousers","ወይድ ትሩዘርስ",           780, 1_000),
    (4,"Cardigan Set","ካርዲጋን ሴት",            820,1_050),
    (5,"Pyjama Set","ፒጃማ ሴት",               620,  800),
    (6,"Toddler Dress","ቶድለር ቀሚስ",           400,  520),
    (7,"Track Suit","ትራክ ሱት",               720,  920),
    (8,"Gabi Kemis","ጋቢ ቀሚስ",             1_000,1_300),
    (1,"Midi Dress","ሚዲ ቀሚስ",                950,1_200),
    (2,"Halter Top","ሃልተር ቶፕ",               520,  680),
    (3,"Palazzo Pants","ፓላዞ ሱሪ",             820,1_050),
    (4,"Trench Coat","ትሬንች ኮት",           1_250,1_600),
    (7,"Sporty Set","ስፖርቲ ሴት",               650,  840),
    (8,"Traditional Set","ባህላዊ ሴት",        1_100,1_400),
]

print("Inserting named products …")
for idx, row in enumerate(named_products):
    name,name_am,price,compare,cat,thumb,stock,feat,new_ = row
    insert_product(name,name_am,price,compare,cat,thumb,stock,feat,new_)
print(f"  {len(named_products)} named products queued")

print("Inserting numbered products …")
for i,(f,meta) in enumerate(zip(numbered_files,num_categories)):
    cat,name,name_am,price,compare = meta
    insert_product(name,name_am,price,compare,cat,P+f,30,0,0)
print(f"  {len(numbered_files)} numbered products queued")

print("Inserting hash-named products …")
for f,meta in zip(hash_files,hash_meta):
    cat,name,name_am,price,compare = meta
    insert_product(name,name_am,price,compare,cat,P+f,30,0,0)
print(f"  {len(hash_files)} hash products queued")

# ─────────────────────────────────────────────────────────────────────────────
# ADVERTISEMENTS
# ─────────────────────────────────────────────────────────────────────────────

AP = "uploads/ads/"

# Static image ads
image_ads = [
    ("Holiday Sale",       "የሆሊዴይ ቅናሽ",  AP+"ad_holiday.jpg",       "ልዩ ቅናሽ — እስከ 40% ቅናሽ!", "ልዩ ቅናሽ — እስከ 40% ቅናሽ!", 0),
    ("New Arrivals",       "አዲስ ምርቶች",    AP+"ad_new_arrivals.jpg",   "አዲስ ምርቶች ገቡ!", "አዲስ ምርቶች ገቡ!", 1),
    ("Special Sale",       "ልዩ ቅናሽ",      AP+"ad_sale.jpg",           "ዋጋ ቅናሽ — አሁን ይዘዙ!", "ዋጋ ቅናሽ — አሁን ይዘዙ!", 2),
    ("Summer Collection",  "ሰመር ስብስብ",    AP+"ad_summer.jpg",         "የሰመር ስብስብ ደረሰ!", "የሰመር ስብስብ ደረሰ!", 3),
    ("Traditional Wear",   "ባህላዊ ልብሶች",   AP+"ad_traditional.jpg",    "ቆንጆ ሀበሻ ቀሚሶች!", "ቆንጆ ሀበሻ ቀሚሶች!", 4),
]
# Banner images in products folder that are actually ads
banner_ads = [
    ("Fashion Banner",    "የፋሽን ባነር",    "uploads/products/ad_01_banner.jpg", "", "", 5),
    ("Promo Banner",      "ፕሮሞ ባነር",     "uploads/products/ad_02_banner.jpg", "", "", 6),
]

# Video ads
video_tokens = [
    "00012f34","101364bc","14e4579c","23b8920d","35f34c06","3d191173",
    "484b86a8","5a8cd1c8","6d29e2ca","814559a5","89d12dbc","95e41886",
    "998d02db","a5eb5e69","b0efd106","c0f7db92","d0ae515a","d44d35ad",
    "d97c5d7d","f7a1f401",
]
video_names = [
    ("ቀሚስ ስብስብ",   "Dress Collection"),
    ("አዲስ ምርቶች",   "New Arrivals"),
    ("ቅናሽ",         "Sale Offer"),
    ("ሰመር ፋሽን",    "Summer Fashion"),
    ("ሀበሻ ቀሚስ",   "Habesha Kemis"),
    ("ቀሚስ ቅናሽ",   "Dress Sale"),
    ("ልዩ ምርቶች",   "Special Items"),
    ("ጂንስ ስታይል",  "Jeans Style"),
    ("ያለቅናሽ ምርቶች","Premium Products"),
    ("ልዩ ቅናሽ",    "Special Sale"),
    ("ባህላዊ ልብስ",  "Traditional Wear"),
    ("ፋሽን ሾው",    "Fashion Show"),
    ("ልብስ ስብስብ",  "Clothing Collection"),
    ("ካፋ ፋሽን",    "Modern Fashion"),
    ("ልዩ ፋሽን",    "Unique Fashion"),
    ("ምርጥ ምርቶች",  "Best Products"),
    ("አዲስ ስታይል",  "New Style"),
    ("ልዩ ቀሚስ",    "Special Dress"),
    ("ፋሽን ቅናሽ",   "Fashion Sale"),
    ("ምርጥ ቅናሽ",   "Best Deals"),
]

print("Inserting image ads …")
for title,title_am,image,desc,desc_am,sort in image_ads + banner_ads:
    insert_ad(title,title_am,image=image,sort_order=sort,
              description=desc,description_am=desc_am)
print(f"  {len(image_ads)+len(banner_ads)} image ads queued")

print("Inserting video ads …")
for i,(tok,(nam_am,nam_en)) in enumerate(zip(video_tokens, video_names)):
    poster = AP + f"ad_{tok}_poster.jpg"
    video  = AP + f"ad_{tok}.mp4"
    insert_ad(nam_en, nam_am, image=poster, media_url=video, sort_order=10+i)
print(f"  {len(video_tokens)} video ads queued")

conn.commit()
cur.close()
conn.close()

# Verification
import psycopg2
conn2 = psycopg2.connect(DATABASE_URL)
cur2  = conn2.cursor()
cur2.execute("SELECT COUNT(*) FROM products")
p = cur2.fetchone()[0]
cur2.execute("SELECT COUNT(*) FROM advertisements")
a = cur2.fetchone()[0]
cur2.execute("SELECT c.name_am, COUNT(pr.id) FROM categories c LEFT JOIN products pr ON pr.category_id=c.id GROUP BY c.name_am ORDER BY c.id")
rows = cur2.fetchall()
cur2.close(); conn2.close()

print(f"\n✅  Done: {p} products, {a} ads inserted")
print("\nProducts per category:")
for r in rows:
    print(f"  {r[0]}: {r[1]}")
