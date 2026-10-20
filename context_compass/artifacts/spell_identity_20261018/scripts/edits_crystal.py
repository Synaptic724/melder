"""melder_0, 2026-10-18: S2's crystallizer record edits (component_patch_crystallizer_record.md; the owner's word,
"make sure you land the binding hash going into crystallizer too"): the SpellCrystal records the binding hash,
RecordVersion 4.3.0, the restore report's binding changes, and S1's restore and graft statements (a spell_id moves
only with the code; a receiving Book's policy moves the binding hash)."""
from apply_common import Applier

CRYSTAL = "src/melder/crystallizer/crystals/spell_crystal.py"
VERSION = "src/melder/crystallizer/persistence/record_version.py"
RESTORE = "src/melder/crystallizer/crystal_loader_system/restore_engine.py"
GRAFT = "src/melder/crystallizer/crystal_loader_system/graft_runner.py"

BINDING_HASH_PROPERTY = (
    "    @property\n"
    "    def binding_hash(self) -> str:\n"
    "        \"\"\"\n"
    "        Return the binding hash recorded at bind (record 4.3.0).\n\n"
    "        Contract:\n"
    "            - The SHA256 of the spell's binding manifest at capture (`Spell.binding_hash`): how\n"
    "              the version was bound - address, spellframe and kind, existence, disposal order,\n"
    "              resolvable and managed settings - hashed apart from its code (`id`).\n"
    "            - A restore compares it with the binding it rebuilds under the receiving Book's\n"
    "              policy and reports a difference (`RestoreReport.record_binding_change`).\n\n"
    "        Returns:\n"
    "            str: 64 hex characters.\n\n"
    "        Raises:\n"
    "            RuntimeError: If the crystal has been cleaned.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        with self._lock:\n"
    "            return self._binding_hash\n\n")


def crystal(applier: Applier) -> None:
    """The `_binding_hash` capture, property, payload key and cleanup (spell_crystal.py)."""
    applier.edit(CRYSTAL, [
        ("        - records a managed spell's options (record 4.2.0) - mode by name, limit,\n"
         "          queue timeout and reset method names - and nothing new for any other\n"
         "          existence, so every other payload is unchanged\n",
         "        - records a managed spell's options (record 4.2.0) - mode by name, limit,\n"
         "          queue timeout and reset method names - and nothing new for any other\n"
         "          existence, so every other payload is unchanged\n"
         "        - records the spell's binding hash (record 4.3.0): the SHA256 of how it is\n"
         "          bound, apart from its code (`Spell.binding_hash`); a restore compares the\n"
         "          binding it rebuilds with it\n"),
        ("        \"_managed_spell_reset_methods\",\n    ]\n",
         "        \"_managed_spell_reset_methods\",\n        \"_binding_hash\",\n    ]\n"),
        ("            - Captures native resolution capability so replay cannot enable a definition.\n",
         "            - Captures native resolution capability so replay cannot enable a definition.\n"
         "            - Captures the spell's binding hash (record 4.3.0), the SHA256 of its\n"
         "              binding manifest; a restore reports a binding it rebuilt differently.\n"),
        ("        self._resolvable: bool = spell.resolvable\n",
         "        self._resolvable: bool = spell.resolvable\n"
         "        # Binding hash (record 4.3.0, EPIC-2026-10-18-spell_identity_is_the_code): the SHA256 of how this\n"
         "        # version is bound - its address, spellframe and kind, existence, disposal order, resolvable and\n"
         "        # managed settings - apart from its code (`spell_id`). A restore compares the binding it rebuilds\n"
         "        # with it and reports a difference.\n"
         "        self._binding_hash: str = spell.binding_hash\n"),
        ("            del self._resolvable\n",
         "            del self._resolvable\n            del self._binding_hash\n"),
        ("    @property\n    def profile_family(self) -> str:\n",
         BINDING_HASH_PROPERTY + "    @property\n    def profile_family(self) -> str:\n"),
        ("                \"resolvable\": self._resolvable,\n",
         "                \"resolvable\": self._resolvable,\n"
         "                # Record 4.3.0: written for every spell; a restore compares it.\n"
         "                \"binding_hash\": self._binding_hash,\n"),
    ], "crystal")


def version(applier: Applier) -> None:
    """RecordVersion 4.3.0 (record_version.py)."""
    applier.edit(VERSION, [
        ("    # for `Existence.managed_spell_quantity`; 4.1 readers ignore them, and a 4.1 record holds no such keys.\n"
         "    CURRENT: ClassVar[str] = \"4.2.0\"\n",
         "    # for `Existence.managed_spell_quantity`; 4.1 readers ignore them, and a 4.1 record holds no such keys.\n"
         "    # Minor 4.3 adds the spell crystal's `binding_hash` (EPIC-2026-10-18-spell_identity_is_the_code, S2):\n"
         "    # the SHA256 of the spell's binding manifest, written for every spell; 4.2 readers ignore it, and a\n"
         "    # 4.2 record read by a 4.3 loader compares no binding.\n"
         "    CURRENT: ClassVar[str] = \"4.3.0\"\n"),
    ], "version")


def report(applier: Applier) -> None:
    """RestoreReport's binding changes (restore_engine.py)."""
    applier.edit(RESTORE, [
        ("        - Recorded ULIDs appear ONLY inside the translation map; they never\n"
         "          escape into the rebuilt world (never-rehydrate-ULIDs policy).\n",
         "        - Recorded ULIDs appear ONLY inside the translation map; they never\n"
         "          escape into the rebuilt world (never-rehydrate-ULIDs policy).\n"
         "        - Binding changes (record 4.3.0): a spell whose binding the receiving\n"
         "          Book rebuilt differently from the record - another disposal order,\n"
         "          say - is listed by custody key with its recorded and live binding\n"
         "          hashes. It is information, never a shortfall: the receiving Book's\n"
         "          policy is the restore's rule, and the spell_id (its code) is kept.\n"),
        ("        \"_identity_map\",\n        \"_status\",\n",
         "        \"_identity_map\",\n        \"_binding_changes\",\n        \"_status\",\n"),
        ("        self._identity_map: Dict[str, str] = {}\n        self._status: str = \"pending\"\n",
         "        self._identity_map: Dict[str, str] = {}\n"
         "        # custody key -> {\"recorded\": hash, \"live\": hash} for each binding rebuilt differently (record 4.3.0).\n"
         "        self._binding_changes: Dict[str, Dict[str, str]] = {}\n"
         "        self._status: str = \"pending\"\n"),
        ("            del self._identity_map\n            del self._status\n",
         "            del self._identity_map\n            del self._binding_changes\n            del self._status\n"),
        ("        Structural ULIDs are always translated. Spell SHA entries are added\n"
         "        when a new bind's resolved signature differs from its recorded one;\n"
         "        unchanged content IDs remain directly addressable without an entry.\n",
         "        Structural ULIDs are always translated. A spell_id entry is added\n"
         "        when a replayed bind returns another spell_id than the recorded one -\n"
         "        the target's code moved since the record (a class edited on disk,\n"
         "        another Python version); unchanged spell_ids need no entry. A binding\n"
         "        the receiving Book's policy rebuilt differently keeps its spell_id and\n"
         "        is reported by `record_binding_change` instead.\n"),
        ("    def translate(self, recorded_id: str) -> Optional[str]:\n",
         "    def record_binding_change(\n"
         "            self,\n"
         "            custody_key: str,\n"
         "            recorded_binding_hash: str,\n"
         "            live_binding_hash: str,\n"
         "    ) -> None:\n"
         "        \"\"\"\n"
         "        Record one binding a replayed bind rebuilt differently from its record (record 4.3.0).\n\n"
         "        Contract:\n"
         "            - Keyed by custody key; a later call for the same key replaces the entry.\n"
         "            - Information only: no shortfall is filed and nothing raises.\n\n"
         "        Args:\n"
         "            custody_key:\n"
         "                The folded custody key of the replayed spell.\n"
         "            recorded_binding_hash:\n"
         "                The binding hash the record carries.\n"
         "            live_binding_hash:\n"
         "                The binding hash of the spell the replayed bind registered.\n\n"
         "        Returns:\n"
         "            None.\n\n"
         "        Raises:\n"
         "            RuntimeError:\n"
         "                If the report has been cleaned.\n"
         "        \"\"\"\n"
         "        self.check_cleaned()\n"
         "        with self._lock:\n"
         "            self._binding_changes[custody_key] = {\n"
         "                \"recorded\": recorded_binding_hash,\n"
         "                \"live\": live_binding_hash,\n"
         "            }\n\n"
         "    def translate(self, recorded_id: str) -> Optional[str]:\n"),
        ("            Recreates checkpoint ids, built counts, shortfall rows, and identity\n"
         "            mappings. The preflight dictionary is copied at its outer boundary;\n",
         "            Recreates checkpoint ids, built counts, shortfall rows, identity\n"
         "            mappings and binding changes (record 4.3.0; empty when every binding\n"
         "            replayed as recorded). The preflight dictionary is copied at its outer boundary;\n"),
        ("                and the identity translation map - fully detached copies.\n",
         "                the identity translation map and the binding changes - fully\n"
         "                detached copies.\n"),
        ("                \"identity_map\": dict(self._identity_map),\n",
         "                \"identity_map\": dict(self._identity_map),\n"
         "                \"binding_changes\": {\n"
         "                    key: dict(entry) for key, entry in self._binding_changes.items()\n"
         "                },\n"),
    ], "report")


def engine(applier: Applier) -> None:
    """The engine's binding comparison and S1's restore statements (restore_engine.py)."""
    applier.edit(RESTORE, [
        ("if TYPE_CHECKING:\n    from melder.aether.conduit.conduit import Conduit\n",
         "if TYPE_CHECKING:\n    from melder.aether.conduit.conduit import Conduit\n"
         "    from melder.aether.spellbook.spell import Spell\n"),
        ("            - Spell SHAs stay stable when recorded signature and receiving policy\n"
         "              agree. A changed signature maps to the actual bind result in the\n"
         "              existing report, before member/selection/contract references replay.\n",
         "            - A spell_id is the target's code, so the receiving policy never moves\n"
         "              it; it moves only when the code moved since the record (a class\n"
         "              edited on disk, another Python version), and a moved id maps to the\n"
         "              actual bind result in the report before member, selection and\n"
         "              contract references replay. A binding the receiving policy rebuilds\n"
         "              differently (another disposal order) keeps its spell_id and is\n"
         "              reported as a binding change (record 4.3.0).\n"),
        ("            Forward ordered disposal names through normal book composition.\n"
         "            Record a changed SHA before resolving dependent staged members.\n",
         "            Forward ordered disposal names through normal book composition.\n"
         "            Record a changed spell_id (the code moved since the record) before\n"
         "            resolving dependent staged members, and report a binding the receiving\n"
         "            Book rebuilt differently (record 4.3.0).\n"),
        ("            Retain the ordered recorded names and map any changed bind identity\n"
         "            before the selection stage resolves this exact parked member.\n",
         "            Retain the ordered recorded names, map a changed spell_id before the\n"
         "            selection stage resolves this exact parked member, and report a\n"
         "            binding the receiving Book rebuilt differently (record 4.3.0).\n"),
        ("        live_spell = spellbook.find_spell_by_spell_id(new_spell_id)\n"
         "        recorded_index_id = self._index_id_for_member(spellbook_id, spell_id)\n"
         "        if recorded_index_id is not None and live_spell is not None:\n",
         "        live_spell = spellbook.find_spell_by_spell_id(new_spell_id)\n"
         "        self._record_binding_change(custody_key, crystal, live_spell)\n"
         "        recorded_index_id = self._index_id_for_member(spellbook_id, spell_id)\n"
         "        if recorded_index_id is not None and live_spell is not None:\n"),
        ("        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)\n"
         "        self._report.record_built(\"spell_staged\")\n",
         "        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)\n"
         "        # The exact lookup (0.2.8253) answers the parked version itself.\n"
         "        self._record_binding_change(custody_key, crystal, spellbook.find_spell_by_spell_id(new_spell_id))\n"
         "        self._report.record_built(\"spell_staged\")\n"),
        ("            - A changed id goes to the report's identity map (as before) and to\n"
         "              the per-Book translation; an unchanged id needs neither.\n",
         "            - A changed id goes to the report's identity map (as before) and to\n"
         "              the per-Book translation; an unchanged id needs neither. A spell_id\n"
         "              changes only with the target's code, never with the receiving\n"
         "              policy (EPIC-2026-10-18-spell_identity_is_the_code).\n"),
        ("    def _translate_spell(self, spellbook_id: str, spell_id: str) -> str:\n",
         "    def _record_binding_change(\n"
         "            self,\n"
         "            custody_key: str,\n"
         "            crystal: Dict[str, object],\n"
         "            live_spell: Optional[Spell],\n"
         "    ) -> None:\n"
         "        \"\"\"\n"
         "        Internal\n\n"
         "        Report one binding a replayed bind rebuilt differently from its record (record 4.3.0).\n\n"
         "        Contract:\n"
         "            - Compares the recorded `binding_hash` with the rebuilt spell's; a\n"
         "              difference goes to `RestoreReport.record_binding_change`, never a\n"
         "              shortfall or a raise - the receiving Book's policy is the rule.\n"
         "            - A record older than 4.3.0 carries no binding hash and is not\n"
         "              compared; a spell the bind did not leave findable is not compared.\n\n"
         "        Args:\n"
         "            custody_key:\n"
         "                The folded custody key the bind replayed.\n"
         "            crystal:\n"
         "                The folded custody payload.\n"
         "            live_spell:\n"
         "                The Spell the replayed bind registered (active or parked), or None.\n\n"
         "        Returns:\n"
         "            None.\n"
         "        \"\"\"\n"
         "        recorded = crystal.get(\"binding_hash\")\n"
         "        if not isinstance(recorded, str) or live_spell is None:\n"
         "            return\n"
         "        live = live_spell.binding_hash\n"
         "        if live != recorded:\n"
         "            self._report.record_binding_change(custody_key, recorded, live)\n\n"
         "    def _translate_spell(self, spellbook_id: str, spell_id: str) -> str:\n"),
        ("            - Detail Spell IDs follow recorded-to-live translation when a bind\n"
         "              changed its signature, within the granting conduit's Book\n"
         "              (0.2.8214); unchanged SHAs remain direct. Conduit endpoints\n",
         "            - Detail spell_ids follow the recorded-to-live translation when a\n"
         "              replayed bind returned another spell_id (its code moved since the\n"
         "              record), within the granting conduit's Book (0.2.8214); unchanged\n"
         "              spell_ids remain direct. Conduit endpoints\n"),
    ], "engine")
    applier.edit(RESTORE, [
        ("                The folded custody key (the spell id, or \"<spell_id>@<frame>\");\n"
         "                receiving policy determines the new bind ID.\n"
         "            crystal:\n"
         "                The folded custody payload.\n\n"
         "        Returns:\n"
         "            None.\n"
         "        \"\"\"\n"
         "        spell_id = self._recorded_spell_id(custody_key, crystal)\n"
         "        target = self._hydrate_target(custody_key, crystal)\n",
         "                The folded custody key (the spell id, or \"<spell_id>@<frame>\");\n"
         "                the replayed spell_id follows the target's code, the receiving\n"
         "                policy its binding.\n"
         "            crystal:\n"
         "                The folded custody payload.\n\n"
         "        Returns:\n"
         "            None.\n"
         "        \"\"\"\n"
         "        spell_id = self._recorded_spell_id(custody_key, crystal)\n"
         "        target = self._hydrate_target(custody_key, crystal)\n"),
        ("                The folded custody key (the spell id, or \"<spell_id>@<frame>\");\n"
         "                receiving policy determines the new bind ID.\n",
         "                The folded custody key (the spell id, or \"<spell_id>@<frame>\");\n"
         "                the replayed spell_id follows the target's code, the receiving\n"
         "                policy its binding.\n"),
    ], "engine args")


def graft(applier: Applier) -> None:
    """S1's graft statements (graft_runner.py)."""
    applier.edit(GRAFT, [
        ("                member count. Parking uses this actual result because receiving\n"
         "                book policy can change the bound member's SHA.\n",
         "                member count. Parking uses this actual result because the bound\n"
         "                member's spell_id follows its code, which may have moved since the\n"
         "                record; the receiving Book's policy decides only its binding.\n"),
        ("                Actual index returned by the selected bind, borrowed for this call.\n"
         "                No recorded-SHA lookup is needed after receiving-book composition.\n",
         "                Actual index returned by the selected bind, borrowed for this call;\n"
         "                no lookup by recorded spell_id is needed.\n"),
        ("            - Receiving-book policy applies at each bind. Selection adoption\n"
         "              follows the live ID returned by the selected member's bind,\n"
         "              which may differ from its recorded SHA.\n",
         "            - Receiving-book policy applies at each bind and decides the binding,\n"
         "              not the spell_id. Selection adoption follows the live spell_id the\n"
         "              selected member's bind returned, which differs from the recorded one\n"
         "              only when the member's code moved since the record.\n"),
    ], "graft")


def apply(applier: Applier) -> None:
    """Stage every crystallizer record edit."""
    crystal(applier)
    version(applier)
    report(applier)
    engine(applier)
    graft(applier)
