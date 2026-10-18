# Component patch: Binding Pipeline - the spell_id is the target's code digest (spell_identity_is_the_code_2026_10_18)

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Component: Binding Pipeline (Bind, Spell, SpellIndex) - `Bind.__init__`, `Bind.cleanup`, `Bind._bind_logic`,
  `Bind.spell_id_inspector`; `Bind.sha256_profile`, `Bind._fingerprint_repr_text` and `Bind._fingerprint_default_text`
  removed; the new `SpellCodeDigest`; `Spellbook.inspect_spell` (stage-3 text) and the three collision refusals
  (remedy text); the docstrings that define the spell_id (architecture patch, "Statements That Define the spell_id
  Today", rows marked S1)
- Status: draft - for the owner's approval
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T13:21:00Z
- Updated: 2026-10-18T13:21:00Z

## Component Purpose and Boundary
- Current boundary: `_bind_logic` builds the general profile, resolves the disposal names, normalizes the managed
  options, then computes `Bind.sha256_profile(binding_profile, spellframe=..., spell_name=..., binding_name=...,
  existence=..., disposal_method_names=..., resolvable=...)` and uses it as `SpellIndex(initial_id=...)` and
  `Spell(spell_id=...)`, all under Bind's lock (`src/melder/aether/spellbook/bind/bind.py:605-893`). The fingerprint
  reads the shallow binding profile - for a class its name, qualname, module, base and MRO names, annotation keys,
  method names and constructor signature text; for a callable its signature, parameter defaults and address-free
  repr; for an object its type and address-free repr - then the bind call, in the hash domain `v4-binding` or
  `v4-binding-non-resolvable` (`bind.py:1011-1129`). It reads no method body.
- Target boundary: at the same point and under the same lock, `_bind_logic` computes
  `spell_id = self._spell_code_digest.spell_id(spell)` from the target alone
  (code_description_patch_spell_code_digest.md).
  The binding profile is still built - validation, the spell type, disposal matching and Nexus publication read it -
  and is no longer hashed. The bind call's values stay on the Spell as today; S2 gathers them into the binding manifest.

## Before/After Behavior Summary
- Before (probe F1-F5 on 0.2.8254): an edited method body keeps the id and staging the edit is refused as a collision
  (F1); a parameter added to a method keeps it (F2); two lambdas with different bodies share it (F5); a constructor
  default (F3) and a rename (F4) move it. One class bound under two binding names, or staged under two existences, is
  two ids and two spells.
- After: every code change is a new id (P1-P10, I1-I9, E01-E34, D1-D4); docstrings, comments and blank lines are not;
  the bind call changes nothing. The same object bound again under any binding has the same id, and the collision
  refusals that exist today stop the second registration (bind and bind_inactive: `spellbook.py:5405-5420`,
  `:5754-5769`; conjure: `spellbook.py:2803-2840`).
- `Bind.spell_id_inspector(spell)` returns the id bind gives that target, whatever binding it is bound with, so
  `Spellbook.inspect_spell` stage 3 finds any registered object by its code (`spellbook.py:2638-2640`; its docstring
  says stage 3 "rarely matches", `:2540-2546`).

## Interface Deltas
- Inputs: `Bind.spell_id_inspector(spell: Any) -> str`. The keywords `spellframe`, `spell_name`, `binding_name`,
  `existence`, `disposal_method_names`, `resolvable` and the four `managed_spell_*` are removed: the id has no binding
  input, and the managed checks the inspector ran are bind's admission, not identity. Internal API - Bind is kernel
  and users call the Spellbook; its only src caller passes the target alone (`spellbook.py:2638-2638`).
- `Bind.sha256_profile`, `Bind._fingerprint_repr_text` and `Bind._fingerprint_default_text` are removed; nothing
  outside bind.py calls them (searched: src/melder).
- Outputs: `Spell.spell_id` and the SpellIndex's initial id are the code digest - 64 hex characters, as before.
- Error semantics: unchanged - every refusal of `_bind_logic` happens where it happens today, and the digest raises
  for no input (code-description patch: a target too deeply nested falls back to today's repr rule). The collision
  refusals keep their logic; their remedy text changes in this landing - "differentiate the binding with a distinct
  spellframe or binding_name" stops working once the binding leaves the id - and S4 makes them name the existing
  registration.

## State and Lifecycle Deltas
- Owned state: `Bind` gains the slot `_spell_code_digest: SpellCodeDigest`, built in `__init__` and, in `cleanup`
  under the lock, cleaned (its memo cleared) and deleted with the other owned fields. SpellCodeDigest owns one weak
  memo of code-object digests and nothing else.
- `spell_id_inspector` stays static and builds a fresh SpellCodeDigest per call: no shared memo, no lock, no state
  left behind.
- Spell and SpellIndex: no field changes.

## Failure Mode Deltas
- New failure mode: none at bind. A second registration of one object under another binding is now refused by the
  existing collision checks (it was accepted as a second spell) - the intended one-object rule, Breaking for callers
  that bound one class or function under several names, existences or Books of one process.
- Removed failure mode: F1 (an edited class refused as a collision of its old version), F2 and F5.
- Changed failure mode: the three collision messages' remedy (see Interface Deltas).

## Dependency and Ordering Constraints
1. Lands with S2 in one pass: the creation cache keys structural payloads by spell_id because "the spell id already
   covers the spell's own signature, names, existence and resolvability" (`structural_snapshot.py:258-287`), its
   world stamp is spell ids, posture and borrowed ids (`:289-323`), the executor tier's full hit is decided by spell
   ids and that stamp (`spellbook_creation_system.py:616-740`), and emitted plans trust that disposal facts "compose
   into the spell fingerprint" (`generalized_manifest_no_overrides_compiler.py:99-101`). Without S2 a binding changed
   under one spell_id could replay a plan built for the old binding.
2. The spellbook.py edits (inspect_spell's text, the three refusal texts) wait for spellbook.py to come back from
   melder_1 (M1-31, S8's landing).
3. The test moves follow the blast-radius classification (architecture patch, step 2).

## Validation Expectations
- Unit, Bind (`tests/unit/melder/spellbook/bind/`): the id equals `SpellCodeDigest().spell_id(target)` for a class,
  a function, a lambda, a bound method and an existing object; one id across spellframes, binding names, existences,
  disposal lists, resolvable and managed settings; `spell_id_inspector` equals bind's id; cleanup is idempotent and
  drops the digest.
- Unit, SpellCodeDigest: the code-description patch's validation list.
- The 14 test files that name the fingerprint today move to the new rule: test_bind.py (61 references),
  test_bind_managed_spell_options.py (12), test_stable_spell_fingerprint.py (8), test_binding_profile_strategy.py (4),
  test_inherited_disposal_binding.py (3), test_ordered_disposal_binding.py (3),
  test_spellbook_component_resolvable_registration.py (2), test_spellbook.py (2), test_bind_lifecycle_hooks.py,
  test_spell_id_process_stability.py, test_spellbook_component_bind.py, test_ordered_disposal_replay.py,
  test_type_checking_annotation_introspection.py and test_deferred_annotations.py (one each).
- Integration: the F1 loop (edit, bind_inactive, notch, meld the new version); a second bind of one class under
  another name refused with the corrected remedy; `inspect_spell` stage 3 finding an object bound in another Book.
- Probes on src: probe_fingerprint_reads_code (F1-F5 now as the owner wants), probe_code_digest_cases,
  probe_code_digest_design_edges.

## Unknowns and Open Decisions
- DECISION_REQUEST (owner): third-party code and objects (architecture patch).
- UNKNOWN: how many tests outside the 14 bind one object twice (the blast-radius run measures it).

## Context / Handoff Summary
- What changed: nothing in `src/`; the prototype measured the rules and the cost (S1's MEASURE note, the D probe).
- Remaining risks: the bind cost of classes over large third-party bases (D9); records holding one object twice (S5).
- Next entrypoint: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic` (the fingerprint call at 795-803).
