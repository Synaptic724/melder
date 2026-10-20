"""melder_0, 2026-10-18: S1's edits to bind.py - the spell_id is the target's code digest (SpellCodeDigest);
`sha256_profile` and its two helpers are removed; `spell_id_inspector` takes the target alone."""
from apply_common import Applier

BIND = "src/melder/aether/spellbook/bind/bind.py"

INSPECTOR = '''    #region Spell Inspector Helpers
    @staticmethod
    def spell_id_inspector(spell: Any) -> str:
        """
        Return the spell_id bind gives a target, without registering it.

        Purpose:
            The read-only path for tooling and diagnostics, and for `Spellbook.inspect_spell`'s stage 3:
            re-derive the id an object is, or would be, registered under.

        Contract:
            - The spell_id is the SHA256 of the target's code (`SpellCodeDigest`), so the target alone decides
              it: the id is the same whatever binding the target is bound with (spellframe, binding name,
              existence, disposal names, resolvable, managed settings), and equals the id `_bind_logic` gives it.
            - Builds a fresh `SpellCodeDigest` per call and cleans it before returning: no shared memo, no lock,
              no state left behind. Registers nothing and checks no binding rule (that is bind's admission).

        Args:
            spell (Any): The class, function or object to identify.

        Returns:
            str: The 64-character spell_id.
        """
        digest = SpellCodeDigest()
        try:
            return digest.spell_id(spell)
        finally:
            digest.cleanup()

'''


def apply(applier: Applier) -> None:
    """Stage every bind.py edit."""
    applier.edit(BIND, [
        ("import inspect\nimport threading\nimport hashlib\nimport math\n",
         "import inspect\nimport threading\nimport math\n"),
        ("    CallableBindingProfile,\n    CallableParameterBindingSummary,\n    InstanceBindingProfile,\n"
         "    OtherBindingProfile,\n)\nfrom melder.aether.spellbook.spell_compiler.spell_examiner.inspectors."
         "inspector_utility import InspectorUtility\n",
         "    CallableBindingProfile,\n    InstanceBindingProfile,\n    OtherBindingProfile,\n)\n"
         "from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest\n"),
        ("    (`Existence`), access policy (`Permissions`), spellframe grouping, and\n"
         "    structural fingerprinting first come together.\n",
         "    (`Existence`), access policy (`Permissions`), spellframe grouping, and\n"
         "    the spell's identity (the code digest) first come together.\n"),
        ("    2.  **Fingerprinting:** Generating a deterministic SHA256 unique ID (`spell_id`) based on the profile.\n",
         "    2.  **Identity:** The `spell_id` is the SHA256 of the object's code (`SpellCodeDigest`); the bind\n"
         "        call's values become the Spell's binding manifest, hashed apart.\n"),
        ("    - Successful registration always flows through canonical profile\n"
         "      examination and deterministic fingerprinting rather than ad hoc ids.\n",
         "    - Successful registration always flows through canonical profile\n"
         "      examination and the code digest (`SpellCodeDigest`) rather than ad hoc ids.\n"
         "    - One object is one spell: binding it again under any name, existence or\n"
         "      spellframe gives the same spell_id, which the Spellbook's duplicate-id\n"
         "      refusals refuse (EPIC-2026-10-18-spell_identity_is_the_code).\n"),
        ("        (`Permissions`), spellframe grouping, and structural fingerprinting\n        first converge.",
         "        (`Permissions`), spellframe grouping, and the code digest\n        first converge."),
        ("        DETERMINISTIC FINGERPRINTING is the property everything downstream\n"
         "        depends on. The `spell_id` is a SHA256 over the examined profile, so it\n"
         "        is CONTENT-DERIVED and stable across processes and sessions - which is\n"
         "        why the crystallizer can replay custody by recorded spell id while\n"
         "        refusing to rehydrate ULIDs, and why the same object bound in two\n"
         "        processes carries the same identity.\n",
         "        DETERMINISTIC IDENTITY is the property everything downstream depends on.\n"
         "        The `spell_id` is the SHA256 of the object's code - its methods with their\n"
         "        bodies, inherited code, class-level values and, for an existing object, its\n"
         "        data - so it is CONTENT-DERIVED and stable across processes and sessions:\n"
         "        the crystallizer can replay custody by recorded spell id while refusing to\n"
         "        rehydrate ULIDs, the same object bound in two processes carries the same\n"
         "        identity, and an edited method is a new version an agent stages and notches.\n"),
        ("        \"_lifecycle_hooks\",\n    ]\n",
         "        \"_lifecycle_hooks\",\n        \"_spell_code_digest\",\n    ]\n"),
        ("            - Owns one `SpellExaminer` helper for profile creation.\n",
         "            - Owns one `SpellExaminer` helper for profile creation and one\n"
         "              `SpellCodeDigest` for spell_ids (its code-object memo lives as long as Bind).\n"),
        ("        self._spell_examiner: SpellExaminer = SpellExaminer()\n",
         "        self._spell_examiner: SpellExaminer = SpellExaminer()\n"
         "        self._spell_code_digest: SpellCodeDigest = SpellCodeDigest()\n"),
        ("        - Cleans the owned `SpellExaminer` before dropping references.\n",
         "        - Cleans the owned `SpellExaminer` and `SpellCodeDigest` before dropping references.\n"),
        ("                self._spell_examiner.cleanup()\n            del self._spellbook\n"
         "            del self._spell_examiner\n            del self._lifecycle_hooks\n",
         "                self._spell_examiner.cleanup()\n            self._spell_code_digest.cleanup()\n"
         "            del self._spellbook\n            del self._spell_examiner\n            del self._spell_code_digest\n"
         "            del self._lifecycle_hooks\n"),
        ("        In both modes, the same binding pipeline is used: examine the target,\n"
         "        fingerprint the binding profile, validate spellframe / existence rules,\n",
         "        In both modes, the same binding pipeline is used: examine the target,\n"
         "        digest its code into the spell_id, validate spellframe / existence rules,\n"),
        ("        * Computes a deterministic fingerprint and SpellIndex from a `SpellBindingProfile`.\n"
         "        * Resolves disposal names once in group priority order, hashes the resolved\n"
         "          list, and passes that same list to Spell without another conversion.\n",
         "        * Computes the spell_id - the SHA256 of the target's code (`SpellCodeDigest`), nothing\n"
         "          from this call - and the SpellIndex from it.\n"
         "        * Resolves disposal names once in group priority order and passes that list to Spell\n"
         "          without another conversion; it enters the Spell's binding manifest, not the spell_id.\n"),
        ("          settings of the one spell, not its identity: the fingerprint never reads them\n"
         "          (owner ruling 2026-10-17), so a managed class bound with other settings at the same\n"
         "          address, existence and disposal list gets the same spell_id.\n",
         "          settings of the one spell, not its identity (owner ruling 2026-10-17): the spell_id\n"
         "          never reads them, and they are part of the binding manifest.\n"),
        ("            Native fingerprint rules are unchanged and callback returns are ignored.\n",
         "            They never change the spell_id rule, and callback returns are ignored.\n"),
        ("            during matching. The shallow profile and its fingerprint inputs do not\n"
         "            expand. Missing names and non-class profiles contribute nothing. Book names\n",
         "            during matching. The shallow profile does not expand. Missing names and\n"
         "            non-class profiles contribute nothing. Book names\n"),
        ("            # 2. Build binding profile and fingerprint\n",
         "            # 2. Build the binding profile; the spell_id is the target's code\n"),
        ("            # and kept by the Spell. They are settings, not identity: the fingerprint below never reads\n"
         "            # them (owner ruling 2026-10-17). Any other existence must leave all four unset. Refusals\n"
         "            # happen before a Spell or index exists.\n",
         "            # and kept by the Spell. They are settings, not identity: the spell_id below never reads them\n"
         "            # (owner ruling 2026-10-17); they are part of the Spell's binding manifest. Any other existence\n"
         "            # must leave all four unset. Refusals happen before a Spell or index exists.\n"),
        ("            fingerprint: str = Bind.sha256_profile(\n"
         "                binding_profile,\n"
         "                spellframe=spellframe,\n"
         "                spell_name=spell_name,\n"
         "                binding_name=binding_name,\n"
         "                existence=existence,\n"
         "                disposal_method_names=resolved_disposal_method_names,\n"
         "                resolvable=resolvable,\n"
         "            )\n"
         "            spell_index = SpellIndex(initial_id=fingerprint)\n",
         "            # The spell_id is the SHA256 of the target's code - methods with their bodies, inherited code,\n"
         "            # class-level values, an existing object's data - and of nothing from this bind call\n"
         "            # (EPIC-2026-10-18-spell_identity_is_the_code). The call's values become the Spell's binding\n"
         "            # manifest, hashed apart, so one object is one spell: the duplicate-id refusals downstream\n"
         "            # refuse a second registration of it.\n"
         "            spell_id: str = self._spell_code_digest.spell_id(spell)\n"
         "            spell_index = SpellIndex(initial_id=spell_id)\n"),
        ("                spell_id=fingerprint,\n", "                spell_id=spell_id,\n"),
        ("            Runs under the existing Bind lock before fingerprinting. Owns no\n",
         "            Runs under the existing Bind lock before the spell_id is computed. Owns no\n"),
        ("        Reject non-boolean capability inputs at independent admission/fingerprint boundaries.\n",
         "        Reject a non-boolean capability input at bind's admission.\n"),
        ("            fails at bind, next to the mistake, and the fingerprint, the Spell and the crystal all read the"
         " same\n",
         "            fails at bind, next to the mistake, and the Spell, its binding manifest and the crystal all read"
         " the same\n"),
        ("        the spellbook before profile fingerprinting and spell construction are\n        allowed to proceed.\n",
         "        the spellbook before spell construction is allowed to proceed.\n"),
    ], "bind")
    applier.cut(BIND, "    #region Spell Inspector Helpers\n    @staticmethod\n    def spell_id_inspector(\n",
                "    @staticmethod\n    def _validate_resolvable(resolvable: bool) -> None:\n", INSPECTOR,
                "bind inspector + sha256_profile")
