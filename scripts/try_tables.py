import pymupdf

PDF = "data/raw_papers/2007.09990v1.pdf"
doc = pymupdf.open(PDF)

# page index 6 = page 7 (Tables I-III), index 10 = page 11 (Table IV), index 1 = page 2 (no tables)
for index in (6, 10, 1):
    page = doc[index]
    default = page.find_tables()
    text = page.find_tables(strategy="text")
    print(f"page {index + 1}: default={len(default.tables)}  text={len(text.tables)}")

# Look at what the text strategy produced for page 7
for table in doc[6].find_tables(strategy="text").tables:
    rows = table.extract()
    print("\n--- table", len(rows), "rows x", len(rows[0]), "cols ---")
    for row in rows[:4]:
        print(row)

print("\n=== hybrid ===")
for index in (6, 10, 1):
    page = doc[index]
    found = page.find_tables(vertical_strategy="text", horizontal_strategy="lines")
    print(f"page {index + 1}: hybrid={len(found.tables)}")
    for table in found.tables:
        rows = table.extract()
        print("  ", len(rows), "rows x", len(rows[0]), "cols; first row:", rows[0])