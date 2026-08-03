# Epic: Capability that exists but cannot be reached from the public root

## Metadata
- Epic ID: EPIC-2026-08-03-unreachable-public-capability
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Created: 2026-08-03T15:18:26Z
- Updated: 2026-08-03T15:18:26Z
- Target Window: UNKNOWN
- Related Program/Initiative: UX/AIX experience ladder (advanced + expert tiers)

## Objective
Close the gap between capability melder HAS and capability a caller can REACH
through `import melder as md`. Where a facade is the only door onto an owned
collaborator, the facade must be TOTAL: a knob it does not carry is a knob no
user can turn.

## Problem / Opportunity

MELDER'S RIFT/AR SURFACE COULD NOT BE POINTED AT A USER'S OWN FRAME.

`Nexus._validate_target_frame_runtime_requirements` (nexus.py:2923-2985) gates
every frame engagement on frame posture:

- AR always requires `rift_enabled=True` on the target frame
  (`nexus.py:2956-2963`, message `"AR requires rift_enabled on target frame"`).
- A codegen room additionally requires `ai_native_enabled=True` and
  `system_state == dynamic`.

`AethericFrameConfiguration` owns all three and exposes `with_rift_enabled`,
`with_ai_native` and `with_system_state` to set them. But the posture object is
CREATED AND RETAINED BY THE SPELLBOOK (`spellbook.py:5533-5556`,
`_initialize_aetheric_frame_configuration`) and is never handed to the caller -
there is no public accessor for it on `Spellbook`. The only public door onto it
was `Spellbook.configure_aether_frame`, which carried TWO of the FOURTEEN
`with_*` builders: `system_state` and `system_caching_enabled`.

`rift_enabled` defaults to `False` (`aetheric_frame_configuration.py:1300`).

So: the default is closed, the gate is real, and the opener was unreachable.
Exporting `AethericFrameConfiguration` from `melder/__init__.py` did not help,
because a caller-constructed posture cannot be installed onto the book's frame
through any public call.

A SECOND, SMALLER INSTANCE OF THE SAME SHAPE: `Conduit.set_new_policy` was
public with NO counterpart read. The ward's policy was write-only from the
public surface.

## Context (why now)
Found while authoring the advanced and expert UX/AIX tiers, which are the
evidence lane for the public surface. The owner had already flagged this lane -
the `ux_aix_experiences` board row records the ruling "aetheric frames +
posture door (A/B) ... = NEXT ITERATION". Owner instruction 2026-08-03: "if
theres an absense you should probably just fucken add it bro its fine make sure
you follow synaptic_python_developer rules."

## MRP Alignment
The absence is not a missing feature - the feature is built, tested and
documented. It is a missing DOOR. Closing it is the cheapest possible correction
and gets the surface right before more lessons are written against a hole.

## Ticket Contract
- ENTRY_GATE: the unreachable capability must be demonstrated against a real
  gate in source, not inferred from a signature. MET (see MEASURE note).
- EXECUTION_BOUNDARY: ADDITIVE ONLY. New keyword parameters with `None`
  defaults and new read-only properties. No existing parameter renamed,
  reordered, retyped-narrower, or given new semantics. NO configuration class
  is edited under this epic - that surface belongs to
  EPIC-2026-08-01-configuration-surface-uniformity, whose EXECUTION_BOUNDARY is
  design-only pending an owner ruling.
- DEPENDENCIES: none. Deliberately disjoint from the config-uniformity epic.
- EXIT_GATE: every `with_*` builder on `AethericFrameConfiguration` reachable
  from the public root; ward policy readable; suites green on the owner's 3.14t
  run.
- FAILURE_ESCALATION: BLOCKER on anything requiring `type: ignore`, `# noqa`,
  or widening to `Any`.

## Goals
- `configure_aether_frame` covers the whole frame posture, permanently.
- The conduit's live linking policy is readable.
- A test that FAILS when a future posture knob is added without a door.

## Non-goals
- Changing what any posture knob does.
- Restructuring how configs store values (that is the uniformity epic).
- Correcting the `Internal` / `Public API` marker drift across nexus/rift
  (already ruled a defect by the owner; separate lane).

## Requirements
- Functional: 14/14 posture builders reachable; ward policy readable.
- Non-functional: rich docstrings per `skills/python/docstrings.md`; typing per
  `skills/python/typing.md` (Optional/Union, no PEP 604); no drive-by refactors.

## Acceptance Criteria
- [x] Every `with_*` on `AethericFrameConfiguration` has a parameter on
      `Spellbook.configure_aether_frame`.
- [x] `Conduit.policy` reads the live ward policy.
- [x] `Conduit.set_new_policy` annotation matches what the ward accepts, so
      read-then-write round-trips.
- [x] Tests written that fail if the door narrows again.
- [ ] Owner runs the suites on 3.14t and they are green.

## Risks / Mitigations
- RISK: a wide keyword list invites callers to treat the door as atomic when it
  is not. MITIGATION: the non-atomicity is stated in the docstring Contract and
  pinned by `test_a_rejected_value_leaves_earlier_values_written`.
- RISK: `ai_native` set without dynamic state fails LATER, at freeze, not at the
  call. MITIGATION: `system_state` is applied first so one call can satisfy
  both; the ordering is commented in-line as load-bearing and pinned by
  `test_dynamic_and_ai_native_settle_in_one_call`.
- RISK: opening `rift_enabled` to users widens the AR attack surface on their
  own frames. MITIGATION: none needed - the default stays `False` and the
  opt-in stays explicit. This restores the intended posture model rather than
  loosening it.

## Child Tasks
- (none - executed directly, single tranche, three files)

## Noting Behavior
- Epic notes: the measurement, the design choice, and what was deliberately
  NOT done.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: MEASURE
  CLAIM: THE DOOR CARRIED 2 OF 14. `AethericFrameConfiguration` declares
    fourteen `with_*` posture builders (excluding `with_defaults`, which is a
    seeder not a knob). `Spellbook.configure_aether_frame` carried parameters
    for two of them - `system_state` and `system_caching_enabled`. The other
    twelve had NO public door, because the posture object is book-owned and
    book-retained with no public accessor:
    with_ai_native, with_rift_enabled,
    with_shared_framewide_spellbook_configuration,
    with_system_cache_root_path, with_disable_all_transactions_after_conjure,
    with_disable_mutations, with_disable_linking, with_disable_bind,
    with_disable_conduit_cluster, with_disable_transfer_of_ownership,
    with_disable_contract_mutation,
    with_max_transaction_wait_time_in_seconds.
  EVIDENCE:
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:507-1176
    - src/melder/aether/spellbook/spellbook.py:6028-6035 (pre-change signature)
    - src/melder/aether/spellbook/spellbook.py:5533-5556 (posture is book-owned)
  IMPACT: Two of the twelve are gate keys. `rift_enabled` defaults False and
    gates AR entirely; `ai_native_enabled` gates codegen rooms. The public
    package could not configure a frame to host a Rift.
  NEXT: Widen the door to 14/14 and pin the totality with a test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: FACT
  CLAIM: THE TEST SUITE HAD ALREADY GROWN A WORKAROUND FOR THIS, which is the
    strongest available evidence that the absence was real and load-bearing
    rather than theoretical. `tests/_frame_posture_test_support.py` exists
    solely to reach around the missing door: it constructs a detached
    `AethericFrameConfiguration`, then calls `Aether()._ensure_frame(...)` and
    `Aether()._get_aetheric_frame_configuration(...)` to sync it onto the live
    frame. `tests/unit/melder/aether/spellbook/test_conjure_settle_or_inherit.py:54-58`
    does the same thing inline via `frame.bind_frame_configuration(...)`.
    Both are private-seam paths that exist because no public one did.
  EVIDENCE:
    - tests/_frame_posture_test_support.py:11-50
    - tests/unit/melder/aether/spellbook/test_conjure_settle_or_inherit.py:51-74
  IMPACT: When the library's own tests must use private seams to set a
    documented public posture, the public surface is incomplete. The support
    module is NOT deleted here - rewriting existing tests is out of this
    epic's boundary - but it is now optional rather than necessary.
  NEXT: Flag as a candidate simplification for whoever next touches that lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: DECISION
  CLAIM: WIDEN THE FACADE; DO NOT EXPOSE THE COLLABORATOR. Two shapes were
    available. (A) Add a public `aetheric_frame_configuration` accessor on
    `Spellbook` and let callers drive the posture object directly. (B) Add the
    twelve missing keyword parameters to `configure_aether_frame`.
    CHOSE B. Reason: the owner's own facade rule from this lane - "IF A FACADE
    COVERS IT, THE COLLABORATOR IS NOT USER SURFACE; export is not the test,
    the presence of a working door is." Shape A would have made a fourth
    exception to a rule already applied to `Scan`, `SpellOverrider` and the
    crystal loaders. It also hands out an object whose builders raise after
    freeze, so every caller would need to reason about settlement timing that
    the facade already owns. B keeps one door, one contract, one place for the
    ordering law to live.
    ORDERING IS LOAD-BEARING AND IS COMMENTED AS SUCH: `ai_native` requires
    dynamic state and that rule is enforced at FREEZE, not at assignment. The
    door applies `system_state` FIRST so a single call can move a frame to
    dynamic and enable AI-native together. Reordering those two lines would
    leave the posture written but make the later freeze raise.
  EVIDENCE:
    - src/melder/aether/spellbook/spellbook.py:6028-6200 (widened door)
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:557-600
      (freeze-time enforcement of the ai_native rule)
  IMPACT: 14/14 reachable. No new public class, no new object lifetime for a
    caller to manage, no fourth facade exception.
  NEXT: Same treatment for the ward policy read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: FACT
  CLAIM: WARD POLICY WAS WRITE-ONLY. `Conduit.set_new_policy` was public;
    nothing public read the result. The conduit itself already needed the value
    internally and reached for `self._conduit_ward._policy.name`
    (conduit.py:456) to publish its Nexus record. Added `Conduit.policy` as a
    read-only property returning the `Policies` member.
    THE ASYMMETRY IS DELIBERATE AND IS DOCUMENTED: the WRITE is gated on a
    dynamic frame and a normal (non-lesser) conduit; the READ is gated on
    neither. An automatic conduit still enforces a policy, and refusing to
    disclose live behaviour behind a mode gate would be the library hiding what
    it is doing.
    ALSO CORRECTED, and it is not cosmetic: `set_new_policy` was annotated
    `policy: str` while the ward resolves through
    `EnumHelpers.convert_enum_and_check(policy, Policies)`, which accepts a
    member OR its string name. Left as `str`, the new reader would return a
    `Policies` that mypy refuses to pass back into the writer - the round-trip
    would fail typecheck despite working at runtime. Widened to
    `Union[str, Policies]`, which is what the code has always accepted.
  EVIDENCE:
    - src/melder/aether/conduit/conduit.py:2141-2170 (pre-change)
    - src/melder/aether/conduit/conduit_ward/conduit_ward.py:617-660
    - src/melder/utilities/helpers/general_helpers.py:69-107
  IMPACT: A caller can now tell "my swap took" from "my swap was refused and
    the old behaviour is still live" - which matters because `set_new_policy`
    has three documented refusal paths.
  NEXT: Pin the round-trip with a test so the annotation cannot narrow again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: MEASURE
  CLAIM: 25 TESTS ADDED ACROSS TWO NEW COMPONENT FILES, grouped by the
    guarantee each defends rather than by method.
    `test_configure_aether_frame_posture_component.py` - 16 rows: COVERAGE (4,
    including a reflective test that FAILS if a future `with_*` is added
    without a parameter), ORDERING (2, one asserting the single-call
    dynamic+ai_native settlement and one asserting the deferred failure),
    OMISSION (2, proving `None` means "do not touch" and `False` is a value),
    ATOMICITY (1, pinning the documented absence of rollback), REACH (3,
    driving the REAL `_validate_target_frame_runtime_requirements` gate from
    refusal to pass), LIFECYCLE (2), plus 2 refusal rows for the non-boolean
    knobs.
    `test_conduit_component_policy_reader.py` - 9 rows: TRUTH (4), ASYMMETRY
    (2, automatic and lesser), ROUND-TRIP (2), LIFECYCLE (1).
    The REACH rows are the ones that matter: they assert the exact gate the
    absence made unreachable, refusing on a default frame and passing on a
    configured one, with a public call as the only difference.
  EVIDENCE:
    - tests/component/melder/aether/test_configure_aether_frame_posture_component.py
    - tests/component/melder/aether/conduit/test_conduit_component_policy_reader.py
  IMPACT: Design coverage on both additions. Zero `hasattr`-only rows.
  NEXT: OWNER RUNS THE SUITES ON 3.14t. Not run here - the sandbox is 3.10 and
    melder requires >=3.14, so nothing in this epic has executed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: RISK
  CLAIM: SELF-REPORTED DEFECT, CAUGHT AND CORRECTED IN-PASS. My first write to
    `conduit.py` converted the whole file from LF to CRLF, turning a ~55-line
    change into a 12,508-line diff and violating "do not reformat files beyond
    what is required for the change"
    (`skills/python/refactor_limits.md`). Normalized back to LF and verified
    byte-identical to the CRLF version modulo line terminators; the diff is now
    60 lines. `spellbook.py` was unaffected.
    THIS IS A KNOWN HAZARD ON THIS MOUNT, not a one-off: the
    `aetheric_mediator_core` board row records the same class of failure
    ("the board has MIXED LINE ENDINGS (14 CRLF / 135 LF) which makes any
    detect-one-terminator edit silently merge the file - that is what broke my
    own writes twice"). Note also that `git status` shows the ENTIRE `src/`
    tree as modified under this mount with no `core.autocrlf` set, so
    `git diff --stat` is the only reliable check that an edit stayed scoped.
  EVIDENCE:
    - context_compass/attention_board.md (aetheric_mediator_core row, board
      defect paragraph)
  IMPACT: Any agent editing this repo through the mount should run
    `git diff --stat` on the touched files immediately after writing and treat
    a whole-file diff as an EOL flip, not as a real change.
  NEXT: Carried as standing guidance; no separate ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T15:18:26Z
  TYPE: FACT
  CLAIM: WHAT WAS DELIBERATELY NOT DONE, so the boundary is legible.
    (1) No configuration class edited. `aetheric_frame_configuration.py` is
    untouched - EPIC-2026-08-01-configuration-surface-uniformity holds a
    design-only boundary over that surface pending an owner ruling on shape.
    (2) `system_state` was NOT widened to `Optional[Union[str, SystemState]]`
    even though `with_system_state` accepts both. It is an existing parameter,
    not an absence, and widening it is a public API change nobody asked for.
    The policy annotation WAS widened, and the difference is that the new
    reader creates a round-trip that would otherwise fail typecheck.
    (3) `Rift.create_frame_link` is documented `Internal` in its docstring
    while the generated agent documentation and `src_architecture_payload`
    both describe it as the public attachment step. That is the nexus/rift
    marker drift the owner already ruled a defect; not touched here.
    (4) `tests/_frame_posture_test_support.py` and the tests that use private
    seams were not rewritten to use the new door.
  EVIDENCE:
    - context_compass/tickets/epics/2026-08-01_configuration_surface_uniformity_epic.md:38-43
    - src/melder/nexus/rift/rift.py:447-450
    - src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:411
  IMPACT: Three follow-ups exist and are named rather than silently absorbed.
  NEXT: Owner rules whether any of them open as their own lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
`Spellbook.configure_aether_frame` carried 2 of the 14 frame-posture builders,
and because the posture object is book-owned with no public accessor, the other
12 were unreachable from `import melder`. Two of them are gate keys:
`rift_enabled` (default False) gates AR onto a frame entirely, and
`ai_native_enabled` gates codegen rooms - so the public package could not
configure a frame to host a Rift. Widened the facade to 14/14 rather than
exposing the collaborator, keeping the owner's facade rule intact.
`system_state` is applied first, deliberately, because `ai_native`'s dynamic
requirement is checked at freeze. Separately, `Conduit.set_new_policy` was
write-only; added `Conduit.policy` and widened the writer's annotation to
`Union[str, Policies]` so read-then-write round-trips under mypy. 25 component
tests added, including a reflective one that fails if the door ever narrows
again. Three files changed, 191 insertions, 6 deletions. NOT RUN - sandbox is
Python 3.10, melder requires >=3.14; the owner's 3.14t run is the exit gate.
