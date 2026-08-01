# Task: Config structural survey - classify every divergence intentional vs accidental

## Metadata
- Task ID: TASK-2026-08-01-config-structural-survey
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Parent: EPIC-2026-08-01-configuration-surface-uniformity
- Created: 2026-08-01T13:32:00Z
- Updated: 2026-08-01T13:50:00Z

## Problem / Opportunity
Before anything is normalized, every divergence must be classified INTENTIONAL
(load-bearing, keep it) or ACCIDENTAL (drift, erase it). Normalizing a
load-bearing difference would break the runtime; leaving an accidental one keeps
the user confusion the epic exists to remove.

## Ticket Contract
- ENTRY_GATE: epic open, survey pass 1 recorded. MET.
- EXECUTION_BOUNDARY: READ ONLY. No config edited under this task.
- DEPENDENCIES: none to classify; owner ruling needed before any edit.
- EXIT_GATE: every structural divergence classified with source evidence.
- FAILURE_ESCALATION: BLOCKER if a divergence cannot be classified from source.

## Applicable Anti-Patterns
- Normalizing a difference because it is a difference, without asking what it buys.

## Acceptance Criteria
- [ ] Every storage/lifecycle/verb divergence classified with evidence.
- [ ] The ACL/codegen config family surveyed (not yet done).
- [ ] A target surface proposed that keeps every INTENTIONAL divergence intact.

## Notes

- DATETIME: 2026-08-01T13:50:00Z
  TYPE: FACT
  CLAIM: THE OWNER IS RIGHT THAT SPELLBOOK AND FRAME ARE MECHANICALLY DIFFERENT,
    and the difference is load-bearing - it must NOT be normalized away. Both use
    `__slots__`, but they store values in opposite ways.
    SPELLBOOK: its slots hold `_properties` (a dict), `available_properties` (a
    runtime type registry) and `_idempotent_keys` (a set). The VALUES live inside a
    dict behind a generic key-value API - `set_property(key, value)` with runtime
    type checking against the registry. It is an extensible policy BAG.
    FRAME: its slots hold the fourteen values DIRECTLY as named fields
    (`_system_state`, `_ai_native_enabled`, `_rift_enabled`,
    `_shared_framewide_spellbook_configuration`, `_system_caching_enabled`,
    `_system_cache_root_path`, the seven `_disable_*` brakes, and
    `_max_transaction_wait_time_in_seconds`). No dict, no registry. Values are read
    as PLAIN ATTRIBUTES (`frame_configuration.disable_linking`), not dict lookups.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:70-77
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:90-109
    - src/melder/aether/aetheric_frame/aetheric_frame.py:696-712
  IMPACT: These are two different KINDS of object, not two styles of the same
    object. Forcing one storage model on both would either put a dict lookup plus
    registry type-check on the frame's gate reads, or strip the spellbook config of
    its extensible bag. Both are losses.
  NEXT: Establish WHY the frame needs direct fields (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:50:00Z
  TYPE: FACT
  CLAIM: THE FRAME CONFIG'S DIVERGENCE IS DRIVEN BY ROLE, and the role is
    identity-critical in a way the spellbook config's is not.
    (1) IT IS THE WORLD'S POSTURE, ONE PER FRAME, SETTLE-ONCE. The canonical
    architecture states settlement mutates the RETAINED posture object IN PLACE and
    rebinds the SAME object, and that it must never mint a parallel one: handed a
    DIFFERENT object while unfrozen, `bind_frame_configuration` copies twelve
    attempted values onto the canonical posture and then calls `cleanup()` on the
    donor. Object IDENTITY is part of the contract.
    (2) ITS FIELDS ARE LIVE-READ BY THE RUNTIME. The `disable_*` gates are
    documented as live reads, and the recorded posture propagates
    `max_transaction_wait_time_in_seconds` into the live transaction mediator at
    bind. These are runtime gate reads, not authoring-time lookups.
    A user-facing policy BAG (spellbook) and a runtime POSTURE read on transaction
    paths (frame) have genuinely different needs. This divergence is INTENTIONAL.
  EVIDENCE:
    - context_compass/system_docs/src_architecture.md:1278-1317
    - src/melder/aether/aetheric_frame/aetheric_frame.py:696-712
  IMPACT: Uniformity must be pursued at the SURFACE, not the STORAGE. Users never
    touch storage; they touch verbs.
  NEXT: Correct the owner's mental model on "devops config" (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:50:00Z
  TYPE: FACT
  CLAIM: THERE IS NO DEVOPS CONFIG CLASS. The owner referred to "devops config" as
    a separate thing that is "probably fine". Searched: no class matching `*Config*`
    exists anywhere under `src/melder/aether/aetheric_frame/dev_ops/`, and no
    config file lives there. The DevOps knobs are the SEVEN `disable_*` brakes that
    live ON `AethericFrameConfiguration` - exactly the family the tier cheatsheet
    prints as "devops brakes". So "devops config" is not a separate object that is
    fine; it is half of the frame posture, which is the one object the owner
    correctly flagged as mechanically different.
  EVIDENCE:
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:101-107
    - UX_and_AIX_experiences/03_advanced/07_frame_posture_cheatsheet.py
  IMPACT: Any plan that treats devops config as separately safe would be
    normalizing the frame posture by accident. Worth correcting before scope is set.
  NEXT: Survey the ACL/codegen family, then propose the uniform surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T13:50:00Z
  TYPE: UNKNOWN
  CLAIM: SCOPE HONESTY - the owner asked me to read all their code and I have NOT
    read 14,300 LOC line by line. What is DONE: a structural survey of all 9 root
    configs (storage model, lifecycle verbs, fluent surface counts, idempotency,
    reload lanes) and a MECHANICAL deep read of the two the owner flagged
    (spellbook, aetheric_frame) sufficient to classify their divergence. What is
    NOT done: line-by-line reads of nexus_configuration (1847), crystallizer (1063),
    aether (771), external_persistence_manager (919), rift (568), and the entire
    ACL/codegen family (~3,600 LOC across 6 files). Their per-knob semantics are
    UNKNOWN and I will not assert they are "safe to modify" on a structural glance -
    the frame config looked like just another config from the outside too.
  EVIDENCE:
    - tickets/epics/2026-08-01_configuration_surface_uniformity_epic.md
  IMPACT: A uniformity sweep planned on structure alone would repeat today's Option
    A error at a much larger blast radius.
  NEXT: Read the remaining configs before any normalization plan is finalized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:50:00Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: PROPOSED TARGET - UNIFORM SURFACE OVER DIVERGENT STORAGE.
    OBJECTIVE: a user learns ONE config vocabulary and it works everywhere.
    CONSTRAINTS: mypy strict, no suppressions, frame posture identity and live-read
    performance preserved, spellbook's extensible bag preserved.
    KNOWN: storage divergence between spellbook and frame is intentional; the
    surface divergence is not.
    UNKNOWNS: per-knob semantics of the six unread configs.
    THE PROPOSAL: leave storage alone. Unify the three things users actually touch.
    (1) ONE AUTHORING VERB SET. Every config gets fluent `with_*` for every knob -
    generated at build time from a per-module schema so it cannot drift. Today the
    counts run 0 to 26 and users fall back to raw-string `set_property` on some
    configs and typed methods on others.
    (2) ONE LIFECYCLE VOCABULARY, with the same word meaning the same thing
    everywhere: validate / freeze / finalize / activate / cleanup. Today finalize is
    on 6 of 9 and activate on 3 of 9, with no stated rule for which get them.
    (3) ONE SET OF VERB SEMANTICS. `with_defaults()` currently means PRESERVE on
    spellbook and DESTRUCTIVE-RECOMPUTE on frame. Same word, opposite behavior, on
    the two objects a user meets first. That single collision is the most likely
    source of the hair-pulling the owner described, and it is pure accident.
  EVIDENCE:
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:725,1334,1362
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:583-585
  IMPACT: Users get one mental model; the runtime keeps the two storage models it
    actually needs. No hot-path cost, no identity risk.
  NEXT: Owner reaction to surface-not-storage before I read the remaining six.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T14:05:00Z
  TYPE: FACT
  CLAIM: CATALOGUE DELIVERED - 8 numbered diffs, all source-read. Three corrections
    to my own earlier survey, which is why cataloguing was the right call over
    proposing a rebuild.
    (1) FOUR storage models, not three. `aether_configuration` carries a
    `_properties` dict (18 refs) but exposes NO `set/get/has_property` API at all -
    the dict is private machinery while every other dict-backed config publishes
    it. Same storage, opposite exposure. I had lumped it with the registry camp.
    (2) THE SAME JOB HAS THREE NAMES. Recorded-reload is `from_recorded_payload`
    (aether), `from_recorded_posture` (frame), `load_recorded_dictionary`
    (spellbook/crystallizer/mutation/nexus), and is ABSENT on rift and epm. Pure
    naming drift over an identical job.
    (3) `with_defaults()` EXISTS WITHOUT A DEFAULTS LOADER. The verb is on 7
    configs; `load_default_dictionary()` on only 3. So one public promise has four
    private implementations and no shared contract.
    Also catalogued: `activate()` marks a real hidden class (the three hosted
    singleton roots) that is simply undocumented; `describe()` on 3 of 8 despite
    the crystallizer twin model treating describe() as the interface; lock spread
    73 down to 4.
  EVIDENCE:
    - artifacts/2026-08-01_configuration_diff_catalogue.md
    - src/melder/aether/aether_configuration.py
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py
  IMPACT: The headline finding is that the uniformity problem is NOT the storage
    layer, which is where both the owner and I started looking. Users never see
    storage. They see verbs, and the verbs are where the drift is: one job with
    three names, one name with two meanings, and no written rule for which object
    gets which verb.
  NEXT: Owner reads the catalogue and rules which ACCIDENTAL diffs to converge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T15:25:00Z
  TYPE: BLOCKER
  CLAIM: "MIRROR, DO NOT INVENT" BLOCKS MOST OF THIS - THERE IS NO SINGLE MODEL TO
    MIRROR. My catalogue said "describe() on 3 of 8". Reading them, they are THREE
    DIFFERENT METHODS WITH THREE DIFFERENT NAMES DOING THREE DIFFERENT JOBS:
    - `describe_posture` (aetheric_frame) - diagnostics/logging, plain scalars,
      explicitly "for diagnostics, logging, and conflict reporting".
    - `describe_configuration_payload` (mutation_research) - the RECORDING twin
      payload, value-coerced so the persisted surface cannot drift between
      emission seams. A persistence contract, not a dump.
    - `describe_presence` (external_persistence_manager) - PRESENCE FLAGS, and it
      is that way by necessity: epm holds USER CALLABLES, and the record stores
      callables as presence flags only.
    These are not one verb spelled three ways. They are three jobs. There is no
    canonical `describe()` to copy onto the missing five.
    SECOND BLOCKER: ZERO slot-based configs have a property API. Adding
    `get_property`/`has_property` to aetheric_frame or epm would require inventing
    a name-to-slot mapping that exists NOWHERE in this repo - which is precisely
    the "adding new shit" the owner just forbade.
  EVIDENCE:
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1969-1985
    - src/melder/mutation_research/mutation_configuration.py:479-497
    - src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py
  IMPACT: Proceeding would mean picking a winner among three semantics and
    inventing a mechanism for slot configs - both are design decisions wearing the
    costume of a mechanical change.
  NEXT: Owner ruling on WHICH describe (or whether it is 2-3 named verbs), and
    whether slot configs get a property API at all.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T15:25:00Z
  TYPE: PLAN
  CLAIM: WHAT IS CLEANLY MIRRORABLE TODAY, with zero invention, if the owner wants
    movement while the above is ruled:
    (1) `aether_configuration` gains `get_property`/`has_property`. It ALREADY has
    the `_properties` dict (18 refs) and is the only dict-backed config hiding it.
    The implementation is copied verbatim from spellbook/crystallizer/mutation.
    True mirror, low risk, no new concept.
    (2) `describe_configuration_payload` onto the other dict-backed configs
    (spellbook, crystallizer, nexus, rift), mirroring mutation_research's
    implementation exactly - they share the dict storage it iterates, so it ports
    without adaptation. This is the RECORDING verb, which is also the one the
    crystallizer twin contract actually needs.
    BLOCKED until ruled: any describe on the slot-based configs, and any property
    API on slot-based configs.
  EVIDENCE:
    - src/melder/aether/aether_configuration.py
    - src/melder/mutation_research/mutation_configuration.py:479-497
  IMPACT: Two real conformance wins available immediately, both pure mirrors.
  NEXT: Owner go-ahead on (1) and (2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Artifact Links (Optional)
- artifacts/2026-08-01_configuration_diff_catalogue.md (promote_to_documentation)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Context / Handoff Summary
Spellbook-vs-frame divergence classified INTENTIONAL with evidence: bag vs posture,
authoring-time vs live-read, replaceable vs identity-critical. There is no devops
config class - those are the frame's seven brakes. Six configs remain unread and
are NOT cleared for modification. Proposal on the table: uniform surface, divergent
storage.
