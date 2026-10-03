"""
Apply the S9 owner-store constants change to a working copy or the tree (anchored edits, line endings kept).

Usage: python apply_s9.py --root <repo root> [--skip-tests]
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

LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
LOWERING_TEST = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
COMPONENT_TEST = "tests/component/melder/aether/conduit/test_conduit_component_owner_store_constants.py"
DOOR_HELD_TEST = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py"


def edit_lowering(root: pathlib.Path) -> None:
    e = Editor(root, LOWERING)
    e.replace(
        "          warm creation whose shared sites all hit builds no dict at all.\n"
        "          Direct-mode plans are unchanged.\n",
        "          warm creation whose shared sites all hit builds no dict at all.\n"
        "          Direct-mode plans are unchanged.\n"
        "        - Owner-store constants (S9, 2026-10-03): a `unique` site whose provider\n"
        "          Spell is owned by an automatic conduit and has an owner store binds\n"
        "          `c{i}` to that store in the namespace and emits no alias line, so the\n"
        "          warm read is `c{i}._creations.get(sid{i})` on a global; every other\n"
        "          shared site (the `meld.<store>` routes, a provider in a dynamic\n"
        "          environment, where ownership transfer repoints the store, or one not\n"
        "          yet owned) emits `c{i} = <route>` as before. The miss keeps its\n"
        "          `c{i}` parameter; the call passes the global. Measured on the VM:\n"
        "          8-10 ns per unique site per creation.\n",
    )
    e.replace(
        "    def _emit_shared_hit(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> None:\n"
        '        """\n'
        "        Emit one shared site where it lives: store read, P2 when pinned, miss call; then its miss.\n"
        '        """\n'
        '        spell_name = f"spells[{index}]"\n'
        '        store = f"c{index}"\n'
        '        sid_name = self._bind(f"sid{index}", step.spell.spell_id)\n'
        '        lines.append(f"{indent}{store} = {self._route(step.existence, spell_name)}")\n',
        "    @staticmethod\n"
        "    def _owner_store_constant(step: SitePlanStep) -> bool:\n"
        '        """\n'
        "        Decide whether one shared site's store is bound as a plan constant (S9, 2026-10-03).\n"
        "\n"
        "        Contract:\n"
        "            True only for `Existence.unique` - the one route that reads\n"
        "            `spells[i]._owner_creations` - when the provider Spell is owned by an\n"
        "            automatic conduit (`_dynamic_environment` False) and already has an\n"
        "            owner store. In a dynamic environment ownership transfer repoints\n"
        "            the store, so the per-creation read stays; a provider not yet owned\n"
        "            keeps the read too, so its failure mode is unchanged.\n"
        "\n"
        "        Args:\n"
        "            step: The shared step.\n"
        "\n"
        "        Returns:\n"
        "            bool: True when `c{i}` is bound in the namespace instead of read per creation.\n"
        '        """\n'
        "        spell = step.spell\n"
        "        return (\n"
        "            step.existence is Existence.unique\n"
        "            and not spell._dynamic_environment\n"
        "            and spell._owner_creations is not None\n"
        "        )\n"
        "\n"
        "    def _emit_shared_hit(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> None:\n"
        '        """\n'
        "        Emit one shared site where it lives: store read (or the bound store), P2 when pinned, miss call;\n"
        "        then its miss.\n"
        '        """\n'
        '        spell_name = f"spells[{index}]"\n'
        '        store = f"c{index}"\n'
        '        sid_name = self._bind(f"sid{index}", step.spell.spell_id)\n'
        "        if self._owner_store_constant(step):\n"
        "            # S9: the owner store of a spell owned by an automatic conduit cannot\n"
        "            # move after conjure, so the plan reads it as a global bound here\n"
        "            # instead of `spells[i]._owner_creations` on every creation.\n"
        "            self._bind(store, step.spell._owner_creations)\n"
        "        else:\n"
        '            lines.append(f"{indent}{store} = {self._route(step.existence, spell_name)}")\n',
    )
    e.save()


def edit_lowering_tests(root: pathlib.Path) -> None:
    e = Editor(root, LOWERING_TEST)
    e.replace(
        "        _lock=threading.RLock(),\n"
        "        _owner_creations=FakeStore(),\n"
        "    )\n",
        "        _lock=threading.RLock(),\n"
        "        _owner_creations=FakeStore(),\n"
        "        # Mirror the live Spell: False until an owning conduit stamps a dynamic environment.\n"
        "        _dynamic_environment=False,\n"
        "    )\n",
    )
    e.text = e.text.rstrip("\n") + "\n" + '''

def _shared_source(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any],
                   keys: Tuple[str, ...]) -> Tuple[str, Dict[str, Any]]:
    """Emit one plan over the shared world and return its (source, namespace) without executing it."""
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", 0), steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, keys)
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=("root", 0),
        root_spell_id="root", root_spell_name="root", arity=0,
    )
    graph.cleanup()
    return source, namespace


def test_unique_site_of_an_automatic_provider_binds_its_owner_store_as_a_constant() -> None:
    """S9: the alias line is gone, `c1` is the owner store itself, and the plan publishes and reuses through it."""
    built, spells, steps, topologies = _shared_world(existence=Existence.unique)
    source, namespace = _shared_source(steps, topologies, ())

    assert "c1 = spells[1]._owner_creations" not in source
    assert "v1 = c1._creations.get(sid1)" in source
    assert namespace["c1"] is spells["s"]._owner_creations
    exec(compile(source, "<test>", "exec"), namespace)
    plan = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
    first = plan(SimpleNamespace(), {})
    second = plan(SimpleNamespace(), {})
    assert first.args[0] is second.args[0] is spells["s"]._owner_creations._creations["s"]
    assert built == Counter({"x": 1, "s": 1, "root": 2})


def test_unique_site_of_a_dynamic_provider_keeps_the_per_creation_store_read() -> None:
    """A provider owned by a dynamic conduit (transfer can repoint its store) is read as before."""
    built, spells, steps, topologies = _shared_world(existence=Existence.unique)
    spells["s"]._dynamic_environment = True
    source, namespace = _shared_source(steps, topologies, ())

    assert "    c1 = spells[1]._owner_creations" in source
    assert "c1" not in namespace
    exec(compile(source, "<test>", "exec"), namespace)
    result = namespace[SitePlanLowering.PLAN_FUNCTION_NAME](SimpleNamespace(), {})
    assert spells["s"]._owner_creations._creations["s"] is result.args[0]


def test_unique_site_of_an_unowned_provider_keeps_the_read() -> None:
    """A provider with no owner store yet emits today's line, so its failure mode is unchanged."""
    _built, spells, steps, topologies = _shared_world(existence=Existence.unique)
    spells["s"]._owner_creations = None
    source, namespace = _shared_source(steps, topologies, ())

    assert "    c1 = spells[1]._owner_creations" in source
    assert "c1" not in namespace


def test_per_conduit_site_read_is_unchanged_by_the_owner_store_constant() -> None:
    """The `meld.<store>` routes never bind a constant: the store is one attribute read on the parameter."""
    _built, _spells, steps, topologies = _shared_world()
    source, namespace = _shared_source(steps, topologies, ())

    assert "    c1 = meld._conduit_creations" in source
    assert "c1" not in namespace
'''
    e.save()


def edit_door_held_root_tests(root: pathlib.Path) -> None:
    e = Editor(root, DOOR_HELD_TEST)
    e.replace(
        "        _lock=threading.RLock(),\n"
        "        _owner_creations=owner_store,\n"
        "    )\n",
        "        _lock=threading.RLock(),\n"
        "        _owner_creations=owner_store,\n"
        "        # Mirror the live Spell: False until an owning conduit stamps a dynamic environment.\n"
        "        _dynamic_environment=False,\n"
        "    )\n",
    )
    e.save()


COMPONENT_SOURCE = '''"""
Component tests of owner-store constants (S9, 2026-10-03) through real conjures.

Scope:
    A Worker over a `unique` Service is melded through a real Conduit in both postures and on a creation-cache
    full hit. In the automatic world the normal plan emitted at hydration binds the Service's owner store as a
    namespace constant and reads no `spells[i]._owner_creations` per creation; a full hit of the same world
    binds the live world's store, never a recorded one; in the dynamic world (ownership transfer can repoint
    the store) the per-creation read is kept. Every world returns one Service object across melds.
"""

import inspect
import shutil
from pathlib import Path
from typing import Any, Dict, Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class Service:
    """The unique provider."""

    def __init__(self) -> None:
        self.calls = 0


class Worker:
    """Transient root over the unique Service."""

    def __init__(self, service: Service) -> None:
        self.service = service


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether and Nexus, as the cache component tests do."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_worlds() -> Iterator[None]:
    """Fresh worlds before and after each case."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def captured_plans(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Tuple[str, Dict[str, Any]]]:
    """Record every normal plan's (source, namespace) by root spell id as the lowering emits it."""
    captured: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    original = SitePlanLowering.emit.__func__

    def capturing(cls: type, **kwargs: Any) -> Any:
        result = original(cls, **kwargs)
        if kwargs.get("normal_mode"):
            captured[kwargs["root_spell_id"]] = (result[0], result[1])
        return result

    monkeypatch.setattr(SitePlanLowering, "emit", classmethod(capturing))
    return captured


def _spellbook(dynamic: bool) -> Spellbook:
    """A Spellbook in the requested posture with the conjure cache off."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state="dynamic" if dynamic else None, disposal=None, disposal_method_names=None,
        system_caching_enabled=False,
    )
    return spellbook


def _bind_world(dynamic: bool) -> Tuple[Spellbook, str, str]:
    """Bind Service (unique) and Worker (many); return (spellbook, service_id, worker_id)."""
    spellbook = _spellbook(dynamic)
    service_id = spellbook.bind(spell=Service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    return spellbook, service_id, worker_id


def test_automatic_world_binds_the_owner_store_and_reuses_the_service(captured_plans: Dict[str, Any]) -> None:
    """The normal plan reads no `spells[i]._owner_creations`; `c0` is the Service's owner store; one Service."""
    spellbook, service_id, worker_id = _bind_world(dynamic=False)
    conduit = spellbook.conjure(name="s9-owner-store-root", dynamic=False)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert isinstance(first, Worker) and first is not second
        assert first.service is second.service and isinstance(first.service, Service)
        source, namespace = captured_plans[worker_id]
        assert "._owner_creations" not in source
        service_spell = spellbook._spell_id_pool[service_id]
        assert namespace["c0"] is service_spell._owner_creations
        assert namespace["c0"]._creations[service_id] is first.service
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_dynamic_world_keeps_the_per_creation_owner_store_read(captured_plans: Dict[str, Any]) -> None:
    """A dynamic conduit's plan reads the owner store per creation (transfer may repoint it); same Service."""
    spellbook, _service_id, worker_id = _bind_world(dynamic=True)
    conduit = spellbook.conjure(name="s9-owner-store-dynamic-root", dynamic=True)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first.service is second.service
        source, namespace = captured_plans[worker_id]
        assert "    c0 = spells[0]._owner_creations" in source
        assert "c0" not in namespace
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def _package_root() -> Path:
    """Return the melder package root the runtime anchors relative cache fragments against."""
    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _fresh_cache_fragment(name: str) -> Path:
    """Empty one repo-local cache root and return it as a package-relative fragment."""
    root = _package_root() / "tests/component/melder/spellbook" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve().relative_to(_package_root())


def _cached_world(frame: str, cache_fragment: Path) -> Tuple[Spellbook, Conduit, str, str]:
    """A fresh automatic world with caching on under the fragment; Service (unique) and Worker (many) conjured."""
    _reset_world()
    configuration = Aether()._ensure_frame(frame).frame_configuration
    configuration.with_system_caching_enabled(True)
    configuration.with_system_cache_root_path(cache_fragment)
    spellbook = Spellbook(aetheric_frame=frame)
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    service_id = spellbook.bind(spell=Service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    conduit = spellbook.conjure(name="s9-owner-store-cached-root")
    return spellbook, conduit, service_id, worker_id


def test_cache_full_hit_binds_the_live_worlds_owner_store(captured_plans: Dict[str, Any]) -> None:
    """A repeat world hydrated from the bundle binds `c0` to ITS Service spell's store and builds its own Service."""
    fragment = _fresh_cache_fragment("_cache_owner_store_constants")
    spellbook, conduit, _service_id, worker_id = _cached_world("s9-owner-store-cached", fragment)
    first_world_service = conduit.meld(spell_id=worker_id).service
    path = spellbook._get_or_create_caching_system().bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)
    conduit.cleanup()
    spellbook.cleanup()

    spellbook, conduit, service_id, worker_id = _cached_world("s9-owner-store-cached", fragment)
    try:
        # The repeat world is a full hit: the bundle is left untouched (the restage contracts' witness).
        assert (path.read_bytes(), path.stat().st_mtime_ns) == written
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first.service is second.service and first.service is not first_world_service
        source, namespace = captured_plans[worker_id]
        assert "._owner_creations" not in source
        assert namespace["c0"] is spellbook._spell_id_pool[service_id]._owner_creations
        assert namespace["c0"]._creations[service_id] is first.service
    finally:
        conduit.cleanup()
        spellbook.cleanup()
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    edit_lowering(root)
    if not args.skip_tests:
        edit_lowering_tests(root)
        edit_door_held_root_tests(root)
        write_new(root, COMPONENT_TEST, COMPONENT_SOURCE)


if __name__ == "__main__":
    main()
