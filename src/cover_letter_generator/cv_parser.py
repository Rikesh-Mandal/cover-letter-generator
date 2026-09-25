import pymupdf

def parsePdf(path):
    if not path.endswith(".pdf"):
        return "Please upload a .pdf file"
    doc = pymupdf.open(path)    # open a file as a doc object
    pages = []  # empty list to append pages in the file
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)

print(parsePdf("D:/C.V/Rikesh_Mandal_CV.pdf"))