# .sealed

Purpose
- Hold private grading artifacts that must not be used during blind answering.

Contents
- `pool_truth_keys.jsonl`
  - truth-option mapping for public pool question IDs
- `exams/cycle_<id>_answer_key.json`
  - per-cycle correct letters after exam-time option shuffling

Policy
- Do not read `.sealed` artifacts before blind submission.
- Grading scripts may read `.sealed` artifacts.
- Private key files are ignored by git and should remain local runtime data.
