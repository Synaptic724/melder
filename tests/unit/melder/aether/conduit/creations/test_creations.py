"""tests/aether/conduit/creations/test_creations.py

Validation: Not run.

These tests target `melder.aether.conduit.creations.creations.Creations`.
They are primarily Rank A/B (behavioral contract + lifecycle invariants) per AGENTS.md.

Notes:
- We intentionally observe behavior via public methods when possible:
  `add_*`, `extract_spell_creations`, `restore_spell_creations`, spellspace helpers, and `cleanup`.
- A small number of tests touch internal helpers (e.g., `_attempt_cleanup`, `_upgrade_from_lesser_conduit`)
  because those are part of the lifecycle contract and have no public wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations


class DummyLogger:
    """Minimal logger stub capturing calls for assertions.

    The codebase uses structured logging (message + kwargs). We keep this permissive.
    """

    def __init__(self) -> None:
        self.events: List[tuple[str, str, dict[str, Any]]] = []

    def debug(self, message: str, **kwargs: Any) -> None:
        self.events.append(("debug", message, dict(kwargs)))

    def error(self, message: str, **kwargs: Any) -> None:
        self.events.append(("error", message, dict(kwargs)))


class FakeConduit:
    """Minimal conduit stub exposing the attributes `Creations` expects."""

    def __init__(self, *, conduit_id: str, state: Optional[ConduitState], logger: DummyLogger) -> None:
        self._id = conduit_id
        self._conduit_state = state
        self._logger = logger


class Probe:
    """A disposable object used to observe which disposal method was invoked."""

    def __init__(self) -> None:
        self.calls: List[str] = []

    def cleanup(self) -> None:
        self.calls.append("cleanup")

    def close(self) -> None:
        self.calls.append("close")

    def dispose(self) -> None:
        self.calls.append("dispose")


class ProbeRaises:
    """A disposable object that raises from a selected method."""

    def __init__(self, *, method: str, exc: Exception) -> None:
        self.calls: List[str] = []
        self._method = method
        self._exc = exc

    def cleanup(self) -> None:
        self.calls.append("cleanup")
        if self._method == "cleanup":
            raise self._exc

    def close(self) -> None:
        self.calls.append("close")
        if self._method == "close":
            raise self._exc

    def dispose(self) -> None:
        self.calls.append("dispose")
        if self._method == "dispose":
            raise self._exc


@dataclass
class _RestoreCase:
    scope: str


@pytest.fixture()
def logger() -> DummyLogger:
    return DummyLogger()


@pytest.fixture()
def normal_conduit(logger: DummyLogger) -> FakeConduit:
    return FakeConduit(conduit_id="conduit-normal", state=ConduitState.normal, logger=logger)


@pytest.fixture()
def lesser_conduit(logger: DummyLogger) -> FakeConduit:
    return FakeConduit(conduit_id="conduit-lesser", state=ConduitState.lesser, logger=logger)


def _mk_creations(*, conduit: FakeConduit, disposal_enabled: bool, disposal_method_names: Optional[list[str]] = None) -> Creations:
    return Creations(disposal_enabled=disposal_enabled, disposal_method_names=disposal_method_names, conduit=conduit)


def _mk_lesser_creations(*, conduit: FakeConduit, disposal_enabled: bool, disposal_method_names: Optional[list[str]] = None) -> LesserCreations:
    return LesserCreations(
        disposal_enabled=disposal_enabled,
        disposal_method_names=disposal_method_names,
        conduit=conduit,
        parent_creations=None,
    )


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

def test_init_requires_conduit_state(logger: DummyLogger) -> None:
    conduit = FakeConduit(conduit_id="c", state=None, logger=logger)
    with pytest.raises(RuntimeError, match="Conduit state is not initialized"):
        _mk_creations(conduit=conduit, disposal_enabled=False, disposal_method_names=[])


def test_init_requires_normal_state(lesser_conduit: FakeConduit) -> None:
    with pytest.raises(RuntimeError, match="only be initialized for normal conduits"):
        _mk_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])


def test_init_accepts_none_disposal_method_names_and_treats_as_empty(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=None)
    probe = Probe()

    # With an empty method list, `_attempt_cleanup` should noop.
    assert creations._attempt_cleanup(probe) is None
    assert probe.calls == []


def test_extract_on_empty_returns_empty(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    assert creations.extract_spell_creations("spell-1") == []


def test_get_spellspace_creation_on_missing_bucket_returns_none(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    assert creations.get_spellspace_creation("ss-1", "spell-1") is None


# -----------------------------------------------------------------------------
# add_* and extraction behavior (prefer public observation via extract)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "add_op,expected_scope",
    [
        ("unique", "unique"),
        ("unique_per_scope", "unique_per_scope"),
        ("unique_per_lineage", "unique_per_lineage"),
        ("unique_per_cluster", "unique_per_cluster"),
    ],
)
def test_add_then_extract_singleton_scopes(normal_conduit: FakeConduit, add_op: str, expected_scope: str) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-1"
    obj = object()

    if add_op == "unique":
        creations.add_unique(spell_id, obj)
    elif add_op == "unique_per_scope":
        creations.add_unique_per_scope(spell_id, obj)
    elif add_op == "unique_per_lineage":
        creations.add_unique_per_lineage(spell_id, obj)
    elif add_op == "unique_per_cluster":
        creations.add_unique_per_cluster(spell_id, obj)
    else:
        raise AssertionError(f"Unhandled add_op={add_op}")

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == expected_scope
    assert extracted[0]["creation"].value is obj

    # Extract is destructive.
    assert creations.extract_spell_creations(spell_id) == []


@pytest.mark.parametrize(
    "add_op",
    [
        "unique",
        "unique_per_scope",
        "unique_per_lineage",
        "unique_per_cluster",
    ],
)
def test_duplicate_key_raises_for_singleton_scopes(normal_conduit: FakeConduit, add_op: str) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-dup"

    if add_op == "unique":
        creations.add_unique(spell_id, object())
        with pytest.raises(ValueError, match="already exists"):
            creations.add_unique(spell_id, object())
    elif add_op == "unique_per_scope":
        creations.add_unique_per_scope(spell_id, object())
        with pytest.raises(ValueError, match="already exists"):
            creations.add_unique_per_scope(spell_id, object())
    elif add_op == "unique_per_lineage":
        creations.add_unique_per_lineage(spell_id, object())
        with pytest.raises(ValueError, match="already exists"):
            creations.add_unique_per_lineage(spell_id, object())
    elif add_op == "unique_per_cluster":
        creations.add_unique_per_cluster(spell_id, object())
        with pytest.raises(ValueError, match="already exists"):
            creations.add_unique_per_cluster(spell_id, object())
    else:
        raise AssertionError(f"Unhandled add_op={add_op}")


@pytest.mark.parametrize(
    "op",
    [
        "add_unique",
        "add_unique_per_scope",
        "add_unique_per_lineage",
        "add_unique_per_cluster",
        "add_many",
        "register_spellspace_creation",
    ],
)
def test_mutations_raise_after_cleanup(normal_conduit: FakeConduit, op: str) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()

    if op == "add_unique":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.add_unique("spell-x", object())
    elif op == "add_unique_per_scope":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.add_unique_per_scope("spell-x", object())
    elif op == "add_unique_per_lineage":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.add_unique_per_lineage("spell-x", object())
    elif op == "add_unique_per_cluster":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.add_unique_per_cluster("spell-x", object())
    elif op == "add_many":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.add_many("spell-x", object())
    elif op == "register_spellspace_creation":
        with pytest.raises(RuntimeError, match="already been cleaned"):
            creations.register_spellspace_creation("ss", "spell-x", object())
    else:
        raise AssertionError(f"Unhandled op={op}")


# -----------------------------------------------------------------------------
# many scope
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 5])
def test_add_many_extract_returns_all_entries(normal_conduit: FakeConduit, n: int) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-many"
    objs = [object() for _ in range(n)]

    for obj in objs:
        creations.add_many(spell_id, obj)

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == n
    assert {e["scope"] for e in extracted} == {"many"}
    assert [e["creation"].value for e in extracted] == objs


def test_add_many_extract_removes_key_after_extraction(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-many-2"
    creations.add_many(spell_id, object())

    assert len(creations.extract_spell_creations(spell_id)) == 1
    assert creations.extract_spell_creations(spell_id) == []


def test_add_many_allows_multiple_calls_same_key(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-many-3"

    a = object()
    b = object()
    creations.add_many(spell_id, a)
    creations.add_many(spell_id, b)

    extracted = creations.extract_spell_creations(spell_id)
    assert [e["creation"].value for e in extracted] == [a, b]


# -----------------------------------------------------------------------------
# SpellSpace buckets
# -----------------------------------------------------------------------------

def test_register_spellspace_and_get_returns_creation(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])

    obj = object()
    creations.register_spellspace_creation("ss-1", "spell-1", obj)

    creation = creations.get_spellspace_creation("ss-1", "spell-1")
    assert creation is not None
    assert creation.value is obj


def test_register_spellspace_duplicate_spell_id_raises(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.register_spellspace_creation("ss-1", "spell-1", object())

    with pytest.raises(ValueError, match="already exists"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_clear_spellspace_instances_missing_id_noop(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])
    creations.clear_spellspace_instances("ss-missing")


def test_clear_spellspace_instances_disposes_and_removes_bucket(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    p1 = Probe()
    p2 = Probe()
    creations.register_spellspace_creation("ss-1", "spell-a", p1)
    creations.register_spellspace_creation("ss-1", "spell-b", p2)

    creations.clear_spellspace_instances("ss-1")

    assert p1.calls == ["dispose"]
    assert p2.calls == ["dispose"]
    assert creations.get_spellspace_creation("ss-1", "spell-a") is None


def test_clear_spellspace_instances_raises_exceptiongroup_on_disposal_error(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    bad = ProbeRaises(method="dispose", exc=ValueError("nope"))
    creations.register_spellspace_creation("ss-1", "spell-a", bad)

    with pytest.raises(ExceptionGroup) as eg:
        creations.clear_spellspace_instances("ss-1")

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)


def test_extract_spell_creations_removes_spellspace_bucket_when_empty(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])

    obj = object()
    creations.register_spellspace_creation("ss-1", "spell-1", obj)

    extracted = creations.extract_spell_creations("spell-1")
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "spellspace"
    assert extracted[0]["spellspace_id"] == "ss-1"

    # The spellspace bucket should be removed when it becomes empty.
    assert creations.get_spellspace_creation("ss-1", "spell-1") is None

    # If the bucket was removed, this should recreate it cleanly.
    creations.register_spellspace_creation("ss-1", "spell-2", object())
    assert creations.get_spellspace_creation("ss-1", "spell-2") is not None


def test_extract_spell_creations_can_extract_across_spellspace_and_singletons(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-shared"

    obj_unique = object()
    obj_spellspace = object()

    creations.add_unique(spell_id, obj_unique)
    creations.register_spellspace_creation("ss-1", spell_id, obj_spellspace)

    extracted = creations.extract_spell_creations(spell_id)
    scopes = {e["scope"] for e in extracted}
    assert scopes == {"unique", "spellspace"}


# -----------------------------------------------------------------------------
# _attempt_cleanup
# -----------------------------------------------------------------------------

def test_attempt_cleanup_returns_none_when_item_none(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])
    assert creations._attempt_cleanup(None) is None


def test_attempt_cleanup_skips_when_disposal_disabled(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=["dispose"])
    probe = Probe()
    assert creations._attempt_cleanup(probe) is None
    assert probe.calls == []


def test_attempt_cleanup_no_methods_configured_is_noop(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=[])
    probe = Probe()
    assert creations._attempt_cleanup(probe) is None
    assert probe.calls == []


@pytest.mark.parametrize(
    "method_list,expected_call",
    [
        (["cleanup", "close"], "cleanup"),
        (["close", "cleanup"], "close"),
        (["dispose", "close"], "dispose"),
    ],
)
def test_attempt_cleanup_calls_first_matching_method(
        normal_conduit: FakeConduit,
        method_list: list[str],
        expected_call: str,
) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=method_list)
    probe = Probe()

    assert creations._attempt_cleanup(probe) is None
    assert probe.calls == [expected_call]


def test_attempt_cleanup_skips_non_callable_and_tries_next(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["cleanup", "close"])

    probe = Probe()
    # Override the method with a non-callable attribute.
    probe.cleanup = "not callable"  # type: ignore[attr-defined]

    assert creations._attempt_cleanup(probe) is None
    assert probe.calls == ["close"]


@pytest.mark.parametrize(
    "method_name",
    [
        "cleanup",
        "close",
    ],
)
def test_attempt_cleanup_wraps_exception_as_runtimeerror(normal_conduit: FakeConduit, method_name: str) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=[method_name])

    bad = ProbeRaises(method=method_name, exc=ValueError("boom"))
    err = creations._attempt_cleanup(bad)

    assert isinstance(err, RuntimeError)
    assert bad.calls == [method_name]


def test_attempt_cleanup_ignores_missing_methods_returns_none(normal_conduit: FakeConduit) -> None:
    class NoDisposal:
        pass

    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["cleanup", "close"])
    err = creations._attempt_cleanup(NoDisposal())
    assert err is None


# -----------------------------------------------------------------------------
# cleanup()
# -----------------------------------------------------------------------------

def test_cleanup_disposes_all_scopes_and_marks_cleaned(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    p_unique = Probe()
    p_scope = Probe()
    p_lineage = Probe()
    p_cluster = Probe()
    p_many_1 = Probe()
    p_many_2 = Probe()
    p_spellspace = Probe()

    creations.add_unique("spell-u", p_unique)
    creations.add_unique_per_scope("spell-s", p_scope)
    creations.add_unique_per_lineage("spell-l", p_lineage)
    creations.add_unique_per_cluster("spell-c", p_cluster)
    creations.add_many("spell-m", p_many_1)
    creations.add_many("spell-m", p_many_2)
    creations.register_spellspace_creation("ss-1", "spell-ss", p_spellspace)

    creations.cleanup()

    assert creations.cleaned is True
    assert p_unique.calls == ["dispose"]
    assert p_scope.calls == ["dispose"]
    assert p_lineage.calls == ["dispose"]
    assert p_cluster.calls == ["dispose"]
    assert p_many_1.calls == ["dispose"]
    assert p_many_2.calls == ["dispose"]
    assert p_spellspace.calls == ["dispose"]


def test_cleanup_is_idempotent_and_does_not_double_dispose(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    p = Probe()
    creations.add_unique("spell-1", p)

    creations.cleanup()
    creations.cleanup()

    assert p.calls == ["dispose"]


def test_cleanup_raises_exceptiongroup_with_all_errors_across_scopes(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    bad_unique = ProbeRaises(method="dispose", exc=ValueError("u"))
    bad_many_1 = ProbeRaises(method="dispose", exc=ValueError("m1"))
    bad_many_2 = ProbeRaises(method="dispose", exc=ValueError("m2"))

    creations.add_unique("spell-u", bad_unique)
    creations.add_many("spell-m", bad_many_1)
    creations.add_many("spell-m", bad_many_2)

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    # Each failing creation produces a wrapped RuntimeError in the group.
    assert len(eg.value.exceptions) == 3
    assert all(isinstance(e, RuntimeError) for e in eg.value.exceptions)


def test_cleanup_cleans_even_when_exceptiongroup_raised(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])
    creations.add_unique("spell-u", ProbeRaises(method="dispose", exc=ValueError("x")))

    with pytest.raises(ExceptionGroup):
        creations.cleanup()

    assert creations.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_unique("spell-new", object())


def test_cleanup_handles_unexpected_exception_in_sequence_and_raises_group(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    # Simulate a fatal bug inside one of the cleanup helpers.
    def boom() -> List[Exception]:
        raise ValueError("boom")

    creations._cleanup_many = boom  # type: ignore[assignment]

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert any(isinstance(e, ValueError) for e in eg.value.exceptions)


def test_cleanup_disposes_spellspace_instances(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    p = Probe()
    creations.register_spellspace_creation("ss-1", "spell-1", p)
    creations.cleanup()

    assert p.calls == ["dispose"]


# -----------------------------------------------------------------------------
# extract/restore
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "scope_case",
    [
        _RestoreCase(scope="unique"),
        _RestoreCase(scope="unique_per_scope"),
        _RestoreCase(scope="unique_per_lineage"),
        _RestoreCase(scope="unique_per_cluster"),
        _RestoreCase(scope="many"),
    ],
)
def test_extract_spell_creations_returns_correct_scope_names(normal_conduit: FakeConduit, scope_case: _RestoreCase) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-x"
    obj = object()

    if scope_case.scope == "unique":
        creations.add_unique(spell_id, obj)
    elif scope_case.scope == "unique_per_scope":
        creations.add_unique_per_scope(spell_id, obj)
    elif scope_case.scope == "unique_per_lineage":
        creations.add_unique_per_lineage(spell_id, obj)
    elif scope_case.scope == "unique_per_cluster":
        creations.add_unique_per_cluster(spell_id, obj)
    elif scope_case.scope == "many":
        creations.add_many(spell_id, obj)
    else:
        raise AssertionError(f"Unhandled scope={scope_case.scope}")

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == scope_case.scope
    assert extracted[0]["creation"].value is obj


@pytest.mark.parametrize(
    "scope_case",
    [
        _RestoreCase(scope="unique"),
        _RestoreCase(scope="unique_per_scope"),
        _RestoreCase(scope="unique_per_lineage"),
        _RestoreCase(scope="unique_per_cluster"),
        _RestoreCase(scope="many"),
    ],
)
def test_restore_spell_creations_restores_each_scope(normal_conduit: FakeConduit, scope_case: _RestoreCase) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-x"
    obj = object()

    if scope_case.scope == "unique":
        creations.add_unique(spell_id, obj)
    elif scope_case.scope == "unique_per_scope":
        creations.add_unique_per_scope(spell_id, obj)
    elif scope_case.scope == "unique_per_lineage":
        creations.add_unique_per_lineage(spell_id, obj)
    elif scope_case.scope == "unique_per_cluster":
        creations.add_unique_per_cluster(spell_id, obj)
    elif scope_case.scope == "many":
        creations.add_many(spell_id, obj)
    else:
        raise AssertionError(f"Unhandled scope={scope_case.scope}")

    extracted = creations.extract_spell_creations(spell_id)
    creations.restore_spell_creations(spell_id, extracted)

    extracted_again = creations.extract_spell_creations(spell_id)
    assert len(extracted_again) == 1
    assert extracted_again[0]["scope"] == scope_case.scope
    assert extracted_again[0]["creation"].value is obj


def test_restore_spell_creations_restores_spellspace_entries(normal_conduit: FakeConduit) -> None:
    """
    Verify restore_spell_creations rehydrates spellspace entries.
    """
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-x"
    obj = object()

    creations.register_spellspace_creation("ss-1", spell_id, obj)
    extracted = creations.extract_spell_creations(spell_id)
    creations.restore_spell_creations(spell_id, extracted)

    restored = creations.get_spellspace_creation("ss-1", spell_id)
    assert restored is not None
    assert restored.value is obj


def test_restore_spell_creations_ignores_invalid_entries(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])

    # Missing scope and/or creation should be ignored.
    creations.restore_spell_creations("spell-x", [{"scope": None, "creation": None}, {}])

    assert creations.extract_spell_creations("spell-x") == []


def test_restore_spell_creations_empty_list_noop(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.restore_spell_creations("spell-x", [])


def test_restore_spell_creations_on_cleaned_with_entries_raises_runtimeerror(
        normal_conduit: FakeConduit,
) -> None:
    """
    Verify restore_spell_creations rejects non-empty restores after cleanup.
    """
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    spell_id = "spell-x"

    creations.add_unique(spell_id, object())
    extracted = creations.extract_spell_creations(spell_id)
    assert extracted

    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.restore_spell_creations(spell_id, extracted)


# -----------------------------------------------------------------------------
# Upgrade from LesserConduit
# -----------------------------------------------------------------------------

def test_transfer_data_and_clear_returns_data_and_marks_cleaned(
        lesser_conduit: FakeConduit,
) -> None:
    """
    Verify transfer_data_and_clear returns data and marks the manager cleaned.
    """
    lesser = _mk_lesser_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])
    p_scope = Probe()
    p_many = Probe()

    lesser.add_unique_per_scope("spell-s", p_scope)
    lesser.add_many("spell-m", p_many)

    data = lesser.transfer_data_and_clear()

    assert lesser.cleaned is True
    assert data["unique_per_scope"]["spell-s"].value is p_scope
    assert data["many"]["spell-m"][0].value is p_many
    with pytest.raises(RuntimeError, match="already been cleaned"):
        lesser.add_unique_per_scope("spell-new", Probe())


def test_upgrade_from_lesser_transfers_unique_per_scope_and_many(
        normal_conduit: FakeConduit,
        lesser_conduit: FakeConduit,
) -> None:
    lesser = _mk_lesser_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])

    p_scope = Probe()
    p_many = Probe()

    lesser.add_unique_per_scope("spell-s", p_scope)
    lesser.add_many("spell-m", p_many)

    data = lesser.transfer_data_and_clear()

    target = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    target._upgrade_from_lesser_conduit(**data)

    extracted_scope = target.extract_spell_creations("spell-s")
    assert len(extracted_scope) == 1
    assert extracted_scope[0]["scope"] == "unique_per_scope"
    assert extracted_scope[0]["creation"].value is p_scope

    extracted_many = target.extract_spell_creations("spell-m")
    assert len(extracted_many) == 1
    assert extracted_many[0]["scope"] == "many"
    assert extracted_many[0]["creation"].value is p_many


def test_upgrade_from_lesser_refuses_when_target_has_both_scopes_nonempty(
        normal_conduit: FakeConduit,
        lesser_conduit: FakeConduit,
) -> None:
    lesser = _mk_lesser_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])
    lesser.add_unique_per_scope("spell-s", Probe())

    data = lesser.transfer_data_and_clear()

    target = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    # Make BOTH buckets non-empty.
    target.add_unique_per_scope("pre-s", Probe())
    target.add_many("pre-m", Probe())

    with pytest.raises(RuntimeError, match="cannot transfer data"):
        target._upgrade_from_lesser_conduit(**data)


def test_upgrade_from_lesser_allows_overwrite_when_only_unique_per_scope_nonempty(
        normal_conduit: FakeConduit,
        lesser_conduit: FakeConduit,
) -> None:
    lesser = _mk_lesser_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])
    lesser.add_unique_per_scope("spell-s", Probe())

    data = lesser.transfer_data_and_clear()

    target = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    target.add_unique_per_scope("pre-s", Probe())

    # The current implementation only refuses when BOTH buckets are non-empty.
    target._upgrade_from_lesser_conduit(**data)

    extracted = target.extract_spell_creations("spell-s")
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique_per_scope"


def test_upgrade_from_lesser_allows_overwrite_when_only_many_nonempty(
        normal_conduit: FakeConduit,
        lesser_conduit: FakeConduit,
) -> None:
    lesser = _mk_lesser_creations(conduit=lesser_conduit, disposal_enabled=False, disposal_method_names=[])
    lesser.add_many("spell-m", Probe())

    data = lesser.transfer_data_and_clear()

    target = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    target.add_many("pre-m", Probe())

    # The current implementation only refuses when BOTH buckets are non-empty.
    target._upgrade_from_lesser_conduit(**data)

    extracted = target.extract_spell_creations("spell-m")
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "many"


# -----------------------------------------------------------------------------
# Public methods should reject after cleanup (beyond mutation ops)
# -----------------------------------------------------------------------------

def test_extract_spell_creations_on_cleaned_raises_runtimeerror(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.extract_spell_creations("spell-1")


def test_register_spellspace_creation_on_cleaned_raises_runtimeerror(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_get_spellspace_creation_on_cleaned_raises_runtimeerror(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.get_spellspace_creation("ss-1", "spell-1")


def test_clear_spellspace_instances_on_cleaned_raises_runtimeerror(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.clear_spellspace_instances("ss-1")


# -----------------------------------------------------------------------------
# Logging assertions (boundary/collaboration tests)
# -----------------------------------------------------------------------------

def test_add_unique_duplicate_logs_error(logger: DummyLogger, normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.add_unique("spell-1", object())

    with pytest.raises(ValueError):
        creations.add_unique("spell-1", object())

    assert any(level == "error" for (level, _msg, _kw) in logger.events)


def test_cleanup_logs_begin_and_complete(logger: DummyLogger, normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=False, disposal_method_names=[])
    creations.cleanup()

    msgs = [m for (_lvl, m, _kw) in logger.events]
    assert "cleanup: begin" in msgs
    assert "cleanup: complete" in msgs


def test_attempt_cleanup_logs_no_method_matched(logger: DummyLogger, normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit, disposal_enabled=True, disposal_method_names=["dispose"])

    class NoDisposal:
        pass

    assert creations._attempt_cleanup(NoDisposal()) is None

    msgs = [m for (_lvl, m, _kw) in logger.events]
    assert "_attempt_cleanup: no disposal method matched; noop" in msgs
