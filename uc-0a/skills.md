# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row from its description alone into category + priority + reason + flag.
    input: One complaint row as a dict containing complaint_id and description text.
    output: A dict with exactly the keys complaint_id, category, priority, reason, flag, where category is one of the ten allowed strings, priority is Urgent/Standard/Low, reason is one sentence citing words from the description, and flag is NEEDS_REVIEW only when the category is genuinely ambiguous.
    error_handling: If the description is missing or empty, or the category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW with a reason explaining the ambiguity.

  - name: batch_classify
    description: Reads the input city test CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to the input CSV (rows with complaint_id and description; category and priority_flag columns are stripped).
    output: A CSV with the header complaint_id, category, priority, reason, flag and one classified row per input row.
    error_handling: Flags nulls or malformed rows instead of crashing; never drops rows silently; always produces an output CSV even if some rows fail.
