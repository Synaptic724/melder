

# Task: Correct five base-class docstrings that still claim they are unguarded

## Metadata
- Task ID: TASK-2026-07-25-unguarded-base-docstring-correction
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: in_progress
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T19:25:00Z
- Updated: 2026-07-25T19:25:00Z

## Objective
Replace the retired-sentinel justification in five base-class `Registration:` sections
with the manifest truth, because all five classes are now IN the manifest and their
docstrings instruct maintainers to preserve an exclusion that no longer exists.

## Ticket Contract
- ENTRY_GATE: owner directed the sentinel cleanup 2026-07-25; manifest membership
  verified per class before any edit; board row created in the same pass as this ticket.
- EXECUTION_BOUNDARY: the `Registration:` docstring section of exactly five files. No
  code, no signatures, no behavior, no other docstring section.
- DEPENDENCIES: none. `bind.py` is deliberately excluded - its sentinel mention is
  correct history, not a stale claim.
- EXIT_GATE: no file claims to be unguarded while present in the manifest; no
  `Do NOT add __melder_internal__` instruction survives outside historical framing.
- FAILURE_ESCALATION: DECISION_REQUEST if any of the five turns out to be deliberately
  ABSENT from the manifest, which would invert the finding.

## Scope Boundaries
- In scope: `cleanable.py`, `sync.py`, `abstract_elastic_pool.py`, `diff_strategy.py`,
  `group_diff_strategy.py` - docstring prose only.
- Out of scope: adding or removing manifest entries; touching `bind.py`; the system-doc
  re-point required by the proxy removal (separate follow-on).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed it, membership is evidenced per class, and the
  contradiction is unambiguous.

## Steps / Checklist
- [ ] `utilities/general_base/cleanable.py` - rewrite the `Registration:` section.
- [ ] `utilities/general_base/sync.py` - same.
- [ ] `utilities/general_base/abstract_elastic_pool.py` - same, including its claim
      that the exclusion "has to hold at every level of the chain".
- [ ] `mutation_research/diff/diff_strategy.py` - same, preserving the open/closed
      extension point reasoning, which is still true and still matters.
- [ ] `mutation_research/group_diff/group_diff_strategy.py` - same.
- [ ] Preserve each section's genuine architectural reasoning; only the MECHANISM claim
      and the resulting instruction are wrong.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Five corrected `Registration:` sections that agree with the shipped manifest.

## Files / Paths Impacted
- src/melder/utilities/general_base/cleanable.py
- src/melder/utilities/general_base/sync.py
- src/melder/utilities/general_base/abstract_elastic_pool.py
- src/melder/mutation_research/diff/diff_strategy.py
- src/melder/mutation_research/group_diff/group_diff_strategy.py

## Validation
- Not run.
- Recommended commands (owner-run, 3.14t):
  - `pytest tests/unit/melder -q`
  - `rg -n "DELIBERATELY UNGUARDED" src/`

## Risks / Rollback Notes
- RISK: docstring-only, zero behavior change, so runtime risk is nil. The real risk is
  editorial - deleting the genuine open/closed reasoning along with the wrong mechanism.
  Mitigation: rewrite the mechanism sentence, keep the design rationale.
- Rollback: git revert of five files.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No deleting comments; wrong comments are UPDATED, never stripped.
- [ ] No drive-by edit to any other docstring section in the touched files.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-25T19:25:00Z
  TYPE: FACT
  CLAIM: Five base classes carry a `Registration:` section reading "BASE CLASS -
    DELIBERATELY UNGUARDED. Do NOT add `__melder_internal__` to this class", justified
    by the sentinel resolving through `getattr` and walking the MRO. All five are
    PRESENT in the generated manifest and are therefore guarded. The justification is
    void under exact `(module, qualname)` matching, which does not inherit, and the
    owner's 2026-07-24 ruling was explicitly "guard EVERY class, NO exclusion list".
    Several also assert that concrete descendants "carry the sentinel individually",
    which is false everywhere - no `__melder_internal__` stamp survives in `src/`.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/internal_manifest.py:577-577
  - src/melder/utilities/general_base/cleanable.py:49-60
  - src/melder/mutation_research/diff/diff_strategy.py:36-46
  IMPACT: These are not merely stale - they instruct a future maintainer to preserve an
    exclusion the shipped manifest does not honour, in the exact place someone checks
    before changing guard behaviour. `abstract_elastic_pool.py` goes furthest, claiming
    the exclusion "has to hold at every level of the chain".
  NEXT: Rewrite `cleanable.py` first; the other four cite it as precedent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T19:25:00Z
  TYPE: DECISION
  CLAIM: The patch-framework gate does NOT apply. Its triggers are architecture or
    component boundary changes, lifecycle behaviour, policy/gating behaviour, or source
    wiring requiring a graph refresh. This is prose-only correction of already-landed
    behaviour with zero runtime delta, which is `staleness_protocol.md` territory. That
    protocol's own rule - refresh the doc to match current code - is the governing one.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:11-19
  - context_compass/agent_onboarding/default/engineer/skills/staleness_protocol.md:10-16
  IMPACT: Avoids ceremony that would not improve safety, while keeping the reasoning
    explicit so the judgement is reviewable rather than assumed.
  NEXT: Implement the five edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Five base-class docstrings still teach the retired sentinel and instruct maintainers not
to guard classes the manifest already guards. Correction is prose-only with zero
behaviour change; `bind.py` is excluded because its sentinel mention is accurate
history. The genuine open/closed extension-point reasoning in the two diff-strategy
files must survive the rewrite - only the mechanism claim and its instruction are wrong.
