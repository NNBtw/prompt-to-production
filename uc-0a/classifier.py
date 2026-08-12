"""
UC-0A — Complaint Classifier
One complaint row in → category + priority + reason + flag out.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlog", "waterlogged", "rainwater", "rain"],
    "Streetlight": ["streetlight", "street light", "lights out", "lamp", "unlit", "darkness"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "bin", "litter", "dead animal", "carcass"],
    "Noise": ["noise", "music", "loud", "honk", "drilling", "idling", "amplifier", "band"],
    "Road Damage": ["pavement", "paving", "footpath", "manhole", "cracked", "cracking", "sinking", "subsided", "subsidence", "collapsed", "crater", "tiles", "buckled", "cobblestone"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "heatwave", "temperature", "sun", "melting", "bubbling"],
    "Drain Blockage": ["drain", "drainage", "draining", "sewage", "choked drain"],
}

URGENT_PATTERN = re.compile(
    r"\b(injury|injuries|injured|child|children|school|hospital|hospitalised|hospitalized|ambulance|fire|hazard|fell|collapse|collapsed|collapsing)\b",
    re.IGNORECASE,
)
LOW_PATTERN = re.compile(r"\b(music|noise|loud|band)\b", re.IGNORECASE)
STANDARD_PATTERN = re.compile(
    r"\b(dark|darkness|safety|smell|blocked|standing|water|dead|health|risk|stranded|danger)\b",
    re.IGNORECASE,
)

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def assign_priority(description: str) -> str:
    if URGENT_PATTERN.search(description):
        return "Urgent"
    if LOW_PATTERN.search(description) and not STANDARD_PATTERN.search(description):
        return "Low"
    return "Standard"


KEYWORD_PATTERNS = {
    category: [
        (kw, re.compile(r"\b" + re.escape(kw) + r"s?\b", re.IGNORECASE))
        for kw in keywords
    ]
    for category, keywords in CATEGORY_KEYWORDS.items()
}


CATEGORY_OVERRIDES = {"Flooding": "Pothole"}


def match_categories(description: str) -> dict:
    matched = {}
    for category, entries in KEYWORD_PATTERNS.items():
        found = [kw for kw, pattern in entries if pattern.search(description)]
        if found:
            matched[category] = found
    for secondary, primary in CATEGORY_OVERRIDES.items():
        if primary in matched and secondary in matched:
            del matched[secondary]
    return matched


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty, so the complaint cannot be classified from the description alone.",
            "flag": "NEEDS_REVIEW",
        }

    priority = assign_priority(description)
    matched = match_categories(description)

    if not matched:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"No category keyword such as \"pothole\", \"flood\", or \"garbage\" appears in the description \"{description[:80]}\".",
            "flag": "NEEDS_REVIEW",
        }

    if len(matched) > 1:
        categories = " and ".join(matched.keys())
        terms = ", ".join(f'"{t}"' for kw in matched.values() for t in kw)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Description mentions both {terms}, so the category is genuinely ambiguous between {categories}.",
            "flag": "NEEDS_REVIEW",
        }

    category, keywords = next(iter(matched.items()))
    terms = ", ".join(f'"{t}"' for t in keywords)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": f"Description mentions {terms}, which indicates {category}; assigned {priority} priority.",
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls/malformed rows instead of crashing; always writes an output.
    """
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception:
                rows.append({
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be parsed; needs review.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
