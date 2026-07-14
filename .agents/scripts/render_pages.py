import fitz

doc = fitz.open("attached_assets/am_Hisn_Almuslim_1784002293780.pdf")
for i in [0, 1, 2, 3, 5, 10, 50, 100, 150, 200, 231]:
    page = doc[i]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    pix.save(f".agents/outputs/page_{i+1}.png")
print("done")
