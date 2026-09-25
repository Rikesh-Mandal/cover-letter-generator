import pymupdf

doc = pymupdf.open("D:/C.V/Rikesh_Mandal_CV.pdf")


def parsePdf(path):
    doc = pymupdf.open(path)    # open a document
    out = open("output.txt", "wb")  # create a text output
    for page in doc:
        text = page.get_text().encode("utf-8")  # get plain text (utf-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimeter (from feed 0x0c)
    out.close()
    doc.close()

parsePdf("D:/C.V/Rikesh_Mandal_CV.pdf")
