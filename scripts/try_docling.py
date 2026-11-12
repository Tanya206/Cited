import sys
from docling.document_converter import DocumentConverter

pdf = sys.argv[1]
result = DocumentConverter().convert(pdf)
doc = result.document

for table in doc.tables:
    page_no = table.prov[0].page_no
    print(f"\n=== page {page_no} ===")
    try:
        print(table.export_to_markdown(doc=doc))
    except TypeError:            # older versions take no argument
        print(table.export_to_markdown())