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

## Context / Handoff Summary
Beginner harness is 51/51 green and pinned the current silent-swallow behavior -
those pins are the regression floor this story flips. Do NOT start consumption at
the meld root only: dependency-position construction is the acceptance bar.
