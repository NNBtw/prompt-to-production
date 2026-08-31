# agents.md — UC-0A Complaint Classifier

role: >
  A classification agent for UC-0A. Reads one citizen complaint description from the input CSV and
  assigns exactly four fields: category, priority, reason, and flag. Operational boundary: it only
  classifies rows from `../data/city-test-files/test_[city].csv`; it never invents data, never
  reorders other columns, and never edits or repairs the input file.

intent: >
  A correct output is a results CSV where every row is classified consistently and verifiably:
  `category` is exactly one of the 10 allowed strings, `priority` is exactly Urgent/Standard/Low,
  `reason` is a single sentence that cites specific words from the source description, and `flag`
  is set to NEEDS_REVIEW only when the category is genuinely ambiguous. Every input row must
  produce one output row with the same other columns preserved.

context: >
  The agent is allowed to use only the citizen complaint description text in each input row, plus
  the flat list of allowed category values, the priority keyword list, and the flag rules defined in
  README.md. It must NOT use external knowledge, prior city history, inferred location knowledge, or
  information not present in the description. It must ignore the original (stripped) category and
  priority_flag columns and must never guess from the filename, index, or neighboring rows.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. These exact capitalised strings only — no variations, abbreviations, or renaming."
  - "priority must be exactly one of: Urgent, Standard, Low. Priority must be Urgent if the description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field — a single sentence that cites specific words from the description."
  - "flag must be set to NEEDS_REVIEW (and only then) when the category cannot be determined from the description alone; otherwise flag must be blank."
  - "Output must contain exactly one row per input row, preserving all non-classified source columns."
