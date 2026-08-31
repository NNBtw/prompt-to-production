# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: One complaint row — the description text plus any non-classified source columns, as a CSV row/dict.
    output: The same row augmented with four fields: category (one of 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing source words), flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or no category matches from the description alone, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the classified results CSV.
    input: A CSV file path to `../data/city-test-files/test_[city].csv` (15 rows, category and priority_flag columns stripped) and an output file path.
    output: A CSV file where every row has the source columns preserved plus valid category, priority, reason, and flag fields.
    error_handling: If a row cannot be classified confidently, mark it Other + NEEDS_REVIEW rather than failing; if the whole file is unreadable, stop and report the error without writing a partial output.
