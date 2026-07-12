"""
Christian Corner — daily rotating content for Protestant and Catholic sections.
Four collections of 30 entries each, indexed by day-of-month (1-based → 0-indexed).
"""

import datetime


# ══════════════════════════════════════════════════════════════════════════════
# PROTESTANT  —  Daily Bible Verse + Tafsir (ዕለታዊ የቅዱስ ቃሉ ጥቅስ)
# ══════════════════════════════════════════════════════════════════════════════

PROTESTANT_BIBLE_VERSES = [
    {
        "verse_am": "ጌታ እረኛዬ ነው — ምንም አያጎድልብኝም።",
        "verse_en": "The Lord is my shepherd; I shall not want.",
        "ref":      "መዝሙር 23:1",
        "tafsir":   "ዳዊት ፈጣሪን እንደ ቸር እረኛ ይቆጥረዋል — ፍላጎቱን ሁሉ ያሟላ። ዛሬ ፈጣሪን እንደ ጠባቂ አምን።",
    },
    {
        "verse_am": "ፈጣሪ ያለፈልኝ ዕቅድ ሰላም እንጂ ክፉ አይደለም — ተስፋና ጥሩ ወደፊት ለመስጠት።",
        "verse_en": "For I know the plans I have for you, declares the Lord — plans for peace and not for evil, to give you a future and a hope.",
        "ref":      "ኤርምያስ 29:11",
        "tafsir":   "ፈጣሪ ዕቅዱ ሰላምና ተስፋ ነው። ዛሬ ሁኔታዎቹ ቢከብዱ እንኳ ፈጣሪ ወደፊቱን ያውቃል።",
    },
    {
        "verse_am": "አምናችሁ ወደ ጌታ ዘንድ ሁሉ ኑ — እኔ አሳርፋችኋለሁ።",
        "verse_en": "Come to me, all who labour and are heavy laden, and I will give you rest.",
        "ref":      "ማቴዎስ 11:28",
        "tafsir":   "ኢየሱስ ሁሉንም ሸክም ተሸካሚዎችን ጠርቷል። ዛሬ ሸክምህን ወደ ፈጣሪ አምጣ።",
    },
    {
        "verse_am": "ልዑሉ ፈቃዱን ባሰበ ሁሉ ነገር ለሚወዱት ለጥሩ ይሆናል።",
        "verse_en": "And we know that for those who love God all things work together for good.",
        "ref":      "ሮሜ 8:28",
        "tafsir":   "ፈጣሪ ምሕረቱ ሁሉ ነገርን ለበጎ ያሰራዋል። ዛሬ ፍቅሩን አምን።",
    },
    {
        "verse_am": "ከፍርሃት አትቁራጥ — ጌታ አምላክህ ከአንተ ጋር ነው።",
        "verse_en": "Be strong and courageous. Do not be frightened, for the Lord your God is with you wherever you go.",
        "ref":      "ኢያሱ 1:9",
        "tafsir":   "ጌታ ለኢያሱ ደፋርነት ሰጠው። ዛሬ ፍርሃቱ ቢኖር ጌታ ይጋፈጠዋል።",
    },
    {
        "verse_am": "አምላኬ ክብሩ ባለ ሃብቱ ፍላጎትህን ሁሉ ያሟላዋል።",
        "verse_en": "And my God will supply every need of yours according to his riches in glory in Christ Jesus.",
        "ref":      "ፊልጵስዩስ 4:19",
        "tafsir":   "ፈጣሪ ሃብቱ ልክ የለውም — ፍላጎቱን ሁሉ ያሟላዋል። ዛሬ በፈጣሪ መቅረብን ምረጥ።",
    },
    {
        "verse_am": "ጌታ ብርሃኔና መዳኔ ነው — ከማን እፈራለሁ?",
        "verse_en": "The Lord is my light and my salvation; whom shall I fear?",
        "ref":      "መዝሙር 27:1",
        "tafsir":   "ብርሃን ጨለማን ያስወግዳዋል — ጌታ ፍርሃትን ያስወግዳዋል። ዛሬ ድፍረቱን ያምናቸው።",
    },
    {
        "verse_am": "ክርስቶስ ኢየሱስ ኃጢያተኞችን ለማዳን ወደ ዓለም መጣ — እኔ ዋናው ነኝ።",
        "verse_en": "Christ Jesus came into the world to save sinners, of whom I am the foremost.",
        "ref":      "1ጢሞቴዎስ 1:15",
        "tafsir":   "ጸጋ ሁሉን ያካትታል — ዋናው ኃጢያተኛም ጸጋ ያገኛል። ዛሬ ጸጋ ለሁሉ ለዕቅፍ አብዛ።",
    },
    {
        "verse_am": "ፈጣሪ ፍቅር ነው — ፍቅር ውስጥ ያለ ሰው በፈጣሪ ውስጥ ያለ ነው።",
        "verse_en": "God is love, and whoever abides in love abides in God, and God abides in him.",
        "ref":      "1ዮሐንስ 4:16",
        "tafsir":   "ፍቅር የፈጣሪ ባሕሪ ዋናው ነው። ዛሬ ፍቅርን ሰጥ — ፈጣሪ ይሁን።",
    },
    {
        "verse_am": "በፍቅር ስር ሁሉ ነገር ታጋሽ ሁን — ያምናችሁ ሁሉ።",
        "verse_en": "I can do all things through him who strengthens me.",
        "ref":      "ፊልጵስዩስ 4:13",
        "tafsir":   "ኃይሉ ከፈጣሪ ነው — ክርስቶስ ያጠናክራል። ዛሬ ፈጣሪ ያጠናክርህ።",
    },
    {
        "verse_am": "ዛሬ ፈጣሪን ፈልግ — ሳለ ቅርብ ሳለ ጥራው።",
        "verse_en": "Seek the Lord while he may be found; call upon him while he is near.",
        "ref":      "ኢሳይያስ 55:6",
        "tafsir":   "ፈጣሪን ፈልጎ ማግኘት ወቅቱ አለው — ዛሬ ፈልጎ ጥራ።",
    },
    {
        "verse_am": "ጌታ ሆይ ኃጢያቴን ሁሉ ምሕረት አድርጉ — ለስምህ ሲሉ።",
        "verse_en": "For your name's sake, O Lord, pardon my guilt, for it is great.",
        "ref":      "መዝሙር 25:11",
        "tafsir":   "ምሕረት ሲጠየቅ ፈጣሪ ሁሌ ያዳምጣዋል። ዛሬ ኃጢያቱን ምሕረት ጠይቅ።",
    },
    {
        "verse_am": "ጌታ ቃሉ ለእግሬ መብራት ነው — ለመንገዴ ብርሃን ነው።",
        "verse_en": "Your word is a lamp to my feet and a light to my path.",
        "ref":      "መዝሙር 119:105",
        "tafsir":   "የፈጣሪ ቃል መሪ ነው — ጨለማን ያስወግዳዋል። ዛሬ ቃሉን አንብብ።",
    },
    {
        "verse_am": "ወደ ፈጣሪ ቅረብ — ወደ አንተ ቀርቦ ይቀርባዋል።",
        "verse_en": "Draw near to God, and he will draw near to you.",
        "ref":      "ያዕቆብ 4:8",
        "tafsir":   "ፈጣሪ ሕቅፍ ሁሌ ክፍት ነው — ቀረበ ካለ ቀርቦ ይቀርቦዋል። ዛሬ ቅረብ።",
    },
    {
        "verse_am": "ቅዱሳን ፈቃዱ ቢሆን ሁሉ ነገር ይሆናል — ተወ ሁሉ ፈቃዱ ይሁን።",
        "verse_en": "Not my will, but yours, be done.",
        "ref":      "ሉቃስ 22:42",
        "tafsir":   "ኢየሱስ ፈቃዱን ለፈጣሪ አስረከበ — ዛሬ ፈቃዱን ፈጣሪ ይምራ።",
    },
    {
        "verse_am": "ፈጣሪ ቸር ነው — ለሚጠብቁት ነፍስ ለሚፈልጉት ሰው።",
        "verse_en": "The Lord is good to those who wait for him, to the soul who seeks him.",
        "ref":      "ሰቆቃ 3:25",
        "tafsir":   "መጠበቅ ፈጣሪ ቸርነትን ያሳያዋል — ዛሬ ተስፋ ቆርጦ አትጠብቅ።",
    },
    {
        "verse_am": "ፍጥረት ሁሉ ፈጣሪን ያወድሳዋል — ቅዱስ ቅዱስ ቅዱስ ጌታ።",
        "verse_en": "Holy, holy, holy is the Lord God Almighty, who was and is and is to come!",
        "ref":      "ራዕይ 4:8",
        "tafsir":   "ዕቅፍ ፈጣሪን ወዶ ማምለክ — ዛሬ ፈጣሪን አወድስ።",
    },
    {
        "verse_am": "ፍቅር ታጋሽ ነው፤ ቸር ነው — ፍቅር አይቀናም አይኮሩም አያሳፍርም።",
        "verse_en": "Love is patient and kind; love does not envy or boast; it is not arrogant.",
        "ref":      "1ቆሮንቶስ 13:4",
        "tafsir":   "ፍቅር ዋናው ምልክት — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "verse_am": "ፈጣሪ ዓለምን ፈቅዶ አንድያ ልጁን ሰጠ — ያምን ሁሉ ይዳን።",
        "verse_en": "For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life.",
        "ref":      "ዮሐንስ 3:16",
        "tafsir":   "ፍቅሩ ዋጋ ያለው ዋጋ — ልጁን ለዓለም ሰጠ። ዛሬ ፍቅሩን አድናቆ።",
    },
    {
        "verse_am": "ፈጣሪ ሆይ ልቤን ፈትሽ — ሃሳቤን ሁሉ እወቅ።",
        "verse_en": "Search me, O God, and know my heart! Try me and know my thoughts!",
        "ref":      "መዝሙር 139:23",
        "tafsir":   "ፈጣሪ ልብን ያውቃዋል — ዛሬ ቅን ልብ ስጥ።",
    },
    {
        "verse_am": "ዓለምን ሳይሆን ፈጣሪን አመስግን — ፈጣሪ አዳኝ ነው።",
        "verse_en": "Salvation belongs to the Lord; your blessing be on your people!",
        "ref":      "መዝሙር 3:8",
        "tafsir":   "ደህንነት ከፈጣሪ ብቻ ነው — ዛሬ ፈጣሪን አምን።",
    },
    {
        "verse_am": "ፈጣሪ ደስተኛ ሰጪ ነው — ለሚሰጥ ሁሉ ደስ ያስደስተዋል።",
        "verse_en": "Each one must give as he has decided in his heart, not reluctantly or under compulsion, for God loves a cheerful giver.",
        "ref":      "2ቆሮንቶስ 9:7",
        "tafsir":   "ደስ ሲለው ሲሰጥ ፈጣሪ ይወደዋል — ዛሬ ደስ ብሎ ሰጥ።",
    },
    {
        "verse_am": "ጸሎቴን ስሰማ ጌታ ሆይ ምሕረት አድርግ — ምሕረት ሰጥ።",
        "verse_en": "Be gracious to me, O Lord, for to you do I cry all the day.",
        "ref":      "መዝሙር 86:3",
        "tafsir":   "ዕለት ዕለት ፈጣሪን ጥሪ — ምሕረቱ ሰፊ ነው።",
    },
    {
        "verse_am": "ፈጣሪ ኃይሌ ጋሻዬ ነው — ልቤ ታምኖበታል።",
        "verse_en": "The Lord is my strength and my shield; in him my heart trusts, and I am helped.",
        "ref":      "መዝሙር 28:7",
        "tafsir":   "ፈጣሪ ኃይሌ — ዛሬ ታምን።",
    },
    {
        "verse_am": "በፈጣሪ ደስ ይበልህ — ልብ ምኞቱን ይሰጥሃል።",
        "verse_en": "Delight yourself in the Lord, and he will give you the desires of your heart.",
        "ref":      "መዝሙር 37:4",
        "tafsir":   "ፈጣሪ ሲደሰቱ ምኞት ይሰጣዋል — ዛሬ ፈጣሪ አግኝ።",
    },
    {
        "verse_am": "ሐዋርያት ሁሉ ጸልዩ ቃሉን ሰብኩ — ፈጣሪ ይሆናቸዋል።",
        "verse_en": "Pray without ceasing.",
        "ref":      "1ተሰሎንቄ 5:17",
        "tafsir":   "ጸሎት ያልቆምበት ሕይወት — ዛሬ ጸልይ።",
    },
    {
        "verse_am": "ኃጢያቴን ለፈጣሪ ናዘዝሁ — ጽድቁን ሸፈነኝ።",
        "verse_en": "If we confess our sins, he is faithful and just to forgive us our sins and to cleanse us from all unrighteousness.",
        "ref":      "1ዮሐንስ 1:9",
        "tafsir":   "ኑዛዜ ምሕረትን ያስከትላዋል — ዛሬ ናዘዝ።",
    },
    {
        "verse_am": "ወደ ፈጣሪ ቁጠሩ ሁሉ ሀሳቦቻችሁን — ሰላሙ ልቤን ይጠብቀዋል።",
        "verse_en": "Do not be anxious about anything, but in everything by prayer and supplication with thanksgiving let your requests be made known to God.",
        "ref":      "ፊልጵስዩስ 4:6",
        "tafsir":   "ጭንቀት ፈጣሪ ዘንድ ምሕረትን ያመጣዋል — ዛሬ ጸልይ።",
    },
    {
        "verse_am": "ኢየሱስ ትናንትናም ዛሬም ለዘለዓለምም አንዱ ነው።",
        "verse_en": "Jesus Christ is the same yesterday and today and forever.",
        "ref":      "ዕብራውያን 13:8",
        "tafsir":   "ኢየሱስ ሁሌ አይለወጥም — ዛሬ ያምን።",
    },
    {
        "verse_am": "ቅዱስ ቅዱስ — ፈጣሪ ኃይሉ ዓለምን ሞልቷዋል።",
        "verse_en": "The heavens declare the glory of God, and the sky above proclaims his handiwork.",
        "ref":      "መዝሙር 19:1",
        "tafsir":   "ፍጥረት ፈጣሪ ምስጋናን ያወጃዋል — ዛሬ ፍጥረትን ሲያይ አወድስ።",
    },
    {
        "verse_am": "ፈጣሪ ኃያል ነው — ካሰበ ሁሉ ይሆናዋል።",
        "verse_en": "For nothing will be impossible with God.",
        "ref":      "ሉቃስ 1:37",
        "tafsir":   "ፈጣሪ ዘንድ የሚሳነው ነገር የለም — ዛሬ ሰፊ ዕምነት ያዝ።",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# PROTESTANT  —  Spiritual Songs / Quotes (የመዝሙር ጥቅሶች ወይም መንፈሳዊ ጥቅሶች)
# ══════════════════════════════════════════════════════════════════════════════

PROTESTANT_SONGS = [
    {
        "title":  "አመሰግናለሁ ጌታዬ",
        "lyric":  "አመሰግናለሁ ጌታዬ — ፍቅርህ ሞልቶ ህይወቴን ሞላ፤ ብርሃንህ ጨለማዬን አስወገደ።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ምስጋና ከልብ ሲወጣ ፈጣሪ ቅርብ ይሆናዋል።",
    },
    {
        "title":  "ኢየሱስ ድኅነቴ",
        "lyric":  "ኢየሱስ ድኅነቴ — ምሕረቱ ሞልቷዋል፤ ፍቅሩ ህይወቴን አደሰ።",
        "author": "ዘማሪ ሻምበል",
        "quote":  "ድኅነት ስጦታ ነው — ዋጋ ሳይከፈልበት ይሰጣዋል።",
    },
    {
        "title":  "ፈጣሪ ሆይ አመሰግናለሁ",
        "lyric":  "ፈጣሪ ሆይ — ዕለቱ ሲጠባ አምስጋናለሁ፤ ህይወቴ ሁሉ ለጌታ ነው።",
        "author": "ዘማሪ ጳዉሎስ",
        "quote":  "ፈጣሪ ፍቅሩ ሁሌ ከጎናችን ነው — ማምስጋን ጀምር።",
    },
    {
        "title":  "ቅዱስ ቅዱስ ቅዱስ",
        "lyric":  "ቅዱስ ቅዱስ ቅዱስ — ጌታ ኃይሉ ዓለምን ሞልቷዋል፤ ምስጋናው ዘለዓለም።",
        "author": "ዘማሪ ክርስቲና",
        "quote":  "ቅዱሳን ሕቅፍ ፈጣሪን ማምለክ — ዛሬ አወድስ።",
    },
    {
        "title":  "ብርሃን ዓለም",
        "lyric":  "ብርሃን ዓለም ኢየሱስ — ጨለማ ውስጥ ብርሃን ሆነ፤ ሕይወቴን አደሰ።",
        "author": "ዘማሪ ሰሎሞን",
        "quote":  "ብርሃን ጨለማን ሁሌ ያሸንፈዋዋል — ኢየሱስ ብርሃን ነው።",
    },
    {
        "title":  "ፍቅርህ አይጠፋም",
        "lyric":  "ፍቅርህ አይጠፋም — ከፍ ሲሆን ዝቅ ሲሆን ምሕረቱ ሁሌ አለ።",
        "author": "ዘማሪ ፅዮን",
        "quote":  "ፈጣሪ ፍቅሩ ዘለዓለም ነው — አይጠፋም።",
    },
    {
        "title":  "ጌታ ናህ",
        "lyric":  "ጌታ ናህ — ከናህ ሌላ አምላክ የለም፤ ምስጋናህ ዘለዓለም ይሁን።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ፈጣሪ አንድ ነው — ዛሬ አምን።",
    },
    {
        "title":  "ደስ ይበለኝ",
        "lyric":  "ደስ ይበለኝ — ፈጣሪ ጎኔ ሲሆን ደስ ይበለኝ፤ ምሕረቱ ሞልቷዋል።",
        "author": "ዘማሪ ኤልሳ",
        "quote":  "ደስታ ከፈጣሪ ጋር ሲሆን ዘለዓለም ነው።",
    },
    {
        "title":  "ምስጋና ዘለዓለም",
        "lyric":  "ምስጋና ዘለዓለም — ፍቅሩ ህይወቴን ሞላ፤ ምሕረቱ አይጠፋም።",
        "author": "ዘማሪ ጸሐዬ",
        "quote":  "ምስጋና ፈጣሪን ያቀርቦዋል — ዛሬ አወድስ።",
    },
    {
        "title":  "ለዘለዓለም ጌታ ናህ",
        "lyric":  "ለዘለዓለም ጌታ ናህ — ምሕረቱ ዘለዓለም ምስጋናህ ያልቆ አያቀርቡህ።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ዘለዓለም ፈጣሪ ነው — ዛሬ ምስጋና ስጥ።",
    },
    {
        "title":  "ጸሎቴ ሰሚ",
        "lyric":  "ጸሎቴ ሰሚ ፈጣሪ — ሁሌ ቅርብ ሆነ፤ ምሕረቱ ሞልቷዋል።",
        "author": "ዘማሪ ሐና",
        "quote":  "ጸሎት ፈጣሪን ቅርብ ያደርጋዋል — ዛሬ ጸልይ።",
    },
    {
        "title":  "ልቤ ይወድሃል",
        "lyric":  "ልቤ ይወድሃል ፈጣሪ — ምሕረቱ ሞልቷዋል፤ ፍቅሩ ህይወቴን ሞላ።",
        "author": "ዘማሪ ናዖሚ",
        "quote":  "ፈጣሪን መውደድ ሁሉ ጥሩ ነገር ያስከትሎዋል።",
    },
    {
        "title":  "ሕይወቴ ለጌታ",
        "lyric":  "ሕይወቴ ለጌታ — ሁሉ ነገሬ ለፈጣሪ፤ ምሕረቱ ሞልቷዋል።",
        "author": "ዘማሪ ዳዊት",
        "quote":  "ሕይወቴን ለፈጣሪ ሰጥ — ምሕረቱ ሊሞላ።",
    },
    {
        "title":  "ፈጣሪ ፍቅሩ",
        "lyric":  "ፈጣሪ ፍቅሩ — ሁሌ አለ ሁሌ ቅርብ ሁሌ ምሕረቱ ሞልቷዋል።",
        "author": "ዘማሪ ሕፃናት",
        "quote":  "ፍቅር ፈጣሪ ዋናው ባሕሪ ነው — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "title":  "አልፍ ኦሜጋ",
        "lyric":  "አልፍ ኦሜጋ — መጀመሪያ መጨረሻ ፈጣሪ ዘለዓለም ነው።",
        "author": "ዘማሪ ኤፍሬም",
        "quote":  "ፈጣሪ ዘለዓለም ነው — ሁሌ አለ።",
    },
    {
        "title":  "ምሕረቱ ሰፊ ነው",
        "lyric":  "ምሕረቱ ሰፊ ነው — ኃጢያቴ ሁሉ ሸፈነ፤ ፈጣሪ ምሕረቱ ሰፊ ነው።",
        "author": "ዘማሪ ስምዖን",
        "quote":  "ምሕረት ኃጢያቴን ሁሉ ይሸፍናዋል — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "title":  "ጌታ ኃይሌ",
        "lyric":  "ጌታ ኃይሌ — ፈጣሪ ጎኔ ሲሆን ኃይሌ ሞልቷዋል።",
        "author": "ዘማሪ ጎርፊ",
        "quote":  "ፈጣሪ ኃይሉን ሲሰጠን ሁሉ ነገር ይቻሎዋል።",
    },
    {
        "title":  "ዘምሩ ለጌታ",
        "lyric":  "ዘምሩ ለጌታ — ምሕረቱ ዘለዓለም ነው፤ ፍቅሩ ይቀጥሎዋል።",
        "author": "ዘማሪ ድምጻዊ",
        "quote":  "ምዝሙር ፈጣሪን ያቀርቦዋል — ዛሬ ዘምር።",
    },
    {
        "title":  "ተስፋ አትቁረጥ",
        "lyric":  "ተስፋ አትቁረጥ — ፈጣሪ ጎኔ ሲሆን ተስፋ አለ፤ ምሕረቱ ሞልቷዋል።",
        "author": "ዘማሪ ኤዲናም",
        "quote":  "ተስፋ ፈጣሪ ዘንድ ሁሌ አለ — አትቁረጥ።",
    },
    {
        "title":  "ፈጣሪ ጎኔ",
        "lyric":  "ፈጣሪ ጎኔ — ሁሌ ቅርብ ሁሌ ምሕረቱ ሞልቷዋል፤ ፍቅሩ ይቆያዋል።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ፈጣሪ ሁሌ ጎናችን ነው — ዛሬ አምን።",
    },
    {
        "title":  "አዲስ ዘፈን",
        "lyric":  "አዲስ ዘፈን — ፈጣሪ ምሕረቱ ዘለዓለም ነው፤ ሕይወቴ አደሰ።",
        "author": "ዘማሪ ቤዛ",
        "quote":  "ፈጣሪ ሕይወቴን አዳሰ — ዛሬ አዲሱን ምስጋና ስጥ።",
    },
    {
        "title":  "ፍቅር ያሸንፋዋል",
        "lyric":  "ፍቅር ያሸንፋዋል — ጠላት ምንም ቢፈጥር ፍቅር ዘለዓለም ያሸንፋዋል።",
        "author": "ዘማሪ ሊዲያ",
        "quote":  "ፈጣሪ ፍቅሩ ሁሉ ፈተናን ያሸንፋዋል — ዛሬ አምን።",
    },
    {
        "title":  "ሕያው ፈጣሪ",
        "lyric":  "ሕያው ፈጣሪ — ሕያው ፈጣሪ ሁሌ ነው፤ ምሕረቱ ዘለዓለም።",
        "author": "ዘማሪ ዘነሽ",
        "quote":  "ፈጣሪ ሕያው ነው — ዛሬ ምሕረቱ ጠይቅ።",
    },
    {
        "title":  "ጸሎቴ ሁሌ",
        "lyric":  "ጸሎቴ ሁሌ — ፈጣሪ ዘንድ ሁሌ ጸሎቴ ቅርብ ነው፤ ምሕረቱ ሰፊ።",
        "author": "ዘማሪ ሰምሶን",
        "quote":  "ጸሎት ፈጣሪን ቅርብ ያደርጋዋል — ዛሬ ጸልይ።",
    },
    {
        "title":  "የጌታ ፍቅር",
        "lyric":  "የጌታ ፍቅር — ዓለም ሁሉ ቢቃወም ፍቅሩ ሁሌ አለ።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ፈጣሪ ፍቅሩ ዘለዓለም ነው — ዛሬ ምሕረቱ አምን።",
    },
    {
        "title":  "ምሕረት ለሁሉ",
        "lyric":  "ምሕረት ለሁሉ — ፈጣሪ ምሕረቱ ሁሉን ያካትታዋል፤ ዛሬ ምሕረት ስጥ።",
        "author": "ዘማሪ ጥቢቲ",
        "quote":  "ምሕረት ሁሉን ያካትታዋል — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "title":  "ደስ ይለኝ",
        "lyric":  "ደስ ይለኝ — ፈጣሪ ጎኔ ሲሆን ደስ ይለኝ፤ ምሕረቱ ዘለዓለም።",
        "author": "ዘማሪ ፈቅሩ",
        "quote":  "ፈጣሪ ጎን ደስታ ሁሌ አለ — ዛሬ ደስ ይበልህ።",
    },
    {
        "title":  "ክብሩ ሞልቷዋል",
        "lyric":  "ክብሩ ሞልቷዋል — ሰማይ ምድር ፈጣሪ ክብሩ ሞልቷዋል።",
        "author": "ዘማሪ ሀብቱ",
        "quote":  "ፈጣሪ ክብሩ ዓለምን ሞልቷዋል — ዛሬ አወድስ።",
    },
    {
        "title":  "ለዘለዓለም",
        "lyric":  "ለዘለዓለም — ፈጣሪ ምሕረቱ ዘለዓለም ነው፤ ምስጋናው ይቀጥሎዋል።",
        "author": "ወንጌላዊ ዘማሪ",
        "quote":  "ፈጣሪ ዘለዓለም ነው — ዛሬ ምሕረቱ አምን።",
    },
    {
        "title":  "ዕረፍቴ ጌታ",
        "lyric":  "ዕረፍቴ ጌታ — ሸክሙ ሁሉ ወደ ጌታ ወስደ ዕረፍቴ ጌታ ነው።",
        "author": "ዘማሪ ትዕዛዝ",
        "quote":  "ፈጣሪ ሸክምን ይወስዳዋል — ዛሬ ወደ ጌታ ቅረብ።",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# CATHOLIC  —  Liturgical Calendar / Daily Reading (ዕለታዊ የሥርዓተ አምልኮ ንባብ)
# ══════════════════════════════════════════════════════════════════════════════

CATHOLIC_LITURGY = [
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱስ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "Then Ezra blessed the Lord, the great God, and all the people answered, Amen, Amen.",
        "season":     "ዘወትር ዘመን (Ordinary Time)",
        "ref":        "ነህምያ 8:6",
        "reflection": "ቃሉን ሰምቶ አሜን ማለት ፈጣሪን ማምለክ ነው — ዛሬ ቃሉን ሰምቶ ተቀበለ።",
    },
    {
        "reading_am": "ፍቅር ታጋሽ ነው ቸር ነው — ፍቅር ፈጣሪ ዋናው ምልክት ነው።",
        "reading_en": "And now abide faith, hope, love, these three; but the greatest of these is love.",
        "season":     "ዘወትር ዘመን",
        "ref":        "1ቆሮንቶስ 13:13",
        "reflection": "ፍቅር ሁሉ ዋናው ነው — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "reading_am": "ፈጣሪ ፈቃዱ ቢሆን ምሕረቱ ሰፊ ነው — ምሕረት ጠይቅ።",
        "reading_en": "Have mercy on me, O God, according to your steadfast love.",
        "season":     "ዐቢይ ጾም (Lent)",
        "ref":        "መዝሙር 51:1",
        "reflection": "ምሕረት ጠይቆ ማምለክ ዐቢይ ጾም ዋናው ነው — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "reading_am": "ቅዱስ ቅዱስ ቅዱስ ጌታ — ሰማይ ምድር ፍቅሩ ሞልቷዋል።",
        "reading_en": "Holy, holy, holy is the Lord of hosts; the whole earth is full of his glory!",
        "season":     "ዘወትር ዘመን",
        "ref":        "ኢሳይያስ 6:3",
        "reflection": "ፈጣሪ ቅዱሳን ክብሩ ዓለምን ሞልቷዋል — ዛሬ አወድስ።",
    },
    {
        "reading_am": "ፈጣሪ ሆይ — ሕዝቡ ቃሉን ሰምቶ ፈሩ ፈጣሪን ፍርሃት ዕውቀት መጀመሪያ ነው።",
        "reading_en": "The fear of the Lord is the beginning of wisdom; a good understanding have all those who do his commandments.",
        "season":     "ዘወትር ዘመን",
        "ref":        "መዝሙር 111:10",
        "reflection": "ፈጣሪን መፍራት ጥበብ ያስከትሎዋል — ዛሬ ፈጣሪን ፍራ።",
    },
    {
        "reading_am": "ኢየሱስ ሰዎችን ፈቅዶ ሁሉ ጠርቶ አስተማረ — ሕዝቡ ደስ ሆነ።",
        "reading_en": "And he opened his mouth and taught them, saying: Blessed are the poor in spirit, for theirs is the kingdom of heaven.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ማቴዎስ 5:2-3",
        "reflection": "ቡሩካን ፈጣሪ ዕቅፍ ቅርብ ናቸው — ዛሬ ቃሉን ሰምቶ ደስ ሁን።",
    },
    {
        "reading_am": "ፈጣሪ ወዳጆቹ ሁሉ ምሕረቱ ሰፊ ነው — ምሕረቱ ዘለዓለም።",
        "reading_en": "Oh give thanks to the Lord, for he is good; for his steadfast love endures forever!",
        "season":     "ምስጋና ዘመን",
        "ref":        "1ዜናዎቸ 16:34",
        "reflection": "ምሕረቱ ዘለዓለም ነው — ዛሬ አምስጋን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ወዶ አዳናቸው — ምሕረቱ ዘለዓለም።",
        "reading_en": "For God so loved the world, that he gave his only Son.",
        "season":     "ሁሉ ዘመን",
        "ref":        "ዮሐንስ 3:16",
        "reflection": "ፍቅሩ ዋጋ ያለው ዋጋ — ዛሬ ፍቅሩን አድናቆ።",
    },
    {
        "reading_am": "ኢየሱስ ሕያው ቤተ ልሔምን ፈጣሪ ኃይሉ ሰጠ — ምሕረቱ ሰፊ ነው።",
        "reading_en": "Jesus said to her, I am the resurrection and the life. Whoever believes in me, though he die, yet shall he live.",
        "season":     "ፋሲካ ዘመን (Easter)",
        "ref":        "ዮሐንስ 11:25",
        "reflection": "ትንሳኤ ተስፋ — ዛሬ ፈጣሪ ሕይወቱን አምን።",
    },
    {
        "reading_am": "ቅዱስ ቅዱሳን ፈጣሪ ምሕረቱ — ፈጣሪ ሕቅፍ ክፍት ነው።",
        "reading_en": "Come to me, all who labour and are heavy laden, and I will give you rest.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ማቴዎስ 11:28",
        "reflection": "ፈጣሪ ሸክምን ወስዶ ዕረፍት ይሰጣዋል — ዛሬ ወደ ጌታ ቅረብ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ተቀበለ — ፈጣሪ ደስ ሆነ።",
        "reading_en": "Blessed rather are those who hear the word of God and keep it!",
        "season":     "ዘወትር ዘመን",
        "ref":        "ሉቃስ 11:28",
        "reflection": "ቃሉን ሰምቶ ማቆየት ቡሩካን ናቸው — ዛሬ ቃሉን ሰምቶ ተቀበለ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ደስ ሆነ።",
        "reading_en": "Your word is truth.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ዮሐንስ 17:17",
        "reflection": "ፈጣሪ ቃሉ እውነት ነው — ዛሬ ቃሉን ሰምቶ ተቀበለ።",
    },
    {
        "reading_am": "ጌታ ሆይ ምሕረት አድርግ — ፈጣሪ ሕቅፍ ሁሌ ክፍት ነው።",
        "reading_en": "Lord, have mercy on me, a sinner.",
        "season":     "ዐቢይ ጾም",
        "ref":        "ሉቃስ 18:13",
        "reflection": "ምሕረት ሲጠየቅ ፈጣሪ ሁሌ ይሰጣዋል — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ሁሉ ፍቅሩ ሰጠ — ፍቅሩ ዘለዓለም።",
        "reading_en": "God is love, and whoever abides in love abides in God.",
        "season":     "ዘወትር ዘመን",
        "ref":        "1ዮሐንስ 4:16",
        "reflection": "ፍቅር ፈጣሪ ዋናው ባሕሪ ነው — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ዛሬ ቃሉን ሰምቶ ደስ ሁን።",
        "reading_en": "Man shall not live by bread alone, but by every word that comes from the mouth of God.",
        "season":     "ዐቢይ ጾም",
        "ref":        "ማቴዎስ 4:4",
        "reflection": "ሕይወት ቃሉ ነው — ዛሬ ቃሉን ሰምቶ ተቀበለ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ፍቅሩ ዘለዓለም ነው — ምሕረቱ ሞልቷዋል።",
        "reading_en": "For the Lord is good; his steadfast love endures forever, and his faithfulness to all generations.",
        "season":     "ምስጋና ዘመን",
        "ref":        "መዝሙር 100:5",
        "reflection": "ፈጣሪ ፍቅሩ ዘለዓለም ነው — ዛሬ አምስጋን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ኢየሱስ ዓለምን ሊያድን ደርሷዋል — ምሕረቱ ሰፊ ነው።",
        "reading_en": "For the Son of Man came to seek and to save the lost.",
        "season":     "ዐቢይ ጾም",
        "ref":        "ሉቃስ 19:10",
        "reflection": "ኢየሱስ ያጡትን ሊያድን ደርሷዋል — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ፈጣሪ ምሕረቱ ሰፊ ነው።",
        "reading_en": "Rejoice in the Lord always; again I will say, rejoice.",
        "season":     "ምስጋና ዘመን",
        "ref":        "ፊልጵስዩስ 4:4",
        "reflection": "ፈጣሪ ዘንድ ደስታ ሁሌ አለ — ዛሬ ደስ ሁን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "I am the way, and the truth, and the life. No one comes to the Father except through me.",
        "season":     "ሁሉ ዘመን",
        "ref":        "ዮሐንስ 14:6",
        "reflection": "ኢየሱስ መንገዱ እውነቱ ሕይወቱ ነው — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ፍቅሩ ሰጠ — ምሕረቱ ዘለዓለም ነው።",
        "reading_en": "Give thanks in all circumstances; for this is the will of God in Christ Jesus for you.",
        "season":     "ዘወትር ዘመን",
        "ref":        "1ተሰሎንቄ 5:18",
        "reflection": "ሁሉ ሁኔታ አምስጋን — ዛሬ ምስጋናህን ስጥ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ሁሉ ፍቅሩ ሰጠ — ምሕረቱ ሰፊ ነው።",
        "reading_en": "Trust in the Lord with all your heart, and do not lean on your own understanding.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ምሳሌ 3:5",
        "reflection": "ፈጣሪን ሙሉ ልብ ያምናዋል — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ፈጣሪ ምሕረቱ ሰፊ ነው።",
        "reading_en": "Do not be conformed to this world, but be transformed by the renewal of your mind.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ሮሜ 12:2",
        "reflection": "ፈጣሪ ሕቅፍ ልቡ ይታደሳዋል — ዛሬ ልብህን ታደስ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "For I am sure that neither death nor life… will be able to separate us from the love of God.",
        "season":     "ሁሉ ዘመን",
        "ref":        "ሮሜ 8:38-39",
        "reflection": "ፈጣሪ ፍቅሩ ምንም ሊለይ አይችልም — ዛሬ ፍቅሩን አምን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ምሕረቱ ዘለዓለም ነው።",
        "reading_en": "He himself bore our sins in his body on the tree, that we might die to sin and live to righteousness.",
        "season":     "ዐቢይ ጾም / ፋሲካ",
        "ref":        "1ጴጥሮስ 2:24",
        "reflection": "ኢየሱስ ኃጢያቴን ተሸከመ — ዛሬ ፍቅሩን አምስጋን።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "Blessed are the pure in heart, for they shall see God.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ማቴዎስ 5:8",
        "reflection": "ቅን ልቡ ፈጣሪን ያያዋል — ዛሬ ቅን ልብ ያዝ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ምሕረቱ ዘለዓለም ነው።",
        "reading_en": "Ask, and it will be given to you; seek, and you will find; knock, and it will be opened to you.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ማቴዎስ 7:7",
        "reflection": "ፈጣሪ ጠይቅ ፈልግ ንኩ — ዛሬ ጸልይ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "In the beginning was the Word, and the Word was with God, and the Word was God.",
        "season":     "ሁሉ ዘመን",
        "ref":        "ዮሐንስ 1:1",
        "reflection": "ቃሉ ፈጣሪ ነው — ዛሬ ቃሉን ሰምቶ ተቀበለ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ምሕረቱ ዘለዓለም ነው።",
        "reading_en": "This is my commandment, that you love one another as I have loved you.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ዮሐንስ 15:12",
        "reflection": "ፍቅር ፈጣሪ ትዕዛዝ ነው — ዛሬ እርስ በርሳችሁ ውደዱ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡን ፈቅዶ ቅዱሱ ቃሉ ሰጠ — ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ።",
        "reading_en": "Peace I leave with you; my peace I give to you.",
        "season":     "ዘወትር ዘመን",
        "ref":        "ዮሐንስ 14:27",
        "reflection": "ፈጣሪ ሰላሙን ሰጠ — ዛሬ ሰላሙን ተቀበለ።",
    },
    {
        "reading_am": "ፈጣሪ ሕዝቡ ቃሉን ሰምቶ ደስ ሆነ — ምሕረቱ ዘለዓለም ነው።",
        "reading_en": "Worthy is the Lamb who was slain, to receive power and wealth and wisdom and might.",
        "season":     "ፋሲካ ዘመን",
        "ref":        "ራዕይ 5:12",
        "reflection": "ኢየሱስ ዋጋ ያለው ዋጋ — ዛሬ ምስጋናህን ስጥ።",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# CATHOLIC  —  Prayers of the Saints (የቅዱሳን ጸሎት)
# ══════════════════════════════════════════════════════════════════════════════

CATHOLIC_SAINT_PRAYERS = [
    {
        "prayer_am": "ጌታ ሆይ — ፍቅርህ ምሕረትህ ሰፊ ነው። ለሕዝቤ ሁሉ ፍቅርህን ስጥ።",
        "prayer_en": "Lord, make me an instrument of your peace.",
        "saint":     "ቅዱስ ፍራንቸስኮስ ዴ አሲሲ",
        "feast":     "ጥቅምት 4",
        "reflection": "ሰላም ሰጪ ሆን — ዛሬ ሰላምን ዙሪያህ አሰራጭ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "O Jesus, I surrender myself to you, take care of everything.",
        "saint":     "ቅዱስ ፒዮ ዳ ፒዬትሬልቺና",
        "feast":     "መስከረም 23",
        "reflection": "ሁሉ ነገር ፈጣሪ ዘንድ ሰጥ — ዛሬ ፈጣሪ ይጠብቅህ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ልቤ ሁሉ ፍቅርህን ይፈልጋዋል። ምሕረትህን ስጠኝ።",
        "prayer_en": "You have made us for yourself, O Lord, and our heart is restless until it rests in you.",
        "saint":     "ቅዱስ አውጉስቲን",
        "feast":     "ነሐሴ 28",
        "reflection": "ልቡ ፈጣሪ ዘንድ ሲቀርብ ዕረፍቱ ያገኛዋል — ዛሬ ፈጣሪ ቅረብ።",
    },
    {
        "prayer_am": "ቅድስት ማርያም ሆይ — ልጅህ ፍቅሩ ሞልቷዋል። ዛሬ ደስ ሁን።",
        "prayer_en": "Hail Mary, full of grace. The Lord is with thee.",
        "saint":     "ቅድስት ድንግል ማርያም",
        "feast":     "ነሐሴ 15",
        "reflection": "ማርያም ፍቅሩ ሞልቷዋል — ዛሬ ፍቅሩን አምስጋን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ዛሬ ምሕረትህን ያዝ።",
        "prayer_en": "Jesus, I trust in you.",
        "saint":     "ቅድስት ፋውስቲና ኮዋልስካ",
        "feast":     "ጥቅምት 5",
        "reflection": "ፈጣሪን ምሕረት ታምን — ዛሬ ዕቅፍ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ሕዝቤ ሁሉ ፍቅርህን ያዝ።",
        "prayer_en": "Without the love of God, all is nothing.",
        "saint":     "ቅዱስ ፊልጶስ ኔሪ",
        "feast":     "ሜይ 26",
        "reflection": "ፍቅር ሁሉ ፈጣሪ ዘንድ ነው — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ልቤ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Do small things with great love.",
        "saint":     "ቅድስት ቴሬዛ ዘካልኩታ",
        "feast":     "መስከረም 5",
        "reflection": "ፍቅር ትንሽ ነገርን ታላቅ ያደርጋዋል — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Grant me, O Lord, to know what I ought to know, to love what I ought to love.",
        "saint":     "ቅዱስ ቶማስ ዘ ኬምፒስ",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ዘንድ ዕውቀቱን ፍቅሩን ሰጥ — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ምሕረትህ ሰፊ ነው። ዛሬ ምሕረትህን ጠይቃለሁ።",
        "prayer_en": "O God, you are my God; earnestly I seek you; my soul thirsts for you.",
        "saint":     "ቅዱስ ዳዊት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪን ሲፈልጉ ፈጣሪ ቅርብ ይሆናዋል — ዛሬ ፈጣሪ ፈልግ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "God, grant me the serenity to accept the things I cannot change.",
        "saint":     "ቅዱስ ሬኒሆልድ ኔቡር (ዘመናዊ ጸሎት)",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ሰላም ፈጣሪ ዘንድ ሲቀርቡ ያገኛዋቸዋል — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Lord, I am not worthy that you should enter under my roof, but only say the word and my soul shall be healed.",
        "saint":     "ካቶሊካዊ ሊቱርጂ",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ምሕረት ሲጠይቁ ፈጣሪ ሁሌ ሊሰጣዋቸዋል — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ልቤ ፍቅርህን ፈልጎ ምሕረትህን ያዝ። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Act of contrition: O my God, I am heartily sorry for having offended you.",
        "saint":     "ካቶሊካዊ ወግ",
        "feast":     "ዐቢይ ጾም",
        "reflection": "ንስሐ ፈጣሪ ዘንድ ምሕረትን ያስከትሎዋል — ዛሬ ናዘዝ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Lord Jesus Christ, Son of God, have mercy on me, a sinner.",
        "saint":     "ቅዱሳን አባቶች (Jesus Prayer)",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ኢየሱስ ምሕረቱ ሁሌ ሰፊ ነው — ዛሬ ምሕረት ጠይቅ።",
    },
    {
        "prayer_am": "ቅድስት ማርያም ሆይ — ፍቅርህ ሕዝቤ ሁሉ ያድናቸዋቸዋል። ዛሬ ምሕረቱን ስጥ።",
        "prayer_en": "Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death.",
        "saint":     "ቅድስት ድንግል ማርያም",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ማርያም ጸሎቱ ለሁሉ — ዛሬ ምሕረቱን ስጥ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "O Divine Providence, I abandon myself into your hands.",
        "saint":     "ቅዱስ ዳን ቦስኮ ዘቱሪን",
        "feast":     "ጥር 31",
        "reflection": "ፈጣሪ እጅ ሁሉ ነገር ሰጥ — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ምሕረትህ ሰፊ ነው። ዛሬ ምሕረትህን ጠይቃለሁ።",
        "prayer_en": "Thank you Lord for this day, for life, for love, for everything.",
        "saint":     "ዘመናዊ ካቶሊካዊ ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "አምስጋና ጸሎቱ ዋናው ነው — ዛሬ አምስጋን ጸልይ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "I live now not with my own life but with the life of Christ who lives in me.",
        "saint":     "ቅዱስ ጳዉሎስ (ጋሊቅያ 2:20)",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ክርስቶስ ሕይወቴ ነው — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "May the Lord bless you and keep you; may the Lord make his face to shine upon you.",
        "saint":     "ካቶሊካዊ ቡሩካን",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ፈጣሪ ቡሩካን — ዛሬ ቡሩካኑን ተቀበለ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Come, Holy Spirit, fill the hearts of your faithful and kindle in them the fire of your love.",
        "saint":     "ፒንቴቆስቴ ጸሎት (ካቶሊካዊ)",
        "feast":     "ፒንቴቆስቴ",
        "reflection": "መንፈስ ቅዱስ ሕዝቤ ልቡ ያድሳዋቸዋቸዋል — ዛሬ ጸልይ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Soul of Christ, sanctify me; Body of Christ, save me.",
        "saint":     "Anima Christi — ካቶሊካዊ ወጉ",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ኢየሱስ ነፍሴን ቀድሰው — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ምሕረትህ ሰፊ ነው። ዛሬ ምሕረትህን ጠይቃለሁ።",
        "prayer_en": "Lord, help me to see you in the eyes of all those I meet today.",
        "saint":     "ዘመናዊ ቅዱሳን ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ሁሉ ሰው ፊት — ዛሬ ፍቅርን ሰጥ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Nothing is too hard for you, Lord; with you, all things are possible.",
        "saint":     "ዘወትር ካቶሊካዊ ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ዘንድ ምንም አይሳነውም — ዛሬ ፈጣሪ ሁን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "We adore you, O Christ, and we bless you, because by your holy cross you have redeemed the world.",
        "saint":     "Via Crucis — ካቶሊካዊ ወጉ",
        "feast":     "ዐቢይ ጾም",
        "reflection": "ኢየሱስ መስቀሉ ዓለምን አዳነ — ዛሬ ምሕረቱን አምስጋን።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Guard me from sin this day; let me never think an evil thought, never speak an evil word.",
        "saint":     "ካቶሊካዊ ጠዋት ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ዛሬ ይጠብቀን — ዛሬ ጸልይ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Into your hands, Lord, I commend my spirit.",
        "saint":     "ካቶሊካዊ ምሽት ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ዘንድ ሁሉ ሰጥ — ዛሬ ፈጣሪ ይጠብቅህ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ምሕረትህ ሰፊ ነው። ዛሬ ምሕረትህን ጠይቃለሁ።",
        "prayer_en": "I believe in God, the Father almighty, creator of heaven and earth.",
        "saint":     "ሃይማኖት ቃል (Apostles' Creed)",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ሃይማኖት ፈጣሪ ዘንድ ቅርብ ያደርጋዋል — ዛሬ ሃይማኖቱን ያዝ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Our Father, who art in heaven, hallowed be thy name.",
        "saint":     "ጌታ ጸሎት (The Lord's Prayer)",
        "feast":     "ሁሉ ዘመን",
        "reflection": "ጌታ ጸሎቱ ሁሉ ጸሎቶቹ ምንጭ ነው — ዛሬ ጸልይ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ምሕረትህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "Mary, conceived without sin, pray for us who have recourse to thee.",
        "saint":     "Miraculous Medal ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ማርያም ጸሎቱ ሕዝቡ ሁሉ ምሕረትን ያስከትሎዋቸዋል — ዛሬ ጸልይ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ፍቅርህ ሞልቷዋል። ዛሬ ምሕረትህን ስጠኝ።",
        "prayer_en": "Lord, make me a channel of your peace, where there is hatred, let me sow love.",
        "saint":     "ቅዱስ ፍራንቸስኮስ ሰላም ጸሎት",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ሰላም ሰጪ ሆን — ዛሬ ፍቅርን ዙሪያህ አሰራጭ።",
    },
    {
        "prayer_am": "ፈጣሪ ሆይ — ሕዝቤ ሁሉ ፍቅርህን ፈልጎ ምሕረትህን ያዝ።",
        "prayer_en": "May the Lord keep you safe this night, and may his angels watch over you.",
        "saint":     "ካቶሊካዊ ምሽት ቡሩካን",
        "feast":     "ዘወትር ዘመን",
        "reflection": "ፈጣሪ ሌሊቱ ይጠብቀን — ዛሬ ፈጣሪ ሰጥ።",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# Helper functions
# ══════════════════════════════════════════════════════════════════════════════

def _day_idx() -> int:
    return (datetime.date.today().day - 1) % 30


def get_today_protestant_verse() -> dict:
    return PROTESTANT_BIBLE_VERSES[_day_idx()]


def get_today_protestant_song() -> dict:
    return PROTESTANT_SONGS[_day_idx()]


def get_today_catholic_liturgy() -> dict:
    return CATHOLIC_LITURGY[_day_idx()]


def get_today_catholic_prayer() -> dict:
    return CATHOLIC_SAINT_PRAYERS[_day_idx()]


# ══════════════════════════════════════════════════════════════════════════════
# BIBLE READING PLAN  —  365-day plan through the entire Bible
# Each day gets 2-3 OT chapters + 0-1 NT chapters (generated algorithmically)
# ══════════════════════════════════════════════════════════════════════════════

_BIBLE_BOOKS_OT = [
    ("ዘፍጥረት",   "Genesis",         50),
    ("ዘጸአት",    "Exodus",          40),
    ("ዘሌዋዊያን",  "Leviticus",       27),
    ("ዘኁልቁ",    "Numbers",         36),
    ("ዘዳግም",    "Deuteronomy",     34),
    ("ኢያሱ",     "Joshua",          24),
    ("መሳፍንት",   "Judges",          21),
    ("ሩት",      "Ruth",             4),
    ("1ሳሙኤል",  "1 Samuel",         31),
    ("2ሳሙኤል",  "2 Samuel",         24),
    ("1ነገሥት",  "1 Kings",          22),
    ("2ነገሥት",  "2 Kings",          25),
    ("1ዜና",    "1 Chronicles",     29),
    ("2ዜና",    "2 Chronicles",     36),
    ("ዕዝራ",    "Ezra",             10),
    ("ነህምያ",   "Nehemiah",         13),
    ("አስቴር",   "Esther",           10),
    ("ኢዮብ",    "Job",              42),
    ("መዝሙር",   "Psalms",          150),
    ("ምሳሌ",    "Proverbs",         31),
    ("መክብብ",   "Ecclesiastes",     12),
    ("መኃልይ",   "Song of Songs",     8),
    ("ኢሳይያስ",  "Isaiah",           66),
    ("ኤርምያስ",  "Jeremiah",         52),
    ("ሰቆቃወ",   "Lamentations",      5),
    ("ሕዝቅኤል",  "Ezekiel",          48),
    ("ዳንኤል",   "Daniel",           12),
    ("ሆሴዕ",    "Hosea",            14),
    ("ዮኤል",    "Joel",              3),
    ("አሞጽ",    "Amos",              9),
    ("ዓብድዩ",   "Obadiah",           1),
    ("ዮናስ",    "Jonah",             4),
    ("ሚክያስ",   "Micah",             7),
    ("ናሆም",    "Nahum",             3),
    ("ዕንባቆም",  "Habakkuk",          3),
    ("ሶፎንያስ",  "Zephaniah",         3),
    ("ሐጌ",     "Haggai",            2),
    ("ዘካርያስ",  "Zechariah",        14),
    ("ሚልክያስ",  "Malachi",           4),
]

_BIBLE_BOOKS_NT = [
    ("ማቴዎስ",         "Matthew",          28),
    ("ማርቆስ",         "Mark",             16),
    ("ሉቃስ",          "Luke",             24),
    ("ዮሐንስ",         "John",             21),
    ("የሐዋርያት",       "Acts",             28),
    ("ሮሜ",           "Romans",           16),
    ("1ቆሮንቶስ",       "1 Corinthians",    16),
    ("2ቆሮንቶስ",       "2 Corinthians",    13),
    ("ገላትያ",         "Galatians",         6),
    ("ኤፌሶን",         "Ephesians",         6),
    ("ፊልጵስዩስ",       "Philippians",       4),
    ("ቆላስይስ",        "Colossians",        4),
    ("1ተሰሎ",         "1 Thessalonians",   5),
    ("2ተሰሎ",         "2 Thessalonians",   3),
    ("1ጢሞቴዎስ",       "1 Timothy",         6),
    ("2ጢሞቴዎስ",       "2 Timothy",         4),
    ("ቲቶ",           "Titus",             3),
    ("ፊልሞና",         "Philemon",          1),
    ("ዕብራዊያን",       "Hebrews",          13),
    ("ያዕቆብ",         "James",             5),
    ("1ጴጥሮስ",        "1 Peter",           5),
    ("2ጴጥሮስ",        "2 Peter",           3),
    ("1ዮሐንስ",        "1 John",            5),
    ("2ዮሐንስ",        "2 John",            1),
    ("3ዮሐንስ",        "3 John",            1),
    ("ይሁዳ",          "Jude",              1),
    ("ራዕይ",          "Revelation",       22),
]


def _build_chapter_list(books):
    """Return a flat list of (am, en, chapter_num) for all books."""
    out = []
    for am, en, cnt in books:
        for ch in range(1, cnt + 1):
            out.append((am, en, ch))
    return out


_OT_CHAPTERS = _build_chapter_list(_BIBLE_BOOKS_OT)  # 929
_NT_CHAPTERS = _build_chapter_list(_BIBLE_BOOKS_NT)  # 260
_OT_TOTAL = len(_OT_CHAPTERS)  # 929
_NT_TOTAL = len(_NT_CHAPTERS)  # 260


def _fmt_reading(chapters):
    """Given a list of (am, en, ch) tuples, produce grouped reading dicts."""
    if not chapters:
        return []
    groups = {}
    order = []
    for am, en, ch in chapters:
        if en not in groups:
            groups[en] = {"am": am, "en": en, "chs": []}
            order.append(en)
        groups[en]["chs"].append(ch)
    result = []
    for key in order:
        g = groups[key]
        chs = g["chs"]
        if len(chs) == 1:
            result.append({
                "am": g["am"], "en": g["en"],
                "ref_am": f"{g['am']} {chs[0]}",
                "ref_en": f"{g['en']} {chs[0]}",
            })
        else:
            result.append({
                "am": g["am"], "en": g["en"],
                "ref_am": f"{g['am']} {chs[0]}–{chs[-1]}",
                "ref_en": f"{g['en']} {chs[0]}–{chs[-1]}",
            })
    return result


def get_reading_plan_day(day_num: int) -> dict:
    """
    Return the Bible reading for a given day (1–365).
    Distributes OT (929 ch) and NT (260 ch) evenly across 365 days.
    """
    day_num = max(1, min(365, day_num))

    ot_start = round((day_num - 1) * _OT_TOTAL / 365)
    ot_end   = round(day_num       * _OT_TOTAL / 365)
    nt_start = round((day_num - 1) * _NT_TOTAL / 365)
    nt_end   = round(day_num       * _NT_TOTAL / 365)

    ot_reading = _fmt_reading(_OT_CHAPTERS[ot_start:ot_end])
    nt_reading = _fmt_reading(_NT_CHAPTERS[nt_start:nt_end])

    total_chapters = (ot_end - ot_start) + (nt_end - nt_start)

    return {
        "day":            day_num,
        "ot":             ot_reading,
        "nt":             nt_reading,
        "total_chapters": total_chapters,
    }


def get_today_reading_plan() -> dict:
    """Return the reading plan entry for today's day-of-year."""
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday  # 1..366
    return get_reading_plan_day(min(day_of_year, 365))
