# Story: bind-kwargs pass-through to the spell object

## Metadata
- Story ID: STORY-2026-07-19-bind-kwargs-transplant
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-19T14:12:00Z
- Updated: 2026-07-19T14:12:00Z
- Patch lane: system_docs/patches/active/bind_kwargs_spell_transplant_2026_07_19/

## Objective
Owner ruling (2026-07-19, twice refined): bind(**kwargs) leftovers - after the hook
transfers pop - are construction arguments FOR THE USER'S SPELL OBJECT, carried
opaquely and passed into it at creation. Rejection authority is the spell object's
own signature. Teaching lands in the INTERMEDIATE tier (owner: "its an intermediate
job").

## Ticket Contract
- ENTRY_GATE: architecture patch in the lane above (owner-refined semantics:
  spell-object payload, NOT binding metadata; precedence spell_override > payload >
  signature defaults; instance spells reject non-empty payloads).
- EXECUTION_BOUNDARY: bind capture -> Spell carriage -> creation consumption ->
  crystal record -> tests -> intermediate example + probe flips. NOT decision A
  (DuplicateSpellNameStrategy) - separate ruling, still open.
- EXIT_GATE: owner 3.14t green incl. new rows; harness probes flipped (silent-swallow
  pin replaced by delivery/rejection/precedence rows); intermediate example teaching
  the feature.
- FAILURE_ESCALATION: DECISION_REQUEST if the codegen seams force semantic
  compromises (e.g., positional __args__ interaction with payload merge).

## Implementation map (investigated 2026-07-19, session f)
1. CAPTURE: Spellbook._add_hooks_to_spell (spellbook.py:4924) reads only the three
   hook keys and IGNORES the rest - split into hook attachment + payload capture at
   the _bind_logic call site; instance-profile spells raise on non-empty payload
   (authority: nothing constructs).
2. CARRIAGE: Spell gains a construction-payload slot (+cleanup +describe surface).
3. CONSUMPTION (the deep part): meld spell_override normalizes via
   Meld._normalize_spell_override (meld.py:1128) into kwargs-dict or
   {"__args__": [...]} feeding a SOCKET-KEYED map consumed by compiled executors;
   a split helper reshapes per socket. The payload must act as the spell's BASELINE
   kwargs wherever it constructs - including as a DEPENDENCY - so consumption
   belongs at creation-compile time: the codegen compilers
   (spell_compiler/codegen_creation_system/strategies/* and
   shared_assets/creation_runtime_door_compiler.py) assemble constructor calls per
   spell and must merge stored payload under socket overrides (per-key; meld
   override wins; __args__ positional override replaces payload wholesale -
   document). The no_overrides fast lane stays byte-identical for spells WITHOUT
   payloads (zero cost for the common case).
4. RECORD: SpellCrystal captures the payload (JSON-serializable verbatim;
   non-serializable -> honest marker) so restored worlds construct identically;
   restore/rebuild parity test.
5. TESTS: bind-family unit rows (capture/validation/instance rejection), creation
   rows (class ctor delivery, callable call delivery, dependency-position delivery,
   precedence vs spell_override, __args__ interaction), crystal round-trip row.
6. UX: intermediate example (bind-site config without factories) + probe flips
   (test_probe_bind_swallows_unknown_kwargs_silently replaced by delivery +
   signature-rejection rows).

## Notes
- DATETIME: 2026-07-19T14:31:00Z
  TYPE: MEASURE
  CLAIM: LANDED (owner: "lets see what happens") - the deep seam ALREADY EXISTED:
    Spell._mutation_override is a persistent stored-override payload meld consumes
    when the caller passes no spell_override (conduit_meld.py:303; caller REPLACES
    stored = the exact ruled precedence). Bind payload rides that lane. CODE: (1)
    Spell.receive_bind_construction_payload (beside apply_mutation_override) - fresh
    dict copy into _mutation_override; no dynamic-runtime guard (spell being born in
    the bind transaction); bind never interprets keys. (2) Spellbook.bind BOTH sites
    (4471/4762): hooks -> _add_hooks_to_spell unchanged; non-hook remainder pushes
    into the spell untouched. (3) 4 unit rows: payload-on-spell verbatim, payload
    reaches object at meld, spell_override replaces per call, typo fails via the
    OBJECT's signature. compile green x3. pytest Not run - owner 3.14t. HONEST
    SCOPE: (a) consumption scope = existing mutation-override scope (root melds);
    dependency-position delivery via phase-11 stays the open acceptance bar; (b)
    instance-profile rejection not yet enforced (stored-but-inert on instance
    spells; next slice); (c) bind payload overwrites a pre-existing restored
    mutation_override - ordering ruling needed if both lanes live on one spell.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1237-1237
  - src/melder/aether/conduit/meld/conduit_meld.py:300-306
  - tests/unit/melder/aether/spellbook/test_bind_construction_payload.py:1-105
  IMPACT: bind(spell=SmtpMailer, host=..., port=...) works end to end for root
    melds on the house stored-override lane.
  NEXT: Owner: pytest tests/unit/melder/aether/spellbook/test_bind_construction_payload.py -q
    then full suite; remaining slices: phase-11 dependency delivery, instance
    rejection, crystal record, tier-02 example, probe flips.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T14:22:00Z
  TYPE: MEASURE
  CLAIM: Owner said SEND IT + refined once more: kwargs must NOT unfold into bind -
    bind pops its three reserved hook keys and PUSHES the untouched remainder into
    the Spell; the Spell carries it; the spell object's signature judges. Design
    locked. Implementation investigation went one seam deeper and STOPPED at the
    honest line: build_package (spell_codegen_creation_cache.py:99) confirms
    constructor assembly is PHASE-11 COMPILER OUTPUT - spell_codegen_plan/model
    objects emitted as code objects + IR rows with a marshal-safe cache above them.
    Consumption therefore lands in the phase-11 plan/model builders (both lanes:
    no_overrides fast lane must stay byte-identical for payload-free spells;
    overrides lane merges payload under socket overrides), NOT in the cache layer
    and NOT at meld entry (root-only = broken for dependency construction, the
    acceptance bar). This is multi-file compiler surgery requiring full context
    headroom; session f is at its working-room tail after five landed waves.
    DECISION: no code landed this wave - a half-understood compiler edit is the
    exact failure mode the probe-vs-guess lesson of today exists to prevent.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:99-150
  IMPACT: The story now carries the COMPLETE seam map down to the phase-11
    boundary; the next session opens here and lands capture + carriage +
    compiler consumption + record + tests + the tier-02 example in one wave.
  NEXT: Fresh-context wave: (1) Spell payload slot + receive verb (spell.py:61
    class); (2) bind split at spellbook.py:4737 region (hooks -> _add_hooks_to_spell
    unchanged; remainder -> spell verb; instance profile rejects non-empty); (3)
    phase-11 plan/model payload inlining (read strategies/generalized compilers
    FIRST); (4) SpellCrystal record field + restore parity; (5) tests incl.
    dependency-position delivery; (6) intermediate example + probe flips.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


## Context / Handoff Summary
Beginner harness is 51/51 green and pinned the current silent-swallow behavior -
those pins are the regression floor this story flips. Do NOT start consumption at
the meld root only: dependency-position construction is the acceptance bar.
