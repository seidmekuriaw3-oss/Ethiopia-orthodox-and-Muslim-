import fitz, os

doc = fitz.open("attached_assets/am_Hisn_Almuslim_1784002293780.pdf")
outdir = ".agents/outputs/pages"
os.makedirs(outdir, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    pix.save(f"{outdir}/p{i+1:03d}.png")
print("rendered", doc.page_count, "pages")
