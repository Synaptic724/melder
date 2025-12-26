"""Additional contract tests for MeldEngine helper methods."""
from threading import RLock
from types import SimpleNamespace
from typing import Any, Iterable

import pytest

from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: Iterable[str],
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Build a SocketRef for override targeting.

    Args:
        node_id: Spell id for the node.
        param_name: Parameter name targeted by the override.
        param_path: Full parameter path tuple.
        socket_kind: SocketKind classification for the socket.

    Returns:
        SocketRef: The constructed socket reference.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=tuple(param_path),
        socket_kind=socket_kind,
    )


def _make_spell(
    *,
    spell_id: str,
    existence: Existence = Existence.unique,
    spell: Any | None = None,
    is_class_spell: bool = True,
    is_method_spell: bool = False,
    is_lambda_spell: bool = False,
    is_existing_creation: bool = False,
    user_created_object: Any = None,
    owner_creations: Any | None = None,
) -> SimpleNamespace:
    """
    Build a minimal spell stub with MeldEngine-required attributes.

    Args:
        spell_id: Spell version id.
        existence: Existence policy for reuse/registration.
        spell: Callable or value backing the spell.
        is_class_spell: True when spell should be treated as class-based.
        is_method_spell: True when spell should be treated as method-based.
        is_lambda_spell: True when spell should be treated as lambda-based.
        is_existing_creation: True for existing-creation spells.
        user_created_object: Optional existing-creation instance.
        owner_creations: Optional owner creations container.

    Returns:
        SimpleNamespace: Spell stub with required attributes.
    """
    if spell is None:
        def _default_callable(**_kwargs: Any) -> str:
            """
            Return a deterministic value for the default spell callable.
            """
            return f"value:{spell_id}"
        spell = _default_callable
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SpellIndex(spell_id),
        spell=spell,
        existence=existence,
        is_class_spell=is_class_spell,
        is_method_spell=is_method_spell,
        is_lambda_spell=is_lambda_spell,
        is_existing_creation=is_existing_creation,
        user_created_object=user_created_object,
        _owner_creations=owner_creations,
        _lock=RLock(),
    )


def _make_context(
    *,
    caller_creations: Any | None = None,
    owner_creations: Any | None = None,
    caller_creations_lock_held: bool = False,
) -> SimpleNamespace:
    """
    Build a minimal MeldEngine context stub.

    Args:
        caller_creations: Optional caller creations container.
        owner_creations: Optional owner creations container.
        caller_creations_lock_held: Whether caller creations lock is held.

    Returns:
        SimpleNamespace: Context stub with the required attributes.
    """
    if caller_creations is None:
        caller_creations = object()
    if owner_creations is None:
        owner_creations = caller_creations
    return SimpleNamespace(
        creations=owner_creations,
        owner_creations=owner_creations,
        caller_creations=caller_creations,
        caller_creations_lock_held=caller_creations_lock_held,
        cancel_event=None,
    )


def _make_engine(
    *,
    root_spell: SimpleNamespace | None = None,
    frame_overrides: dict[str, Any] | None = None,
    override_map: dict[SocketRef, Any] | None = None,
    spell_lookup: dict[str, Any] | None = None,
    caller_creations: Any | None = None,
    owner_creations: Any | None = None,
    caller_creations_lock_held: bool = False,
) -> MeldEngine:
    """
    Build a MeldEngine with minimal stubs for helper testing.

    Args:
        root_spell: Optional root spell stub.
        frame_overrides: Optional ResolutionFrame overrides mapping.
        override_map: Optional socket override map.
        spell_lookup: Optional spell lookup table.
        caller_creations: Optional caller creations container.
        owner_creations: Optional owner creations container.
        caller_creations_lock_held: Caller lock held flag.

    Returns:
        MeldEngine: Engine instance ready for helper tests.
    """
    if root_spell is None:
        root_spell = _make_spell(spell_id="root")
    frame = ResolutionFrame(overrides=frame_overrides or {})
    context = _make_context(
        caller_creations=caller_creations,
        owner_creations=owner_creations,
        caller_creations_lock_held=caller_creations_lock_held,
    )
    return MeldEngine(
        context=context,
        root_spell=root_spell,
        dag=None,
        resolution_frame=None,
        requirements=None,
        frame=frame,
        blueprint=None,
        override_map=override_map or {},
        spell_lookup=spell_lookup or {},
        system_states=None,
    )


def test_detect_any_overrides_true_with_override_map() -> None:
    """
    Verify override detection returns True for socket overrides.

    Contract:
        - Non-empty override_map yields True.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("x",)): 1
    }
    engine = _make_engine(override_map=override_map)
    assert engine._detect_any_overrides() is True


def test_detect_any_overrides_false_with_empty_inputs() -> None:
    """
    Verify override detection returns False with no overrides.

    Contract:
        - Empty override maps and frame overrides yield False.
    """
    engine = _make_engine(override_map={}, frame_overrides={})
    assert engine._detect_any_overrides() is False


def test_collect_override_targets_groups_by_spell_id() -> None:
    """
    Verify override targets are grouped by spell id.

    Contract:
        - SocketRef entries are grouped by node_id.
    """
    override_map = {
        _make_socket_ref(node_id="node-a", param_name="x", param_path=("x",)): "a",
        _make_socket_ref(node_id="node-b", param_name="y", param_path=("y",)): "b",
    }
    engine = _make_engine()
    grouped = engine._collect_override_targets(override_map)
    assert set(grouped.keys()) == {"node-a", "node-b"}
    assert len(grouped["node-a"]) == 1
    assert len(grouped["node-b"]) == 1


def test_has_overrides_for_spell_uses_socket_targets() -> None:
    """
    Verify override detection uses grouped socket targets.

    Contract:
        - target lists indicate overrides for non-root spells.
    """
    engine = _make_engine()
    socket_ref = _make_socket_ref(node_id="node", param_name="x", param_path=("x",))
    engine._override_targets_by_spell_id = {"node": [socket_ref]}
    assert engine._has_overrides_for_spell("node") is True


def test_has_overrides_for_spell_root_uses_frame_overrides() -> None:
    """
    Verify root override detection checks frame overrides.

    Contract:
        - root overrides are detected via ResolutionFrame overrides.
    """
    root_spell = _make_spell(spell_id="root")
    engine = _make_engine(root_spell=root_spell, frame_overrides={"x": 1})
    engine._override_targets_by_spell_id = {}
    assert engine._has_overrides_for_spell("root") is True
    assert engine._has_overrides_for_spell("other") is False


def test_validate_shared_override_targets_raises_on_duplicate_param() -> None:
    """
    Verify shared override validation rejects duplicate params.

    Contract:
        - Multiple overrides for the same param raise MeldExecutionError.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("left", "x")): 1,
        _make_socket_ref(node_id="node", param_name="x", param_path=("right", "x")): 2,
    }
    spell = _make_spell(spell_id="node")
    engine = _make_engine(spell_lookup={"node": spell})
    engine._override_targets_by_spell_id = engine._collect_override_targets(override_map)
    with pytest.raises(MeldExecutionError, match="Multiple overrides"):
        engine._validate_shared_override_targets({"node"})


def test_validate_shared_override_targets_allows_distinct_params() -> None:
    """
    Verify shared override validation allows distinct params.

    Contract:
        - Different parameters do not raise validation errors.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("x",)): 1,
        _make_socket_ref(node_id="node", param_name="y", param_path=("y",)): 2,
    }
    spell = _make_spell(spell_id="node")
    engine = _make_engine(spell_lookup={"node": spell})
    engine._override_targets_by_spell_id = engine._collect_override_targets(override_map)
    engine._validate_shared_override_targets({"node"})


@pytest.mark.parametrize(
    "existence, expected",
    (
        (Existence.many, False),
        (Existence.unique, True),
        (Existence.unique_per_conduit, True),
    ),
)
def test_is_shared_existence_marks_many_as_false(
    existence: Existence,
    expected: bool,
) -> None:
    """
    Verify shared existence detection treats Existence.many as non-shared.

    Contract:
        - Existence.many returns False; others return True.
    """
    assert MeldEngine._is_shared_existence(existence) is expected


@pytest.mark.parametrize(
    "existence, expected_path",
    (
        (Existence.unique, None),
        (Existence.many, ()),
    ),
)
def test_instance_key_for_root_respects_existence(
    existence: Existence,
    expected_path: tuple[str, ...] | None,
) -> None:
    """
    Verify root instance keys follow existence policy.

    Contract:
        - Shared existences use a None path.
        - Existence.many uses the empty path tuple.
    """
    root_spell = _make_spell(spell_id="root", existence=existence)
    engine = _make_engine(root_spell=root_spell)
    assert engine._instance_key_for_root() == ("root", expected_path)


def test_instance_key_for_occurrence_shared_collapses_path() -> None:
    """
    Verify shared occurrences collapse to None paths.

    Contract:
        - Shared existences return (spell_id, None).
    """
    spell = _make_spell(spell_id="node", existence=Existence.unique)
    engine = _make_engine(spell_lookup={"node": spell})
    assert engine._instance_key_for_occurrence(("node", ("left",))) == ("node", None)


def test_instance_key_for_occurrence_many_preserves_path() -> None:
    """
    Verify Existence.many preserves occurrence paths.

    Contract:
        - Many existences return the original path.
    """
    spell = _make_spell(spell_id="node", existence=Existence.many)
    engine = _make_engine(spell_lookup={"node": spell})
    assert engine._instance_key_for_occurrence(("node", ("left",))) == ("node", ("left",))


def test_occurrence_for_instance_key_shared_missing_canonical_raises() -> None:
    """
    Verify shared instance keys require canonical occurrences.

    Contract:
        - Missing canonical entries raise MeldExecutionError.
    """
    engine = _make_engine()
    with pytest.raises(MeldExecutionError, match="Canonical occurrence missing"):
        engine._occurrence_for_instance_key(
            instance_key=("node", None),
            canonical_occurrences_by_spell_id={},
        )


def test_occurrence_for_instance_key_shared_returns_canonical() -> None:
    """
    Verify shared instance keys use canonical occurrences.

    Contract:
        - Canonical occurrence paths are returned for shared instances.
    """
    engine = _make_engine()
    canonical = ("node", ("left",))
    assert engine._occurrence_for_instance_key(
        instance_key=("node", None),
        canonical_occurrences_by_spell_id={"node": canonical},
    ) == canonical


def test_build_instance_override_map_shared_applies_all_params() -> None:
    """
    Verify shared override selection ignores param paths.

    Contract:
        - Shared instances accept all overrides for their spell id.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("left", "x")): "left",
        _make_socket_ref(node_id="node", param_name="y", param_path=("right", "y")): "right",
    }
    spell = _make_spell(spell_id="node")
    engine = _make_engine(spell_lookup={"node": spell}, override_map=override_map)
    overrides = engine._build_instance_override_map(
        spell_id="node",
        occurrence_path=("left",),
        shared=True,
    )
    assert overrides == {"x": "left", "y": "right"}


def test_build_instance_override_map_path_matches_prefix() -> None:
    """
    Verify per-path override selection matches occurrence prefixes.

    Contract:
        - Overrides apply when param_path prefix matches the occurrence path.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("left", "x")): "match",
        _make_socket_ref(node_id="node", param_name="y", param_path=("right", "y")): "skip",
    }
    spell = _make_spell(spell_id="node")
    engine = _make_engine(spell_lookup={"node": spell}, override_map=override_map)
    overrides = engine._build_instance_override_map(
        spell_id="node",
        occurrence_path=("left",),
        shared=False,
    )
    assert overrides == {"x": "match"}


def test_build_kwargs_for_instance_override_precedence() -> None:
    """
    Verify overrides take precedence over dependency values.

    Contract:
        - Override values replace injected dependency values.
    """
    root_spell = _make_spell(spell_id="root", existence=Existence.many)
    parent_spell = _make_spell(spell_id="parent", existence=Existence.many)
    override_map = {
        _make_socket_ref(node_id="root", param_name="dep", param_path=("left", "dep")): "override"
    }
    engine = _make_engine(
        root_spell=root_spell,
        override_map=override_map,
        spell_lookup={"root": root_spell, "parent": parent_spell},
    )
    occurrence_graph = {
        ("root", ("left",)): {"dep": [("parent", ("left", "dep"))]},
        ("parent", ("left", "dep")): {},
    }
    engine._instance_results = {("parent", ("left", "dep")): "parent-value"}
    kwargs = engine._build_kwargs_for_instance(
        instance_key=("root", ("left",)),
        occurrence_graph=occurrence_graph,
        canonical_occurrences_by_spell_id={},
    )
    assert kwargs["dep"] == "override"


def test_build_kwargs_for_instance_injects_list_order() -> None:
    """
    Verify dependency lists preserve occurrence ordering.

    Contract:
        - Multi-parent dependencies inject lists in occurrence order.
    """
    root_spell = _make_spell(spell_id="root", existence=Existence.many)
    parent_a = _make_spell(spell_id="parent-a", existence=Existence.many)
    parent_b = _make_spell(spell_id="parent-b", existence=Existence.many)
    engine = _make_engine(
        root_spell=root_spell,
        spell_lookup={
            "root": root_spell,
            "parent-a": parent_a,
            "parent-b": parent_b,
        },
    )
    occurrence_graph = {
        ("root", ("path",)): {
            "deps": [
                ("parent-a", ("path", "a")),
                ("parent-b", ("path", "b")),
            ]
        },
        ("parent-a", ("path", "a")): {},
        ("parent-b", ("path", "b")): {},
    }
    engine._instance_results = {
        ("parent-a", ("path", "a")): "value-a",
        ("parent-b", ("path", "b")): "value-b",
    }
    kwargs = engine._build_kwargs_for_instance(
        instance_key=("root", ("path",)),
        occurrence_graph=occurrence_graph,
        canonical_occurrences_by_spell_id={},
    )
    assert kwargs["deps"] == ["value-a", "value-b"]


def test_build_kwargs_for_instance_missing_dependency_raises() -> None:
    """
    Verify missing dependency instances raise errors.

    Contract:
        - Missing dependency results raise MeldExecutionError.
    """
    root_spell = _make_spell(spell_id="root", existence=Existence.many)
    parent_spell = _make_spell(spell_id="parent", existence=Existence.many)
    engine = _make_engine(
        root_spell=root_spell,
        spell_lookup={"root": root_spell, "parent": parent_spell},
    )
    occurrence_graph = {
        ("root", ("path",)): {"dep": [("parent", ("path", "dep"))]},
        ("parent", ("path", "dep")): {},
    }
    with pytest.raises(MeldExecutionError, match="Dependency"):
        engine._build_kwargs_for_instance(
            instance_key=("root", ("path",)),
            occurrence_graph=occurrence_graph,
            canonical_occurrences_by_spell_id={},
        )


def test_raise_override_on_existing_root_raises() -> None:
    """
    Verify root overrides are rejected when root already exists.

    Contract:
        - Shared root instances reject overrides after creation.
    """
    root_spell = _make_spell(spell_id="root", existence=Existence.unique)
    engine = _make_engine(root_spell=root_spell)
    engine._any_overrides_present = True
    with pytest.raises(MeldExecutionError, match="root spell"):
        engine._raise_override_on_existing(root_spell)


def test_raise_override_on_existing_non_root_raises() -> None:
    """
    Verify shared non-root overrides are rejected for existing instances.

    Contract:
        - Shared non-root instances reject targeted overrides after creation.
    """
    root_spell = _make_spell(spell_id="root", existence=Existence.unique)
    node_spell = _make_spell(spell_id="node", existence=Existence.unique)
    engine = _make_engine(
        root_spell=root_spell,
        spell_lookup={"root": root_spell, "node": node_spell},
    )
    socket_ref = _make_socket_ref(node_id="node", param_name="x", param_path=("x",))
    engine._override_targets_by_spell_id = {"node": [socket_ref]}
    engine._any_overrides_present = False
    with pytest.raises(MeldExecutionError, match="shared spell"):
        engine._raise_override_on_existing(node_spell)


def test_construct_root_only_returns_value_for_non_factory() -> None:
    """
    Verify root-only construction returns value spells as-is.

    Contract:
        - Non factory spells return their backing value.
    """
    root_spell = _make_spell(
        spell_id="root",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        spell="value",
    )
    engine = _make_engine(root_spell=root_spell)
    assert engine._construct_root_only() == "value"


def test_construct_root_only_wraps_exception() -> None:
    """
    Verify root-only construction wraps invocation errors.

    Contract:
        - Invocation failures raise MeldExecutionError with inner exception.
    """
    def boom() -> None:
        """
        Raise a ValueError for construction error testing.
        """
        raise ValueError("boom")

    root_spell = _make_spell(spell_id="root", spell=boom)
    engine = _make_engine(root_spell=root_spell)
    with pytest.raises(MeldExecutionError) as exc_info:
        engine._construct_root_only()
    assert isinstance(exc_info.value.inner, ValueError)


def test_construct_spell_existing_creation_missing_raises() -> None:
    """
    Verify existing-creation spells require a backing object.

    Contract:
        - Missing user_created_object raises MeldExecutionError.
    """
    spell = _make_spell(
        spell_id="node",
        is_existing_creation=True,
        user_created_object=None,
    )
    engine = _make_engine()
    with pytest.raises(MeldExecutionError, match="EXISTING_CREATION"):
        engine._construct_spell(spell, kwargs={})


def test_select_creations_for_spell_per_conduit_prefers_caller() -> None:
    """
    Verify per-conduit existences prefer caller creations.

    Contract:
        - caller creations are returned for unique_per_conduit lifetimes.
    """
    caller_creations = object()
    owner_creations = object()
    spell = _make_spell(
        spell_id="node",
        existence=Existence.unique_per_conduit,
        owner_creations=owner_creations,
    )
    engine = _make_engine(
        caller_creations=caller_creations,
        owner_creations=owner_creations,
    )
    assert engine._select_creations_for_spell(spell) is caller_creations
