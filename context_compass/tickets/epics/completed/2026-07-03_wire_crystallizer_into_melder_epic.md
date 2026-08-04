# Epic: Wire Crystallizer Into Melder — First Cut (create_spell_crystal path + importlib seed/unseed + bind participation)
- Completed: 2026-07-06T20:45:00Z
- Summary: Phase A COMPLETE and owner-accepted 2026-07-06: C1-C6 + the full recorded-world loop (emissions, custody lifecycle, removal ladder, state switches, memberships, links, contracts, clusters, auto-checkpoints w/ retention + auto-flush, local cache). 3.14t pile green minus one non-crystallizer collection-DI failure. Successors: bootstrap epic (restore engine, design note inside) + persistence epic (adapter LAST).


## Metadata
- Epic ID: EPIC-2026-07-03-wire-crystallizer-into-melder
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: draft
- Owner: cowork
- Agent Name: melder_0 (owner-directed transfer 2026-07-05; crystal_0 = backup)
- Priority: p2
- Created: 2026-07-03T13:29:44Z
- Updated: 2026-07-03T13:29:44Z
- Target Window: 2026-Q3
- Related Program/Initiative: Crystallizer + MutationResearch (combined lane)

## Problem / Opportunity
The crystallizer is a policy/activation root (`configure -> activate -> create_spell_crystal`)
but is NOT wired into melder: `create_spell_crystal` has ZERO callers and `spellbook` bind
(spellbook.py:~4229) has ZERO crystal references. So no bind produces a crystal, no synthetic
module is seeded/unseeded by spell state, and there is no single point where crystallizer
participates in the runtime. This epic is the FIRST CUT that establishes that wiring - the
foundation everything else (mutations, bootloader, history, storage, restore) depends on.
Findings + mechanism: `artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md` and
`artifacts/2026-07-02_import_and_module_lifecycle_findings.md`.

## MRP Alignment
The minimum coherent wiring that makes crystallizer a live participant: one participation seam
(bind), one crystal-creation call path, one importlib add/remove actioning point, gated by one
config. Get this right and mutations/bootloader/history/storage attach to a correct core; get it
wrong and they inherit a broken seam.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; parent EPIC-2026-07-02-agent-object-persistence-loop;
  findings artifacts linked; crystallizer turn-on order confirmed (`configure -> activate -> create`).
- EXECUTION_BOUNDARY: (1) crystallizer<->melder wiring; (2) the `create_spell_crystal` call path;
  (3) importlib seed/unseed actioning timing; (4) the `remove_inactive_synthmodules` config knob;
  (5) bind participation gated on `crystallizer.activated`. EXCLUDES everything in Non-Goals.
- DEPENDENCIES: Crystallizer singleton (configure/activate) [built]; SyntheticModule registry +
  finder/loader [built]; SpellCrystal [built - needs footprint extension]; notch/bind_inactive
  [built]. The content-addressed version store + alias (parent M8) is adjacent - take only the
  minimum needed here.
- EXIT_GATE: a bind, while crystallizer is activated, produces a crystal and seeds its synthetic
  module; deactivate actions importlib per `remove_inactive_synthmodules` (false=leave/insert-only,
  true=remove); validated green on user-run 3.14t.
- FAILURE_ESCALATION: DECISION_REQUEST for alias placement (Crystallizer vs VersionStore vs
  SyntheticModule) and the remove-direction default; CONFLICT if another agent edits
  bind/crystallizer/synthetic_module concurrently.

## Goals (Outcomes)
- Understand + document how crystallizer wires into the rest of melder (host + participation seam).
- Understand + implement the `create_spell_crystal` call path (who calls it, when, with what).
- Understand + implement WHEN to action importlib seed (activate/bind) and unseed (inactive),
  governed by config.
- Add crystallizer config `remove_inactive_synthmodules: bool` (default FALSE = leave / insert-only;
  TRUE = remove). The direction is undecided, so it is a knob.
- Wire bind (the single participation seam) to mint/participate when crystallizer is activated.

## Non-Goals (Explicit Exclusions - LATER)
- Bootloader / bootstrap / fast-load + configs.
- History, version graph, MR merge model, the impact engine.
- Persistence storage / DB adapter internals BEYOND naming the SINGLE db-write entry point + the
  SINGLE hydrate/load point that MR/mutations convey data through later.
- Checkpoint / restore.
- Mutations (depend on this; come later - they just convey data into the crystallizer callables).
- Anything off the 5-item execution boundary.

## Scope Boundaries
- In scope: `src/melder/crystallizer/` (crystallizer.py, spell_crystal.py, synthetic_module.py,
  configuration/crystallizer_configuration.py) and the bind seam in
  `src/melder/aether/spellbook/spellbook.py` (bind at ~4229).
- Out of scope: MR internals, bootloader/loader chain, adapters beyond the single entry/load seam.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: child epic created to scope the first cut; stays draft until the owner picks
  the first story to activate.

## Success Metrics
- With crystallizer activated, a bind produces a crystal + seeds its synthetic module (importable).
- Deactivate honors `remove_inactive_synthmodules` (false: version stays resident + reimportable;
  true: removed).
- No crystal produced when crystallizer is inactive (the gate holds).
- Green on user-run 3.14t.

## Requirements (Functional + Non-Functional)
- R-A. Crystallizer participation is gated on `activated`; nothing happens when inactive.
- R-B. bind (single seam) calls `create_spell_crystal` when crystallizer is activated.
- R-C. Seed on activate/bind (register + publish the synthetic module); unseed on inactive per config.
- R-D. Config knob `remove_inactive_synthmodules` (bool, default FALSE).
- R-E. Footprint: the crystal documents what an activation placed (callsign/module keys, canonical
  alias, file locations) so the remove path (when true) is exact and reversible.
- R-F. Name the single db-write entry point + single hydrate/load point (design only) for later
  MR/mutation data flow.
- R-G. Thread-safe on 3.14t (registry/alias/materialize under the existing RLock discipline).

## Constraints / Assumptions
- bind stays byte-identical when crystallizer is OFF (gate strictly on `activated`).
- Insert-only is validated as the default; the remove path is behind the knob.
- Recurring mount write-fault - verify writes.

## Dependencies / External References
- Parent: `tickets/epics/2026-07-02_agent_object_persistence_loop_epic.md`
- `artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md`
- `artifacts/2026-07-02_import_and_module_lifecycle_findings.md`
- Probes: `tests/experimentation/import_lifecycle_management_suite.py`,
  `synthetic_module_external_library_probe.py`, `owned_physical_synthetic_relationship_probe.py`

## Milestones (Track Progress)
- [x] C1: DONE (crystal_0, 2026-07-03): wiring map + activation-gate model (C1 Findings below).
- [x] C2: DONE (melder_0, 2026-07-05): create_spell_crystal called from bind AND _bind_inactive
      (spellbook_id passthrough); custody owned by the active PersistenceProfile;
      crystallizer.get_spell_crystal lookup chain landed.
- [x] C3: DONE first slice (melder_0, 2026-07-05): activity lane wired - promote ALWAYS
      re-publishes the registered synthetic root module; park unpublishes DEPTH-2 when the
      knob is TRUE; seams = _deactivate/_reactivate_owned_spell (all notch flows).
      Full loader-chain seed (dependency-ordered unfold) remains parent M3.
- [x] C4: DONE (melder_0, 2026-07-05): remove_inactive_synthmodules in
      CrystallizerConfiguration, default FALSE, hazard-documented.
- [x] C5: DONE (melder_0, 2026-07-05): bind participation uniform (pre/post-conjure identical),
      gated activated + _is_dynamic_posture(); conjure-tail sweep RETIRED (owner correction);
      emit-plant (non-owning refs) landed 2026-07-04 by crystal_0.
- [x] C6: DONE as designed (melder_0, 2026-07-05): PersistenceSystem is the single seam;
      CrystallizerCache placeholder pins __crystallizer_cache__ location + store/load verbs;
      adapter behavior = persistence epic.
- NOTE (2026-07-05): epic EXCEEDED its original scope - also landed: PersistenceSystem +
  PersistenceProfile (active-profile model) + twin family + checkpoint crystals (incremental
  journal-segment capture, ULID ids) + 5 configuration-owned emissions + conduit twin at root
  init + conjure configuration-discipline guard + spell lifecycle mirror (active/inactive
  custody locations) + cache-root restructure (__conjure_cache__ migration, 304 bundles).
  Full trail: tickets/stories/2026-07-05_persistence_crystal_profile_and_twin_family_scaffold_story.md.
  REMAINING before epic close: user-run 3.14t green ONLY. Final scope ledger
  (2026-07-06): removal events landed; catch-up walk landed then REMOVED by owner
  decision (no retroactive recording - bind owns emission; canon = activate before
  building); SpellIndexCrystal membership map (9 seams, notch post-repoint fix);
  ConduitCrystal.link_targets live (link/sever/bulk via _remove_contract);
  ContractCrystal relationship map (8 verb seams + fan-outs + sweep net); LOCAL CACHE
  real (flush/reload/list; atomic JSON); 128-test program (21 files); system_docs
  synced 2026-07-06. Bootstrap epic now carries the grounded Restore-Engine Design
  Note; adapter remains the persistence epic's LAST step per owner roadmap.

## Stories (Required to Complete)
- [ ] Story: <TBD> - C1 discovery: crystallizer<->melder wiring map
- [ ] Story: <TBD> - C2 create_spell_crystal call path
- [ ] Story: <TBD> - C3 seed/unseed actioning + timing
- [ ] Story: <TBD> - C4 config knob (default FALSE)
- [ ] Story: <TBD> - C5 bind participation
- [ ] Story: <TBD> - C6 single entry/load seam (design)

## Tasks (Cross-Cutting)
- [ ] Read the crystallizer host wiring in Aether (how the singleton is created/hosted).
- [ ] Read bind (spellbook.py ~4229) end to end to find the exact participation point.
- [ ] Confirm SpellCrystal footprint gaps (callsign, created sys.modules keys, parent attrs, files).

## Acceptance Criteria (Epic Done)
- The 5 first-cut items implemented + tested; bind-while-activated produces a crystal + seeds;
  deactivate honors the config; the gate holds; user 3.14t green; owner accepts.

## Risks / Mitigations
- Risk: touching bind (hot path) destabilizes runtime -> Mitigation: gate strictly on `activated`;
  bind unchanged when crystallizer off; tests.
- Risk: remove-direction wrong -> Mitigation: config knob, default FALSE (insert-only, validated).
- Risk: mount write-fault -> verify writes.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN (alias placement + remove default are decisions to confirm).
- [ ] No bind semantic change when crystallizer is inactive.
- [ ] No scope creep into bootloader/history/storage/mutations.

## Validation / Test Approach
- pytest unit/component/integration under `tests/.../crystallizer` + a bind-participation integration
  test; user-run on 3.14t.

## Rollout / Adoption Plan
- C1-C3 (understand + seed/unseed + config timing) first; then C4 knob; then C5 bind wiring; C6 stub.

## Open Questions
- Alias placement: Crystallizer singleton vs dedicated VersionStore vs SyntheticModule class-level
  (rec: dedicated VersionStore owned by Crystallizer).
- `remove_inactive_synthmodules` default (rec: FALSE / insert-only).
- Does `create_spell_crystal` also SEED the synthetic module, or only build custody (seed separate)?

## Decision Log
- 2026-07-03T13:29:44Z: Created as the first-cut child of EPIC-2026-07-02-agent-object-persistence-loop. Scope =
  wire crystallizer into melder (create_spell_crystal path + importlib seed/unseed + bind
  participation + `remove_inactive_synthmodules` knob). Bootloader/history/storage/mutations
  explicitly deferred; MR conveys data via a single db-write entry + single hydrate/load point
  later. Insert-only validated; the remove path sits behind the config knob (default FALSE).

## Context / Handoff Summary
First-cut child epic to establish crystallizer<->melder<->bind wiring + importlib seed/unseed with a
config knob, BEFORE any bootloader/history/storage/mutation work. Everything else depends on this
core being right.

## C1 Findings (2026-07-03) — enable conditions, mode postures, the codegen-lane requirement
Grounded by reading nexus.py, aether.py, crystallizer.py, spellbook.bind, and SystemState.

- Nexus is Aether-hosted (aether.py:119), created at boot but starts DISABLED + unconfigured.
  `Nexus.enable()` REQUIRES an installed NexusConfiguration (raises RuntimeError otherwise),
  finalizes/freezes it, then sets enabled.
- Frame/spellbook utilization conditions (nexus.py `_validate_target_frame_runtime_requirements`):
  - `rift_enabled=True` on the target frame is ALWAYS required for any AR/Rift attach.
  - CODEGEN rift spaces additionally require `ai_native_enabled=True` AND `system_state == dynamic`.
  - Consistency rule: `ai_native_enabled` implies `system_state == dynamic` (automatic+ai_native raises).
- SystemState = { automatic (safe managed default), dynamic (permissive, AI-native) } - two values only.
- The three postures:
  1. automatic + rift_enabled (not ai_native) -> AR command/view only; NO codegen, NO synthetic modules.
  2. automatic + ai_native -> REJECTED.
  3. dynamic + rift_enabled + ai_native -> codegen / synthetic modules unlocked.
- OWNER RULE (the gate): the CODEGEN LANE (dynamic + rift_enabled + ai_native) REQUIRES Crystallizer
  AND MutationResearch to be ACTIVATED. Enforce at the codegen gate (extend
  `_validate_target_frame_runtime_requirements` or the codegen-rift-space creation path): if the frame
  is ai_native+dynamic, assert `crystallizer.activated` AND `MR.activated`, else raise.
  - Activation order: Crystallizer first, then MR (MR hydrates/derives from crystallizer).
  - Dependency is ONE-DIRECTIONAL: Crystallizer can be active STANDALONE (automatic posture) for
    physical/bytecode bootstrap without the codegen lane; the codegen lane CANNOT exist without
    Crystallizer + MR.
- Crystallizer standalone (automatic posture) = physical + non-physical/bytecode (fileless) bootstrap;
  no synthetic modules. The synthetic-module machinery + `remove_inactive_synthmodules` are strictly a
  codegen-lane (dynamic + ai_native) concern.
- Wiring reach: bind -> `Spellbook._aether` -> `._crystallizer` (Aether hosts it). The bind seam is
  spellbook.py ~4331 (right after `new_spell` is registered), gated on `crystallizer.activated`.

## Subsystem Dependency & Activation-Gate Model (2026-07-03, owner)
Authoritative dependency + gate model for Crystallizer / Nexus / MutationResearch. Enforced in
Nexus (frame-runtime validation) and the MR enable path.

- CRYSTALLIZER: STANDALONE. Depends on NOTHING (no Nexus, no MR). Independently activatable
  (`configure -> activate`). Uses BEYOND the codegen lane: bootstrapping (physical AND
  non-physical/bytecode/fileless), source/bytecode custody, save/restore, and other host
  mechanics. A plain user on the `automatic` posture uses crystallizer this way and never touches
  synthetic modules.
- NEXUS: `enable()` requires an installed NexusConfiguration. Frame utilization requires
  `rift_enabled=True`; the CODEGEN rift space additionally requires `ai_native_enabled=True` AND
  `system_state == dynamic` (ai_native implies dynamic).
- MUTATIONRESEARCH: REQUIRES NEXUS (hard dependency) and Crystallizer. MR may be enabled ONLY when
  the codegen conditions are met (`dynamic + rift_enabled + ai_native`). No Nexus / no codegen lane
  -> no MR.

The CODEGEN LANE (`dynamic + rift_enabled + ai_native`) therefore requires ALL of: Nexus enabled +
Crystallizer active + MR active. Enforcement points:
- Nexus: extend `_validate_target_frame_runtime_requirements` (codegen path) to also assert
  `crystallizer.activated` AND `MR.activated`; raise otherwise.
- MR enable path: assert Nexus enabled + the frame codegen conditions + Crystallizer active; raise
  otherwise (MR cannot be enabled outside the codegen lane).
- Activation order: Crystallizer -> Nexus -> MR (MR derives/hydrates from crystallizer and needs Nexus).

Directionality (one-way):
- Crystallizer: standalone OK (automatic bootstrap); NO upward dependency.
- MR -> requires -> Nexus -> requires -> (frame `dynamic + ai_native + rift_enabled`); MR -> requires
  -> Crystallizer.
- So enabling MR forces the whole codegen lane + crystallizer; enabling crystallizer forces nothing.

## Activation Rules (DECISION, 2026-07-04T14:01:57Z)
Four modes: (1) plain, (2) crystallizer-standalone (automatic; physical/bytecode bootstrap; no synth),
(3) Nexus AR (automatic+rift_enabled; command/view; no synth), (4) codegen lane (dynamic+ai_native+
rift_enabled + Nexus + Crystallizer + MR; synthetic-mod mode). Crystallizer = anytime/independent,
REQUIRED in the codegen lane. Bind participates whenever crystallizer.activated (physical=capture,
synthetic=seed). MR only in the codegen lane (requires Nexus+Crystallizer). Bootstrap: physical-only
-> automatic ; synthetic-containing -> dynamic (codegen lane). Enabling the codegen lane forces
Crystallizer+MR; enabling crystallizer forces nothing. Enforce at nexus.py:2430 + the MR enable path
+ bind gate + restore_aether content-check. Full detail: artifacts/2026-07-03_first_cut_design_detail.md.

## EMIT model (DECISION, 2026-07-04T14:15:20Z)
Structural units EMIT to crystallizer (push); crystallizer is a passive observer/sink (no pull).
Enable crystallizer (store + policy only); frames/conduits/spellbooks/spells/links emit their twin +
lifecycle at create/configure/change; crystallizer records + persists -> it 'just knows what's
configured'. Dissolves the onion (no ordering/reach-in). Bootstrap OPEN-ENDED: restore_conduit/
restore_frame/restore_aether = same op at different subtrees. bind EMITS (no-op when crystallizer off
-> byte-identical). Emit-points: frame finalize, conjure, bind, link (+ MR's existing emit). Detail:
artifacts/2026-07-03_bootstrap_design_detail.md (EMIT/OBSERVER MODEL).

## C5 Emit-Plant — progress + remaining (2026-07-03)
DONE (compiles): aether.py creates Crystallizer FIRST (aether.py:120, before default frame :121).
crystallizer.py has emit() sink (:305; NO-OP when not activated) + _emissions slot(:45)/init(:104)/
cleanup(:133,:138). NOTE: crystallizer.py was MOUNT-TRUNCATED mid-emit during the Edit and repaired via
bash - the SOURCE write-fault is active; edit source via bash + py_compile after EACH change.

REMAINING - plant a NON-OWNING `_crystallizer` ref into each unit (uniform 4-step pattern; do NOT change
any __init__ signature):
1. add "_crystallizer" to the unit's __slots__ ;
2. `self._crystallizer = None` in __init__ ;
3. the PARENT plants it right after creating the child (attribute assignment) ;
4. cleanup: `del self._crystallizer` WITHOUT calling `.cleanup()` on it (NON-OWNING - Aether owns +
   cleans crystallizer at aether.py:165; children must NOT double-clean).

Plant points (grounded this session):
- Aether -> frame: aether.py:121 (default), :690, :751 (_create_frame) -> `frame._crystallizer = self._crystallizer`.
- Aether -> Nexus: aether.py after :125 -> `self._nexus._crystallizer = self._crystallizer`.
- Aether -> MR: aether.py:1468 (`research = MutationResearch(aether=self)`) -> `research._crystallizer = self._crystallizer`.
- Frame -> Spellbook: at the frame's spellbook-creation point (read aetheric_frame.py first).
- Spellbook -> Conduit: at conjure/conduit-creation (read spellbook.py conjure + conduit __init__ first).

Then (LATER, once twins/store exist): emit CALL-SITES at frame finalize / conjure / bind / link ->
`self._crystallizer.emit(kind, payload)`.

Read before editing each: aetheric_frame.py, spellbook.py, conduit.py, mutation_research.py, nexus.py
(each: __init__ / __slots__ / cleanup + the child-creation point).


## C5 Emit-Plant — LANDED (2026-07-04T15:25:24Z, crystal_0)
Non-owning `_crystallizer` unfold COMPLETE across all five units; emit scaffolding removed.
Edited via bash + py_compile (mount source write-fault active); all 7 files compile on the 3.10
sandbox. 3.14t suite: Not run (user runs it).

CORRECTED pattern (SUPERSEDES the 4-step "remaining" list above, per owner directive "we do not
want an init reference we just want to unfold it" + "other areas just none it out"):
1. add "_crystallizer" to the unit's __slots__ ;
2. NO __init__ line (unfold-only — host __init__ bodies stay byte-identical) ;
3. the PARENT unfolds it right after creating/holding the child (attribute assignment) ;
4. cleanup: `self._crystallizer = None` (NONE it out; NON-OWNING — Aether owns + cleans the
   crystallizer; children must NOT call `.cleanup()` on it and do NOT `del` it).

Landed edits (evidence):
- Emit removed: crystallizer.py (emit() + _emissions slot/init/cleanup gone; create_spell_crystal
  + _require_activated intact).
- Aether (owner): builds crystallizer first (aether.py:120), cleans (:171) + del (:185); 5 unfold
  plants -> default frame :122, nexus :131, _ensure_frame :697, _create_frame :759, MR :1477.
- AethericFrame: slot aetheric_frame.py:72 ; none-out :193.
- Spellbook: slot in __slots__ ; none-out spellbook.py:618 ; unfolded FROM its frame at both
  creation sites -> nexus_frame_manager.py:975 + spellbook.py:5145 (clone) ; unfolds INTO the ROOT
  conduit at conjure return spellbook.py:5312.
- Conduit (ROOT only, not lesser): slot ; none-out conduit.py:497 (_permanent_cleanup); lesser
  conduits never receive the ref.
- Nexus: slot ; none-out nexus.py:251 ; unfolded from Aether aether.py:131.
- MutationResearch: slot ; none-out mutation_research.py:147 ; unfolded from Aether aether.py:1477.

## Notes
- DATETIME: 2026-07-04T15:25:24Z
  TYPE: FACT
  CLAIM: C5 non-owning `_crystallizer` unfold + emit-scaffolding removal landed across
    crystallizer/aether/frame/spellbook/root-conduit/nexus/MR. Unfold-only (no __init__ change);
    Aether owns+cleans, non-owning holders None it. All 7 files py_compile-clean (3.10 sandbox).
  EVIDENCE:
  - src/melder/aether/aether.py:120-185
  - src/melder/aether/aether.py:697-759
  - src/melder/aether/spellbook/spellbook.py:5312-5312
  - src/melder/nexus/nexus_frame_manager.py:975-975
  IMPACT: crystallizer is now reachable (non-owning) from every structural unit for the LATER emit
    call-sites; hosts stay byte-identical when crystallizer is disabled (no emit wired yet).
  NEXT: re-add emit() as a CONDITIONAL call at frame-finalize/conjure/bind/link once twins+store
    exist (deferred per owner: "emit should be triggered under specific circumstances").
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-04T15:25:24Z
  TYPE: DECISION
  CLAIM: Two synaptic-skill tensions resolved by owner directive: (1) init_and_ownership "init all
    attrs in __init__" -> overridden to unfold-only (no init line) for byte-identical hosts; (2)
    cleanup_and_disposal default `del` -> overridden to `self._crystallizer = None` for the
    NON-OWNING ref (tombstone-style; Aether is the sole owner/cleaner).
  EVIDENCE:
  - src/melder/aether/aether.py:171-185
  - src/melder/aether/aetheric_frame/aetheric_frame.py:193-193
  IMPACT: children never double-clean the shared crystallizer; hosts untouched when it is off.
  NEXT: emit call-sites (separate story) after twins/store land.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-04T15:37:05Z
  TYPE: FACT
  CLAIM: CORRECTION (owner caught): the unfold-only pattern MUST still initialize the attribute
    deterministically in __init__. Added `self._crystallizer: Optional[Crystallizer] = None` to
    all 5 __init__s + a TYPE_CHECKING `from melder.crystallizer.crystallizer import Crystallizer`.
    "No init reference" meant no constructor PARAMETER / signature change, NOT "no init line".
    Now: __init__ sets None (deterministic default per init_and_ownership.md) -> parent unfolds the
    real ref over it -> cleanup nulls it. Lesser conduits