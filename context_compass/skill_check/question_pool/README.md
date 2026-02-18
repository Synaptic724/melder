# question_pool

Purpose
- Store the public hard-MCQ question pool used to generate blinded exams.
- Keep question prompts/options visible while keeping answer keys sealed.

Files
- `hard_mcq_pool.jsonl`
  - public question rows (no correct-answer field)
- `hard_mcq_pool_meta.json`
  - generation metadata and pool sizing stats

Build command
- `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`

Rules
- The pool must contain only MCQ questions.
- Every row must have exactly 4 options:
  - 1 truth
  - 3 difficult deterministic lies
- Public pool rows must not include explicit answer keys.
