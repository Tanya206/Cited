"""List text blocks that partly overlap a usable table box.

Run from the repo root: python -m scripts.audit_overlap
"""
import glob
import json

import pymupdf

from app.ingestion.extract import TABLE_BLOCK_INSIDE_RATIO, overlap_fraction


risky = 0
for path in sorted(glob.glob("data/extracted_structured/*.json")):
    doc = json.load(open(path, encoding="utf-8"))
    pdf = pymupdf.open(doc["source_pdf"].replace("\\", "/"))
    for page_data in doc["pages"]:
        usable = [t for t in page_data["tables"] if not t["is_suspicious"]]
        if not usable:
            continue
        blocks = pdf[page_data["page_number"] - 1].get_text("blocks")
        for table in usable:
            for block in blocks:
                if block[6] != 0:          # skip image blocks
                    continue
                fraction = overlap_fraction(block[:4], table["bbox"])
                if 0 < fraction < TABLE_BLOCK_INSIDE_RATIO:  # touches the table but is kept in the body
                    risky += 1
                    text = " ".join(block[4].split())[:110]
                    print(f"{doc['doc_id'][:30]:<30} p{page_data['page_number']:<3} "
                          f"{fraction:.2f}  {text}")
print(f"\nPartially overlapping blocks (kept in the body since the 2026-11-12 fix): {risky}")