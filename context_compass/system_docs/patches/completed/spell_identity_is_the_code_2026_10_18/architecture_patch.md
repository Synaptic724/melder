# Architecture patch: spell_identity_is_the_code_2026_10_18

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Status: approved - the owner's word to land S1 with S2's cache keys (chat 2026-10-18; the epic's DECISION note
  of 2026-10-18T15:01:53Z) approves this patch; updated for his decisions of 2026-10-18. S1's and S2's component
  patches and S1's code-description patch are in this folder; S3-S5 add theirs before their code.
- Owner: user (direction and calls, chat 2026-10-18); melder_0 (synaptic_python_developer) (patch)
- Created: 2026-10-18T13:21:00Z
- Updated: 2026-10-18T17:05:55Z
- Ticket: EPIC-2026-10-18-spell_identity_is_the_code; its first story is
  STORY-2026-10-18-spell_id_hashes_the_object_code (S1)

## Patch Scope and Non-Goals
- Objective: the owner's direction (chat 2026-10-18). A spell_id is the SHA256 of the registered object's code - its
  methods and constructor with their bodies, its class-level values, the code it inherits and, for an existing
  object, its data - and of nothing from the bind call. Docstrings, comments, blank lines and line numbers never move
  it; any real code change does, so every edit is a new version an agent can stage and notch. The bind call becomes a
  binding manifest with its own hash (S2) that revalidates the spell when it changes (S3); one object is one spell
  (S4); every spell_id moves once (S5).
- The owner's calls (chat 2026-10-18): (1) a base class's code counts; (2) class-level values are code - "a change
  anywhere is a change"; (3) an existing object is its class's code plus its data; (4) a renamed local variable
  counts; (5) the scope of a registration stays the existing spell-id regime.
- The owner's decisions (chat 2026-10-18): the "conduit manifest" reading confirmed (S2 keys the creation cache on
  each spell's binding hash, S3 revalidates on a change); installed third-party code and objects named by
  qualified name and distribution version (decision B; a configurable later); a record holding one object twice
  restores the first and files a shortfall per dropped duplicate (S5); one object is strictly one spell for now -
  the explicit duplicate bind (S6) is parked - and S1 lands now with S2's cache keys.
- Example: `class Greeter` with `def greet(self, name): return "hi " + name`, bound under the name `greeter`.
  - Today its id hashes Greeter's names, bases, method names and constructor signature, then the spellframe, the
    binding name, the existence and the disposal names. Editing `greet`'s body keeps the id, so staging the edited
    class is refused as a collision (probe F1); binding Greeter again as `greeter2` mints a second id - two spells.
  - After: its id hashes Greeter's module, qualname and bases and the code of `greet` - its instructions and the
    constant "hi ". Editing the body moves the id (a new version); a docstring or a comment does not; binding Greeter
    again under any name or existence gives the same id, and the second registration is refused.
- Non-goals:
  - The managed pool's release routing (set aside by the owner).
  - How versions coexist, notch and are followed by borrowers (the 2026-10-14/15 rulings stand).
  - The spell-id regime itself (call 5): unique per process by default, per frame under per-frame ids.
  - An explicit duplicate bind (S6, parked by the owner) and binding or caching patterns users choose
    (EPIC-2026-10-18-identity_and_caching_configurables, parked).
  - Code a spell names but does not hold: a module-level helper its methods call, a class used in a method body, a
    class held as a class-level value (named, unless nested in it) - probes D7 and D8. Those are other objects;
    when they are spells, their own ids move.
  - melder_1's lane (STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers) and the other correctness stories.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCodeDigest (new: `src/melder/aether/spellbook/bind/spell_code_digest.py`) | add | the canonical code and data encoding and the spell_id; installed third-party code named by distribution version (decision B) (code_description_patch_spell_code_digest.md) | none |
| Binding Pipeline: `Bind` (`__init__`, `cleanup`, `_bind_logic`, `spell_id_inspector`; `sha256_profile`, `_fingerprint_repr_text`, `_fingerprint_default_text` removed) | modify | the spell_id is the target's code digest; Bind owns one SpellCodeDigest | SpellCodeDigest |
| Spell Examination Profiles: `fingerprint_repr`, `default_fingerprint_repr` and their builders | modify (remove) | they exist only for the retired fingerprint | Binding Pipeline |
| Spellbook: `inspect_spell` (stage-3 docstring and comments); the bind, bind_inactive and conjure-integrity refusals (remedy text) | modify (text) | stage 3 becomes an exact lookup; "differentiate the binding" stops being a remedy | spellbook.py back from melder_1 (S9; M0-196, M1-36) |
| Docstrings that define the spell_id (Spell, AetherConfiguration, LookupContainer, Aether, three meld docstrings) | modify (text) | they call it a bind-time fingerprint | Binding Pipeline |
| Binding manifest (S2, new: `src/melder/aether/spellbook/bind/binding_manifest.py`; `Spell` builds, carries and describes it) | add | the bind call as a value record with its own SHA256, the binding hash (component_patch_binding_pipeline.md, S2 section) | S1 (same landing); spell.py back from melder_1 (M0-196, M1-36) |
| Creation cache (S2): the structural key and the world stamp carry the binding hash; generation 23; the docstrings that trust the spell_id to cover the binding | modify | they rely on the spell_id covering the binding (component_patch_creation_cache.md) | Binding manifest |
| Crystallizer record (S2, on the owner's word): `SpellCrystal` records the binding hash; `RecordVersion` 4.3.0; `RestoreReport` and `RestoreEngine` report a binding a restore rebuilt differently; restore and graft docstrings | modify | the owner (chat 2026-10-18): "make sure you land the binding hash going into crystallizer too" (component_patch_crystallizer_record.md) | Binding manifest |
| Revalidation on binding change (S3), one registration per object (S4), migration (S5) | per story | the epic's other stories | S1, S2 |
| Bind-guard manifest (generated) | modify | SpellCodeDigest and BindingManifest join it: 628 -> 630 entries | SpellCodeDigest, Binding manifest |

## Interface and Boundary Deltas
- Public behaviour (Breaking, S1 and S2 in one landing): every spell_id moves once, and from then on it
  - moves for: a method or constructor body, a parameter, a default, an annotation, a class-level value, a nested
    class, a decorator's code, a closure's captured value (a factory-made class), a renamed local variable, a base
    class's code outside the standard library, an existing object's data;
  - stays for: docstrings, comments, blank lines, line numbers, the order a class body defines its members in,
    runtime specialization, sys.monitoring and sys.settrace, the same source executed twice;
  - ignores the bind call: spellframe, binding name, existence, disposal names, resolvable and the managed settings
    leave the id and become S2's binding manifest.
- Consequence under call 5: today's duplicate-id refusals become the one-object rule. Binding an object again -
  under another name, existence or spellframe, in another Book, or (under the default process-wide regime) in another
  frame - is refused: in the Book at bind, frame-wide once the other Book is conjured, otherwise at the second
  conjure ("Conjure refused: ... already registered"). A class, a function or an equal-data object is one spell per
  process by default, per frame under per-frame ids; another conduit shares it (a link, a contract, a cluster)
  instead of binding it again. Two lambdas with the same code and defaults, and two existing objects of one class
  with equal data (D10), are one spell. This holds strictly for now (the owner, 2026-10-18): no option registers
  one object twice, and the corrected refusals name none (S6 parked).
- Binding (S2, same landing): every Spell carries `binding_manifest` - its spellframe and kind, address, existence,
  disposal names, resolvable and managed settings - and `binding_hash`, their SHA256, read-only
  (`BindingManifest.describe()` gives them as plain data), and both creation-cache tiers key on the binding hash
  beside the spell_id. The SpellCrystal records the binding hash (record 4.3.0) and a restore reports each binding
  it rebuilt differently from the record (component_patch_crystallizer_record.md, on the owner's word).
- Interpreter: ids follow the compiled instructions, which differ between Python minor versions and under -O; the
  interpreter's cache tag (`cpython-314` on 3.14.7t) is hashed in. Ids of the GIL and the free-threaded build of one
  version: UNKNOWN (only 3.14.7t is on the device).
- Internal: `Bind.sha256_profile` is removed and `SpellCodeDigest.spell_id(target)` replaces it; `Bind` owns one
  digest (its code-object memo) and cleans it; `Bind.spell_id_inspector(spell)` keeps its name and loses its binding
  keywords; binding profiles lose `fingerprint_repr` and `default_fingerprint_repr`.
- `Spellbook.inspect_spell` stage 3 becomes an exact lookup: an object's re-derived id is the id it was registered
  under, whatever its binding.

## Cross-Component Invariants
1. `spell_id = SHA256("v5-code\n" + sys.implementation.cache_tag + "\n" + encoding(target))`, the encoding being the
   code-description patch's contract; no bind input enters it.
2. Byte-identical across processes, hash seeds and GIL modes for the same code, data and interpreter (measured on
   3.14.7t: E01-E34 and D1-D10, hash seeds 1 and 2, GIL 0 and 1).
3. No source-file read at bind. Code-object digests are memoized (code objects are immutable); class, function and
   object encodings are computed at each bind (they are mutable: an object is hashed as it is at bind, and a
   class-level dict mutated at runtime moves the id, E33).
4. No target code runs while digesting: reads go through type and instance dictionaries, `object.__getattribute__`
   and `inspect.getattr_static`. The only calls into objects are `repr()` (`InspectorUtility.stable_repr`) of a
   target with no Python-visible state, today's rule, and of an object of an installed third-party class
   (invariant 8). An object with neither Python-visible state nor an informative repr cannot be told from another
   of its type, today as after (D6).
5. With identity the code, today's duplicate-id refusals are the one-object rule: bind and bind_inactive (the Book's
   `_spell_ids` and `Aether._check_for_spell`, its process-wide sweep included) and conjure's integrity check. The
   frame's one-active-spell-per-address claim is unchanged.
6. Locks: the digest runs inside Bind's lock, where the fingerprint runs today; SpellCodeDigest takes no lock and
   keeps no strong reference to a target (its memo keys are weak).
7. (S2, same landing) No cache tier or emitted fact keyed by spell_id is read without the binding hash: the
   structural key carries the spell's binding hash and the world stamp every pool and borrowed spell's, so a
   binding changed under one spell_id never replays a plan or a row built for another binding.
8. Installed third-party code (decision B): a class, metaclass or function whose module file lies under an
   installed site-packages directory, and is not standard library, is named by qualified name and distribution
   version, never digested; an object of such a class is named by its type, that version and its address-free
   repr. Application code - the project's own modules, `__main__`, editable installs - is digested. A package
   upgrade moves the ids of the spells that inherit from or hold its code; nothing else of the package enters an
   id.

## Migration and Rollout Order
1. This patch, S1's component patches (Binding Pipeline, Spell Examination Profiles) and S1's code-description
   patch, approved by the owner's word to land (2026-10-18T15:01:53Z) and updated for his decisions; S1's
   section -> implementation -> validation mapping note.
2. A blast-radius run in a /tmp mirror, nothing in the repository edited: the prototype digest in place of the
   fingerprint, the whole tree with the GIL off and on, every failure classified (a test that registers one object
   twice, a pinned id, a message text, a real defect) and reported before any src edit. Done 2026-10-18:
   101 new failures with the GIL off and on, none a Melder defect (S1's MEASURE note).
3. S2's component patches - the binding manifest (component_patch_binding_pipeline.md, S2 section) and the cache
   keys with generation 23 (component_patch_creation_cache.md); the "conduit manifest" reading is confirmed.
4. spell.py and spellbook.py back from melder_1 by message once S9 lands: the owner chose the refusal, so S9
   lands first as 0.2.8256 (M1-37); S1 and S2 are built and run in a /tmp mirror until then. S8 is on hold.
5. One landing pass for S1 and S2, each with its notch above the latest landed (two consecutive numbers): red tests
   (P1-P10, I1-I9, E01-E34 and D1-D10 as regression tests) -> src -> green -> the moved tests -> the whole tree, GIL
   off and on -> bind cost on the gauntlet -> the release-note entry (Breaking) -> system documents, indexes and
   graph -> rebuild last, both checks OK. The three refusals' remedy text is corrected in the same pass; it is false
   from that landing on.
6. S3, then S4 (the refusal names the existing registration and S3's verb), then S5 (records, research history,
   docs), each after its own patch.

## Rollback Strategy
- Rollback trigger: a regression in binding, restore or the creation cache that the landing cannot fix forward.
- Rollback steps: revert the S1+S2 change set as one (they land together); ids return to the v4-binding fingerprint;
  bundles go cold once more (the release changes); a record made under v5 restores through bind, and the restore
  maps its recorded ids to the live ones as it does today.
- Post-rollback verification: the bind, restore and cache suites and the F1-F5 probe on the reverted tree.

## Validation Expectations and Evidence Plan
- Unit (SpellCodeDigest): one symptom-named test per rule of the code-description patch, drawn from P1-P10, I1-I9,
  E01-E34 and D1-D10 (for example `test_editing_a_method_body_changes_the_spell_id`,
  `test_a_docstring_or_comment_does_not_change_the_spell_id`,
  `test_two_lambdas_with_different_bodies_are_two_spells`); a subprocess test for hash-seed stability.
- Unit (Bind): the spell_id does not depend on spellframe, binding name, existence, disposal names, resolvable or
  the managed settings; `spell_id_inspector` equals bind's id; `inspect_spell` stage 3 finds a registered object.
- Integration: an edited class staged with bind_inactive gets a new spell_id and notches (F1); a second bind of one
  class under another name is refused with the corrected remedy; a docstring-only edit is refused as the same spell;
  restore and graft of a world recorded after the change.
- Cost: bind before and after on the gauntlet's bind-heavy worlds; the src/melder corpus (782 targets: today median
  0.064 ms, prototype cold median 0.29 ms and warm 0.11 ms); a class over a large third-party base (D9, digested:
  2.6-3.2 ms cold, 1.9 ms warm, against 0.03 ms for a plain class), which decision B names instead - a
  site-packages check and a distribution-version lookup (about 0.2 ms; 14.7 ms once per SpellCodeDigest when
  `packages_distributions()` is needed, measured on the device) - measured on src at landing.
- Evidence sources: `artifacts/spell_identity_20261018/` (code_digest_v2.py, the E and D probes and their runs) and
  `artifacts/correctness_defects_20261017/` (F1-F5, P1-P10, I1-I9).

## Statements That Define the spell_id Today
Each is corrected in the landing that makes it false.

| where | statement | story |
|---|---|---|
| `src/melder/aether/spellbook/bind/bind.py` (Bind, `_bind_logic`, `spell_id_inspector`, `sha256_profile`) | the fingerprint contract | S1 |
| `src/melder/aether/spellbook/spell.py:121-121`, `:157-157`, `:347-347`, `:382-385` | "generated from its bind-time fingerprint", "structural fingerprint" | S1 |
| `src/melder/aether/spellbook/spellbook.py:2540-2546`, `:2581-2588`, `:2609-2613` | `inspect_spell` stage 3 "rarely matches" | S1 |
| `src/melder/aether/spellbook/spellbook.py:2827-2840`, `:5414-5420`, `:5763-5769` | the refusals' remedy "differentiate the binding" | S1 (remedy), S4 (naming) |
| `src/melder/aether/aetheric_frame/lookup_container.py:24-28` | "the binding signature is folded into the spell_id" | S1 |
| `src/melder/aether/aether.py:2589-2595` | the process-wide sweep comment | S1 |
| `src/melder/aether/aether_configuration.py:105-108`, `:606-609` | the regime's description | S1 |
| `src/melder/aether/conduit/meld/conduit_meld.py:307-308`, `meld.py:453-454`, `spellspace_meld.py:266-267` | "SHA256 structural fingerprint for the SpellIndex" | S1 |
| `structural_snapshot.py:264-268`, `generalized_manifest_no_overrides_compiler.py:99-101`, `generalized_manifest.py:190-193` | "the spell id covers existence / disposal" | S2 |
| `spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`, `caching_system.py:CachingSystem` (class docstring) | the world stamp is "pool ids, posture, borrowed ids" | S2 |
| `meld.py:2080-2080`, `:2161-2161`, `contract/details.py:198-198`, `:434-434`, `inspector_utility.py:72-72` | "SHA256 fingerprint", "the bind fingerprint" (a full sweep of src/ for "fingerprint" at landing) | S1 |
| `restore_engine.py` (`RestoreReport.map_identity`, `RestoreEngine._replay_books_and_binds`, `_bind_one_active`, `_bind_one_staged`, `_map_spell_identity`, `_replay_contracts`, `_replay_one_contract`), `graft_runner.py` (`_bind_selected`, `_merge_members`) | "receiving policy can change the new SHA" | S1 (with S2's record patch) |
| the crystallizer's record and restore docs, the system documents, the README | recorded ids | S5 |

## Ticket Coverage Map
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Stories: STORY-2026-10-18-spell_id_hashes_the_object_code (S1, this folder's first component patches),
  STORY-2026-10-18-binding_manifest_hash (S2), STORY-2026-10-18-revalidate_on_binding_change (S3),
  STORY-2026-10-18-one_registration_per_object (S4), STORY-2026-10-18-spell_id_migration (S5);
  STORY-2026-10-18-explicit_duplicate_binding (S6) is parked in the backlog.
- Tasks: none yet.

## Unknowns and Decision Requests
- DECIDED (owner, 2026-10-18; S2): the "conduit manifest" - each spell's binding hash is recorded in what the
  conduit builds and caches that spell from, and a changed hash revalidates and rebuilds that spell (S2 keys the
  cache on it; S3 revalidates).
- DECIDED (owner, 2026-10-18; S1): B - installed third-party code and objects are named by qualified name and
  distribution version (invariant 8); a configurable for it waits in
  EPIC-2026-10-18-identity_and_caching_configurables. Applied to a third-party object as its type, that version
  and its address-free repr - today's rule for an object, plus the version - because type and version alone
  would make two differently configured library objects (two engines, two clients) one spell, and strict
  uniqueness would then refuse the second; the owner accepted this reading as written (chat 2026-10-18:
  "those 3 things for library version are fine").
- DECIDED (owner, 2026-10-18; S5): a record holding one object twice restores the first registration and files a
  shortfall per dropped duplicate.
- DECIDED (owner, 2026-10-18): one object is strictly one spell for now; the explicit duplicate bind (S6) is
  parked in the backlog and the refusals name no duplicate option.
- Derived from the calls, for the owner to know rather than decide: a closure's captured values count, so two
  classes a factory makes with different captured values are two spells; equal-data objects are one spell; code a
  spell only names is not part of its id (D7, D8); and one object binds once per process by default (call 5), so a
  second Book of the same process that binds the same class is refused and should share it instead.
- UNKNOWN: whether the GIL build and the free-threaded build of one Python version compile identical instructions
  (the device has 3.14.7t only); until measured, ids are documented as per interpreter build.
- MEASURED (2026-10-18, step 2): the blast radius is 101 new failures with the GIL off and on, none a Melder
  defect (S1's MEASURE note); S1 without S2's keys replays the creation cache across bindings (S2's MEASURE
  note); a class's id must skip `__annotate_func__` while it is None (code-description patch).
- RISK (until S3 lands): a rebind under another slotted existence - `cleanup_spell`, then `bind` as
  `unique_per_conduit` of a class bound `unique` - keeps its spell_id, and its first meld returns the object
  the removed definition left in its slot (S3's FACT note); listed in the release note unless S3 lands in
  the same release.
- RISK (until S5 lands): a record written before S1 that holds one object twice fails to restore at its second
  replayed bind (component_patch_crystallizer_record.md, Failure Mode Deltas).

## Context / Handoff Summary
- What changed: nothing in `src/`; the prototype (code_digest_v2.py) and its probes, outside the repository's code,
  measured the rules and the cost (S1's MEASURE note; the D probe's runs).
- What changed since (2026-10-18T15:40:03Z): the owner's word to land S1 with S2's cache keys and his decisions
  (Unknowns and Decision Requests); S2's patches written (the binding manifest, the creation cache).
- What changed since (2026-10-18T16:32:46Z): the blast radius measured (step 2); the owner's word to land the
  binding hash in the SpellCrystal and his acceptance of the third-party reading; the crystallizer record patch.
- What remains: spell.py and spellbook.py back from melder_1 after S9 (0.2.8256; M1-37); the landing pass
  (step 5).
- Next entrypoint: component_patch_binding_pipeline.md, component_patch_creation_cache.md,
  component_patch_crystallizer_record.md, then code_description_patch_spell_code_digest.md.
