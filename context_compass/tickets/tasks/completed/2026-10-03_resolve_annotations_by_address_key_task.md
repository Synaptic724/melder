# Task: Phase 3 resolves annotations by address key - an existing object is matched by its class

- Completed: 2026-10-03T21:22:15Z
- Summary: Landed at 0.2.8218: Phase 3 matches annotations by address key - an existing object resolves by its class,
  a TYPE_CHECKING string and a class object agree, the eq-risky gate is gone; unit and component regressions,
  the harness bound bare, generation 18; docs, graph, README, assets and bundles current; patch docs archived.
  The Autofac-strict tightening is not wanted (owner). Closed by the owner's directive; owner-run suites:
  Not run.

## Metadata
- Task ID: TASK-2026-10-03-resolve-annotations-by-address-key
- Story: none (standalone defect task; found in the S8 lane, owner-directed 2026-10-03)
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-03T19:25:31Z
- Updated: 2026-10-03T21:22:15Z

## Objective
Phase 3 matches a DI annotation to candidate spells by KEY - `normalize_frame_key(annotation)` after the
existing Optional/Union/ForwardRef normalization - against each spell's two names: its address frame key
(spellframe, else its own name) and its type key (`spell_name`, for an existing object the instance's class
name). One rule for class-object and string annotations, Protocol and string frames, class bindings and
existing objects. The three identity branches and the eq-risky index gate go. Nothing that resolves today
stops resolving; an existing object bound bare now satisfies a consumer annotated with its class, and a
binding resolves identically whether the consumer imported the type under `TYPE_CHECKING` or at runtime.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's "go ahead and fix it" (2026-10-03); patch docs under
  `system_docs/patches/active/annotation_address_matching_2026_10_03/` written and linked here with the
  mapping note BEFORE any src edit.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py` (`_matches_annotation`, `_build_candidate_index`, `_get_candidate_index`,
  `_indexed_annotation_candidates`, the class docstring), `tests/unit/.../phases/test_compiler_phase_3.py`,
  a new component test (bare existing object injected through a real conjure, string/object annotation
  parity), `tests/experimentation/codegen_strategy_certification.py` (existing objects bound bare), the S8
  component test's binding, the structural-snapshot generation (`caching_system.py`), the two canonical
  system documents and indexes, graph descriptors, README DI paragraph, `release_docs/next_version_release.md`,
  `__version__`.
- DEPENDENCIES: none; independent of S8 (parked, measured).
- EXIT_GATE: phase-3 unit tests green with the rewritten cases; the suites green on the VM copy (sharded);
  landed with notch, release note, docs, graph, assets and bundles with --check OK; owner-run suites requested.
- FAILURE_ESCALATION: DECISION_REQUEST if any existing test depends on identity-only matching (a same-name
  class deliberately NOT resolving); BLOCKER if the structural snapshot's replay rule cannot stay consistent.

## Scope Boundaries
- In scope: the matcher, its index, tests, the harness bindings, the generation bump, docs, notch, note.
- Out of scope: the Autofac-strict tightening (a framed spell reachable only by its frame) - a separate,
  breaking decision; `_resolve_spellmap_default` (explicit addressing by frame object, unchanged);
  `_eq_safe_object` stays as the structural snapshot's replayability rule (its over-conservatism after this
  change is a follow-up); the cache-staleness investigation (its own task).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's "go ahead and fix it" (2026-10-03T19:25:31Z) after the design discussion in the
  S8 lane.
- from_state: in_progress
- to_state: review
- transition_reason: Landed at 0.2.8218 with docs, graph, patch docs, assets and bundles (2026-10-03T19:36:16Z); owner-run suites
  pending.
- from_state: review
- to_state: done
- transition_reason: Owner's turn-in directive (2026-10-03T21:22:15Z); notch 0.2.8218, note entry and rebuild
  recorded at landing.

## Steps / Checklist
- [x] Read the whole matching region of compiler_phase_3.py (normalization, scan matcher, eq-safe rule, index
      build, index lookup, the two resolvers, the dag's index wiring) and the phase-3 unit tests.
- [x] Patch docs (architecture, component, code description) and the mapping note; link them here.
- [x] Apply script: matcher + index rewrite, unit tests re-pinned and extended, component test, harness and S8
      binding changes, generation bump; run on the working copy; shards.
- [x] Land on the tree (CRLF), notch above `__version__` (0.2.8216 now), release-note section, docs, graph,
      README; promote and archive the patch docs; rebuild assets and LLM bundles LAST; both checks OK.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The key-based matcher and index; tests; the harness bound bare; docs; release-note entry; notch.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/utilities/caching_system/caching_system.py
- tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py
- tests/component/melder/aether/conduit/ (new file)
- tests/experimentation/codegen_strategy_certification.py
- README.md (DI paragraph), context_compass/system_docs/, release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Working copy (S8 + matcher): unit 4238, component 2263, integration 877 + 1017 passed; the owner's full-tree
  suites: Not run. Recommended commands:
  - `python -X gil=0 -m pytest tests/unit/melder/spellbook/spell_compiler/phases -q`
  - `python -X gil=0 -m pytest tests/component tests/integration/melder/spellbook -q`

## Risks / Rollback Notes
- A pool with two same-named classes at distinct frames: unchanged (distinct keys). At one address Phase 4
  already refuses the pair; Phase 3 now agrees instead of resolving by object.
- Rollback: restore the identity branches; keep the generation bumped.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the patch docs and the mapping note.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/annotation_address_matching_20261003/ (apply script, suite logs)
  - system_docs/patches/active/annotation_address_matching_2026_10_03/ (patch docs)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs promoted and archived at turn-in; artifacts kept.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase 3 annotation matching; Address Law; existing objects; TYPE_CHECKING parity
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-03T19:25:31Z
  TYPE: FACT
  CLAIM: The matching region read whole. `_normalize_annotation_for_matching` unwraps ForwardRef and Optional/
    Union. `_matches_annotation` (scan): string annotation -> `spell_name == s`, str frame == s, class frame
    `__name__ == s`; object annotation -> `spell.spell is a` or `spellframe is a / == a`; plus the binding
    filter and the METHOD/LAMBDA exclusion under `require_class_spell`. `_build_candidate_index` buckets by
    spell_name/str-frame/class-frame-name strings and by `id()` of the bound object and the frame, and flags
    `eq_risky` when any object has a custom `__eq__` (then `_get_candidate_index` returns None and the scan
    runs); the frame_str/frame_ident/frame_none buckets are built and never read. `_indexed_annotation_
    candidates` reads the string bucket and the identity bucket and replicates the scan's dict semantics
    (first position, last object per SpellIndex). The two resolvers pass `binding_name=None`. The dag builds
    the index once per pass through `resolution_pass_cache["phase3_candidate_index"]`. `_eq_safe_object` is
    also the structural snapshot's replayability rule (`structural_snapshot.py:327-343`), so it stays. The
    address helpers: `normalize_frame_key` lowercases a class/Protocol `__name__`, a string, else `str()`;
    `make_spell_key_from_parts` takes the spellframe else the spell name; `spell_name` for an instance is
    `type(instance).__name__`. Unit tests stub spells as SimpleNamespaces with spell/spellframe/spell_name/
    binding_name/spell_type/resolvable/spell_index (no `key`), so the matcher computes keys from
    spellframe/spell_name itself.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:140-176
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:178-252
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:254-434
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:436-557
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:862-905
  - src/melder/utilities/helpers/general_helpers.py:241-376
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:60-295
  IMPACT: The rewrite is local: one key helper, two-name spell keys, a by_key index, the scan matcher on the
    same rule, the dead buckets and the eq_risky gate removed; the dag wiring and the resolvers' bodies are
    untouched.
  NEXT: patch docs and the mapping note, then the apply script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T19:36:16Z
  TYPE: FACT
  CLAIM: Implemented, validated and landed. Working copy: the matcher and index rewrite by the anchored script
    `artifacts/annotation_address_matching_20261003/apply_key_matching.py` (phase 3: `_annotation_key`,
    `_spell_keys`, key-based `_matches_annotation`, `by_key` index, no eq-risky gate, docstrings; generation 18
    with the history pin; harness binds existing objects bare; the S8 component test too); unit tests: the
    parametrized matcher cases rewritten as key cases plus three new tests (existing object by class and by
    name, a concrete-class frame as a name, index == scan with `{"by_key"}` only); a new component file (bare
    existing Service injected into a class-annotated and a string-annotated consumer through a real conjure;
    generation pin). Suites on the working copy (S8 + matcher): unit spellbook+conduit+utilities 4238 passed;
    component 2263 passed; integration spellbook+conduit 877, aether+crystallizer 1017 passed; the harness runs
    with bare bindings. Tree: script applied (CRLF kept), `__version__` -> 0.2.8218, release-note section "A
    consumer's annotation resolves by address key", component map (SpellCompiler: "Annotation matching by
    address key"), architecture invariant, handoff and code map, README DI paragraph, both indexes --check OK,
    graph (CompilerPhase3 prose updated and accepted), patch docs archived, assets --check OK (bind guard 620).
    Not run: the owner's full-tree suites.
  EVIDENCE:
  - artifacts/annotation_address_matching_20261003/apply_key_matching.py:1-80
  - artifacts/annotation_address_matching_20261003/logs/shard_unit_spellbook_conduit_utilities.log:1-2
  - artifacts/annotation_address_matching_20261003/logs/shard_component.log:1-2
  - artifacts/annotation_address_matching_20261003/logs/shard_integration_spellbook_conduit.log:1-2
  - artifacts/annotation_address_matching_20261003/logs/shard_integration_aether_crystallizer.log:1-2
  - release_docs/next_version_release.md:345-361
  IMPACT: Existing objects resolve by their class; `TYPE_CHECKING` strings and class objects agree; no behaviour
    that resolved before is lost. Follow-ups for the owner: the Autofac-strict tightening (breaking, its own
    ticket) and the cache-staleness investigation (RISK note in the S8 task).
  NEXT: owner runs the suites and turns it in; then the follow-up decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-10-03T19:25:31Z: IN_PROGRESS. Opened; the matching region is read; patch docs next. Resume from the latest
note's NEXT.

STATE 2026-10-03T19:36:16Z: REVIEW. Landed at 0.2.8218; owner-run suites pending; follow-ups (Autofac-strict tightening,
cache staleness) await the owner. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
