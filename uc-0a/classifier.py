"""
UC-0A — Complaint Classifier
Reads a citizen complaint CSV, classifies each row into category, priority,
reason, and flag, and writes a results CSV preserving all source columns.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "waterlogged", "water logged"]),
    ("Streetlight", ["streetlight", "street light", "light"]),
    ("Waste", ["waste", "garbage", "trash", "litter", "dump"]),
    ("Noise", ["noise", "loud", "music", "honk"]),
    ("Road Damage", ["road damage", "road surface", "cracked road", "broken road"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "heritage site"]),
    ("Heat Hazard", ["heat", "temperature"]),
    ("Drain Blockage", ["drain", "sewer", "blockage"]),
]


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    text = description.lower()

    flag = ""
    matches = [name for name, kws in CATEGORY_KEYWORDS if any(kw in text for kw in kws)]
    if matches:
        category = matches[0]
    else:
        category = "Other"
        if description:
            flag = "NEEDS_REVIEW"

    if any(kw in text for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard" if description else "Low"

    if description:
        keyword_hits = [
            k for _, kws in CATEGORY_KEYWORDS for k in kws if k in text
        ]
        evidence = " or ".join(f'"{k}"' for k in keyword_hits)
        if not evidence:
            evidence = "no category keyword is present"
        reason = (
            f'Classified as {category} because the description mentions {evidence}; '
            f'priority {priority} because the description '
            f'{"contains" if priority == "Urgent" else "does not contain"} '
            f'{"a severity keyword" if priority == "Urgent" else "any severity keyword"}.'
        )
    else:
        reason = "No description provided."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    new_fields = ["category", "priority", "reason", "flag"]
    out_fieldnames = fieldnames + new_fields

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            classified = classify_complaint(row)
            out_row = dict(row)
            out_row.update(classified)
            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
