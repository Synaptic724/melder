# Task: SpellIndex terminology rename — phased execution (no backward compat)

## Metadata
- Task ID: TASK-2026-06-17-spellindex-terminology-rename-execution
- Epic: tickets/epics/2026-06-16_spellindex_terminology_rename_epic.md
- Status: closed
- Owner: cowork
- Agent Name: general_0 (inherited + closed by melder_0 2026-07-12;
  general_0 owner-confirmed departed)
- Priority: p1
- Created: 2026-06-17T10:52:22Z
- Updated: 2026-07-12T08:20:00Z

## Closure Note (melder_0, inheritor)
- DATETIME: 2026-07-12T08:20:00Z
  TYPE: FACT
  CLAIM: CLOSED on inheritance (owner: "yeah sure inherit it" +
    rename-is-done affirmation). The P1-P8 execution was COMPLETE when
    general_0 departed (401 sites; whole-tree grep zero old tokens;
    compileall clean); the only open item was the owner-run 3.14t
    confirmation, which the codebase has since collected many times over
    - most recently the 2026-07-11/12 full-tree runs (9702 passed) that
    exercised every renamed surface (selected_spell_id / has_spell /
    spells_in_index are load-bearing across the restore engine, the MR
    seams, and the graft lane built this week). DISAMBIGUATION for the
    record: this rename (spellbook/index lineage->index vocabulary,
    June) is DISTINCT from mutation_0's 2026-07-11 spell_sha->spell_id
    sweep (MR package vocabulary); both are done. Flagged residuals
    disposition: graph-JSON regen has happened repeatedly since (520+
    node regens by mutation_0 + melder_0); Tier-2 vocab and other-agent
    patch prose ride the inherited genuine_index_operations epic.
  NEXT: none (closed).

## Objective
Execute the SpellIndex terminology rename (lineage vocabulary -> index vocabulary)
as a behavior-preserving, NO-BACKWARD-COMPAT sweep, divide-and-conquer in phases
from easiest to hardest, renaming source AND tests together each phase so the tree
never goes red between phases. User directive 2026-06-17: "no backward compat hit
that hard... start with the easy ones move into the hard ones and cover tests too...
phased approach... hit each one, one at a time."

## Locked mapping (no aliases / no shims)
- `current` (property) + `_current_id` -> `selected_spell_id` (property) + `_selected_spell_id`
- `get_all_versions()` -> `spells_in_index()`
- `has_version(...)` -> `has_spell(...)`
- `_versions` (SpellIndex field) -> `_spells_in_index`
- `_active_spell` -> `_selected_spell`
- `_set_active_member` -> `_select_member` (`_attach_member`/`_detach_member`/`_has_member` keep "member")
- `_version_registry` -> `_selected_spell_registry`
- `find_and_return_spell_index` -> `find_index_for_spell`
- `refresh_version_registry` -> ALREADY GONE (0 hits) — no action
- Tier-2 adjacent vocab (`_spell_versions`, `_contracted_versions`, `current_spell_id`,
  `lineage_to_versions`, ...) is NOT in this task — flagged to user at the end.

## Ticket Contract
- ENTRY_GATE: rename epic accepted; certified general_0; active board row.
- EXECUTION_BOUNDARY: Tier-1 SpellIndex + frame-registry vocabulary across src + tests
  + system_docs sync. EXCLUDES Tier-2 adjacent vocabulary and any behavior change.
- DEPENDENCIES: rename epic (design), map task (evidence).
- EXIT_GATE: zero surviving Tier-1 old-vocabulary tokens; per-phase py_compile clean;
  full unit tree green in the user's 3.14t venv (user-run); rename-only diff review.
- FAILURE_ESCALATION: CONFLICT note if a rename collides with a non-SpellIndex symbol
  (esp. `.current` receivers, `_versions`/`_active_spell` substring matches).

## Phased checklist (one phase at a time; each = src + tests + py_compile + grep-verify)
- [x] P1  find_and_return_spell_index -> find_index_for_spell  (2 src files / 3 test files) — DONE 2026-06-17: 16/16 renamed (incl. 4 test fn names), old token=0, py_compile OK.
- [x] P2  _version_registry -> _selected_spell_registry        (2 src / 3 test files) — DONE 2026-06-17: 20/20 (field+slot+init+comments+1 test name), old=0, py_compile OK. `version_set` locals deferred to P7.
- [x] P3  get_all_versions -> spells_in_index                  (3 src / 6 test files) — DONE 2026-06-17: 43 new/0 old; BOTH defs (SpellIndex + frame) renamed uniformly; py_compile OK.
- [x] P4  has_version -> has_spell — DONE 2026-06-17: 25 files (10 src+15 test), 74 new/0 old; renamed ALL THREE defs (frame, SpellIndex, Detail) — uniform vocab kill; has_spell_payload untouched; py_compile OK.
- [x] P5  internals: _current_id / _versions / _active_spell / _set_active_member — DONE 2026-06-17: _selected_spell_id(19) / _spells_in_index(34) / _selected_spell(31) / _select_member(1); 0 old; danger-siblings (_spell_versions/_contracted_versions/active_spellspace) preserved; py_compile OK.
- [x] P6  property current -> selected_spell_id — DONE 2026-06-17: 1 def + 400 dotted lines (401 occ) + 11 string-literal refs + 7 test-stub defs + 1 @current.setter; ALL 401 .current verified SpellIndex; current_spell_id (84) preserved; full src/melder compileall exit 0. NOTE: 3 mutation_research string edits (mechanical, keep-from-breaking, not semantics).
- [x] P7  docstrings/comments/prose + system_docs sync — DONE 2026-06-17: spell_index.py prose clean (only "inversion"/mutation-note remain); has_spell/find_index params -> spell_id; find_conduit_id_for_version -> find_conduit_id_for_spell (6 refs); Detail/frame "lineage"/"version" prose fixed; src_architecture.md + src_components.md narrative synced. FLAGGED RESIDUALS (not done): graph JSONs need regen (readable_src_graph.json, src_graph.json, 3 patches/active/*.expanded.json); other agents' active patch docs reference spell_index.current (nexus_passive_ingest, spellspace_meld) — their lanes; Tier-2 vocab (_spell_versions/_contracted_versions/current_spell_id/version_set locals) out of scope.
- [x] P8  final verification — DONE 2026-06-17: whole-tree grep = 0 surviving Tier-1 tokens; Tier-2 preserved (current_spell_id=84, _spell_versions/_contracted_versions=42, active_spellspace=5); `python3 -m compileall src/melder` exit 0. Runtime/pytest NOT RUN in sandbox: sandbox is Py3.10.12, repo requires 3.14t (importing melder fails pre-existingly on frame_descriptor.py TYPE_CHECKING annotation — untouched by rename). Full unit tree is USER-RUN in 3.14t.

## Validation approach
- Per phase: `python3 -m py_compile` each touched src file (sandbox syntax gate) +
  `grep` proving zero surviving old-token references for that symbol.
- Final: full unit tree is USER-RUN in 3.14t (no-GIL). I report "Not run" for the
  suite until the user runs it; I never claim a pytest pass I did not execute.
- Codemod scripts live in the scratchpad (outputs), NOT committed to the repo.

## Scope / Files
- Core: src/melder/aether/spellbook/bind/spell_index.py
- Frame: src/melder/aether/aetheric_frame/aetheric_frame.py, src/melder/aether/aether.py
- Consumers across src/melder (per-phase grep) + tests/** + system_docs/**

## Notes
- DATETIME: 2026-06-17T10:52:22Z
  TYPE: PLAN
  CLAIM: Rename-first execution opened (user: no backward compat, phased easy->hard,
    cover tests). Precise scope captured: refresh_version_registry already gone;
    `.current` is ~all SpellIndex receivers in src (138 spell_index.current + 16
    SpellIndex.current + a few index/idx/target_index; 1 ambiguous spell.current to
    verify), so P6 is tractable; tests need receiver-scoping (242 .current, 87 are
    spell_index). 8 phases set up as Cowork tasks + this ticket checklist.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-16_spellindex_terminology_rename_epic.md:1-194
  - src/melder/aether/spellbook/bind/spell_index.py:120-143
  IMPACT: Clean execution path; each phase keeps the tree green by renaming source +
    tests together.
  NEXT: execute P1 (find_and_return_spell_index -> find_index_for_spell).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Phased, no-compat rename of the SpellIndex lineage vocabulary to index vocabulary.
Mapping locked (above). Execute P1->P8 one at a time, renaming src + tests together
each phase, py_compile + grep-verify per phase, full 3.14t suite user-run at the end.
Tier-2 adjacent vocab is out of scope and surfaced to the user at close.
