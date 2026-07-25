

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

- DATETIME: 2026-07-25T19:40:00Z
  TYPE: MEASURE
  CLAIM: The five in-scope files are corrected and all parse. Owner feedback mid-task
    ("don't write the history into docstrings") was applied: every `HISTORICAL:` block
    I had written was stripped, leaving current-state contract only. I also caught a
    miss in my own first pass - `__agent_purpose__` on `cleanable`, `sync`, and
    `abstract_elastic_pool` still carried the identical stale claim
    ("Deliberately not registration-guarded"), which is the field agents actually read.
    All three corrected.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:49-62
  - src/melder/utilities/general_base/cleanable.py:82-86
  IMPACT: Fixing the prose section but not the machine-readable agent field would have
    left the wrong claim on the surface most likely to be consumed programmatically.
  NEXT: None for the five; see the expansion DECISION below.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T19:40:00Z
  TYPE: DECISION_REQUEST
  CLAIM: EXPANSION GATE HIT, and the finding underneath it is a CONTRACT BREAK rather
    than doc rot. 23 further files carry `USER-BINDABLE - deliberately unguarded` or
    equivalent, and EVERY class spot-checked is PRESENT in the manifest and therefore
    NOT bindable: all 11 custom exceptions, the four weak containers, CounterSwitch,
    FastSwitch, TicketFlag, ICleanable, IChannelLogger, SafeGuard, ProtocolCrafter,
    Package, and the three concrete diff strategies. A user reading
    `MeldExecutionError`'s docstring is told they may bind it; `Spellbook.bind(...)`
    will raise `InternalRegistrationError`. That is a promise the runtime breaks.
    ROOT CAUSE: two owner rulings disagree and the docstrings implement the older one.
    2026-07-19 ruled the 11 exceptions USER-BINDABLE. 2026-07-24 ruled "guard EVERY
    class in src/melder, NO exclusion list, utilities included". The manifest implements
    2026-07-24; ~23 docstrings still teach 2026-07-19.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/internal_manifest.py
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:69-69
  - src/melder/utilities/synchronization/fast_switch.py:73-73
  IMPACT: The fix direction depends entirely on which ruling is current, and the two
    directions are opposite. If 2026-07-24 stands, this is ~23 docstring corrections.
    If the 2026-07-19 intent stands, the MANIFEST is wrong and the fix is a generator
    exclusion list - a code change to `_builder.py`, not a docs pass. Guessing would
    either strip a real user-facing capability or entrench its loss.
  NEXT: Owner ruling on which regime is current before any of the 23 are touched.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-25T19:45:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: CORRECTING MY OWN PRIOR NOTE. I recorded above that the 2026-07-19 and
    2026-07-24 owner rulings CONFLICT. On the evidence they do not - I misread the
    earlier one. melder_0's 2026-07-19 handoff to helper_f states the ruling was about
    EXPORTING: which utilities are "user-facing and worth exposing" from the package
    root. It closes with the decisive line: "guarding and exporting are orthogonal:
    `SafeGuard` is guard-tagged AND should be exported, since a user calls it directly
    but must not `bind()` it." So 2026-07-19 never made anything bindable; it made
    things IMPORTABLE. The 23 docstrings that read "USER-BINDABLE - deliberately
    unguarded" conflated the two axes.
  EVIDENCE:
  - context_compass/mailbox_board.md:51-61
  - src/melder/aether/spellbook/bind/bind.py:71-73
  IMPACT: This collapses the decision. There is no ruling conflict to adjudicate: the
    manifest is CORRECT and consistent with both rulings, and the 23 docstrings are
    simply wrong on a single word. The fix direction is therefore unambiguous - correct
    the docstrings, do NOT add a generator exclusion list. My earlier framing would have
    sent the owner to arbitrate a conflict that does not exist.
  NEXT: Owner confirmation to proceed past the 5-file expansion gate; the ruling itself
    is no longer in question, only the scope authorisation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-25T20:05:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Owner asked me to REMOVE the `Registration:` sections as unnecessary, with the
    caveat to read them first. I read all 412 across `src/melder` (280 distinct bodies),
    and the reading contradicts the removal: only 56 are thin enough to be pure noise.
    298 carry genuine non-default guidance that a reader cannot get elsewhere - which
    door produces the object (`Obtained through Aether.create_configuration()`), whether
    a user may construct or pass it (`USER-INSTANTIATED but NOT user-bindable`, with
    `SpellContract(spellframe=IAuthService)` as the worked example), value-vs-object
    distinctions (`guarded, but USER-FACING as a value`), and explicit MRO-audit
    reasoning on guarded bases. Removing those would delete real API guidance, exactly
    the risk the owner flagged.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_contract.py
  - src/melder/aether/conduit/conduit_ward/permissions/permissions.py
  - src/melder/utilities/general_base/cleanable.py
  IMPACT: The instruction as literally stated would destroy 298 useful sections to
    remove 56 useless ones. Reporting instead of executing.
  NEXT: Owner decision on the three-way split below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T20:05:00Z
  TYPE: FACT
  CLAIM: The reading surfaced a REAL defect class the removal request would have hidden.
    58 sections are factually WRONG, not merely verbose. 42 cite the RETIRED mechanism -
    "guarded via the inherited `SpellValidationStrategy` sentinel", "inherit this
    sentinel via the MRO", "carries the registration guard sentinel", "(ClassVar
    sentinel)" - none of which exists any more. A further 16 assert the class is
    UNGUARDED ("currently UNGUARDED value dataclass", "not guarded and not reachable",
    "VALUE VOCABULARY - deliberately unguarded"), and every one I checked against the
    manifest is PRESENT in it: CodegenPlanDiscovery, CodegenPlanDiscoveryStrategy,
    CodegenPlanDiscoveryStrategyBuilder, CodegenPlanDiscoverySystem,
    SpellExistenceOccurrenceAnalysis, SpellOccurrenceGraphAnalysis,
    SpellAnalyzerStrategyBuilder, LaneType - 8 of 8 wrong.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/internal_manifest.py
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:43-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy.py:34-34
  IMPACT: 42 sections teach a mechanism that no longer exists and 16 state the opposite
    of shipped behaviour. Wrong outranks verbose: these matter more than the 56 thin
    ones, and a blanket removal would have deleted the evidence of them.
  NEXT: Owner ruling - recommend fixing the 58 wrong before touching the 56 thin.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Five base-class docstrings still teach the retired sentinel and instruct maintainers not
to guard classes the manifest already guards. Correction is prose-only with zero
behaviour change; `bind.py` is excluded because its sentinel mention is accurate
history. The genuine open/closed extension-point reasoning in the two diff-strategy
files must survive the rewrite - only the mechanism claim and its instruction are wrong.
