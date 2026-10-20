"""melder_0, 2026-10-18: S2's edits to spell.py (the binding manifest) and S1's statements there (the spell_id is the
code digest; the managed settings left it at 0.2.8254)."""
from apply_common import Applier

SPELL = "src/melder/aether/spellbook/spell.py"


def apply(applier: Applier) -> None:
    """Stage every spell.py edit."""
    applier.edit(SPELL, [
        ("from melder.aether.spellbook.bind.spell_index import SpellIndex\n",
         "from melder.aether.spellbook.bind.binding_manifest import BindingManifest\n"
         "from melder.aether.spellbook.bind.spell_index import SpellIndex\n"),
        ("    - Disposal metadata is established once at bind. The ordered list, presence\n"
         "      flag, and bind-time SHA describe that same policy. Post-creation mutation\n",
         "    - Disposal metadata is established once at bind. The ordered list, presence\n"
         "      flag, and binding hash describe that same policy. Post-creation mutation\n"),
        ("    - The managed options of an `Existence.managed_spell_quantity` binding (mode, limit,\n"
         "      queue timeout, reset method names) are fixed per bound version the same way, as\n"
         "      Bind normalized and hashed them, and exposed by read-only properties.\n",
         "    - The managed options of an `Existence.managed_spell_quantity` binding (mode, limit,\n"
         "      queue timeout, reset method names) are fixed per bound version the same way, as\n"
         "      Bind normalized them, and exposed by read-only properties; they are part of the\n"
         "      binding manifest, never of the spell_id.\n"
         "    - `binding_manifest` records how this version is bound - its address, spellframe and\n"
         "      kind, existence, disposal order, resolvable and managed settings - with its own\n"
         "      SHA256, `binding_hash`. Built once at construction from the same arguments and kept\n"
         "      after cleanup, like `spell_id`: what a spell IS is its spell_id, how it is kept is\n"
         "      its binding (EPIC-2026-10-18-spell_identity_is_the_code).\n"),
        ("        - Each spell has a unique SHA256 `spell_id`, generated from its bind-time fingerprint.\n",
         "        - Each spell has a SHA256 `spell_id`: the digest of the registered object's code\n"
         "          (`SpellCodeDigest`) and nothing from the bind call. How it is bound is its\n"
         "          `binding_manifest`, hashed apart as `binding_hash`.\n"),
        ("            Versioned identity for this spell (current + historical fingerprints).\n",
         "            The SpellIndex this spell is organized under; the index selects one member\n"
         "            version as active.\n"),
        ("            Unique identifier derived from object fingerprinting (SHA256).\n",
         "            The SHA256 of the registered object's code (`SpellCodeDigest`); nothing from\n"
         "            the bind call enters it.\n"),
        ("        \"_managed_spell_reset_methods\",\n    ]\n",
         "        \"_managed_spell_reset_methods\",\n        \"binding_manifest\",\n    ]\n"),
        ("            spell_id (str): SHA256 fingerprint for this spell's structural identity.\n",
         "            spell_id (str): The SHA256 of the registered object's code (`SpellCodeDigest`).\n"),
        ("            - TWO DISTINCT IDENTITIES are established. `spell_id` is the\n"
         "              caller-supplied structural fingerprint; `_id` is a fresh ULID\n"
         "              minted here that identifies THIS record. They are not\n"
         "              interchangeable - the fingerprint describes what the spell IS,\n"
         "              the ULID describes which object you are holding.\n",
         "            - TWO DISTINCT IDENTITIES are established. `spell_id` is the\n"
         "              caller-supplied code digest of the target; `_id` is a fresh ULID\n"
         "              minted here that identifies THIS record. They are not\n"
         "              interchangeable - the digest describes what the spell IS,\n"
         "              the ULID describes which object you are holding.\n"
         "            - The binding manifest (`binding_manifest`, `binding_hash`) is built\n"
         "              last, from these same arguments: how this version is bound, hashed\n"
         "              apart from what it is. A value record, kept after cleanup.\n"),
        ("        # Managed options (Existence.managed_spell_quantity): normalized by Bind and hashed into spell_id,\n"
         "        # read-only per-version policy like `_resolvable`; None / None / None / () on any other existence.\n",
         "        # Managed options (Existence.managed_spell_quantity): normalized by Bind, part of the binding manifest\n"
         "        # and never of the spell_id (since 0.2.8254); read-only per-version policy like `_resolvable`;\n"
         "        # None / None / None / () on any other existence.\n"),
        ("        self.spell_id: str = spell_id  # SHA256 unique identifier\n",
         "        self.spell_id: str = spell_id  # SHA256 of the target's code (SpellCodeDigest)\n"),
        ("        self._key = (frame_key, bind_key)\n\n\n    #region Disposal\n",
         "        self._key = (frame_key, bind_key)\n\n"
         "        # How this version is bound, as a value record with its own SHA256 (S2 of\n"
         "        # EPIC-2026-10-18-spell_identity_is_the_code): built last, from the arguments above, so a\n"
         "        # bound, staged, restored or grafted Spell carries one. Kept after cleanup, like `spell_id`.\n"
         "        self.binding_manifest: BindingManifest = BindingManifest.build(\n"
         "            key=self._key,\n"
         "            spellframe=self.spellframe,\n"
         "            spellframe_kind=self.spellframe_kind,\n"
         "            binding_name=self.binding_name,\n"
         "            existence=self.existence,\n"
         "            disposal_method_names=self.disposal_method_names,\n"
         "            resolvable=resolvable,\n"
         "            managed_spell_mode=managed_spell_mode,\n"
         "            managed_spell_limit=managed_spell_limit,\n"
         "            managed_spell_timeout_seconds=managed_spell_timeout_seconds,\n"
         "            managed_spell_reset_methods=managed_spell_reset_methods,\n"
         "        )\n\n\n    #region Disposal\n"),
        ("            - Deletes the disposal-name reference without clearing its list;\n"
         "              creation entries may still retain that established metadata.\n",
         "            - Deletes the disposal-name reference without clearing its list;\n"
         "              creation entries may still retain that established metadata.\n"
         "            - Keeps the identity data readable: `spell_id`, the address (`key`),\n"
         "              the spellframe and its kind, and `binding_manifest` / `binding_hash`.\n"),
        ("            Set once at bind (default elastic for a managed binding) and part of the spell id. No live\n"
         "            setter; changing it takes another binding.\n",
         "            Set once at bind (default elastic for a managed binding) and part of the binding manifest,\n"
         "            not the spell_id. No live setter; changing it takes another binding.\n"),
        ("            most objects alive at once, idle plus out. Set once at bind and part of the spell id.\n",
         "            most objects alive at once, idle plus out. Set once at bind and part of the binding\n"
         "            manifest, not the spell_id.\n"),
        ("            Set once at bind for the queue mode and part of the spell id; always None for elastic and\n"
         "            limited_quantity, which never wait.\n",
         "            Set once at bind for the queue mode and part of the binding manifest, not the spell_id;\n"
         "            always None for elastic and limited_quantity, which never wait.\n"),
        ("            is leased again. Set once at bind and part of the spell id.\n",
         "            is leased again. Set once at bind and part of the binding manifest, not the spell_id.\n"),
        ("        self.check_cleaned()\n        return self._managed_spell_reset_methods\n",
         "        self.check_cleaned()\n        return self._managed_spell_reset_methods\n\n"
         "    @property\n"
         "    def binding_hash(self) -> str:\n"
         "        \"\"\"\n"
         "        Return the SHA256 of this version's binding manifest.\n\n"
         "        Contract:\n"
         "            How this version is bound - address, spellframe and kind, existence, disposal order,\n"
         "            resolvable and managed settings - hashed apart from its code (`spell_id`). Equal bind\n"
         "            arguments give equal hashes in every process; a change of any of them gives another.\n"
         "            Readable after cleanup, like `spell_id` (`binding_manifest` is a value record).\n\n"
         "        Returns:\n"
         "            str: 64 hex characters (`binding_manifest.binding_hash`).\n"
         "        \"\"\"\n"
         "        return self.binding_manifest.binding_hash\n"),
        ("                A list of spell_ids (SHA256 fingerprints) that this spell depends on.\n",
         "                A list of spell_ids (SHA256 code digests) that this spell depends on.\n"),
    ], "spell")
