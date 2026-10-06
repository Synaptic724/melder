"""
Apply the executor-cache world-stamp fix to a working copy or the tree (anchored edits, line endings kept).

Usage: python apply_world_stamp.py --root <repo root> [--skip-tests]
"""
import argparse
import difflib
import pathlib
import sys
from typing import List, Tuple


def _read(path: pathlib.Path) -> Tuple[str, List[str]]:
    raw = path.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    endings = ["\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "") for ln in lines]
    text = "".join(ln[:-2] + "\n" if ln.endswith("\r\n") else ln for ln in lines)
    return text, endings


def _write(path: pathlib.Path, old_text: str, old_endings: List[str], new_text: str) -> None:
    dominant = "\r\n" if old_endings.count("\r\n") >= old_endings.count("\n") else "\n"
    old_lines = old_text.split("\n")
    new_lines = new_text.split("\n")
    if old_lines and old_lines[-1] == "":
        old_lines.pop()
    if new_lines and new_lines[-1] == "":
        new_lines.pop()
    out: List[str] = []
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out.append(new_lines[j1 + k] + (old_endings[i1 + k] or dominant))
        elif tag == "replace":
            for k in range(j2 - j1):
                ending = old_endings[i1 + k] if k < (i2 - i1) else dominant
                out.append(new_lines[j1 + k] + (ending or dominant))
        elif tag == "insert":
            for k in range(j2 - j1):
                out.append(new_lines[j1 + k] + dominant)
    path.write_bytes("".join(out).encode("utf-8"))


class Editor:
    def __init__(self, root: pathlib.Path, rel: str) -> None:
        self.path = root / rel
        self.text, self.endings = _read(self.path)
        self.original = self.text

    def replace(self, old: str, new: str) -> None:
        n = self.text.count(old)
        assert n == 1, f"{self.path.name}: anchor occurs {n} times: {old[:70]!r}"
        self.text = self.text.replace(old, new)

    def replace_between(self, start_anchor: str, end_anchor: str, new: str) -> None:
        assert self.text.count(start_anchor) == 1, (self.path.name, start_anchor[:60])
        assert self.text.count(end_anchor) == 1, (self.path.name, end_anchor[:60])
        i = self.text.index(start_anchor)
        j = self.text.index(end_anchor)
        assert i < j
        self.text = self.text[:i] + new + self.text[j:]

    def save(self) -> None:
        assert self.text != self.original, f"{self.path.name}: no change"
        _write(self.path, self.original, self.endings, self.text)
        print("edited", self.path)


def write_new(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    assert not path.exists(), f"{rel} exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    print("wrote ", path)


LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"

CACHING = "src/melder/utilities/caching_system/caching_system.py"
CREATION = "src/melder/aether/spellbook/spellbook_creation_system.py"
CACHE_UNIT_TEST = "tests/unit/melder/utilities/test_caching_system.py"
RUNTIME_UNIT_TEST = "tests/unit/melder/spellbook/test_cache_runtime_verification.py"
FASTPATH_UNIT_TEST = "tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py"
SCHEMA_TEST = "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"
RUNTIME_INTEGRATION_TEST = "tests/integration/melder/spellbook/test_cache_runtime_integration.py"
COMPONENT_TEST = "tests/component/melder/spellbook/test_spellbook_component_executor_cache_world_stamp.py"
HERE = pathlib.Path(__file__).resolve().parent


def edit_caching_system(root: pathlib.Path) -> None:
    e = Editor(root, CACHING)
    e.replace(
        "          Book captures its own on its next conjure).\n"
        "        - Integrity is regeneration-based: a corrupt or version-mismatched\n",
        "          Book captures its own on its next conjure).\n"
        "        - Since generation 19 the envelope also carries `world_stamp`: the\n"
        "          structural tier's world stamp (sorted pool ids, posture, borrowed\n"
        "          ids) recorded by `set_world_stamp` when the executor payloads were\n"
        "          last staged. The executor tier admits a full hit only when the live\n"
        "          world carries the same stamp; \"\" (an empty store, or a bundle\n"
        "          written without the field) never matches, so the rule fails closed.\n"
        "        - Integrity is regeneration-based: a corrupt or version-mismatched\n",
    )
    e.replace(
        "    # for a parameter the key matcher now resolves.\n"
        "    CACHE_VERSION_HISTORY: ClassVar[Mapping[int, str]] = MappingProxyType({\n",
        "    # for a parameter the key matcher now resolves.\n"
        "    # Version 19 retires bundles without the executor-tier world stamp\n"
        "    # (2026-10-03): the executor full hit now requires the envelope's\n"
        "    # `world_stamp` to equal the live world, so a bundle that cannot carry\n"
        "    # one is cold rather than admitted as a stamp-less full hit.\n"
        "    CACHE_VERSION_HISTORY: ClassVar[Mapping[int, str]] = MappingProxyType({\n",
    )
    e.replace(
        '        18: "annotation_address_matching",\n    })\n',
        '        18: "annotation_address_matching",\n        19: "executor_world_stamp",\n    })\n',
    )
    e.replace(
        '        return self._cache_data["structural_payloads"].keys()\n\n    def cleanup(self) -> None:\n',
        '        return self._cache_data["structural_payloads"].keys()\n\n'
        "    @property\n"
        "    def world_stamp(self) -> str:\n"
        '        """\n'
        "        Return the world stamp recorded when the executor payloads were last staged.\n"
        "\n"
        "        Contract:\n"
        "            - The structural tier's `StructuralSnapshot.world_stamp` digest of\n"
        "              the world the bundle's executor payloads were compiled in, or \"\"\n"
        "              for an empty store and for a loaded bundle written without the\n"
        "              field. The executor tier compares it with the live world before\n"
        "              admitting a full hit; \"\" never matches a live stamp.\n"
        "\n"
        "        Returns:\n"
        "            str:\n"
        "                Hex digest, or \"\" when no staging has recorded one.\n"
        '        """\n'
        '        return self._cache_data["world_stamp"]\n'
        "\n"
        "    def set_world_stamp(self, world_stamp: str) -> bool:\n"
        '        """\n'
        "        Record the world the executor payloads were just staged in.\n"
        "\n"
        "        Contract:\n"
        "            - Called by the conjure-end staging AFTER every live payload was\n"
        "              re-staged, so the stamp on disk is never newer than the payloads\n"
        "              it describes; it is the only writer of the field.\n"
        "            - Reports whether the stored value CHANGED, so the caller can flag\n"
        "              the conjure-end emit for a changed world even when no payload\n"
        "              byte changed, and skip it for an unchanged one.\n"
        "            - Serialized under the instance lock like every other mutation.\n"
        "\n"
        "        Args:\n"
        "            world_stamp:\n"
        "                The live `StructuralSnapshot.world_stamp` digest.\n"
        "\n"
        "        Returns:\n"
        "            bool:\n"
        "                True when the recorded stamp was replaced by a different value.\n"
        '        """\n'
        "        with self._lock:\n"
        '            if self._cache_data["world_stamp"] == world_stamp:\n'
        "                return False\n"
        '            self._cache_data["world_stamp"] = world_stamp\n'
        "            return True\n"
        "\n"
        "    def cleanup(self) -> None:\n",
    )
    e.replace(
        '            "spell_payloads": {},\n            "structural_payloads": {},\n        }\n\n    def _load_or_initialize_from_disk(self) -> None:\n',
        '            "spell_payloads": {},\n            "structural_payloads": {},\n            "world_stamp": "",\n        }\n\n'
        "    def _load_or_initialize_from_disk(self) -> None:\n",
    )
    e.replace(
        "            Accepts only the current format, exact installed Melder release\n"
        "            and interpreter tag. Preserves the accepted release in the returned\n"
        "            envelope so a later emit cannot drop or relabel it. The caller\n"
        "            converts rejected or incomplete envelopes into a cold cache.\n",
        "            Accepts only the current format, exact installed Melder release\n"
        "            and interpreter tag. Preserves the accepted release in the returned\n"
        "            envelope so a later emit cannot drop or relabel it. The caller\n"
        "            converts rejected or incomplete envelopes into a cold cache.\n"
        "            `world_stamp` is optional on load (\"\" when absent, which never\n"
        "            admits an executor full hit) but must be a str when present.\n",
    )
    e.replace(
        '                    f"Structural payload for \'{spell_id}\' is not nested-marshal "\n'
        '                    "bytes."\n'
        "                )\n"
        "        return {\n"
        '            "version": version,\n'
        '            "melder_version": melder_version,\n'
        '            "python": python_tag,\n'
        '            "frame_name": loaded_cache_data.get("frame_name", self._frame_name),\n'
        '            "conduit_name": conduit_name,\n'
        '            "spell_payloads": dict(spell_payloads),\n'
        '            "structural_payloads": dict(structural_payloads),\n'
        "        }\n",
        '                    f"Structural payload for \'{spell_id}\' is not nested-marshal "\n'
        '                    "bytes."\n'
        "                )\n"
        "        # The executor-tier world stamp (generation 19) is optional on load so\n"
        "        # a hand-written envelope still reads; an absent stamp is \"\", which\n"
        "        # never admits a full hit, so the omission fails closed.\n"
        '        world_stamp = loaded_cache_data.get("world_stamp", "")\n'
        "        if not isinstance(world_stamp, str):\n"
        "            raise ValueError(\n"
        '                f"Cache world stamp {world_stamp!r} is not a string."\n'
        "            )\n"
        "        return {\n"
        '            "version": version,\n'
        '            "melder_version": melder_version,\n'
        '            "python": python_tag,\n'
        '            "frame_name": loaded_cache_data.get("frame_name", self._frame_name),\n'
        '            "conduit_name": conduit_name,\n'
        '            "spell_payloads": dict(spell_payloads),\n'
        '            "structural_payloads": dict(structural_payloads),\n'
        '            "world_stamp": world_stamp,\n'
        "        }\n",
    )
    e.replace(
        '            "spell_payloads": self._cache_data["spell_payloads"],\n'
        '            "structural_payloads": self._cache_data["structural_payloads"],\n'
        "        }\n"
        "        serialized_cache_data = marshal.dumps(cache_data)\n",
        '            "spell_payloads": self._cache_data["spell_payloads"],\n'
        '            "structural_payloads": self._cache_data["structural_payloads"],\n'
        '            "world_stamp": self._cache_data["world_stamp"],\n'
        "        }\n"
        "        serialized_cache_data = marshal.dumps(cache_data)\n",
    )
    e.save()


def edit_creation_system(root: pathlib.Path) -> None:
    e = Editor(root, CREATION)
    e.replace(
        "              carry cache payloads, so they must not block the full-hit\n"
        "              classification.\n"
        "            - Creates the Spellbook-owned CachingSystem only when caching is\n"
        "              enabled.\n",
        "              carry cache payloads, so they must not block the full-hit\n"
        "              classification.\n"
        "            - A full hit also requires the bundle's recorded world stamp\n"
        "              (`CachingSystem.world_stamp`, written at staging) to equal the\n"
        "              live `StructuralSnapshot.world_stamp(spellbook)` (2026-10-03,\n"
        "              generation 19): a world that differs only by an existing\n"
        "              creation or a non-resolvable definition - ids outside the live\n"
        "              set - recompiles phases 8-11 instead of replaying executors\n"
        "              compiled in another world. Every payload matched under a\n"
        "              different stamp is the mixed path; nothing matched is the full\n"
        "              miss; an empty live set stays a full miss.\n"
        "            - Creates the Spellbook-owned CachingSystem only when caching is\n"
        "              enabled; the stamp is computed only then.\n",
    )
    e.replace(
        "            Dict[str, Any]:\n"
        "                Cache-state summary containing the cache utility, runtime\n"
        "                posture flags, spell-id sets, and the classified cache path.\n"
        '        """\n'
        "        caching_enabled = spellbook._system_caching_enabled_in_aether()\n",
        "            Dict[str, Any]:\n"
        "                Cache-state summary containing the cache utility, runtime\n"
        "                posture flags, spell-id sets, the live `world_stamp` with\n"
        "                `world_matches`, and the classified cache path.\n"
        '        """\n'
        "        caching_enabled = spellbook._system_caching_enabled_in_aether()\n",
    )
    e.replace(
        "        caching_system: CachingSystem | None = None\n"
        "        cached_spell_ids: set[str] = set()\n"
        "        if caching_enabled:\n"
        "            caching_system = spellbook._get_or_create_caching_system(\n"
        "                conduit_name=conduit_name,\n"
        "            )\n"
        "            cached_spell_ids = set(caching_system.cached_spell_ids)\n"
        "        matched_spell_ids = live_spell_ids.intersection(cached_spell_ids)\n"
        "        missing_spell_ids = live_spell_ids.difference(cached_spell_ids)\n"
        "        stale_cached_spell_ids = cached_spell_ids.difference(live_spell_ids)\n"
        "        is_full_hit = bool(live_spell_ids) and not missing_spell_ids\n"
        "        is_mixed = bool(matched_spell_ids) and bool(missing_spell_ids)\n"
        "        is_full_miss = not is_full_hit and not is_mixed\n",
        "        caching_system: CachingSystem | None = None\n"
        "        cached_spell_ids: set[str] = set()\n"
        "        world_stamp = \"\"\n"
        "        world_matches = False\n"
        "        if caching_enabled:\n"
        "            caching_system = spellbook._get_or_create_caching_system(\n"
        "                conduit_name=conduit_name,\n"
        "            )\n"
        "            cached_spell_ids = set(caching_system.cached_spell_ids)\n"
        "            # The executor payloads are a function of the world the structural\n"
        "            # tier already stamps (pool ids, posture, borrowed ids); a bundle\n"
        "            # staged in another world is never replayed as a full hit.\n"
        "            world_stamp = StructuralSnapshot.world_stamp(spellbook)\n"
        "            world_matches = caching_system.world_stamp == world_stamp\n"
        "        matched_spell_ids = live_spell_ids.intersection(cached_spell_ids)\n"
        "        missing_spell_ids = live_spell_ids.difference(cached_spell_ids)\n"
        "        stale_cached_spell_ids = cached_spell_ids.difference(live_spell_ids)\n"
        "        is_full_hit = bool(live_spell_ids) and not missing_spell_ids and world_matches\n"
        "        is_mixed = bool(matched_spell_ids) and not is_full_hit\n"
        "        is_full_miss = not is_full_hit and not is_mixed\n",
    )
    e.replace(
        '            "stale_cached_spell_ids": stale_cached_spell_ids,\n'
        '            "cache_path": SpellbookCreationSystem._resolve_conjure_cache_path(\n',
        '            "stale_cached_spell_ids": stale_cached_spell_ids,\n'
        '            "world_stamp": world_stamp,\n'
        '            "world_matches": world_matches,\n'
        '            "cache_path": SpellbookCreationSystem._resolve_conjure_cache_path(\n',
    )
    e.replace(
        "            - Flags the conjure-end emit when anything was removed, so a pruned\n"
        "              bundle is persisted even if nothing re-staged.\n",
        "            - Flags the conjure-end emit when anything was removed, so a pruned\n"
        "              bundle is persisted even if nothing re-staged.\n"
        "            - Records the live world stamp (`cache_state[\"world_stamp\"]`) in\n"
        "              the envelope AFTER every live spell is re-staged, through\n"
        "              `CachingSystem.set_world_stamp`, and flags the conjure-end emit\n"
        "              when the recorded value changed: a stamp is never persisted\n"
        "              ahead of its payloads, and a changed world is persisted even\n"
        "              when no payload byte changed (2026-10-03, generation 19).\n",
    )
    e.replace(
        "        for spell_id in sorted(cache_state[\"live_spell_ids\"]):\n"
        "            spellbook._emit_spell_cache(spellbook._spell_id_pool[spell_id])\n"
        "        if removed_any:\n"
        "            spellbook._cache_emit_required = True\n",
        "        for spell_id in sorted(cache_state[\"live_spell_ids\"]):\n"
        "            spellbook._emit_spell_cache(spellbook._spell_id_pool[spell_id])\n"
        "        if removed_any:\n"
        "            spellbook._cache_emit_required = True\n"
        "        # The stamp follows the payloads it describes; a changed world must\n"
        "        # reach the disk even when every re-staged byte is unchanged.\n"
        "        if caching_system.set_world_stamp(cache_state[\"world_stamp\"]):\n"
        "            spellbook._cache_emit_required = True\n",
    )
    e.save()


def edit_caching_unit_tests(root: pathlib.Path) -> None:
    e = Editor(root, CACHE_UNIT_TEST)
    e.replace(
        '        pytest.param("structural_payloads", {"a" * 64: {}}, id="decoded-structural-payload"),\n',
        '        pytest.param("structural_payloads", {"a" * 64: {}}, id="decoded-structural-payload"),\n'
        '        pytest.param("world_stamp", 7, id="non-string-world-stamp"),\n',
    )
    e.replace(
        '            "version", "melder_version", "python", "frame_name", "conduit_name",\n'
        '            "spell_payloads", "structural_payloads",\n'
        "        }\n",
        '            "version", "melder_version", "python", "frame_name", "conduit_name",\n'
        '            "spell_payloads", "structural_payloads", "world_stamp",\n'
        "        }\n",
    )
    e.text = e.text.rstrip("\n") + "\n" + '''

def test_caching_system_new_store_carries_an_empty_world_stamp(tmp_path: Path) -> None:
    """An empty store records no world: the stamp is "" until a staging sets it."""
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.world_stamp == ""
    finally:
        caching_system.cleanup()


def test_caching_system_set_world_stamp_reports_a_change_and_round_trips(tmp_path: Path) -> None:
    """
    The setter reports whether the recorded value changed, and the stamp survives emit and reload.

    Contract: the first set of a fresh store changes it; the same value again does not; a different value
    does; the persisted envelope carries the stamp and a reload exposes it.
    """
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.set_world_stamp("a" * 64) is True
        assert caching_system.set_world_stamp("a" * 64) is False
        assert caching_system.set_world_stamp("b" * 64) is True
        assert caching_system.world_stamp == "b" * 64
        caching_system.upsert_spell_payload("c" * 64, _make_spell_payload("stamped"))
        caching_system.emit()
        persisted = marshal.loads(caching_system.bundle_path.read_bytes())
        assert persisted["world_stamp"] == "b" * 64
    finally:
        caching_system.cleanup()
    reloaded = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert reloaded.world_stamp == "b" * 64
        assert reloaded.get_spell_payload("c" * 64) == _make_spell_payload("stamped")
    finally:
        reloaded.cleanup()


def test_caching_system_accepts_current_bundle_without_world_stamp_as_unstamped(tmp_path: Path) -> None:
    """A current-generation bundle written without the field loads with an empty stamp (never a full hit)."""
    bundle = _make_populated_cache_bundle()
    assert "world_stamp" not in bundle
    _write_cache_bundle(tmp_path, marshal.dumps(bundle))
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.get_spell_payload("a" * 64) == _make_spell_payload("cached")
        assert caching_system.world_stamp == ""
        assert caching_system.set_world_stamp("d" * 64) is True
        caching_system.emit()
        assert marshal.loads(caching_system.bundle_path.read_bytes())["world_stamp"] == "d" * 64
    finally:
        caching_system.cleanup()
'''
    e.save()


def edit_runtime_unit_tests(root: pathlib.Path) -> None:
    e = Editor(root, RUNTIME_UNIT_TEST)
    e.replace(
        "from melder.aether.spellbook.spellbook import Spellbook\n"
        "from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem\n",
        "from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (\n"
        "    StructuralSnapshot,\n"
        ")\n"
        "from melder.aether.spellbook.spellbook import Spellbook\n"
        "from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem\n",
    )
    e.replace(
        "        self._payloads: Dict[str, Any] = dict(payloads or {})\n"
        "        self.emit_calls = 0\n"
        "        self.fail_emit = False\n",
        "        self._payloads: Dict[str, Any] = dict(payloads or {})\n"
        "        self.emit_calls = 0\n"
        "        self.fail_emit = False\n"
        "        # Mirror the envelope's world stamp: \"\" until a staging records one.\n"
        "        self.world_stamp = \"\"\n",
    )
    e.replace(
        "    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:\n"
        "        self._payloads[spell_id] = spell_payload\n"
        "\n"
        "    def emit(self) -> None:\n",
        "    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:\n"
        "        self._payloads[spell_id] = spell_payload\n"
        "\n"
        "    def remove_spell_payload(self, spell_id: str) -> bool:\n"
        "        return self._payloads.pop(spell_id, None) is not None\n"
        "\n"
        "    def set_world_stamp(self, world_stamp: str) -> bool:\n"
        "        if self.world_stamp == world_stamp:\n"
        "            return False\n"
        "        self.world_stamp = world_stamp\n"
        "        return True\n"
        "\n"
        "    def emit(self) -> None:\n",
    )
    e.replace(
        "        _spell_id_pool=payload,\n"
        "        _system_caching_enabled_in_aether=lambda: caching_enabled,\n",
        "        _spell_id_pool=payload,\n"
        "        # The world stamp reads the posture and the borrowed ids: none bound here.\n"
        "        _aetheric_frame_configuration=None,\n"
        "        _contracted_spells={},\n"
        "        _system_caching_enabled_in_aether=lambda: caching_enabled,\n",
    )
    e.replace(
        '@pytest.mark.parametrize(\n'
        '    ("caching_enabled", "cached_ids", "expected_path", "expected_full_hit", "expected_mixed", "expected_full_miss"),\n'
        "    [\n"
        '        (False, (), "disabled", False, False, True),\n'
        '        (True, ("spell-a", "spell-b"), "full_hit", True, False, False),\n'
        '        (True, ("spell-a", "spell-b", "stale-spell"), "full_hit", True, False, False),\n'
        '        (True, ("spell-a",), "mixed", False, True, False),\n'
        '        (True, (), "full_miss", False, False, True),\n'
        '        (True, ("stale-spell",), "full_miss", False, False, True),\n'
        "    ],\n"
        ")\n"
        "def test_build_conjure_cache_state_classifies_live_vs_cached_spell_sets(\n"
        "        monkeypatch: pytest.MonkeyPatch,\n"
        "        caching_enabled: bool,\n"
        "        cached_ids: tuple[str, ...],\n"
        "        expected_path: str,\n"
        "        expected_full_hit: bool,\n"
        "        expected_mixed: bool,\n"
        "        expected_full_miss: bool,\n"
        ") -> None:\n"
        '    """Verify cache-state classification is driven by live subset coverage."""\n'
        '    caching_system = _StubCachingSystem({spell_id: {"spell_id": spell_id} for spell_id in cached_ids})\n'
        "    spellbook = _make_spellbook_stub(\n"
        '        live_spell_ids=("spell-a", "spell-b"),\n'
        "        caching_enabled=caching_enabled,\n"
        "        caching_system=caching_system,\n"
        "    )\n"
        "\n"
        "    cache_state = SpellbookCreationSystem._build_conjure_cache_state(\n",
        '@pytest.mark.parametrize(\n'
        '    ("caching_enabled", "cached_ids", "stamp", "expected_path", "expected_full_hit", "expected_mixed", "expected_full_miss"),\n'
        "    [\n"
        '        (False, (), "live", "disabled", False, False, True),\n'
        '        (True, ("spell-a", "spell-b"), "live", "full_hit", True, False, False),\n'
        '        (True, ("spell-a", "spell-b", "stale-spell"), "live", "full_hit", True, False, False),\n'
        '        (True, ("spell-a",), "live", "mixed", False, True, False),\n'
        '        (True, (), "live", "full_miss", False, False, True),\n'
        '        (True, ("stale-spell",), "live", "full_miss", False, False, True),\n'
        "        # A bundle staged in another world (or never stamped) is never a full hit, however\n"
        "        # complete its payload set: every payload matched is the mixed path, none the full miss.\n"
        '        (True, ("spell-a", "spell-b"), "other", "mixed", False, True, False),\n'
        '        (True, ("spell-a", "spell-b", "stale-spell"), "", "mixed", False, True, False),\n'
        '        (True, ("spell-a",), "other", "mixed", False, True, False),\n'
        '        (True, (), "other", "full_miss", False, False, True),\n'
        '        (True, ("stale-spell",), "", "full_miss", False, False, True),\n'
        "    ],\n"
        ")\n"
        "def test_build_conjure_cache_state_classifies_live_vs_cached_spell_sets(\n"
        "        monkeypatch: pytest.MonkeyPatch,\n"
        "        caching_enabled: bool,\n"
        "        cached_ids: tuple[str, ...],\n"
        "        stamp: str,\n"
        "        expected_path: str,\n"
        "        expected_full_hit: bool,\n"
        "        expected_mixed: bool,\n"
        "        expected_full_miss: bool,\n"
        ") -> None:\n"
        '    """Verify cache-state classification is driven by live subset coverage and the world stamp."""\n'
        '    caching_system = _StubCachingSystem({spell_id: {"spell_id": spell_id} for spell_id in cached_ids})\n'
        "    spellbook = _make_spellbook_stub(\n"
        '        live_spell_ids=("spell-a", "spell-b"),\n'
        "        caching_enabled=caching_enabled,\n"
        "        caching_system=caching_system,\n"
        "    )\n"
        '    live_stamp = StructuralSnapshot.world_stamp(spellbook)\n'
        '    caching_system.world_stamp = live_stamp if stamp == "live" else ("x" * 64 if stamp == "other" else "")\n'
        "\n"
        "    cache_state = SpellbookCreationSystem._build_conjure_cache_state(\n",
    )
    e.replace(
        '    assert cache_state["cache_path"] == expected_path\n'
        '    assert cache_state["is_full_hit"] is expected_full_hit\n'
        '    assert cache_state["is_mixed"] is expected_mixed\n'
        '    assert cache_state["is_full_miss"] is expected_full_miss\n'
        "\n"
        "\n"
        '@pytest.mark.parametrize("dynamic", [True, False])\n',
        '    assert cache_state["cache_path"] == expected_path\n'
        '    assert cache_state["is_full_hit"] is expected_full_hit\n'
        '    assert cache_state["is_mixed"] is expected_mixed\n'
        '    assert cache_state["is_full_miss"] is expected_full_miss\n'
        '    assert cache_state["world_stamp"] == (live_stamp if caching_enabled else "")\n'
        '    assert cache_state["world_matches"] is (caching_enabled and stamp == "live")\n'
        "\n"
        "\n"
        '@pytest.mark.parametrize("dynamic", [True, False])\n',
    )
    e.text = e.text.rstrip("\n") + "\n" + '''

def _stage(spellbook: Any, caching_system: _StubCachingSystem, world_stamp: str) -> None:
    """Run the conjure-end staging with no live spells and the given live stamp."""
    SpellbookCreationSystem._stage_spell_payloads_at_conjure_end(
        spellbook=spellbook,
        cache_state={
            "caching_system": caching_system,
            "live_spell_ids": set(),
            "world_stamp": world_stamp,
        },
    )


def test_stage_spell_payloads_records_the_world_stamp_and_flags_the_emit_when_it_changed() -> None:
    """A changed world reaches the disk even when no payload was removed or re-staged."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True, caching_system=caching_system)

    _stage(spellbook, caching_system, "s" * 64)

    assert caching_system.world_stamp == "s" * 64
    assert spellbook._cache_emit_required is True


def test_stage_spell_payloads_does_not_flag_the_emit_for_an_unchanged_stamp() -> None:
    """Re-staging an unchanged world with nothing to remove writes nothing."""
    caching_system = _StubCachingSystem()
    caching_system.world_stamp = "s" * 64
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True, caching_system=caching_system)

    _stage(spellbook, caching_system, "s" * 64)

    assert caching_system.world_stamp == "s" * 64
    assert spellbook._cache_emit_required is False


def test_stage_spell_payloads_still_flags_the_emit_for_a_pruned_payload() -> None:
    """A stale payload removed under an unchanged stamp is persisted as before."""
    caching_system = _StubCachingSystem({"stale-spell": {"spell_id": "stale-spell"}})
    caching_system.world_stamp = "s" * 64
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True, caching_system=caching_system)

    _stage(spellbook, caching_system, "s" * 64)

    assert tuple(caching_system.cached_spell_ids) == ()
    assert spellbook._cache_emit_required is True


def test_stage_spell_payloads_noops_without_a_cache_utility() -> None:
    """Caching off: no stamp is read or written."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=False)

    SpellbookCreationSystem._stage_spell_payloads_at_conjure_end(
        spellbook=spellbook,
        cache_state={"caching_system": None, "live_spell_ids": set(), "world_stamp": "s" * 64},
    )

    assert spellbook._cache_emit_required is False
'''
    e.save()


def edit_fastpath_unit_tests(root: pathlib.Path) -> None:
    e = Editor(root, FASTPATH_UNIT_TEST)
    e.replace(
        "from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem\n",
        "from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (\n"
        "    StructuralSnapshot,\n"
        ")\n"
        "from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem\n",
    )
    e.replace(
        "        self._payloads_by_spell_id = payloads_by_spell_id or {}\n"
        "\n"
        "    @property\n"
        "    def cached_spell_ids(self):\n",
        "        self._payloads_by_spell_id = payloads_by_spell_id or {}\n"
        "        # Mirror the envelope's executor-tier world stamp (generation 19).\n"
        "        self.world_stamp: str = \"\"\n"
        "\n"
        "    @property\n"
        "    def cached_spell_ids(self):\n",
    )
    stub_attrs = (
        "        _system_caching_enabled_in_aether=lambda: True,\n"
        "        _get_or_create_caching_system=lambda conduit_name=None: caching_system,\n"
        "    )\n"
    )
    assert e.text.count(stub_attrs) == 3, e.text.count(stub_attrs)
    e.text = e.text.replace(
        stub_attrs,
        "        _system_caching_enabled_in_aether=lambda: True,\n"
        "        _get_or_create_caching_system=lambda conduit_name=None: caching_system,\n"
        "        _aetheric_frame_configuration=None,\n"
        "        _contracted_spells={},\n"
        "    )\n",
    )
    full_hit_call = (
        "    cache_state = SpellbookCreationSystem._build_conjure_cache_state(\n"
        "        spellbook=spellbook,\n"
        "        dynamic=False,\n"
        "    )\n"
        "\n"
        "    assert cache_state[\"caching_enabled\"] is True\n"
    )
    e.replace(
        full_hit_call,
        "    caching_system.world_stamp = StructuralSnapshot.world_stamp(spellbook)\n" + full_hit_call,
    )
    surplus_call = (
        "    cache_state = SpellbookCreationSystem._build_conjure_cache_state(\n"
        "        spellbook=spellbook,\n"
        "        dynamic=False,\n"
        "    )\n"
        "\n"
        "    assert cache_state[\"cache_path\"] == \"full_hit\"\n"
    )
    e.replace(
        surplus_call,
        "    caching_system.world_stamp = StructuralSnapshot.world_stamp(spellbook)\n" + surplus_call,
    )
    e.save()


def edit_schema_test(root: pathlib.Path) -> None:
    e = Editor(root, SCHEMA_TEST)
    e.replace(
        '    18: "annotation_address_matching",\n}\n',
        '    18: "annotation_address_matching",\n    19: "executor_world_stamp",\n}\n',
    )
    e.save()


def edit_runtime_integration_test(root: pathlib.Path) -> None:
    e = Editor(root, RUNTIME_INTEGRATION_TEST)
    e.replace(
        '@pytest.mark.parametrize("dynamic", [False, True])\n'
        "def test_cache_integration_stale_surplus_cache_still_full_hits(dynamic: bool) -> None:\n"
        '    """Verify extra cached spell ids do not block full-hit reload for live ids."""\n'
        "    cache_root_path = _prepare_case_cache_root(\n"
        "        f\"_cache_runtime_surplus_full_hit_{'dynamic' if dynamic else 'automatic'}\"\n"
        "    )\n",
        '@pytest.mark.parametrize("dynamic", [False, True])\n'
        "def test_cache_integration_removed_spell_reruns_once_then_full_hits(dynamic: bool) -> None:\n"
        '    """\n'
        "    A removed spell is a changed world: the next run recompiles, the one after full-hits.\n"
        "\n"
        "    Before generation 19 a surplus cached id was ignored and the second world full-hit although its\n"
        "    executors were compiled in a world with one more spell; the world stamp now retires that bundle\n"
        "    once, and the re-staged bundle serves the repeat world as a full hit.\n"
        '    """\n'
        "    cache_root_path = _prepare_case_cache_root(\n"
        "        f\"_cache_runtime_removed_spell_{'dynamic' if dynamic else 'automatic'}\"\n"
        "    )\n",
    )
    e.replace(
        "    second_spell_ids = _bind_simple_spells(second_spellbook, include_logger=False)\n"
        '    second_conduit = _conjure(second_spellbook, conduit_name="root", dynamic=dynamic)\n'
        "    try:\n"
        "        spell = _get_spell(second_spellbook, second_spell_ids[BasicService])\n"
        "        assert spell._creation_context is not None\n"
        "        assert spell.resolution_required is False\n"
        "    finally:\n"
        "        second_conduit.cleanup()\n",
        "    second_spell_ids = _bind_simple_spells(second_spellbook, include_logger=False)\n"
        '    second_conduit = _conjure(second_spellbook, conduit_name="root", dynamic=dynamic)\n'
        "    try:\n"
        "        spell = _get_spell(second_spellbook, second_spell_ids[BasicService])\n"
        "        # Rerun: phases 8-11 compiled the spell again; no context was preloaded.\n"
        "        assert spell._creation_context is None\n"
        "        assert spell._compiler_artifact._spell_codegen_creation is not None\n"
        "    finally:\n"
        "        second_conduit.cleanup()\n"
        "    _reset_runtime_singletons()\n"
        "\n"
        "    third_spellbook = _make_spellbook(\n"
        '        frame_name="cache-runtime-surplus",\n'
        "        cache_root_fragment=_build_cache_root_fragment(cache_root_path),\n"
        "        dynamic=dynamic,\n"
        "    )\n"
        "    third_spell_ids = _bind_simple_spells(third_spellbook, include_logger=False)\n"
        '    third_conduit = _conjure(third_spellbook, conduit_name="root", dynamic=dynamic)\n'
        "    try:\n"
        "        spell = _get_spell(third_spellbook, third_spell_ids[BasicService])\n"
        "        # The repeat of the re-staged world is a full hit.\n"
        "        assert spell._creation_context is not None\n"
        "        assert spell.resolution_required is False\n"
        "    finally:\n"
        "        third_conduit.cleanup()\n",
    )
    e.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    edit_caching_system(root)
    edit_creation_system(root)
    if not args.skip_tests:
        edit_caching_unit_tests(root)
        edit_runtime_unit_tests(root)
        edit_fastpath_unit_tests(root)
        edit_schema_test(root)
        edit_runtime_integration_test(root)
        write_new(root, COMPONENT_TEST, (HERE / "component_test_source.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
