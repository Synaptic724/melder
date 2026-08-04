# Story: crystal_loader_system + BootMediator (S4 - the unfold owner)

- Completed: 2026-07-10T09:10:00Z
- Summary: the unfold got its owner - LoadPlan/BootMediator/
  CrystalLoaderSystem + moved engine/bootstrap; blockers refuse pre-replay at
  the fold seam (verdict law standard; proven live by the SHA-refusal);
  scope-aware admission (S1 flip-back landed); durable last-load state;
  ledger never constructs engines; owner-run sentinel green; owner accepted
  at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-crystal-loader-system-boot-mediator
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T05:20:00Z
- Updated: 2026-07-10T05:20:00Z

## Problem / Opportunity
Loading has no owner: the ledger constructs engines, nobody remembers what
was last loaded, and the preflight verdict gates nothing by default. V3:
every load is a mediated boot transaction (plan -> map -> verdict -> execute
-> remember) with blockers refusing standard, warnings proceeding + report.

## Design
Per component_patch_crystal_loader_system.md (entry gate satisfied 05:20Z).
KEY DESIGN CALL: the verdict gate lives INSIDE the engine (refuse_on_blockers
after fold+preflight, before replay) because that is the only seam owning
authoritative FOLDED truth - the mediator stays small (plan/policy/adjudicate/
remember) and no fold logic is duplicated.

## Ticket Contract
- ENTRY_GATE: S3 sentinel GREEN (owner, 2026-07-10); component patch linked.
- EXECUTION_BOUNDARY: new crystal_loader_system/ package; engine + bootstrap
  moves; persistence_system.py (detach verb in, 2 engine legs out);
  crystallizer.py (third child + 2 facade reroutes); engine gains ONLY the
  refusal knob + gate; test import re-points for moved modules; NEW unit
  tests; S1 formation test gains the admission flip-back assertion.
- DEPENDENCIES: S1-S3 accepted.
- EXIT_GATE: facade parity (additive keys only); grep gates (no
  persistence.restore_engine / crystallizer_bootstrap paths; ledger has no
  engine references); REROUTE CHECKLIST fully ticked (S3 lesson - every
  facade/caller row explicitly verified); owner sentinel green.
- FAILURE_ESCALATION: fold/stage semantic deltas -> CONFLICT + stop.

## Reroute Checklist (every row ticked before the owner run - S3 lesson)
- [x] Crystallizer.load_checkpoint -> loader (grep-verified)
- [x] Crystallizer.restore_formation -> asset load + loader engine leg
- [x] PersistenceSystem.load_checkpoint REMOVED; internal callers 0 (grep)
- [x] PersistenceSystem.restore_formation_record REMOVED; callers 0 (grep)
- [x] restore_engine import sites re-pointed (ledger's 2 lazy imports died
      with the removed verbs; sentinel unit :12 + integration :23 re-pointed)
- [x] CrystallizerBootstrap import sites re-pointed (integration :656; no
      other importers existed repo-wide)
- [x] bootstrap's post-restore gate deleted; knob = accepted no-op (docstring
      rewritten as ABSORBED)
- [x] engine lazy imports inside moved modules resolve (engine module-level
      melder import = Cleanable only; preflight lazy import re-pointed in S1;
      mediator lazy-imports the new engine path)

## Tasks
- [x] T1: moves done (bootstrap_loader.py rename; package dir materialized
      file-tool-first per the S3 mount lesson). DONE 05:35Z.
- [x] T2: ledger - detach_profile_chain added (the :1084-1098 assembly
      verbatim, returns {"profile_name","checkpoint_ids","chain"});
      load_checkpoint + restore_formation_record removed with NOTE comments.
      DONE 05:45Z.
- [x] T3: load_plan.py (declarative carrier, distinct-key counts, scope
      validation) + boot_mediator.py (plan_checkpoint_load /
      plan_formation_load with the canonical-kind-order minting moved from
      the ledger / execute_plan / pure _adjudicate_for_scope) +
      crystal_loader_system.py (owner; durable _last_load;
      describe_last_load). DONE 06:00Z.
- [x] T4: engine refuse_on_blockers ctor knob (default False = legacy
      parity) + pre-replay gate at the fold->preflight seam
      (mark_failed("admission") + teach-grade error naming blocker rows).
      DONE 06:10Z.
- [x] T5: crystallizer third child (loader borrows record), cleanup
      borrowers-before-owner (loader -> assets -> record), 2 facades
      rerouted with additive "admission" payload key. DONE 06:15Z.
- [x] T6: bootstrap thinned - post-restore gate deleted, with_preflight_gate
      = accepted no-op (ABSORBED docstring). DONE 06:20Z.
- [x] T7: NEW unit suite (8 tests, 271L,
      tests/unit/melder/crystallizer/crystal_loader_system/): plan counts +
      scope refusal, formation window minting order, scope adjudication
      (clean-for-scope / mixed warnings / blockers preserved), world
      passthrough, ADMISSION REFUSAL (teach-grade, pre-replay), legacy
      default parity (report-only), loader initial state, detach KeyError.
      S1 FLIP-BACK landed: the formation integration test now asserts
      admission {"scope":"conduit","verdict":"clean"} with >=1 reclassified
      row while raw preflight stays "warnings". DONE 06:30Z.
- [x] T8: gates 0 (old engine/bootstrap paths + removed-verb callers);
      parse floor GREEN on all 5 package files + new test file;
      persistence_system/crystallizer replicas rotted (disks verified);
      checklist above fully ticked; sentinel run REQUESTED. DONE 06:35Z.

## Notes (validation runs)
- DATETIME: 2026-07-10T06:50:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 1 (owner): 8+22+7+26 unit GREEN; integration 12/13
    with ONE failure that is the S4 gate WORKING: the M3 boot-boundary test
    stamps its synthetic module with a placeholder SHA ("m3-live-sha"), the
    synthetic_source_integrity strategy correctly reads that as tampering
    (recorded != computed), and admission now REFUSES to execute unverified
    source pre-replay (pre-S4 the blocker rode the report advisorily and
    the test never asserted it). FIX: fixture made honest - it computes the
    real hashlib SHA256 of its source text, with a comment naming the law.
    Strategy and gate behavior untouched. Execution: Not run - rerun of the
    integration suite requested.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:823-845
  IMPACT: First real-world proof of the verdict law: a lying payload cannot
    boot anymore.
  NEXT: owner reruns the integration suite; on green, S4 closes ->
    S-test + S5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Acceptance Criteria
- Every load path passes engine-gated admission (blockers refuse pre-replay,
  teach-grade).
- Conduit-scoped formation loads show admission verdict clean-for-scope
  (S1 flip-back) while raw preflight stays untouched.
- Loader owns durable last-load state (describe_last_load()).
- Ledger contains zero engine references; facades byte-compatible with
  additive-only payload keys; sentinel green.

## Applicable Anti-Patterns
- [ ] No fold-logic duplication in the mediator.
- [ ] No facade signature changes; additive payload keys only.
- [ ] Raw preflight findings never rewritten (adjudication is a VIEW).
- [ ] "Not run." for anything not executed.

## Noting Behavior
- Story notes: seam evidence, checklist completion, gate results.

## Notes
- DATETIME: 2026-07-10T05:20:00Z
  TYPE: PLAN
  CLAIM: Design pinned: ledger's chain assembly (:1084-1098) becomes
    detach_profile_chain verbatim; the formation synthetic-window minting
    moves ledger->mediator; the verdict gate rides the engine's existing
    fold->preflight->replay seam (S1 wired preflight at exactly that point).
    Build order T1->T8 with the reroute checklist as a hard exit gate.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:1046-1117
  - codex/context_compass/system_docs/patches/active/crystallizer_decomposition_2026_07_09/component_patch_crystal_loader_system.md:1-99
  IMPACT: Completes the V3 subsystem model's build; only S-test + S5 remain.
  NEXT: T1 moves.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
The unfold gets its owner: engine+bootstrap move into crystal_loader_system/,
the ledger hands out detached chains, the mediator plans/adjudicates/
remembers, and blocker refusal becomes standard admission at the engine's
fold seam. Reroute checklist enforced per the S3 lesson.
