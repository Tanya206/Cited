import sys
from app.ingestion.extract import extract_document

doc_id = sys.argv[1]
result = extract_document(f"data/raw_papers/{doc_id}.pdf", doc_id, "data/crops")
for page in result["pages"]:
    for table in page["tables"]:
        print(f"p{page['page_number']} table {table['extraction_index']} "
              f"suspicious={table['is_suspicious']} empty={table['empty_cell_ratio']}")
        print(table["markdown"][:500], "\n")
    for caption in page["captions"]:
        print(f"p{page['page_number']} caption: {caption['refers_to']} {caption['number']}")