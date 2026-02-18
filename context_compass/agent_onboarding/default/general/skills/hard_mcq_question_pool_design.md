# hard_mcq_question_pool_design

Purpose
- Define quality requirements for hard MCQ pool generation.

Question design rules
1) Exactly four options per question.
2) Exactly one true statement.
3) Three deterministic lies that are close to truth.
4) No obvious distractors.
5) Source anchor required for each question.

Difficulty rules
- Lies should differ by narrow policy semantics:
  - modality flips (`must` vs `must not`)
  - sequence flips (`before` vs `after`)
  - scope shifts (`all` vs `some`, `only` vs broad)
- Keep wording highly similar to avoid easy elimination.

Pool sizing rules
- Default target is 10x current question inventory.
- Ensure per-doc depth supports `1 question per 100 LOC` exam quotas.

Separation rules
- Public pool stores prompts/options only.
- Truth mappings are written to sealed storage.
