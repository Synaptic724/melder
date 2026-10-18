"""melder_0, 2026-10-18: promote S1 and S2 (0.2.8257-0.2.8258) into src_architecture.md - one all-or-nothing pass.

The glossary, the boundary list, the guardrail's bind-guard count, the bind sequence, a new operational invariant,
supersession marks on the entries it overrides, two failure modes, the capability diagram, the code map (changed
files re-measured, the two new modules added), the sources and the handoff summary. The index is regenerated after.
"""
import sys

from docs_common import DocsRecord

CHANGED = {
    "src/melder/aether/spellbook/spellbook.py":
        "The duplicate-id refusals name the one-object rule and `inspect_spell`'s stage 3 is an exact lookup "
        "(0.2.8257).",
    "src/melder/aether/spellbook/spellbook_creation_system.py":
        "The cache-state docstring names the binding hash in the world stamp (0.2.8258).",
    "src/melder/aether/spellbook/bind/bind.py":
        "The spell_id is `SpellCodeDigest.spell_id(target)`; `sha256_profile` and its helpers are removed and "
        "`spell_id_inspector(spell)` takes the target alone (0.2.8257).",
    "src/melder/aether/spellbook/bind/spell_index.py": None,
    "src/melder/aether/spellbook/spell.py":
        "Builds and carries the binding manifest and `binding_hash` (0.2.8258); its spell_id docstrings say code "
        "digest (0.2.8257).",
    "src/melder/aether/aether.py": "The spell-id regime's comment says a spell_id is the object's code (0.2.8257).",
    "src/melder/aether/aether_configuration.py":
        "`process_wide_unique_spell_ids` says a second bind of the same object is refused (0.2.8257).",
    "src/melder/crystallizer/crystals/spell_crystal.py":
        "Records the binding hash (RecordVersion 4.3.0, 0.2.8258).",
    "src/melder/crystallizer/crystal_loader_system/restore_engine.py":
        "Reports each binding a restore rebuilt differently (`binding_changes`, 0.2.8258).",
    "src/melder/crystallizer/crystal_loader_system/graft_runner.py":
        "Its docstrings say a receiving policy moves the binding hash, not the spell_id (0.2.8258).",
    "src/melder/aether/conduit/meld/meld.py": "Its spell_id docstrings say the object's code (0.2.8257).",
    "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py":
        "The verdict-retirement docstring says a rebind of the same class mints its code's id (0.2.8257).",
    "src/melder/aether/aetheric_frame/lookup_container.py": None,
    "src/melder/aether/conduit/conduit_ward/contract/details.py": None,
    "src/melder/aether/conduit/meld/conduit_meld.py": None,
    "src/melder/aether/conduit/meld/spellspace_meld.py": None,
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/"
    "generalized_manifest_no_overrides_compiler.py": None,
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/"
    "generalized_manifest.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py": None,
    "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py": None,
    "src/melder/utilities/caching_system/caching_system.py": "Generation 23, \"binding_manifest_keys\" (0.2.8258).",
    "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py": None,
    "src/melder/crystallizer/persistence/record_version.py": None,
}


class LandDocsArch(DocsRecord):

    # The committed bind-guard manifest after this landing's rebuild (630 entries), measured on the asset
    # build of the landed source in /tmp/m0_mq/guardcount; the rebuild itself runs last.
    GUARD_MANIFEST_LINES = 652

    def glossary_and_boundary(self) -> None:
        text = self.read(self.ARCH)
        text = self.once(text, (
            "- ReleaseManagedSpell: the process singleton Aether builds last and owns - the class-keyed "
            "registry of the pools\n  live root stores hold, through which a managed object goes back to its pool "
            "(0.2.8244).\n"), (
            "- ReleaseManagedSpell: the process singleton Aether builds last and owns - the class-keyed "
            "registry of the pools\n  live root stores hold, through which a managed object goes back to its pool "
            "(0.2.8244).\n"
            + self.wrap("spell_id: the SHA256 of a registered object's code - its functions' instructions and the "
                        "constants they load, its class-level values, the code of its bases outside the standard "
                        "library and, for an existing object, its data - and of nothing from the bind call "
                        "(`SpellCodeDigest`, 0.2.8257). Docstrings, comments and line numbers never move it; any code "
                        "change does. One object is one spell.", "- ", "  ") + "\n"
            + self.wrap("Binding manifest: how a spell is kept - its spellframe and kind, address, existence, "
                        "disposal names, resolvable and managed settings - as a value record whose SHA256 is the "
                        "binding hash (`BindingManifest`, `Spell.binding_manifest`, `Spell.binding_hash`, 0.2.8258).",
                        "- ", "  ") + "\n"), "glossary")
        text = self.once(text, "- `Spellbook.bind(...)` and `SpellBinder` fluent binding helpers.\n", (
            "- `Spellbook.bind(...)` and `SpellBinder` fluent binding helpers.\n"
            + self.wrap("`Spell.binding_manifest` and `Spell.binding_hash` (0.2.8258): the binding a spell was "
                        "registered with and its SHA256, read-only; `BindingManifest.describe()` gives them as plain "
                        "data. The SpellCrystal records the binding hash (record 4.3.0) and a restore's "
                        "`RestoreReport.describe()[\"binding_changes\"]` lists each binding it rebuilt differently.",
                        "- ", "  ") + "\n"), "boundary")
        text = self.once(text, (
            "alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (628 at\n"
            "  0.2.8246: the managed-spell classes joined at 0.2.8242-0.2.8244; 620 at 0.2.8216)."), (
            "alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (630 at\n"
            "  0.2.8257: `SpellCodeDigest` and `BindingManifest` joined; 628 at 0.2.8246: the managed-spell classes\n"
            "  joined at 0.2.8242-0.2.8244; 620 at 0.2.8216)."), "guard count")
        text = self.once(text, "the real manifest (628 entries at 0.2.8246) begin refusing",
                         "the real manifest (630 entries at 0.2.8257) begin refusing", "guard count 2")
        text = self.once(text, (
            "   - Disposal candidates resolve once into a Spell-owned ordered list before fingerprinting.\n"
            "     Book names own overlaps; priority places their block first or last (default).\n"), (
            "   - Disposal candidates resolve once into a Spell-owned ordered list.\n"
            "     Book names own overlaps; priority places their block first or last (default).\n"
            "   - The spell_id is the SHA256 of the target's code (`SpellCodeDigest`, 0.2.8257), nothing from "
            "the bind\n"
            "     call; the Spell builds its binding manifest and binding hash from the bind call (0.2.8258).\n"),
            "bind sequence")
        self.stage(self.ARCH, text)

    def invariant(self) -> str:
        body = (
            "A spell_id is the object's code; its binding is a manifest (2026-10-18, 0.2.8257-0.2.8258; "
            "EPIC-2026-10-18-spell_identity_is_the_code, S1 and S2, on the owner's direction - \"a change anywhere "
            "is a change\" - and his calls 1-5): `Bind._bind_logic` takes the spell_id from "
            "`SpellCodeDigest.spell_id(target)`, the SHA256 of `v5-code`, the interpreter's cache tag and the "
            "target's encoding, where it took `Bind.sha256_profile(...)` (removed, with `_fingerprint_repr_text`, "
            "`_fingerprint_default_text` and the binding profiles' `fingerprint_repr` fields). A class encodes as its "
            "module, qualname, metaclass and bases and, for itself and every class of its MRO outside the standard "
            "library, its namespace: each function by its code - the instruction stream with the constants it "
            "loads, argument counts, flags, name tables (so a renamed local counts) and exception table, never "
            "line numbers, a docstring or a comment - its defaults, annotations, closure values and type "
            "parameters, and every class-level value. An existing object is its class's code plus its slots and "
            "`__dict__` by value. Installed third-party code is named by qualified name and distribution version, "
            "never digested (decision B). Nothing from the bind call enters it: spellframe, binding name, "
            "existence, disposal names, resolvable and the managed settings are the binding manifest "
            "(`BindingManifest`, built last in `Spell.__init__`), whose SHA256 is `Spell.binding_hash`. Code-object "
            "digests are memoized per Bind (weakly keyed by code object); classes and objects are encoded at each "
            "bind, as they are then; no target code runs but `repr()` of a target with no Python-visible state, "
            "of a value type's object or of an installed third-party object. Every spell_id moved once; the same "
            "code is the same spell_id in every process, hash seed and GIL mode; and the duplicate-id refusals "
            "are the one-object rule - an object bound again "
            "under any binding, or in another Book where spell_ids are unique, is refused at bind, bind_inactive "
            "or conjure's integrity check, whose texts name the rule and the remedies (share it; `cleanup_spell` "
            "and bind again to change its binding; a changed method is a new spell_id to stage and notch). Both "
            "creation-cache tiers key on the binding hash beside the spell_id (structural key format 2; the world "
            "stamp hashes `<spell_id>=<binding_hash>` per pool and borrowed spell; generation 23), so a binding "
            "changed under one spell_id never replays a plan or row built for another; the SpellCrystal records "
            "the binding hash (RecordVersion 4.3.0) and a restore reports each binding it rebuilt differently "
            "(`RestoreReport.describe()[\"binding_changes\"]`), never a shortfall. `Bind.spell_id_inspector(spell)` "
            "takes the target alone and equals bind's id, so `Spellbook.inspect_spell`'s stage 3 finds any "
            "registered object by its code. Locks: the digest takes none; Bind calls it under its own lock, where "
            "the fingerprint ran, `spell_id_inspector` builds a fresh one per call, and it keeps no strong "
            "reference to a target. Cost: +37 to +55 us a bind on the gauntlet and "
            "on 200 generated classes; conjure and melds unchanged. Open: a rebind under another slotted existence "
            "keeps its spell_id, so its first meld can return the removed definition's slotted object (S3); a "
            "record made before 0.2.8257 that holds one object twice fails at its second replayed bind (S5); and "
            "until STORY-2026-10-17-minted_index_missing_from_frame_registry lands, bind's collision check misses "
            "a version alone in an index `remove_from_spell_index` minted.")
        evidence = (
            "EVIDENCE: `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest.spell_id`, "
            "`SpellCodeDigest._target_encoding`, `SpellCodeDigest._class_digest`, `SpellCodeDigest._code_digest`, "
            "`src/melder/aether/spellbook/bind/binding_manifest.py:BindingManifest.build`, "
            "`src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic`, `Bind.spell_id_inspector`, "
            "`src/melder/aether/spellbook/spell.py:Spell.binding_hash`, "
            "`src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:"
            "StructuralSnapshot.world_stamp`, `src/melder/crystallizer/crystals/spell_crystal.py:"
            "SpellCrystal.binding_hash` and `src/melder/crystallizer/crystal_loader_system/restore_engine.py:"
            "RestoreEngine._record_binding_change`.")
        return self.wrap(body, "- ", "  ") + "\n" + self.wrap(evidence, "  ", "  ") + "\n"

    def invariants(self) -> None:
        text = self.read(self.ARCH)
        text = self.once(text, "## Operational Invariants\n", "## Operational Invariants\n" + self.invariant(),
                         "invariant")
        text = self.once(text, (
            "- A managed spell's settings are not part of its spell_id (2026-10-18, 0.2.8254; the owner's ruling, chat "
            "2026-10-17:\n"), (
            "- A managed spell's settings are not part of its spell_id (2026-10-18, 0.2.8254; SUPERSEDED in part at\n"
            "  0.2.8257 by the entry above - no bind input is part of the spell_id, and `sha256_profile` is gone; the\n"
            "  pool rebind stands; the owner's ruling, chat 2026-10-17:\n"), "supersede 8254")
        text = self.once(text, (
            "  with another disposal list is still a second version with its own pool (part B of\n"
            "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, pending).\n"
            "  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile`, "
            "`Bind.spell_id_inspector`,\n"), (
            "  with another disposal list is still a second version with its own pool (part B of\n"
            "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, pending; since 0.2.8257 that\n"
            "  staging is refused, one object being one spell).\n"
            "  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile` (until 0.2.8257),\n"
            "  `Bind.spell_id_inspector`,\n"), "8254 evidence")
        text = self.once(text, (
            "  True preserves the existing v4-binding fingerprint; False uses a separate hash domain. Application\n"), (
            "  True preserves the existing v4-binding fingerprint; False uses a separate hash domain (until 0.2.8257;\n"
            "  resolvable is a binding-manifest field since 0.2.8258 and no part of the spell_id). Application\n"),
            "capability")
        self.stage(self.ARCH, text)

    def failure_modes(self) -> None:
        breaking = (
            "Breaking (0.2.8257-0.2.8258): every spell_id moves once, and from then on it moves with the object's "
            "code and with nothing from the bind call. A second registration of one object is refused: `bind` and "
            "`bind_inactive` raise RuntimeError \"Spell ID collision detected: this object is already registered as "
            "spell_id <id>. A spell_id is the SHA256 of the object's code (its methods, constructor, class-level "
            "values and base classes, or an existing object's class and data), and one object is one spell: "
            "registering it again ... is refused. Use the spell already registered ..., or cleanup_spell it and "
            "bind it again to change how it is bound. A changed method, constructor, class-level value or base "
            "class is a new spell_id: stage it with bind_inactive and notch to it.\" - it was a second spell under "
            "another binding name, existence or spellframe - and conjure's integrity check refuses a second Book's "
            "binding of it, its text naming the rule. An edited class staged with `bind_inactive` is a new version "
            "(it was refused as a collision when only a method body changed). `Bind.spell_id_inspector(spell)` takes "
            "the target alone (TypeError for the binding keywords it took). Creation-cache bundles of generation 22 "
            "are cold once (23). A Crystallizer record made before 0.2.8257 restores through bind and maps its ids as "
            "before, and one that holds one object twice fails to restore at its second replayed bind (until S5). "
            "A restore under another receiving policy (another disposal order) keeps the spell_id and reports the "
            "binding change in `binding_changes` (before, the spell_id moved and the identity map held both).")
        evidence = (
            "EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.bind`, `Spellbook.bind_inactive`, "
            "`src/melder/aether/spellbook/bind/bind.py:Bind.spell_id_inspector` and "
            "`src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreReport.record_binding_change`.")
        text = self.read(self.ARCH)
        text = self.once(text, "## Failure Modes and Error Paths\n",
                         "## Failure Modes and Error Paths\n" + self.wrap(breaking, "- ", "  ") + "\n"
                         + self.wrap(evidence, "  ", "  ") + "\n", "failure modes")
        text = self.once(text, (
            "  one SpellIndex at another address or with another disposal list is still a second version with its own "
            "pool, so\n  an unfiltered release after a notch still goes to the active version's pool; pass `spell_id=` "
            "to route it.\n"), (
            "  one SpellIndex at another address or with another disposal list is still a second version with its own "
            "pool, so\n  an unfiltered release after a notch still goes to the active version's pool; pass `spell_id=` "
            "to route it.\n  Since 0.2.8257 such a staging is refused: the class is one spell whatever its binding.\n"),
            "part B")
        for old in ("  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile` and\n",):
            count = text.count(old)
            if count != 2:
                sys.exit(f"sha256 evidence lines: {count}")
            text = text.replace(old, "  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile` "
                                     "(until 0.2.8257) and\n")
        self.stage(self.ARCH, text)

    def diagram(self) -> None:
        text = self.read(self.ARCH)
        text = self.once(text, (
            "bind / bind_inactive -> Bind bool admission + fingerprint -> Spell.resolvable\n"
            "                               |                                  |\n"
            "                     True: legacy hash domain          spellbook descriptions\n"
            "                     False: distinct hash domain\n"), (
            "bind / bind_inactive -> Bind bool admission -> Spell.resolvable (a binding-manifest field, 0.2.8258)\n"
            "                                                     |\n"
            "                                          spellbook descriptions\n"
            "(the spell_id is the target's code and does not depend on resolvable since 0.2.8257)\n"), "diagram")
        text = self.once(text, "  B[Active or inactive bind] --> V[Bind: validate bool and fingerprint]\n",
                         "  B[Active or inactive bind] --> V[Bind: validate the bool]\n", "mermaid")
        self.stage(self.ARCH, text)

    def code_map_and_sources(self) -> None:
        missing = [path for path, note in CHANGED.items() if not self.remeasure(self.ARCH, path, note)]
        print("not in the architecture code map:", missing)
        self.add_entry_after(self.ARCH, "src/melder/aether/spellbook/bind/bind.py",
                             "src/melder/aether/spellbook/bind/spell_code_digest.py",
                             "`SpellCodeDigest`: the spell_id, the SHA256 of a registration target's code and data "
                             "(0.2.8257).")
        self.add_entry_after(self.ARCH, "src/melder/aether/spellbook/bind/spell_code_digest.py",
                             "src/melder/aether/spellbook/bind/binding_manifest.py",
                             "`BindingManifest`: a spell's binding as a value record and its SHA256, the binding hash "
                             "(0.2.8258).")
        text = self.read(self.ARCH)
        text = self.once(text, "- `src/melder/aether/spellbook/bind/bind.py`\n", (
            "- `src/melder/aether/spellbook/bind/bind.py`\n"
            "- `src/melder/aether/spellbook/bind/spell_code_digest.py`\n"
            "- `src/melder/aether/spellbook/bind/binding_manifest.py`\n"), "sources")
        self.stage(self.ARCH, text)

    def supersede_more(self) -> None:
        """The older statements the identity change makes historical, and the bind-guard manifest's new extent."""
        text = self.read(self.ARCH)
        text = self.once(text, "  spell_id (0.2.8254).\n",
                         "  spell_id (0.2.8254); since 0.2.8258 they are fields of its binding manifest.\n",
                         "glossary managed")
        text = self.once(text, "  replaying anchors, selections, and contract grants.\n", (
            "  replaying anchors, selections, and contract grants (until 0.2.8257: since then a receiving\n"
            "  policy moves the binding hash, never the spell_id, and the restore reports each such binding in\n"
            "  `binding_changes`, 0.2.8258).\n"), "restore invariants")
        text = self.once(text, "  M --> S[Spell-owned ordered list and content ID]\n",
                         "  M --> S[Spell-owned ordered list, a binding-manifest field]\n", "ordered disposal mermaid")
        text = self.once(text, (
            "policy source. Receiving-book order wins on replay. The loader follows changed binding IDs\n"
            "without rewriting the original record or existing live IDs.\n"), (
            "policy source. Receiving-book order wins on replay. Until 0.2.8257 the order was part of the\n"
            "spell_id and the loader followed changed binding IDs without rewriting the original record or\n"
            "existing live IDs; since then the order is a binding-manifest field, so a receiving book's order\n"
            "keeps the spell_id, moves the binding hash and is reported in the restore's `binding_changes`\n"
            "(0.2.8258).\n"), "ordered disposal text")
        text = self.once(text, (
            "  fingerprint (affected classes changed id once when this landed). Every annotation in "
            "`src/melder`\n"), (
            "  fingerprint (affected classes changed id once when this landed; until 0.2.8257 - the spell_id "
            "now\n  reads an annotate function's code, never an annotation's value). Every annotation in "
            "`src/melder`\n"),
            "annotation reflection")
        text = self.once(text, (
            "  are settings, not identity - see the 0.2.8254 entry at the top of this section); the crystal "
            "records them\n  (RecordVersion 4.2.0) and restore and graft replay them. Every stamped managed\n"), (
            "  are settings, not identity - see the 0.2.8254 entry above - and since 0.2.8258 binding-manifest "
            "fields); the\n  crystal records them (RecordVersion 4.2.0) and restore and graft replay them. "
            "Every stamped managed\n"),
            "managed pools")
        self.stage(self.ARCH, text)
        self.remeasure(self.ARCH, "src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py",
                       "630 entries at 0.2.8257 (`SpellCodeDigest`, `BindingManifest`), measured on this landing's "
                       "rebuild output.", count=self.GUARD_MANIFEST_LINES)

    def handoff(self) -> None:
        body = (
            "2026-10-18 spell identity is the code (0.2.8257-0.2.8258; S1 and S2 of "
            "EPIC-2026-10-18-spell_identity_is_the_code, on the owner's direction and calls): a spell_id is the "
            "SHA256 of the registered object's code (`SpellCodeDigest`), nothing from the bind call, so every real "
            "edit is a new version and one object is one spell; the bind call is the binding manifest, whose hash "
            "keys both creation-cache tiers (generation 23) and rides the SpellCrystal (record 4.3.0), a restore "
            "reporting each binding it rebuilt differently. The glossary, the boundary list, the guardrail's "
            "bind-guard count (630), the bind sequence, a new operational invariant (the 0.2.8254 entry marked "
            "superseded in part), a Breaking failure mode, the capability diagram, the code map (the changed files "
            "re-measured, two modules added) and the sources carry it; the component map carries the per-component "
            "contracts. Numeric citations into the changed files were remapped line by line from 0.2.8256. Open: S3 "
            "(a changed binding revalidates), S4 (the refusal names the existing registration), S5 (records "
            "holding one object twice).")
        text = self.read(self.ARCH)
        text = self.once(text, "\n## Context / Handoff Summary\n\n",
                         "\n## Context / Handoff Summary\n\n" + self.wrap(body, "", "") + "\n\n", "handoff")
        self.stage(self.ARCH, text)


def main() -> None:
    record = LandDocsArch("docs_arch")
    record.glossary_and_boundary()
    record.invariants()
    record.failure_modes()
    record.diagram()
    record.supersede_more()
    record.code_map_and_sources()
    record.handoff()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
