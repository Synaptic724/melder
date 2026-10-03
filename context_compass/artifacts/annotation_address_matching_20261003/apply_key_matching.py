"""
Apply the Phase 3 address-key matching change (anchored edits, line endings kept).

Usage: python apply_key_matching.py --root <repo root> [--skip-tests]
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


P3 = "src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py"
CACHING = "src/melder/utilities/caching_system/caching_system.py"
CACHE_TEST = "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"
P3_TEST = "tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py"
HARNESS = "tests/experimentation/codegen_strategy_certification.py"

MATCHER = '''    @staticmethod
    def _annotation_key(annotation: Any) -> str:
        """
        Return the address key a DI annotation names.

        Contract:
            A `ForwardRef` keys by its name; everything else keys through
            `SpellInputUtils.normalize_frame_key` - a class or Protocol by
            `__name__`, a string by itself, anything else by `str()` -
            lowercased, the normalization every spell address already uses.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: The lowercased key.
        """
        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__
        return SpellInputUtils.normalize_frame_key(annotation)

    @staticmethod
    def _spell_keys(spell_obj: Spell) -> Tuple[str, ...]:
        """
        Return the keys a spell answers to: its address frame key and its type key.

        Contract:
            The frame key is the spellframe when one was given, else the spell's
            own name - exactly what `make_spell_key_from_parts` stores at bind.
            The type key is the spell's name: a class's name, or an existing
            object's class name. Equal keys collapse to one entry, so a bare
            binding answers to one key and a framed binding to two.

        Args:
            spell_obj: The candidate spell (any object with `spell_name` and `spellframe`).

        Returns:
            Tuple[str, ...]: One or two lowercased keys.
        """
        type_key = SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        frame = spell_obj.spellframe
        if frame is None:
            return (type_key,)
        frame_key = SpellInputUtils.normalize_frame_key(frame)
        if frame_key == type_key:
            return (type_key,)
        return (frame_key, type_key)

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
    ) -> bool:
        """
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by address key, 2026-10-03):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell's keys (`_spell_keys`): its address frame key or its type
              key. A class-object annotation and its string spelling therefore
              resolve identically, an existing object is matched by its class,
              and a spellframe is a category or a shape label - never compared
              by object identity.
            - `binding_name`, when given, must equal the spell's binding name.
            - `require_class_spell=True` excludes METHOD/LAMBDA spell kinds.

        Args:
            annotation:
                Canonicalized annotation to match.
            binding_name:
                Optional binding-name filter.
            spell_obj:
                Candidate spell.
            require_class_spell:
                When True, only class-like spells are allowed.

        Returns:
            bool: `True` when the candidate should be considered for this
            dependency.
        """
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        if self._annotation_key(annotation) not in self._spell_keys(spell_obj):
            return False
        if binding_name is not None and spell_obj.binding_name != binding_name:
            return False
        return True

'''

INDEX_BUILD = '''    def _build_candidate_index(self, spellbook: Spellbook) -> Dict[str, Any]:
        """
        Build the pass-scoped phase-3 candidate index over the live pool.

        Purpose:
            Collapse the O(dependencies x spells) annotation scans into one
            bucket lookup per dependency. Bucket keys are the spells' address
            keys (`_spell_keys`), which derive from pass-invariant inputs
            (binds are transactional and the resolution pass runs post-bind):
            spellframe and spell_name.

        Contract:
            - Entries are `(pool_position, spell_index, spell_obj)` so a bucket
              can be re-sorted into `_spell_id_pool` iteration order, keeping
              collection-injection order identical to the scan implementation.
            - Each spell is appended once per distinct key (one or two).
            - Keys are strings, so bucket membership equals scan membership for
              every pool; no equality guard is needed (2026-10-03).

        Returns:
            Dict[str, Any]: `{"by_key": {key: [entries]}}`.
        """
        by_key: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            for key in self._spell_keys(spell_obj):
                by_key.setdefault(key, []).append(entry)
        return {"by_key": by_key}

'''

INDEX_LOOKUP = '''    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
    ) -> Dict[Any, "Spell"]:
        """
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the one bucket of the annotation's key (`_annotation_key`);
              membership equals scan membership because both sides use the
              same keys (2026-10-03).
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        """
        bucket = candidate_index["by_key"].get(self._annotation_key(annotation))

        # Replicate the scan's dict semantics exactly: when one SpellIndex
        # matches through multiple pool entries (version lineages), the scan
        # keeps the FIRST insertion position but the LAST matching spell
        # object (dict insert-then-overwrite).
        # collected: id(index) -> [first_pos, value_pos, index, spell_obj]
        collected: Dict[int, List[Any]] = {}
        for position, index, spell_obj in (bucket or ()):
            if require_class_spell and spell_obj.spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                continue
            record = collected.get(id(index))
            if record is None:
                collected[id(index)] = [position, position, index, spell_obj]
                continue
            if position < record[0]:
                record[0] = position
            if position > record[1]:
                record[1] = position
                record[3] = spell_obj

        ordered = sorted(collected.values(), key=lambda record: record[0])
        return {record[2]: record[3] for record in ordered}

'''


def edit_phase3(root: pathlib.Path) -> None:
    e = Editor(root, P3)
    e.replace(
        "        - Directly ports the canonical `SpellCrafter` phase-3 behavior.\n",
        "        - Directly ports the canonical `SpellCrafter` phase-3 behavior.\n"
        "        - Annotation matching is by address key (2026-10-03): a DI annotation\n"
        "          names `normalize_frame_key(annotation)`, and a spell is a candidate\n"
        "          when that key is its address frame key (spellframe, else its own\n"
        "          name) or its type key (`spell_name`; an existing object's class\n"
        "          name). No identity comparison: a spellframe is a category or a\n"
        "          shape label, never a type, and a `TYPE_CHECKING`-only annotation\n"
        "          (a string at runtime) resolves exactly as the class object does.\n",
    )
    e.replace_between("    def _matches_annotation(\n", "    @staticmethod\n    def _eq_safe_object(", MATCHER)
    e.replace(
        "        Purpose:\n            The pass-scoped candidate index replaces `is`/`==` scans with\n"
        "            bucket lookups. That substitution is only exact when no bound\n"
        "            spell object or spellframe carries a custom `__eq__` that could\n"
        "            match objects beyond identity (or plain string equality).\n",
        "        Purpose:\n            The structural snapshot's replayability rule: it marks a pool\n"
        "            non-replayable when a bound object or spellframe carries a custom\n"
        "            `__eq__`. Phase 3 itself no longer needs it - its index matches by\n"
        "            address key, which is exact for every pool (2026-10-03).\n",
    )
    e.replace_between("    def _build_candidate_index(", "    def _get_candidate_index(", INDEX_BUILD)
    e.replace(
        "            - Returns None (scan path) when no pass cache was supplied or\n"
        "              when the built index is eq-risky.\n",
        "            - Returns None (scan path) only when no pass cache was supplied;\n"
        "              the key index is exact for every pool (2026-10-03).\n",
    )
    e.replace(
        "        if index[\"eq_risky\"]:\n            return None\n        return index\n",
        "        return index\n",
    )
    e.replace_between("    def _indexed_annotation_candidates(", "    def _resolve_single_by_annotation(", INDEX_LOOKUP)
    e.replace(
        "        # Pass-scoped candidate index (None -> original scan semantics).\n"
        "        # Built lazily once per resolution pass; eq-risky pools disable it.\n",
        "        # Pass-scoped candidate index (None -> original scan semantics).\n"
        "        # Built lazily once per resolution pass; exact for every pool (key matching).\n",
    )
    e.save()


def edit_caching(root: pathlib.Path) -> None:
    e = Editor(root, CACHING)
    e.replace(
        '        17: "lazy_instance_results",\n    })\n',
        '        17: "lazy_instance_results",\n        18: "annotation_address_matching",\n    })\n',
    )
    e.replace(
        "    # (2026-10-03): they still run correctly, but allocate and fill the\n"
        "    # dict on every warm creation of a dict-mode root.\n",
        "    # (2026-10-03): they still run correctly, but allocate and fill the\n"
        "    # dict on every warm creation of a dict-mode root.\n"
        "    # Version 18 retires bundles captured before address-key matching\n"
        "    # (2026-10-03): their structural rows may hold an unresolved input\n"
        "    # for a parameter the key matcher now resolves.\n",
    )
    e.save()
    t = Editor(root, CACHE_TEST)
    t.replace('    17: "lazy_instance_results",\n', '    17: "lazy_instance_results",\n    18: "annotation_address_matching",\n')
    t.save()


def edit_harness(root: pathlib.Path) -> None:
    e = Editor(root, HARNESS)
    e.replace(
        '        book.bind(spell=cls(n), spellframe=cls, existence=Existence.unique, permissions="create")\n',
        '        book.bind(spell=cls(n), existence=Existence.unique, permissions="create")\n',
    )
    e.save()


CASES = '''@pytest.mark.parametrize(
    ("spell_type", "annotation_kind", "binding_name", "candidate_binding_name", "require_class_spell", "expected"),
    [
        (SpellType.SPELL, "type", None, None, True, True),
        (SpellType.SPELL, "type", "alpha", "beta", True, False),
        (SpellType.SPELL, "frame", None, None, True, True),
        (SpellType.SPELL, "type_name", None, None, True, True),
        (SpellType.SPELL, "frame_name", None, None, True, True),
        (SpellType.SPELL, "other", None, None, True, False),
        (SpellType.METHOD, "type", None, None, True, False),
        (SpellType.METHOD, "type", None, None, False, True),
    ],
)
def test_matches_annotation_cases(
        spell_type: SpellType,
        annotation_kind: str,
        binding_name: Optional[str],
        candidate_binding_name: Optional[str],
        require_class_spell: bool,
        expected: bool,
) -> None:
    """Phase 3 matches by address key: the type key, the frame key, their names; binding and kind filters hold."""
    phase = CompilerPhase3()

    class _FrameType:
        pass

    class CandidateSpell:
        pass

    class _Other:
        pass

    annotation: Any
    if annotation_kind == "type":
        annotation = CandidateSpell
    elif annotation_kind == "frame":
        annotation = _FrameType
    elif annotation_kind == "type_name":
        annotation = "CandidateSpell"
    elif annotation_kind == "frame_name":
        annotation = "_FrameType"
    else:
        annotation = _Other

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=CandidateSpell,
        spellframe=_FrameType,
        spell_name="CandidateSpell",
        binding_name=candidate_binding_name,
        spell_type=spell_type,
    )

    assert phase._matches_annotation(
        annotation,
        binding_name,
        candidate,
        require_class_spell=require_class_spell,
    ) is expected


'''

NEW_TESTS = '''def test_matches_annotation_matches_an_existing_object_by_its_class_and_by_its_name() -> None:
    """A bare existing object answers to its class object and to its class name, and to nothing else."""
    phase = CompilerPhase3()

    class Service:
        pass

    class Other:
        pass

    candidate = _make_spell_stub(
        "service",
        spell_obj=Service(),
        spellframe=None,
        spell_name="Service",
    )

    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("Service", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(Other, None, candidate, require_class_spell=True) is False
    assert phase._spell_keys(candidate) == ("service",)


def test_matches_annotation_treats_a_concrete_class_frame_as_a_name() -> None:
    """A concrete class used as a spellframe is only a name: the spell answers to it and to its own type."""
    phase = CompilerPhase3()

    class Service:
        pass

    class Impl:
        pass

    candidate = _make_spell_stub(
        "impl",
        spell_obj=Impl,
        spellframe=Service,
        spell_name="Impl",
    )

    assert phase._spell_keys(candidate) == ("service", "impl")
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("service", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(Impl, None, candidate, require_class_spell=True) is True


def test_indexed_candidates_equal_the_scan_for_an_existing_object() -> None:
    """The by-key index resolves a bare existing object exactly as the scan does, with no equality gate."""
    phase = CompilerPhase3()

    class Service:
        pass

    class Other:
        pass

    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    service = _make_spell_stub("svc", spell_obj=Service(), spellframe=None, spell_name="Service")
    other = _make_spell_stub("other", spell_obj=Other, spellframe=None, spell_name="Other")
    spellbook = SimpleNamespace(_spell_id_pool={"svc": service, "other": other})
    dep = _make_dependency(
        spell_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=Service,
    )

    scanned = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
    index = phase._build_candidate_index(spellbook)
    indexed = phase._resolve_single_by_annotation(root_spell, spellbook, dep, index)

    assert list(scanned.values()) == [service]
    assert indexed == scanned
    assert set(index) == {"by_key"}
    assert sorted(index["by_key"]) == ["other", "service"]


'''

COMPONENT_TEST = '''"""
Component tests of address-key annotation matching (2026-10-03) through real conjures.

Scope:
    A consumer annotated with a class is served by an existing object of that class bound bare
    (no spellframe), whether the annotation is the class object or its `TYPE_CHECKING`-style
    string spelling; the cache generation that retires bundles captured under the identity
    matcher is 18.
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
    """The existing object the consumers depend on."""

    def __init__(self) -> None:
        self.calls = 0


class TypedWorker:
    """Consumer annotated with the class object."""

    def __init__(self, service: Service) -> None:
        self.service = service


class NamedWorker:
    """Consumer annotated with the class name, as a TYPE_CHECKING-only import leaves it at runtime."""

    def __init__(self, service: "Service") -> None:
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
    """An automatic-posture Spellbook with the conjure cache off."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def _bind_world() -> Tuple[Spellbook, Service, str, str]:
    """Bind one bare existing Service and the two consumers; return (spellbook, service, typed_id, named_id)."""
    spellbook = _spellbook()
    service = Service()
    spellbook.bind(spell=service, existence=Existence.unique, permissions="create")
    typed_id = spellbook.bind(spell=TypedWorker, existence=Existence.many, permissions="create")
    named_id = spellbook.bind(spell=NamedWorker, existence=Existence.many, permissions="create")
    return spellbook, service, typed_id, named_id


def test_a_bare_existing_object_serves_a_consumer_annotated_with_its_class() -> None:
    """No spellframe is needed: the instance's class is its type key."""
    spellbook, service, typed_id, _named_id = _bind_world()
    conduit = spellbook.conjure(name="key-matching-root", dynamic=False)
    try:
        worker = conduit.meld(spell_id=typed_id)
        assert worker.service is service
        assert conduit.meld(spell_id=typed_id).service is service
    finally:
        conduit.permanent_cleanup()


def test_the_string_and_the_object_annotation_resolve_the_same_binding() -> None:
    """A TYPE_CHECKING-style string annotation and the class object are the same key."""
    spellbook, service, typed_id, named_id = _bind_world()
    conduit = spellbook.conjure(name="key-matching-root", dynamic=False)
    try:
        typed = conduit.meld(spell_id=typed_id)
        named = conduit.meld(spell_id=named_id)
        assert typed.service is service and named.service is service
    finally:
        conduit.permanent_cleanup()


def test_cache_generation_18_retires_bundles_captured_under_identity_matching() -> None:
    """The creation-cache generation names the key matcher so older bundles are regenerated."""
    assert CachingSystem.CURRENT_VERSION >= 18
    assert CachingSystem.CACHE_VERSION_HISTORY[18] == "annotation_address_matching"
'''


def edit_tests(root: pathlib.Path) -> None:
    e = Editor(root, P3_TEST)
    e.replace_between(
        "@pytest.mark.parametrize(\n    (\"spell_type\", \"annotation_kind\", \"binding_name\"",
        "def test_matches_annotation_rejects_binding_mismatch_on_frame(",
        CASES,
    )
    e.replace(
        "@pytest.mark.parametrize(\n    (\"drop_spell_id\", \"expected_message\"),\n",
        NEW_TESTS + "@pytest.mark.parametrize(\n    (\"drop_spell_id\", \"expected_message\"),\n",
    )
    e.save()
    write_new(root, "tests/component/melder/aether/conduit/test_conduit_component_annotation_address_matching.py", COMPONENT_TEST)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    edit_phase3(root)
    edit_caching(root)
    edit_harness(root)
    if not args.skip_tests:
        edit_tests(root)
    print("key matching applied under", root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
