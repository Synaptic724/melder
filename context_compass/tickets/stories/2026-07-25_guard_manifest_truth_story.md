

# Story: Bring guard truth into the docs, the graph, and the guard module itself

## Metadata
- Story ID: STORY-2026-07-25-guard-manifest-truth
- Epic: EPIC-2026-07-22-internal-bind-guard-replacement
- Status: in_progress
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-25T18:19:28Z

## User Narrative
As an agent or engineer reorienting from a blank slate, I want the system docs, the
source graph, and the guard module to describe the manifest mechanism that actually
shipped, so that I do not reason about bind refusal through a sentinel that no longer
exists.

## Value / MRP Alignment
Durable context is the repo's stated top priority. The guard is the single gate that
decides what may become a spell; three canonical surfaces currently teach a retired
mechanism with inverted subclass semantics. An agent trusting them would predict the
opposite bind outcome. MRP: fix the foundational truth, do not layer new work on a
doc surface that lies.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routes to this story; the landed guard
  mechanism verified in source before any doc claim is written.
- EXECUTION_BOUNDARY: `system_docs/src_architecture.md`, `system_docs/src_components.md`,
  `system_docs/src_graph.json`, `system_docs/readable_src_graph.json`, the guard module,
  and the two stale docstrings named in TASK-2026-07-25-sentinel-deadcode-strip. No
  other runtime code.
- DEPENDENCIES: owner ruling recorded at EPIC-2026-07-22 Notes 2026-07-24T00:05:00Z;
  patch artifacts required before the code task implements.
- EXIT_GATE: all four child tasks done; owner-confirmed acceptance; board synced;
  epic Status/Handoff repaired.
- FAILURE_ESCALATION: DECISION_REQUEST on any public-surface removal beyond the
  `sentinel` property; BLOCKER if the manifest cold-boot lane cannot be evidenced.

## Requirements (Functional)
- Every guard claim in `src_architecture.md` and `src_components.md` describes the
  build-time `(module, qualname)` manifest, exact-match lookup, and the accepted
  subclass behavior flip.
- `src_components.md` carries a real C1 Code Map (full package inventory) instead of
  a two-entry truncation stub.
- The `MelderRegistrationGuard` node in `src_graph.json` states manifest truth, and
  `readable_src_graph.json` is regenerated from it via the documented recipe.
- The guard module no longer exposes sentinel machinery that cannot work.

## Requirements (Non-Functional)
- Doc prose 90-110 chars target, 120 hard cap (`configuration_standards.md`).
- No invented paths: every C1 entry filesystem-verified before it is listed.
- Graph regeneration is delimiter-only reflow; no semantic reshaping of JSON.

## Scope Boundaries
- In scope: the four surfaces named in EXECUTION_BOUNDARY.
- Out of scope: the `__melder_cache__.__init_cache__` packaging defect observed in the
  owner's 2026-07-25 gauntlet run (recorded as RISK below, owner routed it elsewhere);
  regenerating `src_graph.json` wholesale from source; the sibling agent-metadata epic.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the work and answered all three scope forks;
  mechanism verified in source; board row created in the same pass.

## Dependencies / Related Work
- EPIC-2026-07-22-internal-bind-guard-replacement (parent; Status/Handoff stale, this
  story repairs it)
- TASK-2026-07-23-bind-guard-sentinel-vs-set-benchmark (Lane D; its conclusion was
  superseded by the owner ruling one day later)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-07-25-guard-doc-truth - correct guard claims in both system docs
- [ ] Task: TASK-2026-07-25-c1-code-map-restore - rebuild the C1 Code Map
- [ ] Task: TASK-2026-07-25-guard-graph-node - fix graph node, regenerate readable
- [ ] Task: TASK-2026-07-25-sentinel-deadcode-strip - remove dead sentinel surface
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `grep -n "sentinel" system_docs/src_architecture.md system_docs/src_components.md`
  returns only historical//superseded framing, never a live mechanism claim.
- `src_components.md` C1 Code Map lists filesystem-verified paths with no truncation
  note standing in for content.
- Graph guard node names the manifest; `owns_state` no longer claims `_sentinel`.
- `readable_src_graph.json` validates as JSON after regeneration.
- Guard module exposes no sentinel property, slot, or class constant.

## Validation / Test Plan
- Not run.
- Recommended (owner-run, 3.14t): `pytest tests/unit/melder -q`, plus
  `pytest tests/unit/melder/test_package_public_surface.py -q` for the root surface.
- JSON validation of the regenerated readable graph per
  `graph_details_readable_generation.md` Validation section.

## UX / API / Data Notes
- Removing `MelderRegistrationGuard.sentinel` is a public-shape change on an exported
  class. Owner explicitly requested it in this lane; recorded here so the decision is
  not silently inherited later.

## Risks / Mitigations
- RISK: a full-package C1 inventory drifts fastest of any doc section. Mitigation:
  generate it from a filesystem walk, not by hand, so it is reproducible.
- RISK: removing the `sentinel` property breaks an unknown consumer. Mitigation:
  repo-wide grep before edit; the strip task blocks on that evidence.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Does `code_description_patch_` apply to the dead-code strip, or is the removal
  mechanical enough to be covered by architecture + component patches alone?

## Decision Log
- 2026-07-25: Owner chose full package inventory for the C1 map, whole-graph
  regeneration, and inclusion of the dead-code strip in this lane.
- 2026-07-25: melder_1 raised that regeneration alone cannot fix the guard node, since
  the recipe is a delimiter-only reflow of `src_graph.json`, which carries the same
  stale text. Canonical storage is edited first, then readable is regenerated.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/guard_manifest_truth_2026_07_25/architecture_patch.md
  - system_docs/patches/active/guard_manifest_truth_2026_07_25/component_patch_registration_guard.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: at story closure, once durable deltas are merged into the canonical
  system docs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: The shipped mechanism is a build-time generated frozenset of
    `(module, qualname)` tuples, not a runtime-built set and not the sentinel. 578
    entries, stamped `BUILT_FOR_VERSION`. Loader resolution order is cached-module ->
    cold-boot scan+write -> in-memory scan on read-only installs. Enforcement is one
    exact-match membership test with no MRO walk, at a single call site.
  EVIDENCE:
  - src/melder/__melder_cache__/__init_cache__/manifest_loader.py:32-69
  - src/melder/__melder_cache__/__init_cache__/internal_manifest.py:1-24
  - src/melder/__melder_registration_guard__.py:189-210
  - src/melder/aether/spellbook/bind/bind.py:285-285
  IMPACT: Every doc sentence describing a sentinel tag or MRO-inherited refusal is
    wrong in mechanism AND in outcome; user subclasses of internal classes now bind.
  NEXT: Correct the five drift sites listed in TASK-2026-07-25-guard-doc-truth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Regenerating `readable_src_graph.json` cannot fix the stale guard node.
    The documented recipe inserts line breaks at safe delimiters and explicitly does
    not reshape content, and `src_graph.json` contains the identical `sentinel tag`
    and `"owns_state":["_sentinel"]` text. Regeneration would reproduce the defect.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_readable_generation.md:20-30
  - context_compass/system_docs/src_graph.json (grep hits: `sentinel tag`,
    `"owns_state":["_sentinel"]`)
  IMPACT: The owner's chosen option only achieves its goal when canonical storage is
    corrected first; otherwise the lane closes green having changed nothing.
  NEXT: Edit the guard node in `src_graph.json`, then regenerate readable from it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: RISK
  CLAIM: The manifest cold-boot lane is documented as always-correct
    ("Correctness never depends on the write succeeding"), but the owner's 2026-07-25
    gauntlet run raised `ModuleNotFoundError: No module named
    'melder.__melder_cache__.__init_cache__'` at guard import, which means the package
    shell was absent and the loader never got the chance to rebuild.
  EVIDENCE:
  - src/melder/__melder_cache__/__init_cache__/manifest_loader.py:1-22
  - src/melder/__melder_registration_guard__.py:11-11
  IMPACT: Docs must describe the cold-boot fallback as the coded design, not as an
    evidenced runtime guarantee, until the packaging defect is resolved elsewhere.
  NEXT: Word the doc sections so the fallback is attributed to the loader contract,
    and leave the packaging defect to the owner-routed lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Landed guard mechanism verified in source: build-time `(module, qualname)` manifest,
exact match, no inheritance, one bind call site. Five doc drift sites identified plus
an empty C1 Code Map and a stale graph node. Owner chose full C1 inventory, graph
regeneration (corrected to storage-first), and inclusion of the dead sentinel strip.
The code task is patch-gated and must not implement before its patch docs exist.
