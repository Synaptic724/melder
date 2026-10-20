"""melder_0, 2026-10-18: promote S1 and S2 (0.2.8257-0.2.8258) into src_components.md - one all-or-nothing pass.

The Binding Pipeline (the spell_id rule, the binding manifest, the older fingerprint entries marked superseded),
Spellbook Core (creation cache generation 23, the one-object refusals, `inspect_spell`'s stage 3), the Crystallizer
(record 4.3.0, the restore's binding changes), Spell Examination Profiles (the fingerprint-only fields removed), the
bind flow, two subcomponents, the code map, the package inventory, the sources and the handoff summary. The index is
regenerated after.
"""
import sys

from docs_common import DocsRecord

CHANGED = {
    "src/melder/aether/spellbook/spellbook.py": None,
    "src/melder/aether/spellbook/spellbook_creation_system.py": None,
    "src/melder/aether/spellbook/bind/bind.py": None,
    "src/melder/aether/spellbook/bind/spell_index.py": None,
    "src/melder/aether/spellbook/spell.py": None,
    "src/melder/aether/aether.py": None,
    "src/melder/aether/aether_configuration.py": None,
    "src/melder/crystallizer/crystals/spell_crystal.py": None,
    "src/melder/crystallizer/crystal_loader_system/restore_engine.py": None,
    "src/melder/crystallizer/crystal_loader_system/graft_runner.py": None,
    "src/melder/crystallizer/persistence/record_version.py": None,
    "src/melder/aether/conduit/meld/meld.py": None,
    "src/melder/aether/conduit/meld/conduit_meld.py": None,
    "src/melder/aether/conduit/meld/spellspace_meld.py": None,
    "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py": None,
    "src/melder/aether/aetheric_frame/lookup_container.py": None,
    "src/melder/aether/conduit/conduit_ward/contract/details.py": None,
    "src/melder/utilities/caching_system/caching_system.py":
        "Generation 23, the binding hash in the structural key and the world stamp (0.2.8258).",
    "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py": None,
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/"
    "generalized_manifest_no_overrides_compiler.py": None,
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/"
    "generalized_manifest.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py": None,
}
DIGEST = "src/melder/aether/spellbook/bind/spell_code_digest.py"
MANIFEST = "src/melder/aether/spellbook/bind/binding_manifest.py"


class LandDocsComp(DocsRecord):

    def identity_entry(self) -> str:
        body = (
            "Spell identity and the binding manifest (2026-10-18, 0.2.8257-0.2.8258; S1 and S2 of "
            "EPIC-2026-10-18-spell_identity_is_the_code, on the owner's direction - \"the bind signature shouldn't "
            "impact the spells identity\" - and his calls): `Bind` owns one `SpellCodeDigest` (`_spell_code_digest`, "
            "built in `__init__`, cleaned and deleted in `cleanup` under the lock), and `_bind_logic` takes "
            "`spell_id = self._spell_code_digest.spell_id(spell)` where it called `sha256_profile(...)`, at the same "
            "point and under the same lock. The binding profile is still built - validation, the spell type, "
            "disposal matching and Nexus publication read it - and is no longer hashed; `sha256_profile`, "
            "`_fingerprint_repr_text` and `_fingerprint_default_text` are removed. The id is the SHA256 of "
            "`v5-code`, `sys.implementation.cache_tag` and the target's encoding: a class is its module, qualname, "
            "metaclass and bases and, per class of its MRO, its own namespace digest (standard-library classes "
            "named, installed third-party classes named by distribution version - decision B - any other "
            "digested); a namespace is every entry but interpreter bookkeeping (`__doc__`, `__dict__`, "
            "`__weakref__`, `__firstlineno__`, `__static_attributes__`, `__annotations_cache__`; "
            "`__annotate_func__` while None), sorted; a function is its code digest (the deoptimized instruction "
            "stream with the constants it loads, in first-load order, the argument counts, flags without "
            "CO_HAS_DOCSTRING, the name tables and the exception table - no line numbers, docstring or file "
            "path), its defaults, its annotate function, its closure values and type parameters; an existing "
            "object of application code with Python-visible state is its class's digest plus its slots and "
            "`__dict__` by value; a bound method, partial, enum member, scalar, container or builtin is encoded "
            "as a value; an object of an installed third-party class is its type, distribution version and "
            "address-free repr; anything else its type and address-free repr. So a method body, a parameter, "
            "a default, a class-level value, a decorator's code, a captured value, a renamed local or a base "
            "class's code moves the id, and a docstring, a comment, a blank line, member order or "
            "specialization never does. Code-object digests are memoized per digest, weakly keyed; classes and "
            "objects are encoded at each call, as they are then. The digest never raises for a target (an "
            "unknown value is `opaque:<type>`, data nested past the recursion limit falls back to the repr "
            "rule) and runs no target code but `repr()` of a target with no Python-visible state, of a value "
            "type's object or of an installed third-party object. `spell_id_inspector(spell)` takes the target "
            "alone (its binding keywords and managed checks are removed) and builds a fresh digest per call. "
            "The bind call becomes the Spell's binding manifest: `Spell.__init__` builds "
            "`BindingManifest.build(...)` last from its own arguments - the address keys, the spellframe as "
            "text and its kind, the binding name, the existence, the resolved disposal names in order, "
            "resolvable and the four managed settings - and `binding_hash` is the SHA256 of `v1-binding` and one "
            "`<field>=<repr(value)>` line per field; permissions, hooks, metadata and the frame are not in it. "
            "The manifest is an immutable value record: `Spell.binding_manifest` and `Spell.binding_hash` "
            "survive cleanup like `spell_id`, and `BindingManifest.describe()` gives the fields and the hash as "
            "plain data. The creation cache keys on it (Spellbook Core, generation 23) and the SpellCrystal "
            "records it (Crystallizer, record 4.3.0). With identity the code, the Book's duplicate-id refusals "
            "are the one-object rule (Spellbook Core): one object is one spell, strictly for now (S6 parked). "
            "Cost: +37 to +55 us a bind (the gauntlet's 29 classes; 200 generated classes), conjure and melds "
            "unchanged. Open: a rebind under another slotted existence keeps its spell_id and its first meld "
            "can return the removed definition's slotted object (S3); a record made before 0.2.8257 that holds "
            "one object twice fails at its second replayed bind (S5).")
        evidence = (
            "EVIDENCE: `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest.spell_id`, "
            "`SpellCodeDigest._target_encoding`, `SpellCodeDigest._class_digest`, "
            "`SpellCodeDigest._namespace_digest`, `SpellCodeDigest._function_digest`, "
            "`SpellCodeDigest._code_digest`, `src/melder/aether/spellbook/bind/bind.py:Bind.__init__`, "
            "`Bind.cleanup`, `Bind._bind_logic`, `Bind.spell_id_inspector`, "
            "`src/melder/aether/spellbook/bind/binding_manifest.py:BindingManifest.build`, "
            "`BindingManifest.describe` and `src/melder/aether/spellbook/spell.py:Spell.binding_manifest`, "
            "`Spell.binding_hash`.")
        return self.wrap(body, "", "") + "\n" + self.wrap(evidence, "", "") + "\n\n"

    def binding_pipeline(self) -> None:
        text = self.read(self.COMP)
        text = self.once(text, (
            "- Convert user objects into registered spell metadata with stable index identities.\n\n"
            "Managed options (2026-10-15, 0.2.8242)"), (
            "- Convert user objects into registered spell metadata with stable index identities.\n\n"
            + self.identity_entry() + "Managed options (2026-10-15, 0.2.8242)"), "identity")
        text = self.once(text, "runs once, after the disposal names and\nbefore the fingerprint. Another",
                         "runs once, after the disposal names and\nbefore the spell_id. Another", "managed 1")
        text = self.once(text, (
            "once. `spell_id_inspector` normalizes the four as bind does (it refuses what bind refuses) and hashes "
            "without them.\n"), (
            "once. `spell_id_inspector` normalized the four as bind does and hashed without them. Since 0.2.8257 no "
            "bind input is\npart of the spell_id (`sha256_profile` is removed and `spell_id_inspector` takes the "
            "target alone), and since 0.2.8258\nthe four are binding-manifest fields (Spell identity, above).\n"),
            "managed 2")
        text = self.once(text, (
            "EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`, "
            "`Bind.sha256_profile`,\n`Bind.spell_id_inspector`, `Bind._bind_logic`,\n"), (
            "EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`,\n"
            "`Bind.sha256_profile` (until 0.2.8257), `Bind.spell_id_inspector`, `Bind._bind_logic`,\n"), "managed ev")
        text = self.once(text, (
            "Step 4's member check runs only for `contract`. The fingerprint is unchanged -\n"
            "  the kind is derived from the frame, not hashed.\n"), (
            "Step 4's member check runs only for `contract`. The fingerprint was unchanged -\n"
            "  the kind is derived from the frame, not hashed; since 0.2.8258 it is a binding-manifest field.\n"),
            "kind")
        text = self.once(text, (
            "Pre receives the exact target before reflection. Native policy/profile/fingerprint construction\n"
            "creates the Spell, then activation receives it before profile completion. Book publishes an active\n"), (
            "Pre receives the exact target before reflection. Native policy, profile and spell_id construction (the\n"
            "code digest since 0.2.8257) creates the Spell, then activation receives it before profile completion.\n"
            "Book publishes an active\n"), "callbacks")
        text = self.once(text, "Process-stable fingerprints (2026-09-26):\n", (
            "Process-stable fingerprints (2026-09-26; SUPERSEDED at 0.2.8257 by Spell identity, above: "
            "`sha256_profile`,\n`fingerprint_repr` and `default_fingerprint_repr` are removed, and a function body "
            "moves its spell_id):\n"), "process-stable")
        text = self.once(text, (
            "- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile`, "
            "`Bind._fingerprint_repr_text`,\n  `Bind._fingerprint_default_text`;\n"), (
            "- EVIDENCE (until 0.2.8257): `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile`,\n"
            "  `Bind._fingerprint_repr_text`, `Bind._fingerprint_default_text`;\n"), "process-stable ev")
        text = self.once(text, (
            "  the same. Omitted/True keep the v4-binding hash sequence unchanged; False changes only the domain\n"
            "  to v4-binding-non-resolvable. Method bodies remain outside existing class-version identity.\n"), (
            "  the same. Omitted/True kept the v4-binding hash sequence unchanged; False changed only the domain\n"
            "  to v4-binding-non-resolvable (until 0.2.8257: resolvable is a binding-manifest field since "
            "0.2.8258, no\n  part of the spell_id, which reads method bodies).\n"), "capability")
        text = self.once(text, (
            "- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic`, `Bind.sha256_profile`,\n"
            "  `Bind.spell_id_inspector`; `src/melder/aether/spellbook/spell.py:Spell.resolvable`.\n"), (
            "- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic`, `Bind.sha256_profile` (until "
            "0.2.8257),\n  `Bind.spell_id_inspector`; `src/melder/aether/spellbook/spell.py:Spell.resolvable`.\n"),
            "capability ev")
        text = self.once(text, (
            "- That resolved order participates in the bind SHA and is retained directly by Spell.\n"), (
            "- That resolved order participated in the bind SHA until 0.2.8257 and is a binding-manifest field "
            "since\n  0.2.8258; Spell retains it directly.\n"), "ordered 1")
        text = self.once(text, (
            "  The shallow method_names profile is unchanged. Only a changed resolved disposal list changes the\n"
            "  disposal contribution to the fingerprint; unrelated inherited members do not change spell IDs.\n"), (
            "  The shallow method_names profile is unchanged. Until 0.2.8257 only a changed resolved disposal list "
            "changed\n  the disposal contribution to the fingerprint and unrelated inherited members did not change "
            "spell IDs;\n  since then the list moves the binding hash, never the spell_id, and a base class's code "
            "outside the\n  standard library is part of the spell_id.\n"), "ordered 2")
        text = self.once(text, (
            "- Compute fingerprints and create SpellIndex entries (the stable index that categorizes and targets "
            "spells).\n"), (
            "- Compute the spell_id - the target's code digest (`SpellCodeDigest`, 0.2.8257) - and create SpellIndex "
            "entries\n  (the stable index that categorizes and targets spells); every Spell builds its binding "
            "manifest (0.2.8258).\n"), "responsibilities")
        text = self.once(text, "- Spell: metadata, hooks, dependency placeholders, ownership fields.\n", (
            "- Spell: metadata, hooks, dependency placeholders, ownership fields, the binding manifest "
            "(`binding_manifest`,\n  `binding_hash`, 0.2.8258; value data kept after cleanup).\n"
            "- Bind: one `SpellCodeDigest` (`_spell_code_digest`, 0.2.8257), cleaned and deleted in `Bind.cleanup` "
            "under its lock.\n"), "owned state")
        text = self.once(text, "- ValueError if method/lambda spells are bound with non-unique existence.\n", (
            "- ValueError if method/lambda spells are bound with non-unique existence.\n"
            "- RuntimeError \"Spell ID collision detected: this object is already registered as spell_id <id>. "
            "...\" from\n  `Spellbook.bind` and `bind_inactive` for a second registration of one object, and "
            "\"[SPELLBOOK] Conjure refused: ...\"\n  for one another Book bound where spell_ids are unique "
            "(0.2.8257, the one-object rule; Spellbook Core).\n"), "failure")
        text = self.once(text, (
            "- `src/melder/aether/spellbook/bind/bind.py`\n- `src/melder/aether/spellbook/bind/spell_index.py`\n"
            "- `src/melder/aether/spellbook/spell.py`\n"), (
            "- `src/melder/aether/spellbook/bind/bind.py`\n- `" + DIGEST + "`\n- `" + MANIFEST + "`\n"
            "- `src/melder/aether/spellbook/bind/spell_index.py`\n- `src/melder/aether/spellbook/spell.py`\n"),
            "key files")
        text = self.once(text, "   - Fingerprints the profile and constructs a SpellIndex.\n", (
            "   - Takes the spell_id from the target's code (`SpellCodeDigest`; it fingerprinted the profile until "
            "0.2.8257)\n     and constructs a SpellIndex.\n"), "narrative 1")
        text = self.once(text, "   - Creates a Spell with metadata (existence, permissions, spellframe).\n", (
            "   - Creates a Spell with metadata (existence, permissions, spellframe) and its binding manifest "
            "(0.2.8258).\n"), "narrative 2")
        self.stage(self.COMP, text)

    def spellbook_core(self) -> None:
        text = self.read(self.COMP)
        text = self.once(text, (
            "None by default) and pass them to Bind, which normalizes, refuses and fingerprints them (Component: "
            "Binding\nPipeline); the Conduit facades forward them. Owner stamping - `define_conduit_into_spells` at "
            "conjure, the\n"), (
            "None by default) and pass them to Bind, which normalizes and refuses them; they are binding-manifest "
            "fields since\n0.2.8258, no part of the spell_id (Component: Binding Pipeline); the Conduit facades "
            "forward them. Owner\nstamping - `define_conduit_into_spells` at conjure, the\n"), "core managed")
        gen23 = (
            "Generation 23 (2026-10-18, `binding_manifest_keys`, 0.2.8258): the envelope is unchanged; the "
            "structural key gains each spell's binding hash (`StructuralSnapshot.PAYLOAD_FORMAT` 2, `{format, "
            "spell_id, binding_hash, annotation_refs}`; `payload_well_formed` refuses format 1) and the world stamp "
            "hashes every pool spell and every borrowed spell as `<spell_id>=<binding_hash>`. The spell_id became "
            "the object's code at 0.2.8257 and no longer covers the binding, so a binding changed under one "
            "spell_id - existence, disposal names, address, spellframe, resolvable or managed settings - misses "
            "both tiers for the Book, as a changed spell_id did; a repeat world is a byte-identical full hit, and "
            "a generation-22 bundle is cold once. Residual (RISK, low): a package staged at a meld for an id the "
            "bundle lacked - only after that spell's conjure-end staging failed, which is logged - is replayed by "
            "a later full hit of the stamped world even when the spell was rebound in between; the restaging that "
            "follows any miss replaces it.")
        gen23_evidence = (
            "EVIDENCE: `src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:"
            "StructuralSnapshot.structural_key`, `StructuralSnapshot.world_stamp`, "
            "`StructuralSnapshot.payload_well_formed` and "
            "`src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.")
        anchor = (
            "  already cold-starts it, and the bump records why, as the owner asked (\"you gotta notch the version "
            "for the cache\").\n  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:"
            "CachingSystem.CACHE_VERSION_HISTORY`.\n")
        text = self.once(text, anchor, anchor + self.wrap(gen23, "- ", "  ") + "\n"
                         + self.wrap(gen23_evidence, "  ", "  ") + "\n", "generation 23")
        refusal = (
            "Since 0.2.8257 a duplicate spell id is one object registered twice (the one-object rule): bind and "
            "bind_inactive raise \"Spell ID collision detected: this object is already registered as spell_id "
            "<id>. ...\", naming the rule and the remedies (share it; `cleanup_spell` and bind again to change its "
            "binding; a changed method is a new spell_id to stage and notch), and conjure's integrity check "
            "raises \"[SPELLBOOK] Conjure refused: ... A spell_id is the SHA256 of the registered object's code "
            "...\" for an object another Book of the frame already bound.")
        text = self.once(text, "- RuntimeError for duplicate spell ids or lookup key collisions.\n", (
            "- RuntimeError for duplicate spell ids or lookup key collisions.\n" + self.wrap(refusal, "  ", "  ")
            + "\n"), "core refusal")
        stage3 = (
            "`inspect_spell`'s stage 3 re-derives the object's spell_id with `Bind.spell_id_inspector(spell)` - the "
            "target's code digest, equal to bind's id whatever binding it was bound with - and confirms it with "
            "`Aether._check_for_spell`, so it finds any registered object by its code (0.2.8257; it rarely matched "
            "while the id hashed the bind call).")
        anchor = (
            "  `Aether._check_for_spell` runs with no lock held, because those take frame locks and frame teardown "
            "takes\n  frame -> conduit -> Book.\n")
        text = self.once(text, anchor, anchor + self.wrap(stage3, "- ", "  ") + "\n", "stage 3")
        text = self.once(text, (
            "with a custom `__eq__`), a changed world stamp or a malformed payload is a structural miss and "
            "regenerates\nthrough the unchanged phases. Parity contracts (bind after conjure, notch, remove, "
            "transfer, contract grant,\n"), (
            "with a custom `__eq__`), a changed world stamp or binding hash (0.2.8258) or a malformed payload is a "
            "structural\nmiss and regenerates through the unchanged phases. Parity contracts (bind after conjure, "
            "notch, remove,\ntransfer, contract grant,\n"), "seam")
        self.stage(self.COMP, text)

    def crystallizer(self) -> None:
        body = (
            "Binding hash in the record (2026-10-18, 0.2.8258; S2 of EPIC-2026-10-18-spell_identity_is_the_code, on "
            "the owner's word): `SpellCrystal` captures `Spell.binding_hash` at bind (`binding_hash`; "
            "`describe()[\"binding_hash\"]` for every spell; the slot deleted at cleanup). RecordVersion 4.2.0 -> "
            "4.3.0 (minor: an additive key 4.2 readers ignore; a 4.2 record carries none and is not compared). "
            "`RestoreEngine._bind_one_active` and `_bind_one_staged` call `_record_binding_change(custody_key, "
            "crystal, live_spell)` after their bind (the staged path finds its parked spell with "
            "`find_spell_by_spell_id`): a recorded hash that differs from the rebuilt spell's goes to "
            "`RestoreReport.record_binding_change`, and `RestoreReport.describe()[\"binding_changes\"]` holds "
            "`{<custody key>: {\"recorded\": <hash>, \"live\": <hash>}}`, empty when every binding replayed as "
            "recorded - information only, never a shortfall or a raise: the receiving Book's policy is the rule. "
            "The report writes the dict under its lock (the parallel driver's units write from worker threads, "
            "each its own custody keys) and deletes it at cleanup. Since the spell_id is the code (0.2.8257), a "
            "receiving policy with another disposal order keeps the spell_id and moves the binding hash, so "
            "selections, parked members and contract grants resolve without translation; a spell whose spell_id "
            "moved (its code or the interpreter changed) maps through the identity map as before. A graft reports "
            "no binding change (it has no identity map). Until S5, a record made before 0.2.8257 that holds one "
            "object twice meets the one-object refusal at its second replayed bind and the all-or-nothing restore "
            "rolls back.")
        evidence = (
            "EVIDENCE: `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.binding_hash`, "
            "`src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreReport.record_binding_change`, "
            "`RestoreEngine._record_binding_change` and "
            "`src/melder/crystallizer/persistence/record_version.py:RecordVersion`.")
        text = self.read(self.COMP)
        anchor = "`src/melder/crystallizer/persistence/record_version.py:RecordVersion`.\n\nNamed lesser structure"
        text = self.once(text, anchor, (
            "`src/melder/crystallizer/persistence/record_version.py:RecordVersion`.\n\n" + self.wrap(body, "", "")
            + "\n" + self.wrap(evidence, "", "") + "\n\nNamed lesser structure"), "record")
        text = self.once(text, (
            "- Changed Spell SHAs use the existing RestoreReport translation map. Staged anchors, exact\n"
            "  selected members, and contract grants follow the actual rebuilt binding identities.\n"), (
            "- Changed Spell SHAs use the existing RestoreReport translation map. Staged anchors, exact\n"
            "  selected members, and contract grants follow the actual rebuilt binding identities. Since\n"
            "  0.2.8257-0.2.8258 the order moves the binding hash, never the spell_id; the restore reports it\n"
            "  (`binding_changes`) and the translation map holds only spells whose spell_id moved.\n"),
            "ordered capture")
        self.stage(self.COMP, text)

    def examination_profiles(self) -> None:
        text = self.read(self.COMP)
        text = self.once(text, (
            "- The binding profile's `init_signature` and callable `signature` strings - the text\n"
            "  `Bind.sha256_profile` hashes - use that rendering, so a class whose constructor names such a type\n"
            "  keeps one spell id across processes. `init_signature_object` stays the FORWARDREF signature the\n"), (
            "- The binding profile's `init_signature` and callable `signature` strings - the text\n"
            "  `Bind.sha256_profile` hashed until 0.2.8257 - use that rendering, so a class whose constructor names\n"
            "  such a type kept one spell id across processes; since then the spell_id reads the code, not these\n"
            "  strings. `init_signature_object` stays the FORWARDREF signature the\n"), "profiles 1")
        text = self.once(text, (
            "  source text (`'Decimal'`, `'list[Decimal]'`). `Bind.sha256_profile` hashes the sorted keys, so every\n"
            "  annotated field counts in the spell id, and Nexus publishes the fields. Before, one such name dropped "
            "every\n"), (
            "  source text (`'Decimal'`, `'list[Decimal]'`). `Bind.sha256_profile` hashed the sorted keys until "
            "0.2.8257,\n  so every annotated field counted in the spell id (since then the class's annotate "
            "function's code does),\n  and Nexus publishes the fields. Before, one such name dropped every\n"),
            "profiles 2")
        text = self.once(text, "  - src/melder/aether/spellbook/bind/bind.py:1072-1082\n", (
            "  - `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest._namespace_digest` (the "
            "annotate\n    function since 0.2.8257; the fingerprint read the keys until then)\n"), "profiles 3")
        text = self.once(text, (
            "- Binding profiles carry the fingerprint text beside the display text (2026-09-26): `fingerprint_repr` "
            "on\n"), (
            "- Binding profiles carried the fingerprint text beside the display text (2026-09-26; removed at "
            "0.2.8257 with\n  the fingerprint, their only reader): `fingerprint_repr` on\n"), "profiles 4")
        text = self.once(text, (
            "- Both limits recorded here earlier on 2026-09-26 are fixed: function spell fingerprints hash an\n"
            "  address-free repr (process-stable ids), and class binding-profile annotations keep names unbound at\n"
            "  runtime. A class whose annotations cannot be read at all (not a NameError) still binds with `{}`.\n"
            "  EVIDENCE:\n"
            "  - src/melder/aether/spellbook/bind/bind.py:1083-1099\n"
            "  - src/melder/aether/spellbook/bind/bind.py:1132-1152\n"), (
            "- Both limits recorded here earlier on 2026-09-26 are fixed: function spell fingerprints hashed an\n"
            "  address-free repr (process-stable ids; since 0.2.8257 a function's spell_id is its code, address-free "
            "by\n  construction), and class binding-profile annotations keep names unbound at runtime. A class "
            "whose\n  annotations cannot be read at all (not a NameError) still binds with `{}`.\n"
            "  EVIDENCE:\n"
            "  - `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest._function_digest` (the "
            "fingerprint's\n    repr text until 0.2.8257)\n"), "profiles 5")
        self.stage(self.COMP, text)

    def flows_and_subcomponents(self) -> None:
        text = self.read(self.COMP)
        text = self.once(text, (
            "   - Bind runs pre(reference), then native admission/profile/fingerprint construction.\n"), (
            "   - Bind runs pre(reference), then native admission and profile construction; the spell_id is the "
            "target's code\n     digest (`SpellCodeDigest`, 0.2.8257) and the Spell builds its binding manifest "
            "(0.2.8258).\n"), "flow 1")
        text = self.once(text, "   - Checks native collisions before registering local lookup keys.\n", (
            "   - Checks native collisions before registering local lookup keys - since 0.2.8257 the one-object "
            "rule: a\n     second registration of one object is refused, its message naming the rule and the "
            "remedies.\n"), "flow 2")
        text = self.once(text, "- `Spellbook.bind(...)` and `Bind._bind_logic(...)`.\n", (
            "- `Spellbook.bind(...)` and `Bind._bind_logic(...)`.\n"
            "- The spell_id is `SpellCodeDigest.spell_id(target)` (0.2.8257); the Spell carries its binding manifest "
            "and\n  `binding_hash` (0.2.8258).\n"), "subcomponent 1")
        text = self.once(text, (
            "- `src/melder/aether/spellbook/spellbook.py`\n- `src/melder/aether/spellbook/bind/bind.py`\n\n"
            "### Subcomponent: SpellIndex"), (
            "- `src/melder/aether/spellbook/spellbook.py`\n- `src/melder/aether/spellbook/bind/bind.py`\n"
            "- `" + DIGEST + "`\n- `" + MANIFEST + "`\n\n### Subcomponent: SpellIndex"), "subcomponent 2")
        text = self.once(text, "  619-entry manifest start refusing binds mid-suite with no signal. Preserve\n",
                         "  630-entry manifest (0.2.8257) start refusing binds mid-suite with no signal. Preserve\n",
                         "guard 1")
        text = self.once(text, "  `MANIFEST_ENTRY_COUNT` (619 at 0.2.8215).\n",
                         "  `MANIFEST_ENTRY_COUNT` (630 at 0.2.8257; 619 at 0.2.8215).\n", "guard 2")
        self.stage(self.COMP, text)

    def code_map_inventory_sources(self) -> None:
        missing = [path for path, note in CHANGED.items() if not self.remeasure(self.COMP, path, note)]
        print("not in the component code map:", missing)
        self.add_entry_after(self.COMP, "src/melder/aether/spellbook/bind/bind.py", DIGEST,
                             "`SpellCodeDigest`, the spell_id: the SHA256 of a target's code and data (0.2.8257).")
        self.add_entry_after(self.COMP, DIGEST, MANIFEST,
                             "`BindingManifest`, a spell's binding and its SHA256, the binding hash (0.2.8258).")
        text = self.read(self.COMP)
        text = self.once(text, (
            "- `src/melder/aether/spellbook/bind/bind.py`\n"
            "  Spellbook registration gateway for classes, callables, and concrete objects\n"
            "- `src/melder/aether/spellbook/bind/scan.py` - Frozen payload describing how a decorated object should "
            "be bound later\n"), (
            "- `src/melder/aether/spellbook/bind/bind.py`\n"
            "  Spellbook registration gateway for classes, callables, and concrete objects\n"
            "- `" + MANIFEST + "`\n"
            "  How one spell version is kept, with its own SHA256 (the binding hash), apart from its code\n"
            "- `src/melder/aether/spellbook/bind/scan.py` - Frozen payload describing how a decorated object should "
            "be bound later\n"
            "- `" + DIGEST + "`\n"
            "  The spell_id: the SHA256 of a registration target's code and, for an existing object, its data\n"),
            "inventory")
        text = self.once(text, (
            "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
            "- `src/melder/aether/spellbook/bind/bind.py`\n"), (
            "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
            "- `src/melder/aether/spellbook/bind/bind.py`\n- `" + DIGEST + "`\n- `" + MANIFEST + "`\n"),
            "sources")
        self.stage(self.COMP, text)

    def handoff(self) -> None:
        body = (
            "2026-10-18 spell identity is the code (0.2.8257-0.2.8258; S1 and S2 of "
            "EPIC-2026-10-18-spell_identity_is_the_code): the Binding Pipeline carries the spell_id rule "
            "(`SpellCodeDigest`: what moves an id and what never does, decision B, the memo, the never-raise and "
            "no-target-code contracts), the binding manifest and its hash, `spell_id_inspector`'s single argument "
            "and the one-object rule, with the older fingerprint entries marked superseded; Spellbook Core carries "
            "creation cache generation 23 (the binding hash in the structural key and the world stamp), the "
            "collision refusals and `inspect_spell`'s exact stage 3; the Crystallizer carries record 4.3.0 and the "
            "restore's `binding_changes`; Spell Examination Profiles drops the fingerprint-only fields; the bind "
            "flow, two subcomponents (the guard's count is 630), the code map (the changed files remeasured, two "
            "modules added), the inventory and the sources follow. Numeric citations into the changed files were "
            "remapped line by line from 0.2.8256; the three that cited the removed fingerprint now cite the "
            "digest.")
        text = self.read(self.COMP)
        text = self.once(text, "## Context / Handoff Summary\n\n",
                         "## Context / Handoff Summary\n\n" + self.wrap(body, "", "") + "\n\n", "handoff")
        self.stage(self.COMP, text)


def main() -> None:
    record = LandDocsComp("docs_comp")
    record.binding_pipeline()
    record.spellbook_core()
    record.crystallizer()
    record.examination_profiles()
    record.flows_and_subcomponents()
    record.code_map_inventory_sources()
    record.handoff()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
