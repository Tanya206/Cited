# scripts/inspect_table.py — quick manual check of any flagged table
import json
import os
import sys

def inspect(doc_id, page_number, table_index):
    path = f"data/extracted_structured/{doc_id}.json"
    doc = json.load(open(path, encoding="utf-8"))
    page = next(p for p in doc["pages"] if p["page_number"] == page_number)
    table = next(t for t in page["tables"] if t["extraction_index"] == table_index)

    print(f"is_suspicious: {table['is_suspicious']}")
    print(f"empty_cell_ratio: {table['empty_cell_ratio']}")
    print(f"row_repair_applied: {table['row_repair_applied']}")
    print(f"\nMarkdown:\n{table['markdown']}")
    os.startfile(table["source_image_path"])

if __name__ == "__main__":
    inspect(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))