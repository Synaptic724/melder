# Task: Implement Plain-Ref Creation Storage For Non-Disposable Entries

## Metadata
- Task ID: TASK-2026-05-26-implement-plain-ref-creation-storage-for-non-disposable-entries
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p0
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Stop using `Creation` as the universal runtime storage wrapper. Store plain
retained objects directly when no disposal methods exist, and keep `Creation`
only for entries that actually need explicit disposal metadata.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested implementation after the bounded
  investigation of `Meld`, `CreationContext`, phases `10-12`, and `Creations`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/creations/creation.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py`
  - directly implicated transfer/runtime tests
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/**`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `system_docs/patches/active/creations_plain_ref_disposal_split/architecture_patch.md`
  - `system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creations.md`
  - `system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_meld.md`
  - `system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creation_runtime_codegen.md`
  - `system_docs/patches/active/creations_plain_ref_disposal_split/code_description_patch_creations.md`
- EXIT_GATE:
  - non-disposable retained entries are stored as raw refs
  - disposable retained entries still carry explicit disposal metadata
  - runtime retrieval and extract/restore flows stay correct
  - focused validation passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the split forces a wider
  runtime storage redesign than the agreed plain-ref/disposable-only cut.

## Scope Boundaries
- In scope:
  - split plain storage vs disposal-tracked storage inside `Creations`
  - adjust runtime retrieval in `Meld` and generated creation-context code
  - adjust transfer extract/restore payload shape
  - keep `many` behavior unchanged except where needed for type correctness
- Out of scope:
  - broad scheduler/compiler redesign
  - changing spellspace ownership model
  - changing `many` retention semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the storage-model
  implementation cut after the investigation findings were established.

## Steps / Checklist
- [ ] Consume the patch docs and record the implementation/validation mapping.
- [ ] Split `Creations` storage between raw refs and disposal-tracked entries.
- [ ] Update `Meld` and creation-context runtime retrieval paths.
- [ ] Update transfer extract/restore to support the new stored-entry shape.
- [ ] Run focused validation.
- [ ] Summarize the landed storage split and remaining risks.

## Deliverables
- plain-ref storage for non-disposable retained entries
- disposal-only use of `Creation`
- focused validation result

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/aether/conduit`
  - `pytest -q tests/unit/melder/aether/conduit/creations`
  - `pytest -q tests/unit/melder/aether/conduit/meld`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creations.md`
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_meld.md`
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creation_runtime_codegen.md`
  - `codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/code_description_patch_creations.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure after canonical docs absorb the delta

## Noting Behavior
- Note focus: storage-model split, runtime retrieval impact, validation, and
  one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-26T22:36:42Z
  TYPE: PLAN
  CLAIM: The agreed implementation cut is narrower than a full `Creations`
    redesign: keep `Creation` only for disposal-tracked entries, store raw refs
    for plain retained entries, and update the few runtime sites that currently
    assume every retained entry is a `Creation`.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md
  IMPACT: The blast radius is real but bounded to `Creations`, retrieval paths,
    and extract/restore payload shape.
  NEXT: create the patch-lane docs, map section -> code touch -> validation,
    then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: DECISION
  CLAIM: The patch-to-code map is explicit and bounded. `architecture_patch.md`
    constrains the cut to storage split plus retrieval alignment. `component_patch_creations.md`
    maps to `creations.py` storage, extract/restore, and reset paths.
    `component_patch_meld.md` maps to `meld.py` retrieval unwrapping only.
    `component_patch_creation_runtime_codegen.md` maps to
    `creation_context_codegen.py` and the shared phase-12 existing-creation
    helper. `code_description_patch_creations.md` makes transfer and pooled
    reset behavior the validation focus.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/architecture_patch.md
  - codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creations.md
  - codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_meld.md
  - codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/component_patch_creation_runtime_codegen.md
  - codex/context_compass/system_docs/patches/active/creations_plain_ref_disposal_split/code_description_patch_creations.md
  IMPACT: The implementation can now stay on the real storage/retrieval seam
    and avoid drifting into broader compiler or scheduler churn.
  NEXT: patch `creations.py`, `meld.py`, `creation_context_codegen.py`, and
    the phase-12 existing-creation helper, then run focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: MEASURE
  CLAIM: The tuple-based storage split is landed on the requested contract. `Creation`
    is no longer the universal retained-entry wrapper. `Creations` now keeps
    plain retained entries in `_creations`, keeps disposal-tracked entries as
    `(object, disposal_method_names)` tuples in `_disposable_creations`, keeps
    disposable many entries in lists under `_disposable_creations`, and returns
    raw runtime objects on the retrieval path. `Meld` and the creation-runtime
    codegen paths were aligned to that split, and the focused direct rings are
    green.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py
  - tests/unit/melder/aether/conduit/creations/test_creations.py
  - tests/unit/melder/aether/conduit/meld/test_meld.py
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py
  - tests/integration/melder/conduit/test_conduit_integration_creations.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\creations\test_creations.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py tests\unit\melder\aether\conduit\meld\test_meld_2.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_creations.py`
  IMPACT: Plain retained entries now drop out of cleanup/reset with straight map clears instead of universal wrapper handling, and the runtime retrieval path no longer depends on `Creation.value` for the normal case.
  NEXT: get user review on the tuple-storage cut, then decide whether to widen validation into the broader conduit ring or move to the next creation-runtime savings seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: MEASURE
  CLAIM: Wider validation was partially green and partially unrelated. The
    directly implicated `creation_context_codegen` expectation file was aligned
    and is now green. The broad conduit unit/integration rings exposed red
    tests outside this storage split: two preexisting-looking conduit-dynamic
    failures around lesser-link/gate behavior and three transaction-concurrency
    failures in conduit integration that point at mediator admission conflicts,
    not creation-storage shape.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_codegen.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\creation_context\test_creation_context_codegen.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit`
  IMPACT: The storage split itself is covered by green direct rings, but I am
    not claiming the full conduit surfaces are green because the broader run
    hit unrelated red tests that were not fixed in this slice.
  NEXT: review the tuple-storage cut first; only widen into the unrelated
    conduit-dynamic or transaction-concurrency failures if you want that as the
    next lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T00:00:00Z
  TYPE: MEASURE
  CLAIM: The phase-12 blueprint drift is fixed on the requested contract. The
    no-overrides and overrides executor test stubs now match the live runtime
    storage model: raw refs for plain entries, tuple storage for disposable
    entries, and direct `get_creation(...)` / `get_spellspace_creation(...)`
    retrieval. The two blueprint files are green again without adding backward-
    compat runtime shims.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints\test_phase12_no_overrides_executor.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints\test_phase12_overrides_executor.py`
  IMPACT: The exact phase-12 drift you surfaced is repaired, and the codegen
    tests now validate the tuple/raw-ref model instead of the deleted universal
    `Creation` wrapper contract.
  NEXT: get review on the storage-model cut and decide whether to widen into
    broader suite validation or move to the next runtime savings seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T00:00:00Z
  TYPE: MEASURE
  CLAIM: The live `Creations` model now matches the requested contract. `_creations`
    is the only authoritative live-object registry, `_disposable_creations` is
    cleanup-only metadata, the disposal stacks are gone, and normal retrieval
    paths only read `_creations`. The directly implicated `Creations`, `Meld`,
    and phase-12 rings are green on that model.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py
  - tests/unit/melder/aether/conduit/creations/test_creations.py
  - tests/unit/melder/aether/conduit/meld/test_meld.py
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\creations\test_creations.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py tests\unit\melder\aether\conduit\meld\test_meld_2.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints\test_phase12_no_overrides_executor.py tests\unit\melder\spellbook\spell_crafter\blueprints\test_phase12_overrides_executor.py`
  IMPACT: The hot path no longer double-looks into cleanup metadata or carries
    the old universal-wrapper/storage-stack design.
  NEXT: if we keep optimizing, the next real target is the generated miss/create
    lock coordination in `creation_context_codegen.py`, not more `Creations`
    cleanup churn.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T00:00:00Z
  TYPE: FACT
  CLAIM: The final getter contract is now strict and simple. `get_creation(...)`
    is just the non-spellspace live lookup over `_creations`, and
    `get_spellspace_creation(...)` is just the spellspace-bucket lookup over
    `_creations`. Neither helper checks cleanup-only metadata and neither one
    shape-normalizes impossible internal states. The only remaining storage
    branching stays on maintenance paths (`extract`, `restore`, cleanup, reset),
    not on live retrieval.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py
  - tests/unit/melder/aether/conduit/creations/test_creations.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\creations\test_creations.py`
  IMPACT: The hot lookup surface is no longer paying pointless list/dict guard
    branches or any cleanup-metadata lookup cost.
  NEXT: if we continue, the next meaningful optimization target is the
    generated miss/create coordination lock in `creation_context_codegen.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the plain-ref/non-disposable and disposal-only/Creation
split that came out of the creation-runtime investigation.

