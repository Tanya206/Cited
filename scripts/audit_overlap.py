import glob
import json

import pymupdf


def overlap_fraction(block, bbox) -> float:
    """Share of the text block that lies inside the table box."""
    ax0, ay0, ax1, ay1 = block[:4]
    bx0, by0, bx1, by1 = bbox
    width = min(ax1, bx1) - max(ax0, bx0)
    height = min(ay1, by1) - max(ay0, by0)
    if width <= 0 or height <= 0:
        return 0.0
    return (width * height) / max((ax1 - ax0) * (ay1 - ay0), 1e-6)


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
                fraction = overlap_fraction(block, table["bbox"])
                if 0 < fraction < 0.8:     # removed, but mostly OUTSIDE the table
                    risky += 1
                    text = " ".join(block[4].split())[:110]
                    print(f"{doc['doc_id'][:30]:<30} p{page_data['page_number']:<3} "
                          f"{fraction:.2f}  {text}")
print(f"\nPartially overlapping blocks currently deleted: {risky}")