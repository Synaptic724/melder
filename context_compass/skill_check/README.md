# skill_check (Hard MCQ Blind-Submission System)

Purpose
- Run score-grounded post-compaction checks with:
  - hard MCQ questions only,
  - blind JSON submission,
  - sealed answer-key grading,
  - deterministic rank output.

Core intent (non-negotiable)
1) Questions are MCQ only.
2) Each question has one truth + three difficult deterministic lies.
3) Exam quota is `1 question per 100 LOC` for each required doc.
4) Answer keys are sealed and not exposed in public exam artifacts.
5) Grading is script-driven from sealed keys and submitted JSON answers.

Directory structure
- `context_compass/skill_check/question_pool/`
  - public question pool with no explicit answer keys
- `context_compass/skill_check/.sealed/`
  - private key material used only by generator/grader
- `context_compass/skill_check/tests/`
  - generated exam markdowns for blind reading
- `context_compass/skill_check/submissions/`
  - answer JSON files
- `context_compass/skill_check/historical_test_results/`
  - grader outputs and cycle score reports

Primary commands
1) Build/refresh pool (10x size target):
   - `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`
2) Generate blinded exam:
   - `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <cycle_id>`
3) Submit JSON answers, then grade:
   - `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <cycle_id> --submission <path>`

Canonical policy
- `context_compass/skill_check/skill_check_policy.md`
