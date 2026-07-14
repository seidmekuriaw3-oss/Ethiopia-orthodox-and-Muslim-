import fitz
import sys

doc = fitz.open("attached_assets/am_Hisn_Almuslim_1784002293780.pdf")
print("Page count:", doc.page_count)

full_text = []
for i, page in enumerate(doc):
    text = page.get_text("text")
    full_text.append(f"\n=== PAGE {i+1} ===\n" + text)

with open(".agents/outputs/hisn_full_text.txt", "w", encoding="utf-8") as f:
    f.write("".join(full_text))

print("done, total chars:", sum(len(t) for t in full_text))
