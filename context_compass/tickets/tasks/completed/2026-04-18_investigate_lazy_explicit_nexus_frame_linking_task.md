# Task: Investigate Lazy Explicit Nexus Frame Linking
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after downstream lazy-linking implementation landed.

## Metadata
- Task ID: TASK-2026-04-18-investigate-lazy-explicit-nexus-frame-linking
- Story: STORY-2026-04-18-investigate-lazy-explicit-nexus-frame-linking
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:41:23Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Map the current eager/default Rift/Nexus frame model and produce the concrete
no-backward-compat refactor plan for lazy explicit Nexus-frame linking.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an epic and plan before the frame/
  default-state refactor.
- EXECUTION_BOUNDARY: investigation and planning only; no runtime edits yet.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/configuration/nexus_configuration.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/nexus_frame_record.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
- EXIT_GATE: the eager/default blast radius and the implementation plan are
  explicit enough to propose before any code changes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor depends on a
  larger target-opening or space-contract redesign first.

## Scope Boundaries
- In scope:
  - eager Rift creation-time Nexus-frame attachment
  - Rift-owned default Nexus/target frame state
  - default-based Nexus access/viewer call paths
  - detach/removal implications
  - direct unit-test assumptions
- Out of scope:
  - actual implementation
  - future explicit space-opening APIs
  - event-system work

## Steps / Checklist
- [ ] Map `Nexus.create_rift(...)` and `Nexus.add_rift(...)` eager frame behavior.
- [ ] Map `Rift` constructor/default frame state.
- [ ] Map default-based `Nexus` access/viewer paths.
- [ ] Map detach/removal implications.
- [ ] Map direct tests that assume eager/default behavior.
- [ ] Produce the bounded refactor plan.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed blast-radius inventory
- concrete no-compat refactor plan

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Notes
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: FACT
  CLAIM: Rift creation is currently eager with respect to Nexus frames.
    `Nexus.create_rift(...)` computes a Nexus frame name up front, passes
    `nexus_frame_names` / `default_nexus_frame_name` into `Rift`, and then
    `Nexus.add_rift(...)` immediately validates Nexus-frame budget and calls
    `_attach_rift_to_nexus_frames(rift)`, which in turn
    `_get_or_create_nexus_frame_record(...)` and attaches the Rift id.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:691-706
  - src/melder/aether/nexus/nexus.py:736-755
  - src/melder/aether/nexus/nexus.py:2757-2783
  - src/melder/aether/nexus/nexus.py:2963-3005
  IMPACT: Removing eager frame realization requires changes to both
    `create_rift(...)` and `add_rift(...)`, not just a constructor cleanup on
    `Rift`.
  NEXT: map the default-based access/viewer APIs and the detach path so the
    full no-compat refactor boundary is explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: FACT
  CLAIM: The eager/default model is still wired into three runtime areas:
    1) `Rift` constructor/storage (`nexus_frame_names`,
       `default_nexus_frame_name`, `target_frame_names`,
       `default_target_frame_name`)
    2) default-based Nexus internal frame access
       (`get_nexus_frame_for_rift`, `create_nexus_frame_for_rift`)
    3) default-based viewer creation metadata/default view frame
       (`create_frame_viewer_for_rift`, `create_cached_frame_viewer_for_rift`)
    Additionally, `Nexus.remove_rift(...)` currently depends on Rift-owned
    Nexus-frame names to detach and dispose frame records.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:102-189
  - src/melder/aether/nexus/rift/rift.py:334-376
  - src/melder/aether/nexus/rift/rift.py:470-542
  - src/melder/aether/nexus/nexus.py:1590-1643
  - src/melder/aether/nexus/nexus.py:1846-1889
  - src/melder/aether/nexus/nexus.py:2043-2160
  - src/melder/aether/nexus/nexus.py:2785-2814
  IMPACT: The refactor must either remove or tighten all three areas together,
    and `remove_rift(...)` needs a new detach strategy that scans Nexus frame
    records instead of iterating Rift-owned frame-name state.
  NEXT: map the direct unit-test assumptions and then propose the implementation sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: FACT
  CLAIM: The direct test blast radius is concentrated, not repo-wide. The main
    assumptions are:
    - direct `Rift(...)` constructor tests that still require
      `nexus_frame_names` / `default_nexus_frame_name` /
      `target_frame_names` / `default_target_frame_name`
    - eager frame materialization tests in `test_nexus.py`
      (shared, one_per_workspace, indexed)
    - target default assertions after `rift.target_frame(...)`
    The `NexusConfiguration.default_target_frame_name` setting is validated as
    config policy, but `Nexus.create_rift(...)` does not currently seed it into
    new Rifts; those start with `default_target_frame_name=None`.
  EVIDENCE:
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:169-240
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:490-515
  - tests/unit/melder/aether/test_nexus.py:536-539
  - tests/unit/melder/aether/test_nexus.py:4093-4260
  - src/melder/aether/nexus/configuration/nexus_configuration.py:255-324
  - src/melder/aether/nexus/nexus.py:543-578
  - src/melder/aether/nexus/nexus.py:699-699
  IMPACT: The no-compat refactor is feasible, but it requires rewriting the
    eager-frame tests and deciding whether target defaults survive at all or are
    deferred to later explicit target-opening work.
  NEXT: propose the concrete refactor sequence and the minimal survivor APIs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: PLAN
  CLAIM: The bounded no-backward-compat refactor plan is:
    1. Remove from `Rift.__init__` and `IRift`:
       `nexus_frame_names`, `default_nexus_frame_name`,
       `target_frame_names`, `default_target_frame_name`
    2. Remove eager attachment/materialization from `Nexus.create_rift(...)`
       and `Nexus.add_rift(...)`
    3. Make `Nexus.remove_rift(...)` detach by scanning
       `NexusFrameRecord.attached_rift_ids` instead of iterating
       Rift-owned Nexus-frame state
    4. Change `get_nexus_frame_for_rift(...)` and
       `create_nexus_frame_for_rift(...)` to require explicit frame intent
       or derive policy-owned frame names internally at request time
    5. Remove default-target-based viewer creation for now or fail fast until
       later explicit target-opening APIs are built
    6. Rewrite the focused unit tests to the new explicit/lazy model
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:691-706
  - src/melder/aether/nexus/nexus.py:736-755
  - src/melder/aether/nexus/nexus.py:2043-2160
  - src/melder/aether/nexus/nexus.py:2757-2814
  - src/melder/aether/nexus/rift/rift.py:102-189
  - user_instruction: "nexus never build a frame ever unless requested"
  IMPACT: This isolates the current eager/default cleanup without pretending the
    full future explicit link/open API already exists.
  NEXT: return this plan to the user for approval before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigate-first planning pass for removing eager/default
Rift/Nexus frame state and switching to lazy explicit Nexus-frame linking.
