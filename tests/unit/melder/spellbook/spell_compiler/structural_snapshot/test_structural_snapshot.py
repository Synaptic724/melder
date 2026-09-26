"""
Unit contracts for the structural snapshot capture seam.

Every value the seam writes is address-free: type references are (module, qualname) rows, the world
stamp is a digest over sorted ids and the posture name, and the payload rows hold spell ids and enum
names only. The stubs here mirror the shapes the seam borrows (requirements, profile, registry).
"""

import hashlib
import logging
import marshal
import typing
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (
    StructuralSnapshot,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.utilities.caching_system.caching_system import CachingSystem


class _Alpha:
    """Plain class used as an annotation target."""


class _Beta:
    """Second plain class used as an annotation target."""


class _CustomEq:
    """Instance type overriding equality (eq-risky under phase 3)."""

    def __eq__(self, other: object) -> bool:
        return True

    __hash__ = object.__hash__


class _Parameter:
    """Stub of one bind-time parameter row."""

    __slots__ = ("di_shape", "annotation", "collection_element_annotation", "spellmap_default")

    def __init__(
            self,
            di_shape: ParameterDIShape,
            annotation: Any = None,
            collection_element_annotation: Any = None,
            spellmap_default: Any = None,
    ) -> None:
        self.di_shape = di_shape
        self.annotation = annotation
        self.collection_element_annotation = collection_element_annotation
        self.spellmap_default = spellmap_default


class _SpellMap:
    """Stub of a SpellMap default."""

    __slots__ = ("spell", "spellframe", "binding_name")

    def __init__(self, spell: Any = None, spellframe: Any = None, binding_name: Optional[str] = None) -> None:
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = binding_name


class _Requirements:
    """Stub of the phase-1 requirements a profile holds."""

    __slots__ = ("parameters", "cleaned", "spell_id")

    def __init__(self, parameters: List[_Parameter], spell_id: str, cleaned: bool = False) -> None:
        self.parameters = parameters
        self.cleaned = cleaned
        self.spell_id = spell_id


class _ResolutionProfile:
    __slots__ = ("requirements",)

    def __init__(self, requirements: Any) -> None:
        self.requirements = requirements


class _Profile:
    __slots__ = ("resolution_profile",)

    def __init__(self, resolution_profile: Any) -> None:
        self.resolution_profile = resolution_profile


class _Index:
    __slots__ = ("id",)

    def __init__(self, index_id: str) -> None:
        self.id = index_id


class _Spell:
    """Stub spell carrying the durable fields the seam reads."""

    __slots__ = ("spell_id", "profile", "spell_index", "dependencies", "spell", "spellframe", "_caching_enabled")

    def __init__(
            self,
            spell_id: str,
            requirements: Any = None,
            *,
            index_id: Optional[str] = None,
            dependencies: Optional[List[str]] = None,
            bound: Any = _Alpha,
            spellframe: Any = None,
            caching_enabled: bool = True,
    ) -> None:
        self.spell_id = spell_id
        self.profile = None if requirements is None else _Profile(_ResolutionProfile(requirements))
        self.spell_index = None if index_id is None else _Index(index_id)
        self.dependencies = [] if dependencies is None else dependencies
        self.spell = bound
        self.spellframe = spellframe
        self._caching_enabled = caching_enabled


class _State:
    __slots__ = ("validity", "flags")

    def __init__(self, validity: SpellValidity, flags: Optional[set] = None) -> None:
        self.validity = validity
        self.flags = set() if flags is None else flags


class _Registry:
    """Stub of the frame registry lookups the seam uses."""

    def __init__(self) -> None:
        self.states: Dict[str, _State] = {}
        self.topologies: Dict[str, SpellLocalTopology] = {}

    def get_by_index_id(self, index_id: str) -> Optional[_State]:
        return self.states.get(index_id)

    def get_local_topology(self, spell_index: _Index) -> Optional[SpellLocalTopology]:
        return self.topologies.get(spell_index.id)


class _Posture(Enum):
    basic = auto()
    strict = auto()


class _FrameConfiguration:
    __slots__ = ("system_state",)

    def __init__(self, system_state: _Posture) -> None:
        self.system_state = system_state


class _Logger:
    """Records error calls."""

    def __init__(self) -> None:
        self.errors: List[Tuple[str, str]] = []

    def error(self, message: str, context: str, exc_info: bool = False) -> None:
        self.errors.append((message, context))


class _Spellbook:
    """Stub Book with the world fields the seam reads."""

    def __init__(self, pool: Dict[str, _Spell], posture: Optional[_Posture] = _Posture.basic) -> None:
        self._spell_id_pool = pool
        self._aetheric_frame_configuration = None if posture is None else _FrameConfiguration(posture)
        self._contracted_spells: Dict[str, Dict[str, _Spell]] = {}
        self._spells: Dict[str, _Spell] = {}
        self._spell_system_states = _Registry()
        self._logger = _Logger()


def _sid(label: str) -> str:
    """Deterministic 64-hex spell id."""
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# type_refs / annotation_refs
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(None, [("none", "None")], id="none"),
        pytest.param("Engine", [("str", "Engine")], id="string"),
        pytest.param(typing.ForwardRef("Car"), [("forward_ref", "Car")], id="forward-ref"),
        pytest.param(_Alpha, [(__name__, "_Alpha")], id="class"),
        pytest.param(Optional[_Alpha], [(__name__, "_Alpha")], id="optional"),
        pytest.param(typing.Union[_Alpha, _Beta], [(__name__, "_Alpha"), (__name__, "_Beta")], id="union"),
        pytest.param(_Alpha | None, [(__name__, "_Alpha")], id="pep604-optional"),
        pytest.param(typing.List[_Alpha], [("typing", repr(typing.List[_Alpha]))], id="typing-generic"),
        pytest.param(list[_Alpha], [("typing", repr(list[_Alpha]))], id="builtin-generic"),
        pytest.param(_Beta(), [("object", f"{__name__}._Beta")], id="instance"),
    ],
)
def test_type_refs_render_address_free_rows(value: Any, expected: List[Tuple[str, str]]) -> None:
    """Each annotation-like value renders to (kind|module, name) rows without object addresses."""
    rows = StructuralSnapshot.type_refs(value)
    assert rows == expected
    assert all("0x" not in text for _kind, text in rows)


def test_annotation_refs_collect_sorted_unique_rows_per_shape() -> None:
    """SINGLE/COLLECTION/SPELLMAP contribute; PLAIN and SPELL_CONTRACT do not; rows are sorted and unique."""
    requirements = _Requirements(
        [
            _Parameter(ParameterDIShape.SINGLE_BY_ANNOTATION, annotation=_Beta),
            _Parameter(ParameterDIShape.COLLECTION_BY_ANNOTATION, annotation=list[_Alpha],
                       collection_element_annotation=_Alpha),
            _Parameter(ParameterDIShape.COLLECTION_BY_ANNOTATION, annotation=_Beta),
            _Parameter(ParameterDIShape.SPELLMAP_DEFAULT,
                       spellmap_default=_SpellMap(spell=_Alpha, spellframe=_Beta, binding_name="svc")),
            _Parameter(ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=_SpellMap()),
            _Parameter(ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=None),
            _Parameter(ParameterDIShape.PLAIN, annotation=int),
            _Parameter(ParameterDIShape.SPELL_CONTRACT, annotation=_Alpha),
        ],
        _sid("consumer"),
    )
    rows = StructuralSnapshot.annotation_refs(requirements)
    assert rows == sorted({(__name__, "_Alpha"), (__name__, "_Beta"), ("binding_name", "svc"), ("binding_name", "")})
    assert rows == sorted(rows)


# --------------------------------------------------------------------------- #
# bind_time_requirements / structural_key
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "make_spell",
    [
        pytest.param(lambda: _Spell(_sid("s")), id="no-profile"),
        pytest.param(lambda: _Spell(_sid("s"), requirements=_Requirements([], _sid("s"), cleaned=True)), id="cleaned"),
        pytest.param(lambda: _Spell(_sid("s"), requirements=_Requirements([], _sid("other"))), id="foreign-id"),
    ],
)
def test_bind_time_requirements_borrow_rule_rejects_unusable_profiles(make_spell: Any) -> None:
    """Missing, cleaned or foreign requirements yield None, so the spell has no key."""
    spell = make_spell()
    assert StructuralSnapshot.bind_time_requirements(spell) is None
    assert StructuralSnapshot.structural_key(spell) is None


def test_bind_time_requirements_tolerates_missing_profile_links() -> None:
    """A profile without a resolution profile, or one without requirements, yields None."""
    spell = _Spell(_sid("s"))
    spell.profile = _Profile(None)
    assert StructuralSnapshot.bind_time_requirements(spell) is None
    spell.profile = _Profile(_ResolutionProfile(None))
    assert StructuralSnapshot.bind_time_requirements(spell) is None


def test_structural_key_holds_format_id_and_sorted_refs() -> None:
    """The key is value-only: format, the spell id and the sorted annotation refs."""
    requirements = _Requirements([_Parameter(ParameterDIShape.SINGLE_BY_ANNOTATION, annotation=_Alpha)], _sid("s"))
    spell = _Spell(_sid("s"), requirements=requirements)
    assert StructuralSnapshot.bind_time_requirements(spell) is requirements
    assert StructuralSnapshot.structural_key(spell) == {
        "format": StructuralSnapshot.PAYLOAD_FORMAT,
        "spell_id": _sid("s"),
        "annotation_refs": [(__name__, "_Alpha")],
    }


# --------------------------------------------------------------------------- #
# world_stamp / pool_replayable
# --------------------------------------------------------------------------- #

def _expected_stamp(pool_ids: List[str], posture: str, borrowed: List[str]) -> str:
    text = "\n".join((
        "pool:" + ",".join(sorted(pool_ids)),
        "posture:" + posture,
        "borrowed:" + ",".join(sorted(borrowed)),
    ))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_world_stamp_digests_sorted_pool_posture_and_borrowed_ids() -> None:
    """The stamp is order-independent over the pool and borrowed ids and carries the posture name."""
    a, b, c = _sid("a"), _sid("b"), _sid("c")
    forward = _Spellbook({a: _Spell(a), b: _Spell(b)}, _Posture.strict)
    reverse = _Spellbook({b: _Spell(b), a: _Spell(a)}, _Posture.strict)
    forward._contracted_spells = {"conduit-1": {"idx": _Spell(c)}}
    reverse._contracted_spells = {"conduit-2": {"idx": _Spell(c)}}

    assert StructuralSnapshot.world_stamp(forward) == _expected_stamp([a, b], "strict", [c])
    assert StructuralSnapshot.world_stamp(forward) == StructuralSnapshot.world_stamp(reverse)


def test_world_stamp_changes_with_pool_posture_or_borrowed_set() -> None:
    """Any of the three inputs moves the stamp; no frame configuration renders an empty posture."""
    a, b = _sid("a"), _sid("b")
    base = _Spellbook({a: _Spell(a)}, _Posture.basic)
    stamp = StructuralSnapshot.world_stamp(base)

    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a), b: _Spell(b)}, _Posture.basic)) != stamp
    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a)}, _Posture.strict)) != stamp
    borrowed = _Spellbook({a: _Spell(a)}, _Posture.basic)
    borrowed._contracted_spells = {"conduit": {"idx": _Spell(b)}}
    assert StructuralSnapshot.world_stamp(borrowed) != stamp
    assert StructuralSnapshot.world_stamp(_Spellbook({a: _Spell(a)}, None)) == _expected_stamp([a], "", [])


def test_pool_replayable_follows_the_phase3_eq_safety_rule() -> None:
    """Plain classes, strings and default-eq instances replay; a custom __eq__ on a bound object or frame does not."""
    a, b = _sid("a"), _sid("b")
    safe = _Spellbook({a: _Spell(a, bound=_Alpha, spellframe="Alpha"), b: _Spell(b, bound=_Beta(), spellframe=_Beta)})
    assert StructuralSnapshot.pool_replayable(safe) is True

    risky_object = _Spellbook({a: _Spell(a, bound=_CustomEq(), spellframe=None)})
    assert StructuralSnapshot.pool_replayable(risky_object) is False

    risky_frame = _Spellbook({a: _Spell(a, bound=_Alpha, spellframe=_CustomEq())})
    assert StructuralSnapshot.pool_replayable(risky_frame) is False


# --------------------------------------------------------------------------- #
# build_payload
# --------------------------------------------------------------------------- #

def _consumer_world() -> Tuple[_Spellbook, _Spell, str, str]:
    """Book with a provider and a consumer whose registry state and topology are populated."""
    provider_id, consumer_id = _sid("provider"), _sid("consumer")
    requirements = _Requirements([_Parameter(ParameterDIShape.SINGLE_BY_ANNOTATION, annotation=_Alpha)], consumer_id)
    consumer = _Spell(consumer_id, requirements=requirements, index_id="idx-consumer", dependencies=[provider_id])
    provider = _Spell(provider_id, requirements=_Requirements([], provider_id), index_id="idx-provider")
    book = _Spellbook({provider_id: provider, consumer_id: consumer})
    book._spells = {"idx-provider": provider, "idx-consumer": consumer}
    registry = book._spell_system_states
    registry.states["idx-consumer"] = _State(SpellValidity.valid, {SpellState.contract_unvalidated})
    registry.states["idx-provider"] = _State(SpellValidity.valid)
    registry.topologies["idx-consumer"] = SpellLocalTopology(consumer_id, [
        SpellSocketDescriptor(
            spell_id=consumer_id, param_name="alpha", position=0, socket_kind=SocketKind.NORMAL,
            is_collection=False, is_optional=False, target_spell_ids=(provider_id,),
            dependency_key=("annotation", "_Alpha"), contract_key=None, referenced_spell_ids=(provider_id,),
            parameter_kind="POSITIONAL_OR_KEYWORD",
        ),
    ])
    registry.topologies["idx-provider"] = SpellLocalTopology(provider_id, [])
    return book, consumer, provider_id, consumer_id


def test_build_payload_renders_phase3_and_phase4_rows_from_durable_state() -> None:
    """The payload carries the key, stamp, verdict, dependency ids, socket rows and the lineage validity."""
    book, consumer, provider_id, consumer_id = _consumer_world()
    payload = StructuralSnapshot.build_payload(consumer, book._spell_system_states, world_stamp="stamp", replayable=True)
    assert payload == {
        "key": {"format": 1, "spell_id": consumer_id, "annotation_refs": [(__name__, "_Alpha")]},
        "world_stamp": "stamp",
        "replayable": True,
        "phase3": {
            "dependency_ids": [provider_id],
            "sockets": [(
                "alpha", 0, "NORMAL", False, False, (provider_id,), ("annotation", "_Alpha"), None,
                (provider_id,), "POSITIONAL_OR_KEYWORD",
            )],
        },
        "phase4": {"validity": "valid", "contract_unvalidated": True},
    }
    assert marshal.loads(marshal.dumps(payload)) == payload


def test_build_payload_returns_none_when_any_durable_input_is_missing() -> None:
    """No key, no index, no lineage state or no topology each make the spell a structural miss."""
    book, consumer, _provider_id, consumer_id = _consumer_world()
    registry = book._spell_system_states
    build = lambda: StructuralSnapshot.build_payload(consumer, registry, world_stamp="s", replayable=True)

    assert build() is not None
    topology = registry.topologies.pop("idx-consumer")
    assert build() is None
    registry.topologies["idx-consumer"] = topology
    state = registry.states.pop("idx-consumer")
    assert build() is None
    registry.states["idx-consumer"] = state
    index = consumer.spell_index
    consumer.spell_index = None
    assert build() is None
    consumer.spell_index = index
    consumer.profile = None
    assert build() is None


# --------------------------------------------------------------------------- #
# capture_at_conjure_end
# --------------------------------------------------------------------------- #

def _make_caching_system(tmp_path: Path) -> CachingSystem:
    return CachingSystem(
        frame_name="frame",
        conduit_name="root",
        cache_root_path=tmp_path,
        logger=logging.getLogger("test_structural_snapshot"),
    )


def test_capture_stores_one_payload_per_owned_spell_and_reports_changes(tmp_path: Path) -> None:
    """First capture adds both payloads (True); an identical world re-captures nothing (False)."""
    book, _consumer, provider_id, consumer_id = _consumer_world()
    caching_system = _make_caching_system(tmp_path)
    try:
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is True
        assert set(caching_system.cached_structural_spell_ids) == {provider_id, consumer_id}
        stamp = StructuralSnapshot.world_stamp(book)
        for spell_id in (provider_id, consumer_id):
            payload = caching_system.get_structural_payload(spell_id)
            assert payload["world_stamp"] == stamp
            assert payload["replayable"] is True
            assert payload["key"]["spell_id"] == spell_id
        assert caching_system.get_structural_payload(provider_id)["phase3"] == {"dependency_ids": [], "sockets": []}
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is False
        assert book._logger.errors == []
    finally:
        caching_system.cleanup()


def test_capture_drops_stale_disabled_and_unbuildable_ids(tmp_path: Path) -> None:
    """Ids no longer owned, spells with caching disabled and spells without a payload lose their entries."""
    book, consumer, provider_id, consumer_id = _consumer_world()
    caching_system = _make_caching_system(tmp_path)
    try:
        stale_id = _sid("stale")
        caching_system.upsert_structural_payload(stale_id, {"key": {}, "phase3": {}, "phase4": {}})
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is True
        assert stale_id not in caching_system.cached_structural_spell_ids

        consumer._caching_enabled = False
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is True
        assert set(caching_system.cached_structural_spell_ids) == {provider_id}
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is False

        consumer._caching_enabled = True
        book._spell_system_states.topologies.pop("idx-consumer")
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is False
        assert set(caching_system.cached_structural_spell_ids) == {provider_id}
        assert book._logger.errors == []
    finally:
        caching_system.cleanup()


def test_capture_is_best_effort_per_spell(tmp_path: Path) -> None:
    """A build failure for one spell is logged and skipped; the other spells are still captured."""
    book, consumer, provider_id, consumer_id = _consumer_world()
    consumer.dependencies = None
    caching_system = _make_caching_system(tmp_path)
    try:
        assert StructuralSnapshot.capture_at_conjure_end(book, caching_system) is True
        assert set(caching_system.cached_structural_spell_ids) == {provider_id}
        assert len(book._logger.errors) == 1
        message, context = book._logger.errors[0]
        assert consumer_id in message
        assert context == "capture_at_conjure_end"
    finally:
        caching_system.cleanup()


def test_capture_marks_every_payload_non_replayable_for_an_eq_risky_pool(tmp_path: Path) -> None:
    """Replayability is a pool property: one custom __eq__ in the pool flags every payload of the book."""
    book, _consumer, provider_id, consumer_id = _consumer_world()
    book._spell_id_pool[provider_id].spellframe = _CustomEq()
    caching_system = _make_caching_system(tmp_path)
    try:
        StructuralSnapshot.capture_at_conjure_end(book, caching_system)
        for spell_id in (provider_id, consumer_id):
            assert caching_system.get_structural_payload(spell_id)["replayable"] is False
    finally:
        caching_system.cleanup()
