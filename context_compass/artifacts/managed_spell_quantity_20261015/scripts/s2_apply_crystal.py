"""S2: the spell crystal records a managed spell's options; restore and graft replay them; record 4.2.0."""
import pathlib


def edit(path_text: str, pairs: list) -> None:
    """Apply (old, new) replacements to one file, each exactly once."""
    path = pathlib.Path(path_text)
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        count = text.count(old)
        assert count == 1, (path_text, count, old[:80])
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("edited", path_text)


# --- SpellCrystal ---------------------------------------------------------------------------------------------
edit("src/melder/crystallizer/crystals/spell_crystal.py", [
    (
        "from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Union\n",
        "from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union\n",
    ),
    (
        "        - records the spell's frame and its record key (`custody_key`): the\n",
        "        - records a managed spell's options (record 4.2.0) - mode by name, limit,\n"
        "          queue timeout and reset method names - and nothing new for any other\n"
        "          existence, so every other payload is unchanged\n"
        "        - records the spell's frame and its record key (`custody_key`): the\n",
    ),
    (
        "        \"_user_root_paths\",\n"
        "        \"_site_package_root_paths\",\n"
        "    ]\n",
        "        \"_user_root_paths\",\n"
        "        \"_site_package_root_paths\",\n"
        "        \"_managed_spell_mode_name\",\n"
        "        \"_managed_spell_limit\",\n"
        "        \"_managed_spell_timeout_seconds\",\n"
        "        \"_managed_spell_reset_methods\",\n"
        "    ]\n",
    ),
    (
        "            - Captures native resolution capability so replay cannot enable a definition.\n",
        "            - Captures native resolution capability so replay cannot enable a definition.\n"
        "            - Captures a managed spell's options (record 4.2.0) as plain values - the\n"
        "              mode's name, the limit, the queue timeout and the reset names - only when\n"
        "              the existence is `managed_spell_quantity`; other spells capture nothing new.\n",
    ),
    (
        "        self._resolvable: bool = spell.resolvable\n",
        "        self._resolvable: bool = spell.resolvable\n"
        "        # Managed options (record 4.2.0): read only for a managed spell, so every other crystal - and its\n"
        "        # describe() payload - is unchanged. Plain values: the mode is recorded by NAME, never the enum.\n"
        "        if self._existence_name == \"managed_spell_quantity\":\n"
        "            self._managed_spell_mode_name: Optional[str] = spell.managed_spell_mode.name\n"
        "            self._managed_spell_limit: Optional[int] = spell.managed_spell_limit\n"
        "            self._managed_spell_timeout_seconds: Optional[float] = spell.managed_spell_timeout_seconds\n"
        "            self._managed_spell_reset_methods: List[str] = list(spell.managed_spell_reset_methods)\n"
        "        else:\n"
        "            self._managed_spell_mode_name = None\n"
        "            self._managed_spell_limit = None\n"
        "            self._managed_spell_timeout_seconds = None\n"
        "            self._managed_spell_reset_methods = []\n",
    ),
    (
        "            del self._resolvable\n"
        "            del self._disposal_method_names\n",
        "            del self._resolvable\n"
        "            del self._managed_spell_mode_name\n"
        "            del self._managed_spell_limit\n"
        "            del self._managed_spell_timeout_seconds\n"
        "            del self._managed_spell_reset_methods\n"
        "            del self._disposal_method_names\n",
    ),
    (
        "    @property\n"
        "    def profile_family(self) -> str:\n",
        "    @property\n"
        "    def managed_spell_options(self) -> Optional[Dict[str, Any]]:\n"
        "        \"\"\"\n"
        "        Return the managed options recorded at bind (record 4.2.0).\n"
        "\n"
        "        Contract:\n"
        "            - A detached dictionary under the bind option names: `managed_spell_mode` (the\n"
        "              mode's name), `managed_spell_limit`, `managed_spell_timeout_seconds` and\n"
        "              `managed_spell_reset_methods` (a new list).\n"
        "            - None for a spell of any other existence.\n"
        "\n"
        "        Returns:\n"
        "            Optional[Dict[str, Any]]: The recorded options, or None.\n"
        "\n"
        "        Raises:\n"
        "            RuntimeError: If the crystal has been cleaned.\n"
        "        \"\"\"\n"
        "        self.check_cleaned()\n"
        "        with self._lock:\n"
        "            if self._managed_spell_mode_name is None:\n"
        "                return None\n"
        "            return {\n"
        "                \"managed_spell_mode\": self._managed_spell_mode_name,\n"
        "                \"managed_spell_limit\": self._managed_spell_limit,\n"
        "                \"managed_spell_timeout_seconds\": self._managed_spell_timeout_seconds,\n"
        "                \"managed_spell_reset_methods\": list(self._managed_spell_reset_methods),\n"
        "            }\n"
        "\n"
        "    @staticmethod\n"
        "    def managed_bind_options(payload: Mapping[str, object]) -> Dict[str, object]:\n"
        "        \"\"\"\n"
        "        Return the bind keywords that replay a recorded spell's managed options.\n"
        "\n"
        "        Purpose:\n"
        "            The one reader of the four managed keys for the restore and graft lanes, so each\n"
        "            replayed bind passes a managed version's own options and gets its own spell id back.\n"
        "\n"
        "        Contract:\n"
        "            - Without a recorded `managed_spell_mode` (another existence, or a record older than\n"
        "              4.2.0) returns {} - the replay passes nothing new.\n"
        "            - Otherwise returns the four bind keywords: the mode as its recorded name (bind\n"
        "              converts it), the limit and the timeout as recorded, and the reset names as a new\n"
        "              list, or None when none were recorded. Values are not validated here; bind does.\n"
        "\n"
        "        Args:\n"
        "            payload: One spell's custody payload (a `describe()` snapshot, as recorded).\n"
        "\n"
        "        Returns:\n"
        "            Dict[str, object]: Keyword arguments for `Spellbook.bind` / `bind_inactive`.\n"
        "        \"\"\"\n"
        "        mode_name = payload.get(\"managed_spell_mode\")\n"
        "        if mode_name is None:\n"
        "            return {}\n"
        "        reset_methods = payload.get(\"managed_spell_reset_methods\")\n"
        "        return {\n"
        "            \"managed_spell_mode\": str(mode_name),\n"
        "            \"managed_spell_limit\": payload.get(\"managed_spell_limit\"),\n"
        "            \"managed_spell_timeout_seconds\": payload.get(\"managed_spell_timeout_seconds\"),\n"
        "            \"managed_spell_reset_methods\": (\n"
        "                [str(name) for name in reset_methods] if isinstance(reset_methods, (list, tuple))\n"
        "                and reset_methods else None\n"
        "            ),\n"
        "        }\n"
        "\n"
        "    @property\n"
        "    def profile_family(self) -> str:\n",
    ),
    (
        "            analysis_payload = self._analysis.describe()\n"
        "            return {\n"
        "                \"id\": self._id,\n",
        "            analysis_payload = self._analysis.describe()\n"
        "            payload: Dict[str, Any] = {\n"
        "                \"id\": self._id,\n",
    ),
    (
        "                \"ast_from_import_targets_by_module\": analysis_payload[\n"
        "                    \"ast_from_import_targets_by_module\"\n"
        "                ],\n"
        "            }\n",
        "                \"ast_from_import_targets_by_module\": analysis_payload[\n"
        "                    \"ast_from_import_targets_by_module\"\n"
        "                ],\n"
        "            }\n"
        "            # Managed options (record 4.2.0): only a managed spell's payload gains the four keys, so\n"
        "            # every other payload is the one 4.1.0 wrote.\n"
        "            if self._managed_spell_mode_name is not None:\n"
        "                payload[\"managed_spell_mode\"] = self._managed_spell_mode_name\n"
        "                payload[\"managed_spell_limit\"] = self._managed_spell_limit\n"
        "                payload[\"managed_spell_timeout_seconds\"] = self._managed_spell_timeout_seconds\n"
        "                payload[\"managed_spell_reset_methods\"] = list(self._managed_spell_reset_methods)\n"
        "            return payload\n",
    ),
])

# --- RestoreEngine --------------------------------------------------------------------------------------------
edit("src/melder/crystallizer/crystal_loader_system/restore_engine.py", [
    (
        "            Preserve recorded capability; only legacy absence defaults to True.\n"
        "            The spell id comes from the payload, the custody key names\n",
        "            Preserve recorded capability; only legacy absence defaults to True.\n"
        "            Replay a managed spell's recorded options (record 4.2.0), so it\n"
        "            rebinds with its own options and spell id.\n"
        "            The spell id comes from the payload, the custody key names\n",
    ),
    (
        "            profile=str(crystal.get(\"profile_family\", \"general\")),\n"
        "            resolvable=crystal.get(\"resolvable\", True),\n"
        "        )\n"
        "        self._report.record_built(\"spell_active\")\n",
        "            profile=str(crystal.get(\"profile_family\", \"general\")),\n"
        "            resolvable=crystal.get(\"resolvable\", True),\n"
        "            **SpellCrystal.managed_bind_options(crystal),\n"
        "        )\n"
        "        self._report.record_built(\"spell_active\")\n",
    ),
    (
        "            Preserve the parked version's own resolution capability.\n",
        "            Preserve the parked version's own resolution capability and, for a\n"
        "            managed version, its own recorded options (record 4.2.0).\n",
    ),
    (
        "            profile=str(crystal.get(\"profile_family\", \"general\")),\n"
        "            resolvable=crystal.get(\"resolvable\", True),\n"
        "        )\n"
        "        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)\n"
        "        self._report.record_built(\"spell_staged\")\n",
        "            profile=str(crystal.get(\"profile_family\", \"general\")),\n"
        "            resolvable=crystal.get(\"resolvable\", True),\n"
        "            **SpellCrystal.managed_bind_options(crystal),\n"
        "        )\n"
        "        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)\n"
        "        self._report.record_built(\"spell_staged\")\n",
    ),
])

# --- GraftRunner ----------------------------------------------------------------------------------------------
graft = pathlib.Path("src/melder/crystallizer/crystal_loader_system/graft_runner.py")
graft_text = graft.read_text(encoding="utf-8")
old_import = "from melder.crystallizer.persistence.record_version import RecordVersion\n"
assert graft_text.count(old_import) == 1
graft_text = graft_text.replace(
    old_import,
    "from melder.crystallizer.crystals.spell_crystal import SpellCrystal\n" + old_import,
    1,
)
call_tail = (
    "profile=str(crystal.get(\"profile_family\", \"general\")),\n"
)
for indent in ("            ", "                "):
    old = (
        indent + call_tail
        + indent + "resolvable=crystal.get(\"resolvable\", True),\n"
    )
    new = old + indent + "**SpellCrystal.managed_bind_options(crystal),\n"
    expected = 1 if indent == "            " else 2
    assert graft_text.count(old) == expected, (indent, graft_text.count(old))
    graft_text = graft_text.replace(old, new)
for old, new in (
    (
        "        Recorded resolution capability is preserved; legacy absence defaults to True.\n",
        "        Recorded resolution capability is preserved; legacy absence defaults to True. A managed\n"
        "        member's recorded options (record 4.2.0) are replayed with it.\n",
    ),
    (
        "        Every member retains its own recorded resolution capability.\n",
        "        Every member retains its own recorded resolution capability and, when managed, its own\n"
        "        recorded options (record 4.2.0).\n",
    ),
    (
        "            - Each parked member retains its recorded resolution capability.\n",
        "            - Each parked member retains its recorded resolution capability and, when\n"
        "              managed, its recorded options (record 4.2.0).\n",
    ),
):
    assert graft_text.count(old) == 1, old
    graft_text = graft_text.replace(old, new, 1)
graft.write_text(graft_text, encoding="utf-8", newline="\n")
print("edited", graft)

# --- RecordVersion --------------------------------------------------------------------------------------------
edit("src/melder/crystallizer/persistence/record_version.py", [
    (
        "    # a 4.1 loader rebinds frames by name as before.\n"
        "    CURRENT: ClassVar[str] = \"4.1.0\"\n",
        "    # a 4.1 loader rebinds frames by name as before.\n"
        "    # Minor 4.2 adds a managed spell's options to its spell crystal (`managed_spell_mode`,\n"
        "    # `managed_spell_limit`, `managed_spell_timeout_seconds`, `managed_spell_reset_methods`), written only\n"
        "    # for `Existence.managed_spell_quantity`; 4.1 readers ignore them, and a 4.1 record holds no such keys.\n"
        "    CURRENT: ClassVar[str] = \"4.2.0\"\n",
    ),
])
