"""melder_0, 2026-10-18: S2's test doubles and pins. Every spell double the crystal, the structural snapshot and the
creation cache read carries a binding hash (`Spell.binding_hash`); the structural key and stamp are format 2 with the
binding hash; cache generation 23 and record 4.3.0 are pinned; the crystal's binding hash gets its own unit tests."""

HARNESS = "tests/mocks/crystallizer/spell_crystal_harness.py"
CRYSTALLIZER = "tests/unit/melder/crystallizer/test_crystallizer.py"
SNAPSHOT = "tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py"
RUNTIME = "tests/unit/melder/spellbook/test_cache_runtime_verification.py"
FASTPATH = "tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py"
CAPTURE = "tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py"
SCHEMA = "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"
MANAGED = "tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py"
NEW_CRYSTAL = "tests/unit/melder/crystallizer/test_spell_crystal_binding_hash.py"

DOUBLE_HASH = (
    "        # Binding hash (record 4.3.0): SpellCrystal records the spell's `binding_hash`, the SHA256 of its\n"
    "        # binding manifest (`Spell.binding_hash`). A double carries a fixed 64-hex value per spell_id.\n"
    "        self.binding_hash = hashlib.sha256((\"binding:\" + spell_id).encode(\"utf-8\")).hexdigest()\n"
)


def crystal_doubles(applier) -> None:
    applier.edit(HARNESS, [
        ("import importlib\nimport sys\n", "import hashlib\nimport importlib\nimport sys\n"),
        ("        self.disposal_method_names = []\n        self.profile = SimpleNamespace()\n\n\ndef clear_modules(",
         "        self.disposal_method_names = []\n        self.profile = SimpleNamespace()\n" + DOUBLE_HASH
         + "\n\ndef clear_modules("),
    ], "harness")
    applier.edit(CRYSTALLIZER, [
        ("import importlib\nfrom pathlib import Path\n", "import hashlib\nimport importlib\nfrom pathlib import Path\n"),
        ("        self.disposal_method_names = []\n        self.profile = SimpleNamespace()\n\n\n"
         "@pytest.fixture(autouse=True)\ndef reset_crystallizer_singleton",
         "        self.disposal_method_names = []\n        self.profile = SimpleNamespace()\n" + DOUBLE_HASH
         + "\n\n@pytest.fixture(autouse=True)\ndef reset_crystallizer_singleton"),
    ], "crystallizer double")


def snapshot_stub(applier) -> None:
    applier.edit(SNAPSHOT, [
        ("Every value the seam writes is address-free: type references are (module, qualname) rows, the world\n"
         "stamp is a digest over sorted ids and the posture name, and the payload rows hold spell ids and enum\n"
         "names only. The stubs here mirror the shapes the seam borrows (requirements, profile, registry).\n",
         "Every value the seam writes is address-free: type references are (module, qualname) rows, the world\n"
         "stamp is a digest over the sorted `<spell_id>=<binding_hash>` entries and the posture name, and the\n"
         "payload rows hold spell ids and enum names only. A spell's binding hash (S2) sits in its key beside its\n"
         "spell_id (payload format 2), so a payload captured for one binding is never replayed for another. The\n"
         "stubs here mirror the shapes the seam borrows (requirements, profile, registry).\n"),
        ("        \"spell_id\", \"profile\", \"spell_index\", \"dependencies\", \"spell\", \"spellframe\", "
         "\"_caching_enabled\",\n        \"build_details\",\n    )",
         "        \"spell_id\", \"profile\", \"spell_index\", \"dependencies\", \"spell\", \"spellframe\", "
         "\"_caching_enabled\",\n        \"build_details\", \"binding_hash\",\n    )"),
        ("            caching_enabled: bool = True,\n    ) -> None:\n        self.spell_id = spell_id\n",
         "            caching_enabled: bool = True,\n            binding_hash: Optional[str] = None,\n    ) -> None:\n"
         "        self.spell_id = spell_id\n"
         "        # The spell's binding hash (S2): how the version is bound, apart from its code. A stub derives one\n"
         "        # per spell_id unless a test binds the same spell_id another way.\n"
         "        self.binding_hash = _binding_hash(spell_id) if binding_hash is None else binding_hash\n"),
        ("def _sid(label: str) -> str:\n    \"\"\"Deterministic 64-hex spell id.\"\"\"\n"
         "    return hashlib.sha256(label.encode(\"utf-8\")).hexdigest()\n",
         "def _sid(label: str) -> str:\n    \"\"\"Deterministic 64-hex spell id.\"\"\"\n"
         "    return hashlib.sha256(label.encode(\"utf-8\")).hexdigest()\n\n\n"
         "def _binding_hash(spell_id: str) -> str:\n"
         "    \"\"\"Deterministic 64-hex binding hash a stub spell carries by default.\"\"\"\n"
         "    return _sid(\"binding:\" + spell_id)\n"),
    ], "snapshot stub")


def snapshot_key_and_stamp(applier) -> None:
    applier.edit(SNAPSHOT, [
        ("    \"\"\"The key is value-only: format, the spell id and the sorted annotation refs.\"\"\"\n",
         "    \"\"\"The key is value-only: format 2, the spell id, its binding hash and the sorted annotation refs.\"\"\"\n"),
        ("    assert StructuralSnapshot.structural_key(spell) == {\n"
         "        \"format\": StructuralSnapshot.PAYLOAD_FORMAT,\n"
         "        \"spell_id\": _sid(\"s\"),\n"
         "        \"annotation_refs\": [(__name__, \"_Alpha\")],\n"
         "    }\n",
         "    assert StructuralSnapshot.PAYLOAD_FORMAT == 2\n"
         "    assert StructuralSnapshot.structural_key(spell) == {\n"
         "        \"format\": StructuralSnapshot.PAYLOAD_FORMAT,\n"
         "        \"spell_id\": _sid(\"s\"),\n"
         "        \"binding_hash\": _binding_hash(_sid(\"s\")),\n"
         "        \"annotation_refs\": [(__name__, \"_Alpha\")],\n"
         "    }\n\n\n"
         "def test_structural_key_follows_the_binding_hash_under_one_spell_id() -> None:\n"
         "    \"\"\"One spell_id bound two ways keys two payloads, so neither is replayed for the other binding.\"\"\"\n"
         "    requirements = _Requirements([], _sid(\"s\"))\n"
         "    first = _Spell(_sid(\"s\"), requirements=requirements, binding_hash=_sid(\"unique binding\"))\n"
         "    second = _Spell(_sid(\"s\"), requirements=requirements, binding_hash=_sid(\"many binding\"))\n"
         "    first_key = StructuralSnapshot.structural_key(first)\n"
         "    second_key = StructuralSnapshot.structural_key(second)\n"
         "    assert first_key[\"spell_id\"] == second_key[\"spell_id\"]\n"
         "    assert first_key != second_key\n"),
        ("def _expected_stamp(pool_ids: List[str], posture: str, borrowed: List[str]) -> str:\n"
         "    text = \"\\n\".join((\n"
         "        \"pool:\" + \",\".join(sorted(pool_ids)),\n"
         "        \"posture:\" + posture,\n"
         "        \"borrowed:\" + \",\".join(sorted(borrowed)),\n"
         "    ))\n",
         "def _expected_stamp(pool_ids: List[str], posture: str, borrowed: List[str]) -> str:\n"
         "    \"\"\"The stamp of stub spells with their default binding hashes: `<spell_id>=<binding_hash>` entries.\"\"\"\n"
         "    text = \"\\n\".join((\n"
         "        \"pool:\" + \",\".join(sorted(f\"{spell_id}={_binding_hash(spell_id)}\" for spell_id in pool_ids)),\n"
         "        \"posture:\" + posture,\n"
         "        \"borrowed:\" + \",\".join(sorted(f\"{spell_id}={_binding_hash(spell_id)}\" for spell_id in borrowed)),\n"
         "    ))\n"),
        ("    \"\"\"The stamp is order-independent over the pool and borrowed ids and carries the posture name.\"\"\"\n",
         "    \"\"\"The stamp is order-independent over the pool and borrowed entries and carries the posture name.\"\"\"\n"),
        ("    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a)}, None)) == _expected_stamp([a], \"\", [])\n",
         "    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a)}, None)) == _expected_stamp([a], \"\", [])\n"
         "\n\n"
         "def test_world_stamp_moves_with_a_binding_change_under_one_spell_id() -> None:\n"
         "    \"\"\"One spell_id bound another way is another world, in the Book's pool and among its borrowed spells.\"\"\"\n"
         "    a, b = _sid(\"a\"), _sid(\"b\")\n"
         "    other = _sid(\"another binding\")\n"
         "    stamp = StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a)}))\n"
         "    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a, binding_hash=other)})) != stamp\n"
         "    lent = _Spellbook({a: _Spell(a)})\n"
         "    lent._contracted_spells = {\"conduit\": {\"idx\": _Spell(b)}}\n"
         "    relent = _Spellbook({a: _Spell(a)})\n"
         "    relent._contracted_spells = {\"conduit\": {\"idx\": _Spell(b, binding_hash=other)}}\n"
         "    assert StructuralSnapshot.world_stamp(relent) != StructuralSnapshot.world_stamp(lent)\n"),
    ], "snapshot key and stamp")


def snapshot_payloads(applier) -> None:
    applier.edit(SNAPSHOT, [
        ("        \"key\": {\"format\": 1, \"spell_id\": consumer_id, \"annotation_refs\": [(__name__, \"_Alpha\")]},\n",
         "        \"key\": {\n"
         "            \"format\": 2, \"spell_id\": consumer_id, \"binding_hash\": _binding_hash(consumer_id),\n"
         "            \"annotation_refs\": [(__name__, \"_Alpha\")],\n"
         "        },\n"),
        ("        \"key\": {\"format\": 1, \"spell_id\": spell_id, \"annotation_refs\": [(\"m\", \"T\")]},\n",
         "        \"key\": {\n"
         "            \"format\": 2, \"spell_id\": spell_id, \"binding_hash\": _binding_hash(spell_id),\n"
         "            \"annotation_refs\": [(\"m\", \"T\")],\n"
         "        },\n"),
        ("        pytest.param((\"key\", \"format\"), 2, id=\"format\"),\n",
         "        pytest.param((\"key\", \"format\"), 1, id=\"format\"),\n"),
        ("    assert StructuralSnapshot.payload_well_formed({\"key\": {\"format\": 1, \"spell_id\": spell_id, "
         "\"annotation_refs\": []},\n"
         "                                                  \"world_stamp\": \"s\", \"replayable\": True, \"phase3\": None, "
         "\"phase4\": {}}, spell_id) is False\n",
         "    no_sections = {\n"
         "        \"key\": {\"format\": 2, \"spell_id\": spell_id, \"binding_hash\": _binding_hash(spell_id), "
         "\"annotation_refs\": []},\n"
         "        \"world_stamp\": \"s\", \"replayable\": True, \"phase3\": None, \"phase4\": {},\n"
         "    }\n"
         "    assert StructuralSnapshot.payload_well_formed(no_sections, spell_id) is False\n"),
        ("    \"\"\"Each hit condition is necessary: world stamp, key, replayable flag, live key and a bound index.\"\"\"\n",
         "    \"\"\"Each hit condition is necessary: world stamp, key (its binding hash too), replayable, live key, index.\"\"\"\n"),
        ("        caching_system.upsert_structural_payload(consumer_id, _mutate(consumer_payload, (\"key\", "
         "\"annotation_refs\"), [(\"m\", \"Other\")]))\n"
         "        assert StructuralSnapshot.classify(book, caching_system)[\"misses\"] == {consumer_id}\n",
         "        caching_system.upsert_structural_payload(consumer_id, _mutate(consumer_payload, (\"key\", "
         "\"annotation_refs\"), [(\"m\", \"Other\")]))\n"
         "        assert StructuralSnapshot.classify(book, caching_system)[\"misses\"] == {consumer_id}\n\n"
         "        rebound = _mutate(consumer_payload, (\"key\", \"binding_hash\"), _sid(\"another binding\"))\n"
         "        caching_system.upsert_structural_payload(consumer_id, rebound)\n"
         "        assert StructuralSnapshot.classify(book, caching_system)[\"misses\"] == {consumer_id}\n"),
    ], "snapshot payloads")


def cache_doubles(applier) -> None:
    # The working tree holds this file with 692 CRLF and 4 LF line ends; it is written all CRLF.
    applier.normalize_mixed[RUNTIME] = "\r\n"
    applier.edit(RUNTIME, [
        ("import threading\n", "import hashlib\nimport threading\n"),
        ("        self.spell_name = spell_id\n        self._caching_enabled = caching_enabled\n",
         "        self.spell_name = spell_id\n"
         "        # The binding hash the world stamp and the structural key read (`Spell.binding_hash`, S2).\n"
         "        self.binding_hash = hashlib.sha256((\"binding:\" + spell_id).encode(\"utf-8\")).hexdigest()\n"
         "        self._caching_enabled = caching_enabled\n"),
    ], "runtime double")
    applier.edit(FASTPATH, [
        ("        _spell_id_pool={\"spell-a\": types.SimpleNamespace(is_existing_creation=False, resolvable=True)},\n",
         "        _spell_id_pool={\n"
         "            \"spell-a\": types.SimpleNamespace(is_existing_creation=False, resolvable=True, binding_hash=\"b\" * 64),\n"
         "        },\n"),
    ], "fastpath long double")
    applier.edit_all(FASTPATH, "types.SimpleNamespace(is_existing_creation=False, resolvable=True)",
                     "types.SimpleNamespace(is_existing_creation=False, resolvable=True, binding_hash=\"b\" * 64)",
                     6, "fastpath doubles")


def capture_and_pins(applier) -> None:
    applier.edit(CAPTURE, [
        ("    assert engine_payload[\"key\"] == {\"format\": StructuralSnapshot.PAYLOAD_FORMAT, \"spell_id\": engine_id, "
         "\"annotation_refs\": []}\n"
         "    assert car_payload[\"key\"] == {\n"
         "        \"format\": StructuralSnapshot.PAYLOAD_FORMAT,\n"
         "        \"spell_id\": car_id,\n",
         "    engine_hash = book.find_spell_by_spell_id(engine_id).binding_hash\n"
         "    car_hash = book.find_spell_by_spell_id(car_id).binding_hash\n"
         "    assert engine_payload[\"key\"] == {\n"
         "        \"format\": StructuralSnapshot.PAYLOAD_FORMAT, \"spell_id\": engine_id, \"binding_hash\": engine_hash,\n"
         "        \"annotation_refs\": [],\n"
         "    }\n"
         "    assert car_payload[\"key\"] == {\n"
         "        \"format\": StructuralSnapshot.PAYLOAD_FORMAT,\n"
         "        \"spell_id\": car_id,\n"
         "        \"binding_hash\": car_hash,\n"),
        ("    Contract: Executor and structural tiers name the same ids; Car's rows point at Engine by id; both\n",
         "    Contract: Executor and structural tiers name the same ids; each key carries its spell's binding hash;\n"
         "        Car's rows point at Engine by id; both\n"),
    ], "capture")
    applier.edit(SCHEMA, [
        ("    22: \"managed_settings_leave_spell_id\",\n}\n",
         "    22: \"managed_settings_leave_spell_id\",\n    23: \"binding_manifest_keys\",\n}\n"),
    ], "schema")
    applier.edit(MANAGED, [
        ("def test_record_version_is_4_2_and_reads_4_1_records() -> None:\n"
         "    \"\"\"4.2.0 adds keys (a minor); 4.1 and 4.2 payloads stay readable.\"\"\"\n"
         "    assert RecordVersion.CURRENT == \"4.2.0\"\n"
         "    RecordVersion.check_readable({RecordVersion.KEY: \"4.1.0\"}, \"older record\")\n"
         "    RecordVersion.check_readable({RecordVersion.KEY: \"4.2.0\"}, \"current record\")\n"
         "    with pytest.raises(ValueError, match=\"newer than this code's 4.2.0\"):\n",
         "def test_record_version_is_4_3_and_reads_4_1_and_4_2_records() -> None:\n"
         "    \"\"\"4.2.0 added the managed options and 4.3.0 the binding hash (minors); 4.1-4.3 payloads stay readable.\"\"\"\n"
         "    assert RecordVersion.CURRENT == \"4.3.0\"\n"
         "    RecordVersion.check_readable({RecordVersion.KEY: \"4.1.0\"}, \"older record\")\n"
         "    RecordVersion.check_readable({RecordVersion.KEY: \"4.2.0\"}, \"managed-options record\")\n"
         "    RecordVersion.check_readable({RecordVersion.KEY: \"4.3.0\"}, \"current record\")\n"
         "    with pytest.raises(ValueError, match=\"newer than this code's 4.3.0\"):\n"),
    ], "managed record version")


def apply(applier) -> None:
    crystal_doubles(applier)
    snapshot_stub(applier)
    snapshot_key_and_stamp(applier)
    snapshot_payloads(applier)
    cache_doubles(applier)
    capture_and_pins(applier)
    applier.copy(NEW_CRYSTAL)
