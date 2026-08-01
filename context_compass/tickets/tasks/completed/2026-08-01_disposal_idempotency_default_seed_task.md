# Task: FINDING-1 - disposal is unreachable because defaults consume its set-once write

## Metadata
- Task ID: TASK-2026-08-01-disposal-idempotency-default-seed
- Status: review
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Parent: EPIC-2026-08-01-ux-aix-harness-red-remediation
- Created: 2026-08-01T11:18:00Z
- Updated: 2026-08-01T12:58:00Z

## Problem / Opportunity
4 of the 7 harness reds. `disposal` and `disposal_method_names` are declared
set-once, but the default loader pre-seeds both by writing the property dict
DIRECTLY. The seed consumes the single allowed write, so every later public write
is refused. On a default-constructed `Spellbook` the documented route to enabling
teardown cannot work at all.

## Context
Teardown is advertised as core to Melder's correctness contract, and the README
sells automatic teardown as a headline capability. This defect makes the public
route to it unreachable. It was surfaced by four independent tier callers, which is
the tier working exactly as intended.

## Ticket Contract
- ENTRY_GATE: source-evidenced root cause (below). MET.
- EXECUTION_BOUNDARY: `spellbook_configuration.py` and the two spellbook call sites
  ONLY, and ONLY after an owner ruling. Public semantics - patch docs required
  before any edit per patch_framework_gating.md.
- DEPENDENCIES: owner ruling between the three options below.
- EXIT_GATE: the 4 reds green; `configure_aether_frame(disposal=...)` usable on a
  default-constructed book, or explicitly declared not-a-supported-path; docstrings
  agree with behavior; canonical docs updated if semantics change.
- FAILURE_ESCALATION: BLOCKER if the fix would widen the public surface.

## Applicable Anti-Patterns
- Rewriting the four callers to work around the defect and calling it fixed.
- Silently relaxing the idempotency rule without deciding what set-once MEANS.

## Requirements
- Functional: a user who constructs `Spellbook()` normally must be able to enable
  disposal through a documented public route, OR the docs must stop promising it.
- Non-functional: no change to the resolution hot path; `disposal` bookkeeping must
  stay off it, per the existing `Creations` split of live vs disposable registries.

## Acceptance Criteria
- [ ] Owner has chosen option A, B or C below.
- [ ] `set_property("disposal", ...)` behavior matches its own docstring.
- [ ] `with_defaults()` docstring's "call it FIRST and override afterwards" is
      either TRUE or corrected.
- [ ] The four reds pass on an owner 3.14t run.

## Risks / Mitigations
- RISK: removing the seed breaks `validate()` for configs that never call
  `load_default_dictionary()`. MITIGATION: `_validate_required_properties_exist`
  already backfills `_OPTIONAL_PROPERTY_DEFAULTS`; confirm whether disposal belongs
  there before removing it from the eager defaults dict.
- RISK: relaxing idempotency weakens a deliberate safety rule. MITIGATION: option B
  keeps set-once for USER writes and only exempts the default seed.

## Validation Plan
Owner runs the harness plus `pytest tests/component/melder/aether/conduit -q` on
3.14t. That component suite is the one that currently compensates for this defect,
so it is the regression surface that matters most.

## Notes

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: ROOT CAUSE, three linked facts. (1) `_idempotent_keys = {"disposal",
    "disposal_method_names"}`. (2) `set_property` refuses when
    `key in self._idempotent_keys and key in self._properties` - it tests PRESENCE,
    not provenance, so it cannot tell a user write from a default seed.
    (3) `load_default_dictionary()` seeds `disposal: False` and
    `disposal_method_names: []` by writing `self._properties[key] = value`
    DIRECTLY, bypassing `set_property` entirely. Therefore the first public write
    always arrives second and is always refused.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:148
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:232-233
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:576-585
  IMPACT: Not a tier problem. Any user following the documented order hits it.
  NEXT: Confirm the blast radius on the public surface (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: BLAST RADIUS - this reaches a method whose own docstring says
    "Public API". `Spellbook.configure_aether_frame(*, system_state, disposal,
    disposal_method_names, system_caching_enabled=None)` takes `disposal` as a
    REQUIRED keyword and calls `configuration.set_property("disposal", disposal)`.
    A default-constructed `Spellbook` loads defaults during `__init__`
    (`_initialize_configuration` -> `load_default_dictionary()`), so by the time a
    user can call this method the seed is already in place. Passing ANY bool -
    True or False - raises `RuntimeError`. Only `disposal=None` survives, by
    skipping the branch. A documented public parameter is therefore unusable on
    the default path.
  EVIDENCE:
    - src/melder/aether/spellbook/spellbook.py:5854-5862
    - src/melder/aether/spellbook/spellbook.py:5900-5907
    - src/melder/aether/spellbook/spellbook.py:5281-5282
  IMPACT: Raises this from "examples are wrong" to "a public API method cannot be
    called with its own documented arguments".
  NEXT: Establish whether ANY working path exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: A WORKING PATH EXISTS, AND THE TEST SUITE ALREADY KNOWS ABOUT IT. The
    reachable order is: construct a bare `SpellbookConfiguration()`, set disposal
    FIRST, then load defaults (the loader only fills keys `not in _properties`), then
    hand the object to `Spellbook(configuration=...)`. The component suite does
    exactly this and documents why, verbatim: "disposal settings are set before
    defaults to respect idempotency". So the behavior has been observed and silently
    compensated for in tests rather than reported as a defect - which is why the
    green suite never caught it and four tier examples did.
  EVIDENCE:
    - tests/component/melder/aether/conduit/test_conduit_component_creations.py:47
    - tests/component/melder/aether/conduit/test_conduit_component_creations.py:56-60
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:583-585
  IMPACT: Confirms this is a CONTRACT/ORDERING defect, not a total breakage - and
    that the required order is the exact REVERSE of what `with_defaults()` documents
    ("Applies the standard local rich-config defaults in place, overwriting anything
    set earlier, so call it FIRST and override afterwards"). The docstring actively
    leads users into the refusal.
  NEXT: Owner ruling between A, B, C.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Three compliant options. I recommend A.
    OPTION A - stop seeding idempotent keys. Remove `disposal` and
    `disposal_method_names` from the `load_default_dictionary()` defaults dict and
    let `_validate_required_properties_exist` backfill them at validate() time if
    still absent. The user's first write then wins, set-once keeps its plain
    meaning, and `with_defaults()`'s docstring becomes true. Smallest semantic
    change; the backfill machinery already exists.
    OPTION B - make idempotency provenance-aware: track which keys were seeded by
    defaults and let exactly one USER write override a seed. Preserves the current
    default-population behavior but adds state and a subtler rule.
    OPTION C - declare the current behavior correct, fix the `with_defaults`
    docstring to say disposal must be set BEFORE defaults, and rewrite the four
    callers. Zero runtime risk, but leaves `configure_aether_frame(disposal=...)`
    permanently broken on the default path, which I do not think is acceptable for
    a method marked Public API.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:446-458
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1063-1064
  IMPACT: A and B change public semantics and need patch docs before implementation.
    C is docs-plus-examples only.
  NEXT: OWNER RULING. No edit until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T12:20:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: OWNER CHALLENGED MY RECOMMENDATION AND THE OWNER IS RIGHT. OPTION A IS
    WITHDRAWN - it is the option that breaks the most, and one grep I should have
    run BEFORE recommending proves it. `_OPTIONAL_PROPERTY_DEFAULTS` contains
    exactly ONE key (`generalized_singleton_specialization_enabled`). Every other
    entry in `available_properties` - INCLUDING `disposal` and
    `disposal_method_names` - is HARD-REQUIRED at validate():
    `_validate_required_properties_exist` raises "Missing required configuration
    property" for any absent key not in that one-item optional set. So removing
    disposal from the defaults seed would make `with_defaults()` produce a config
    that CANNOT VALIDATE. My "smallest semantic change" would have broken the
    defaults path outright.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:438-440
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:453-458
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:136-142
  IMPACT: This inverts the finding. Defaults MUST populate every hard-required key
    - that is their job - which means defaults are COMPLETE, and a complete
    configuration is terminal by construction. The idempotency rule is not fighting
    the defaults; it is what makes "defaults" mean something. The owner's framing is
    the correct one: `with_defaults()` is a TERMINAL act ("I want the standard set,
    done"), not a base layer to override. The two paths are alternatives - take
    defaults, OR set your own values then freeze - and they were never meant to
    compose.
  NEXT: Re-scope this task to the two things that are actually wrong (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T12:20:00Z
  TYPE: DECISION_REQUEST
  CLAIM: RE-SCOPED. Under the corrected model the runtime is RIGHT and two smaller
    things are wrong.
    (1) DOCSTRING TEACHES THE BACKWARDS MODEL. `with_defaults()` says it "applies
    the standard local rich-config defaults in place, overwriting anything set
    earlier, so call it FIRST and override afterwards." That sentence invites
    exactly the layering the design rejects, and it is what all four failing callers
    followed. It should say: defaults are complete and terminal; if you intend to
    configure, set your values first and do not call this, or call it and stop.
    (2) `configure_aether_frame(*, system_state, disposal, disposal_method_names,
    ...)` IS THE REAL LEFTOVER. It is marked "Public API" and offers to set disposal
    on a book whose configuration is, by construction, already complete - because
    `Spellbook.__init__` loads defaults for any book not handed a configuration. So
    the method advertises a required keyword that can never be used on the path that
    reaches it. Under the corrected model that is not an idempotency bug, it is a
    method offering an operation its own design forbids.
    OPTIONS FOR (2): (i) drop `disposal`/`disposal_method_names` from that
    signature - configuration belongs to the configuration object, not to a
    post-hoc frame verb; (ii) keep them but document that they only apply to books
    constructed WITH an explicit configuration, and make the refusal message say so;
    (iii) leave as-is and rely on the four examples being rewritten.
    I am NOT recommending one this time until you tell me whether that method is
    meant to configure at all, because that is a design intent question and I just
    demonstrated what happens when I infer intent from prose.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1063-1064
    - src/melder/aether/spellbook/spellbook.py:5854-5862
    - src/melder/aether/spellbook/spellbook.py:5281-5282
  IMPACT: The four failing callers are now EXAMPLE defects, not library victims -
    they follow a docstring that teaches a model the library does not have. The
    library change, if any, is small and confined to one method's surface.
  NEXT: Owner ruling on (2)(i/ii/iii); then rewrite the four callers to the
    configure-then-freeze shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T12:20:00Z
  TYPE: RISK
  CLAIM: PROCESS FAILURE WORTH RECORDING, because it will repeat otherwise. I
    treated a docstring as the contract, inferred a defect from it, and proposed
    changing RUNTIME SEMANTICS to match prose. policy_skills.md's authority order
    puts code LAST as a source of truth, but a docstring is not a design ruling
    either - and I had neither. The invariant that decides the whole question
    (`_OPTIONAL_PROPERTY_DEFAULTS` being a one-item set) was one grep away and I
    recommended before running it.
  EVIDENCE:
    - agent_onboarding/default/general/policies/policy_skills.md:126-131
  IMPACT: Recommendations must be gated on the invariant that constrains them, not
    on the narrative that surrounds them.
  NEXT: For the remaining findings, establish the constraining invariant BEFORE
    posting an option table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:34:00Z
  TYPE: FACT
  CLAIM: FINDING-5, raised by the owner and confirmed: the invariant I leaned on in
    the note above is itself a scar, not a design. `_OPTIONAL_PROPERTY_DEFAULTS`
    exists to exempt EXACTLY ONE key, and that key is not user configuration.
    Four facts. (1) NOT THE SAME KIND OF THING: the other four properties are
    user-facing world behavior (disposal, disposal_method_names, phase-scheduler
    workers/timeout); `generalized_singleton_specialization_enabled` tunes a
    phase-11 codegen internal - the generalized no-overrides hydration lane. It
    configures the COMPILER, not the user's world. (2) NO PUBLIC AUTHORING SURFACE:
    every other property has a fluent setter (`with_disposal`,
    `with_disposal_method_names`, `with_phase_scheduler_workers`,
    `with_phase_scheduler_barrier_timeout`). This one has NONE - the only way to set
    it is `set_property("generalized_singleton_specialization_enabled", True)` by
    raw string. It sits in the public property registry with no public way to author
    it. (3) THE READER DOES NOT NEED IT REGISTERED: `_specialization_enabled_for_spell`
    checks `has_property(...)` and returns False, wraps the whole read in
    `except (RuntimeError, KeyError, AttributeError) -> False`, and documents that
    "a missing flag must behave exactly like OFF". Absence is already correct
    behavior by design. (4) THEREFORE THE REGISTRATION CAUSED THE MECHANISM: being
    in `available_properties` makes validate() hard-require it; hard-requiring an
    opt-in perf flag broke hand-assembled configs; so a ClassVar dict, a backfill
    loop, and a documented contract clause were added to exempt one key - the
    docstring says exactly that ("never fail validation over optional optimization
    flags").
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:141-144
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:438-455
    - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:540-573
  IMPACT: The required-vs-optional split in `SpellbookConfiguration` is not a
    designed distinction. It is the accommodation of one internal flag placed in a
    user-facing registry. That matters for the disposal question because I cited
    that split as an invariant - it is real, but it is load-bearing scar tissue
    rather than intent.
  NEXT: Establish the constraining invariant BEFORE proposing removal (next note) -
    the discipline I said I would apply after the Option A error.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T12:34:00Z
  TYPE: UNKNOWN
  CLAIM: The constraint that decides whether the flag can simply be DEREGISTERED is
    the recorded-config reload lane, and I have not yet verified it. If a sealed
    world recorded `generalized_singleton_specialization_enabled` in its property
    payload, `load_recorded_dictionary` would replay that key into a registry that
    no longer contains it - and `set_property` raises `KeyError: Unknown
    SpellbookConfiguration property` for unregistered keys. Whether the reload lane
    routes through `set_property` or writes `_properties` directly, and whether it
    reports-and-skips unknown keys, is UNVERIFIED. Until that is read, "just remove
    it from available_properties" is a HYPOTHESIS, not a plan.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:228-231
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:587-600
  IMPACT: Deregistering could break restore of any world sealed while the key was
    registered. That is a persistence-compatibility question, not a config-tidiness
    one.
  NEXT: Read `load_recorded_dictionary`'s unknown-key handling; then propose.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T13:18:00Z
  TYPE: FACT
  CLAIM: DOCS NOT UPDATED, AND THE DOCSTRING IS WRONG IN TWO INDEPENDENT WAYS - I
    had only isolated one. The `with_defaults()` contract block says it "applies
    the standard local rich-config defaults in place, OVERWRITING ANYTHING SET
    EARLIER, so call it FIRST and override afterwards."
    (1) "overwriting anything set earlier" is FLATLY FALSE. The loader is
    `for key, value in defaults.items(): if key not in self._properties:
    self._properties[key] = value` - it PRESERVES existing values and writes only
    absent ones. The docstring states the exact opposite of the code.
    (2) "call it FIRST and override afterwards" is the advice that FOLLOWS from
    that false claim, and it is false for the set-once pair.
    THE IRONY WORTH RECORDING: the working path - set disposal BEFORE defaults -
    only works BECAUSE the docstring is wrong. If `with_defaults()` actually
    overwrote as documented, the component suite's workaround would fail too, and
    so would the example fixes made under this epic. The code is right; the prose
    describes a DIFFERENT function, one that overwrites and supports layering.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1062-1064
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:583-585
  IMPACT: The cause of all four reds is STILL PRESENT in source. The example fixes
    route around it; they do not remove it. The next reader who follows that
    contract block walks into the same refusal.
  NEXT: Owner decision - this is a `src/` edit and the lane is scope-locked to
    examples, so I will not touch it unsolicited.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:18:00Z
  TYPE: HYPOTHESIS
  CLAIM: A LIKELY ORIGIN, offered as hypothesis not fact. There are TWO config
    classes carrying a `with_defaults()` verb, and they have OPPOSITE semantics.
    `AethericFrameConfiguration`'s version genuinely IS destructive - its own docs
    say "later `with_defaults()` silently RECOMPUTES this back to the..." and
    "DESTRUCTIVE. This is `with_defaults()` followed by...". `SpellbookConfiguration`'s
    version preserves. Same verb, opposite behavior, and the spellbook one is
    documented AS IF it were the frame one. That is a plausible copy-across, and
    it is also a live trap independent of this bug: an agent or user who learns
    the verb on one class will be wrong about the other.
  EVIDENCE:
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:725,1334,1362
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:583-585
  IMPACT: If true, fixing only the spellbook docstring leaves the naming collision
    that produced it.
  NEXT: Owner call. Not investigated further - frame-config internals are outside
    this lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T13:18:00Z
  TYPE: FACT
  CLAIM: BLAST RADIUS OF THE BAD PROSE IS BOUNDED. `SpellbookConfiguration.
    with_defaults()` is not mentioned in README.md, src_architecture.md, or
    src_components.md - the only `with_defaults` references in the canonical docs
    are the CRYSTALLIZER's and MUTATION-RESEARCH's own versions, which are
    different objects. So no user-facing or canonical document teaches the
    layering pattern; the wrong instruction lives only in the docstring itself.
  EVIDENCE:
    - README.md
    - context_compass/system_docs/src_components.md:656,2943,2958
  IMPACT: A docstring-only fix would close the whole documented surface. No
    canonical doc update is required.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Artifact Links (Optional)
- none yet; options A and B require patch docs before implementation.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Context / Handoff Summary
Root cause proven, blast radius proven, working path proven, and the test suite's
own comment proves the behavior was already known. Blocked on an owner ruling
between A, B and C. Nothing edited.
