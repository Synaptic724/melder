"""
Apply the S8 lazy instance_results change to a working copy or the tree (anchored edits, line endings kept).

Usage: python apply_s8.py --root <repo root> [--skip-tests]
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
CACHE_TEST = "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"
LOWERING_TEST = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"


def edit_lowering(root: pathlib.Path) -> None:
    e = Editor(root, LOWERING)
    e.replace(
        "        - Dict mode (`instance_results`) is emitted only when a generic step\n"
        "          needs dependency values by instance key; misses then receive the dict\n"
        "          and record their sites in it.\n",
        "        - Generic steps read their dependency values through a dict LITERAL\n"
        "          (lazy `instance_results`, 2026-10-03): each generic construction is\n"
        "          preceded by `instance_results = {key: v, ...}` holding exactly the\n"
        "          (masked) step's dependency keys, built where the step runs from\n"
        "          locals the plan already holds. No dict is allocated at the plan top,\n"
        "          nothing is stored per step and misses take no dict parameter, so a\n"
        "          warm creation whose shared sites all hit builds no dict at all.\n"
        "          Direct-mode plans are unchanged.\n",
    )
    e.replace(
        "        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],\n"
        "          v...)`: the outer values its sites read, in step order. It builds the\n",
        "        - A miss function takes `(meld, ov, c{i}, [args], v...)`: the outer\n"
        "          values its sites read (call operands or dict-literal values), in\n"
        "          step order. It builds the\n",
    )
    e.replace('        "_direct",\n        "_dict_mode",\n', '        "_direct",\n        "_index_by_key",\n')
    e.replace(
        "        self._direct: List[bool] = []\n        self._dict_mode: bool = False\n",
        "        self._direct: List[bool] = []\n        self._index_by_key: Dict[SiteInstanceKey, int] = {}\n",
    )
    e.replace("        del self._direct\n        del self._dict_mode\n", "        del self._direct\n        del self._index_by_key\n")
    e.replace(
        "        self._direct = [self._is_direct(step) for step in self._steps]\n"
        "        self._dict_mode = not all(self._direct)\n        self._place()\n",
        "        self._direct = [self._is_direct(step) for step in self._steps]\n        self._place()\n",
    )
    e.replace(
        "        body.extend(self._unresolved_check_lines(None, \"    \"))\n"
        "        if self._dict_mode:\n            body.append(\"    instance_results = {}\")\n",
        "        body.extend(self._unresolved_check_lines(None, \"    \"))\n",
    )
    e.replace(
        "            - Then each shared site's outer values are computed bottom-up: the\n"
        "              direct operands of the steps built inside its miss (and of its own\n"
        "              construction) that live outside it, plus what its nested misses need.\n",
        "            - Then each shared site's outer values are computed bottom-up: the\n"
        "              operands - call operands or dict-literal values - of the steps built\n"
        "              inside its miss (and of its own construction) that live outside it,\n"
        "              plus what its nested misses need.\n",
    )
    e.replace(
        "        index_by_key = {step.instance_key: index for index, step in enumerate(steps)}\n"
        "        providers_by_consumer: List[List[int]] = []\n",
        "        index_by_key = {step.instance_key: index for index, step in enumerate(steps)}\n"
        "        self._index_by_key = index_by_key\n"
        "        providers_by_consumer: List[List[int]] = []\n",
    )
    e.replace(
        "                # A nested shared site builds inside its own miss: only what that\n"
        "                # miss needs from outside passes through here.\n"
        "                if self._shared[member]:\n"
        "                    needed.update(value_params[member])\n"
        "                elif self._direct[member]:\n"
        "                    needed.update(providers_by_consumer[member])\n"
        "            if self._direct[index]:\n"
        "                needed.update(providers_by_consumer[index])\n",
        "                # A nested shared site builds inside its own miss: only what that\n"
        "                # miss needs from outside passes through here. A generic member\n"
        "                # reads its providers through its dict literal, so they pass\n"
        "                # through exactly like a direct member's call operands.\n"
        "                if self._shared[member]:\n"
        "                    needed.update(value_params[member])\n"
        "                else:\n"
        "                    needed.update(providers_by_consumer[member])\n"
        "            needed.update(providers_by_consumer[index])\n",
    )
    e.replace(
        "        Contract:\n            `instance_results` in dict mode, `args` for the root when `__args__` is\n"
        "            supplied, then the outer values in step order.\n"
        "        \"\"\"\n        names: List[str] = []\n        if self._dict_mode:\n"
        "            names.append(\"instance_results\")\n        if self._arity > 0",
        "        Contract:\n            `args` for the root when `__args__` is supplied, then the outer\n"
        "            values in step order (a generic member's providers included).\n"
        "        \"\"\"\n        names: List[str] = []\n        if self._arity > 0",
    )
    e.replace(
        "            elif self._emit_many(index, step, indent, lines):\n"
        "                uses_many_store = True\n"
        "            if self._dict_mode:\n"
        "                key_name = self._bind(f\"key{index}\", step.instance_key)\n"
        "                lines.append(f\"{indent}instance_results[{key_name}] = v{index}\")\n"
        "        return uses_many_store\n",
        "            elif self._emit_many(index, step, indent, lines):\n"
        "                uses_many_store = True\n"
        "        return uses_many_store\n",
    )
    e.replace(
        "    def _emit_construct(\n",
        "    def _emit_results_literal(self, step: SitePlanStep, indent: str, lines: List[str]) -> None:\n"
        "        \"\"\"\n"
        "        Emit the dict literal one generic construction reads: its dependency values by instance key.\n"
        "\n"
        "        Contract:\n"
        "            `step` is the step the construct helper receives (the masked copy\n"
        "            when values are supplied), so the literal carries exactly the keys\n"
        "            `_build_kwargs_no_overrides` reads from `dependency_resolution_order`,\n"
        "            in that order, each bound to its provider's local; a provider feeding\n"
        "            two parameters appears once. A step that reads no key gets `{}`.\n"
        "            Every provider is a local in scope where the step is constructed:\n"
        "            providers precede consumers, and `_place` passes outer providers into\n"
        "            a miss. The literal is rebuilt per construction; nothing shared is\n"
        "            held in the namespace.\n"
        "\n"
        "        Args:\n"
        "            step: The step (or masked copy) handed to the construct helper.\n"
        "            indent: Indentation of the emitted line.\n"
        "            lines: Target line list, appended in place.\n"
        "\n"
        "        Raises:\n"
        "            RuntimeError: When a dependency key has no kept step.\n"
        "\n"
        "        Returns:\n"
        "            None.\n"
        "        \"\"\"\n"
        "        entries: List[str] = []\n"
        "        providers: List[int] = []\n"
        "        for _, dependency_keys in step.dependency_resolution_order:\n"
        "            for key in dependency_keys:\n"
        "                provider = self._index_by_key.get(key)\n"
        "                if provider is None:\n"
        "                    raise RuntimeError(\n"
        "                        f\"Key-set plan dependency {key!r} of {step.instance_key!r} has no kept step.\"\n"
        "                    )\n"
        "                if provider in providers:\n"
        "                    continue\n"
        "                providers.append(provider)\n"
        "                key_name = self._bind(f\"key{provider}\", key)\n"
        "                entries.append(f\"{key_name}: v{provider}\")\n"
        "        lines.append(f\"{indent}instance_results = {{{', '.join(entries)}}}\")\n"
        "\n"
        "    def _emit_construct(\n",
    )
    e.replace(
        "            Direct steps call the spell with operands and route failures through\n"
        "            `_raise_meld_construction_error`. Generic steps call the no-overrides helper, or the\n"
        "            supplied-values helper on a masked copy when the step has winners.\n",
        "            Direct steps call the spell with operands and route failures through\n"
        "            `_raise_meld_construction_error`. Generic steps first get their dict literal\n"
        "            (`_emit_results_literal`), then call the no-overrides helper, or the\n"
        "            supplied-values helper on a masked copy when the step has winners.\n",
    )
    e.replace(
        "            if not supplied and not is_root_args:\n"
        "                step_name = self._bind(f\"st{index}\", step)\n",
        "            if not supplied and not is_root_args:\n"
        "                self._emit_results_literal(step, indent, lines)\n"
        "                step_name = self._bind(f\"st{index}\", step)\n",
    )
    e.replace(
        "            masked = step.masked(supplied, is_root_args)\n"
        "            self._masked.append(masked)\n"
        "            masked_name = self._bind(f\"st{index}\", masked)\n",
        "            masked = step.masked(supplied, is_root_args)\n"
        "            self._masked.append(masked)\n"
        "            self._emit_results_literal(masked, indent, lines)\n"
        "            masked_name = self._bind(f\"st{index}\", masked)\n",
    )
    e.save()


def edit_caching(root: pathlib.Path) -> None:
    e = Editor(root, CACHING)
    e.replace(
        "    # trim (2026-10-01): they still call the public `add_many_creations`\n"
        "    # and stay correct, but pay the old keyword call per creation.\n",
        "    # trim (2026-10-01): they still call the public `add_many_creations`\n"
        "    # and stay correct, but pay the old keyword call per creation.\n"
        "    # Version 17 retires site plans emitted before lazy `instance_results`\n"
        "    # (2026-10-03): they still run correctly, but allocate and fill the\n"
        "    # dict on every warm creation of a dict-mode root.\n",
    )
    e.replace(
        '        16: "many_registration_per_key_methods",\n    })\n',
        '        16: "many_registration_per_key_methods",\n        17: "lazy_instance_results",\n    })\n',
    )
    e.save()
    t = Editor(root, CACHE_TEST)
    t.replace('    16: "many_registration_per_key_methods",\n', '    16: "many_registration_per_key_methods",\n    17: "lazy_instance_results",\n')
    t.save()


UNIT_TESTS = '''

# ---------------------------------------------------------------------------------------------------------------
# Lazy instance_results (S8, 2026-10-03): no dict on the warm path; a literal per generic construction.


def _generic_miss_world() -> Tuple[Counter, Dict[str, SimpleNamespace], Tuple[SitePlanStep, ...], Dict[str, Any]]:
    """Root(s: S(x: X(y: Y, z: Z, c=contract)), z: Z) with S and Z shared and X generic (contract payload)."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "y": _spell("y", built), "z": _spell("z", built, shared), "x": _spell("x", built),
        "s": _spell("s", built, shared), "root": _spell("root", built),
    }
    generic = SitePlanStep(
        instance_key=("x", 3), spell=spells["x"], existence=Existence.many,
        dependency_resolution_order=(("y", (("y", 4),)), ("z", (("z", None),))),
        collection_param_names=frozenset(), uses_positional_override=False, contract_positional_override=None,
        has_contract_payload=True, contract_payload={"c": "contract"}, use_spell_lock_hint=False,
    )
    steps = (
        _step(("y", 4), spells["y"]),
        _step(("z", None), spells["z"]),
        generic,
        _step(("s", None), spells["s"], ("x", (("x", 3),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),)), ("z", (("z", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "z", 1))),
        "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
        "x": SpellLocalTopology("x", (_socket("x", "y", 0), _socket("x", "z", 1))),
    }
    return built, spells, steps, topologies


def _emit_source(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any], root_key: Key,
                 keys: Tuple[str, ...] = ()) -> Tuple[Callable[..., Any], str]:
    """Resolve, emit and compile one override-mode plan; return it with its source."""
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=root_key, steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, keys)
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=root_key,
        root_spell_id="root", root_spell_name="root", arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    graph.cleanup()
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], source


def test_dict_mode_plan_builds_no_dict_on_the_warm_path_and_a_literal_in_the_miss() -> None:
    """The plan top allocates and stores nothing; X, built inside S's miss, gets a literal of exactly {y, z}."""
    built, _spells, steps, topologies = _generic_miss_world()
    plan, source = _emit_source(steps, topologies, ("root", 0))
    body = source[source.index(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}"):]
    assert "instance_results" not in body
    assert "instance_results[" not in source
    assert re.search(r"def _miss3\\(meld, ov, c3, v1\\):", source), source
    assert source.count("instance_results = ") == 1
    assert "instance_results = {key0: v0, key1: v1}" in source
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = plan(meld, {})
    x = first.args[0].args[0]
    assert x.kwargs["y"].name == "y" and x.kwargs["c"] == "contract" and x.kwargs["z"] is first.args[1]
    second = plan(meld, {})
    assert second.args == first.args
    assert built == Counter({"y": 1, "z": 1, "x": 1, "s": 1, "root": 2})


def test_generic_step_without_dependencies_gets_an_empty_literal() -> None:
    """An existing-object site reads no key: its miss builds from `{}` and the warm hit reads the store only."""
    built: Counter = Counter()
    existing = _spell("e", built, Existence.unique)
    existing.is_existing_creation = True
    existing.user_created_object = object()
    spells = {"e": existing, "root": _spell("root", built)}
    steps = (_step(("e", None), spells["e"]), _step(("root", 0), spells["root"], ("e", (("e", None),))))
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "e", 0),))}
    plan, source = _emit_source(steps, topologies, ("root", 0))
    assert source.count("instance_results = {}") == 1
    assert "instance_results[" not in source
    assert "instance_results" not in source[source.index(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}"):]
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = plan(meld, {})
    assert first.args[0] is existing.user_created_object
    assert plan(meld, {}).args[0] is first.args[0]
    assert built == Counter({"root": 2})


def test_masked_generic_step_literal_omits_the_supplied_parameter() -> None:
    """With X's `y` supplied, X's literal carries only Z (Y is cut from the plan) and the value is applied last."""
    built, _spells, steps, topologies = _generic_miss_world()
    plan, source = _emit_source(steps, topologies, ("root", 0), ("s>x>y",))
    # The demand cuts Y, so the kept steps renumber (z=0, x=1, s=2, root=3): X's literal is Z alone.
    assert source.count("instance_results = ") == 1
    assert "instance_results = {key0: v0}" in source
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = plan(meld, {"s>x>y": "given"})
    x = first.args[0].args[0]
    assert x.kwargs["y"] == "given" and x.kwargs["c"] == "contract" and x.kwargs["z"] is first.args[1]
    assert built == Counter({"z": 1, "x": 1, "s": 1, "root": 1})


def test_generic_collection_parameter_literal_carries_every_member_key() -> None:
    """A contract-payload step with a two-member list parameter gets both member keys and a two-element list."""
    built: Counter = Counter()
    spells = {
        "m1": _spell("m1", built), "m2": _spell("m2", built), "x": _spell("x", built), "root": _spell("root", built),
    }
    generic = SitePlanStep(
        instance_key=("x", 3), spell=spells["x"], existence=Existence.many,
        dependency_resolution_order=(("items", (("m1", 1), ("m2", 2))),), collection_param_names=frozenset({"items"}),
        uses_positional_override=False, contract_positional_override=None, has_contract_payload=True,
        contract_payload={"c": "contract"}, use_spell_lock_hint=False,
    )
    steps = (
        _step(("m1", 1), spells["m1"]), _step(("m2", 2), spells["m2"]), generic,
        _step(("root", 0), spells["root"], ("x", (("x", 3),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "x", 0),)),
        "x": SpellLocalTopology("x", (_socket("x", "items", 0, collection=True),)),
    }
    plan, source = _emit_source(steps, topologies, ("root", 0))
    assert "instance_results = {key0: v0, key1: v1}" in source
    first = plan(SimpleNamespace(_conduit_creations=FakeStore()), {})
    x = first.args[0]
    assert [member.name for member in x.kwargs["items"]] == ["m1", "m2"] and x.kwargs["c"] == "contract"
    assert built == Counter({"m1": 1, "m2": 1, "x": 1, "root": 1})
'''

COMPONENT_TEST = '''"""
Component tests of lazy instance_results (S8, 2026-10-03) through real conjures.

Scope:
    A root whose site plan runs in dict mode - its dependency is an existing object, a generic site -
    is melded through a real Conduit and a real SpellSpace: warm and cold melds return the bound
    object, and the creation-cache generation that retires eagerly emitted plans is 17.
"""

from typing import Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.caching_system.caching_system import CachingSystem
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class Service:
    """The existing object a Worker depends on."""

    def __init__(self) -> None:
        self.calls = 0


class Worker:
    """Transient root over the existing Service (a dict-mode site plan)."""

    def __init__(self, service: Service) -> None:
        self.service = service


@pytest.fixture(autouse=True)
def reset_aether_singleton() -> None:
    """Fresh Aether per test, as the other component conduit tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _spellbook() -> Spellbook:
    """An automatic-posture Spellbook with the conjure cache off, as the certification harness builds its worlds."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def _bind_world() -> Tuple[Spellbook, Service, str]:
    """Bind one existing Service (unique) and Worker (many); return (spellbook, service, worker_id)."""
    spellbook = _spellbook()
    service = Service()
    spellbook.bind(spell=service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    return spellbook, service, worker_id


def test_conduit_meld_of_a_root_over_an_existing_object_returns_it_warm_and_cold() -> None:
    """The first (cold) and second (warm) melds both receive the bound Service object."""
    spellbook, service, worker_id = _bind_world()
    conduit = spellbook.conjure(name="s8-lazy-root", dynamic=False)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first is not second
        assert first.service is service and second.service is service
    finally:
        conduit.permanent_cleanup()


def test_spellspace_meld_of_the_same_root_returns_the_existing_object() -> None:
    """A space-scoped meld of the dict-mode root receives the same bound Service."""
    spellbook, service, worker_id = _bind_world()
    conduit = spellbook.conjure(name="s8-lazy-root", dynamic=False)
    try:
        with conduit.enter_spellspace() as space:
            worker = space.meld(spell_id=worker_id)
            again = space.meld(spell_id=worker_id)
        assert worker.service is service and again.service is service and worker is not again
    finally:
        conduit.permanent_cleanup()


def test_cache_generation_17_retires_eagerly_emitted_plans() -> None:
    """The creation-cache generation names the lazy dict so older executors are regenerated."""
    assert CachingSystem.CURRENT_VERSION >= 17
    assert CachingSystem.CACHE_VERSION_HISTORY[17] == "lazy_instance_results"
'''


def edit_tests(root: pathlib.Path) -> None:
    e = Editor(root, LOWERING_TEST)
    e.replace("import threading\n", "import re\nimport threading\n")
    e.text = e.text.rstrip("\n") + "\n" + UNIT_TESTS
    e.save()
    write_new(root, "tests/component/melder/aether/conduit/test_conduit_component_lazy_instance_results.py", COMPONENT_TEST)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    edit_lowering(root)
    edit_caching(root)
    if not args.skip_tests:
        edit_tests(root)
    print("S8 applied under", root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
