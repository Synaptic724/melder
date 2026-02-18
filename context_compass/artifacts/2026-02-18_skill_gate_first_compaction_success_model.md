# Skill-Gate-First Compaction Success Model

Created: 2026-02-18T16:53:27Z
Owner: codex
Linked Epic: `tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md`

## Why This Exists

This artifact captures the exact operating model agreed in discussion:

1. Post-compaction success must be measured from scored test answers.
2. The loop must reduce read volume over cycles as retention stabilizes.
3. Relearning must target failed documents, not full baseline rereads.

This is the planning source for upcoming discovery and implementation tickets.

## Agreed Outcome

The system should exit compaction and run a deterministic measurement loop that:

1. Reads only the minimum docs needed to execute the skill gate.
2. Takes tests blind.
3. Grades answers against canonical answer keys.
4. Records cycle scores and misses.
5. Re-onboards only weak/failed docs.
6. Regenerates a fresh next-cycle suite.
7. Shrinks test volume over time while preserving P0 sentinels.

## Terms (Operational Definitions)

`skill_gate_onboard`
- Minimal readset needed to run the measurement process safely and honestly.
- Excludes full role baseline rereads before testing.

`true fidelity` (as requested)
- Empirical agreement with reality measured by blind test answers vs answer keys.
- Not a manual claim-vs-doc attestation.

`knowledge_test row`
- Question-level scored evidence (`agent_answer` vs `correct_answer_ref`).

`targeted relearn`
- Mandatory reread set generated from failed/weak docs in current cycle.

`adaptive shrink`
- Automatic question-count reduction for stable docs across cycles.

## Target Cycle Contract

### Phase 0: Compaction Exit
- Enter measurement mode.
- Do not do full role onboarding first.

### Phase 1: Skill-Gate Onboarding (Minimum)
- Read only:
  - active manifest
  - active cycle tests
  - scoring/rubric/anti-cheat mechanics
  - board schema needed to write scored rows
- Do not read answer keys or under-test skill docs yet.

### Phase 2: Blind Test Submission
- Answer all required test questions from `skill_check/tests/**`.
- Submit full answer payload.
- Declare `ANSWERS_UNREAD: true`.

### Phase 3: Grading
- Read answer keys after submission only.
- Score per question and per doc.
- Record:
  - `knowledge_test` rows
  - `knowledge_score`
  - `knowledge_pass_rate`
  - `p0_miss_count`
  - `critical_p0_miss_count`
  - cycle rank/global score

### Phase 4: Targeted Relearn
- Build failed/weak doc set from misses.
- Reread only failed/weak docs plus required P0 dependencies.
- Record relearn completion and remaining weak areas.

### Phase 5: Fresh Cycle Reset
- Generate new test/answer cycle.
- Remove stale cycle artifacts.
- Keep one active cycle only.

### Phase 6: Adaptive Shrink
- Shrink only stable docs by streak.
- Never remove permanent P0 sentinels.
- Failed docs stay dense or increase.

## Success Criteria

1. A cycle without graded answers is `incomplete`, not pass.
2. Score comes from graded test outcomes, not attestation prose.
3. Read volume and test volume trend downward over stable cycles.
4. Failed-doc rereads are explicit and auditable each cycle.

## Data Model Changes Required (Discovery Scope)

1. Differential board semantics:
  - make scored `knowledge_test` evidence primary for cycle success
  - treat manual parity notes as secondary diagnostics only

2. Cycle summary contract:
  - pass/fail driven by graded metrics
  - `Not run` blocks completion status

3. Onboarding contract:
  - add explicit `skill_gate_onboard` stage before grading
  - prohibit full skill reread before blind testing

4. Suite lifecycle:
  - enforce single active cycle
  - maintain streak-driven shrink and failed-doc reinforcement

## Open Design Questions For Discovery

1. Naming: keep `fidelity_diff` label or rename scored-row type for clarity.
2. Shrink activation threshold: streak >=1 vs >=2 vs >=3.
3. How strictly to require P0 dependency rereads during targeted relearn.

## Non-Goals

1. Runtime feature changes outside skill-check and onboarding policy layers.
2. Any fake or inferred score reporting without graded evidence.
