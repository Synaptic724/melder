# architecture_patch

## Metadata
- Patch ID: host_read_surface_2026_09_29
- Status: archived without promotion (owner turn-in, 2026-09-29)
- Owner: user (agent melder_0)
- Created: 2026-09-29T21:27:17Z
- Updated: 2026-09-29T22:26:28Z

## Patch Scope and Non-Goals
- Objective: a host that creates frames (MelderOps) can find them and read the configuration facts it compares
  against through public, read-only calls: noncreating frame lookups on Aether, the frame-wide shared Spellbook
  configuration on AethericFrame, `frozen` on frame and Spellbook configurations, a Spellbook configuration's
  frame, and a conduit's Spellbook.
- Non-goals: how frames are created, owned, detached or cleaned; the existing frame-scoped Aether calls (they
  keep creating "default" when it is missing); Melder's own private registry readers; atomic retire-if-idle and
  creation attribution (parked story).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Aether Singleton (Global Runtime) | modify | no public call returns a frame without creating one | none |
| AethericFrame Services | modify | shared rich configuration and posture freeze state had no public read | none |
| Spellbook Configuration and System State | modify | freeze state and target frame had no public read | none |
| Conduit Runtime (Normal and Lesser) | modify | a conduit's Spellbook had no public read | none |

## Interface and Boundary Deltas
- Boundary delta: none. Aether stays the owner of every frame; the new calls hand out borrowed references.
- Interface delta (additions only): `Aether.find_frame(aetheric_frame_name) -> Optional[AethericFrame]`,
  `Aether.get_frame(aetheric_frame_name) -> AethericFrame`, `Aether.list_frame_names() -> tuple[str, ...]`,
  `AethericFrame.shared_spellbook_configuration`, `AethericFrameConfiguration.frozen`,
  `SpellbookConfiguration.frozen`, `SpellbookConfiguration.aether_frame`, `Conduit.spellbook`.

## Cross-Component Invariants
- A frame lookup never creates a frame ("default" included), takes no plane claim and never seals or freezes the
  Aether configuration. Only `_ensure_frame` / `_create_frame` create frames, as before.
- Lookups grant no lease: a returned frame can be cleaned by its owner at any time; a frame that is cleaned but
  not yet detached reads as absent.
- The accessors are reads of state that already exists; none adds a lock, a lock-order edge or meld-path work.

## Migration and Rollout Order
1. Red tests for every new call (they fail with AttributeError on 0.2.8207).
2. Add the calls with their docstrings; tests green; meld/conduit and package suites on 3.14t.
3. System docs, graph, user docs, release note, `__version__` notch; assets and LLM bundles last.
4. MelderOps adopts the calls in its own lane once a wheel carrying this notch is installed there.

## Rollback Strategy
- Rollback trigger: a name clash or a contract a host cannot rely on.
- Rollback steps: revert the additions, the two test files and the doc sections of this patch.
- Post-rollback verification: the meld/conduit and package suites.

## Validation Expectations and Evidence Plan
- Validation item: red-then-green new tests, including "no lookup creates a frame or freezes the Aether
  configuration"; existing suites unchanged.
- Evidence source: context_compass/artifacts/host_read_surface_20260929/.

## Ticket Coverage Map
- Epic: tickets/epics/completed/2026-09-29_host_integration_read_surface_epic.md
- Story: tickets/stories/completed/2026-09-29_frame_lookups_and_read_accessors_story.md
- Tasks: tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md

## Unknowns and Decision Requests
- UNKNOWN: none; each accessor mirrors a read MelderOps performs today.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: implemented as specified and landed at 0.2.8208 (21:34:06Z) with 27 tests; the release
  note section "Look up frames without creating them" describes it. The 0.2.8208 wheel carries it and is
  installed in MelderOps' env. The owner turned the lane in (2026-09-29) before the canonical system
  documents, the graph and docs/intermediate/scopes.md were updated, so this patch was archived without
  promotion.
- What remains: promotion into src_architecture, src_components, tests_components, the graph and
  scopes.md, plus remapping 13 citations this lane's insertions shifted, in:
  tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md.
- Next entrypoint: tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
