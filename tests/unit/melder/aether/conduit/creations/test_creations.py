from __future__ import annotations

from typing import Optional

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creation import Creation
from melder.aether.conduit.creations.creations import Creations


class FakeConduit:
    def __init__(self, *, conduit_id: str, state: Optional[ConduitState]) -> None:
        self._id = conduit_id
        self._conduit_state = state


class Probe:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def cleanup(self) -> None:
        self.calls.append("cleanup")

    def close(self) -> None:
        self.calls.append("close")

    def dispose(self) -> None:
        self.calls.append("dispose")


class ProbeRaises:
    def __init__(self, *, method: str, exc: Exception) -> None:
        self.calls: list[str] = []
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


@pytest.fixture()
def normal_conduit() -> FakeConduit:
    return FakeConduit(conduit_id="conduit-normal", state=ConduitState.normal)


@pytest.fixture()
def lesser_conduit() -> FakeConduit:
    return FakeConduit(conduit_id="conduit-lesser", state=ConduitState.lesser)


def _mk_creations(*, conduit: FakeConduit) -> Creations:
    return Creations(conduit=conduit)


def test_init_requires_conduit_state() -> None:
    conduit = FakeConduit(conduit_id="c", state=None)
    with pytest.raises(RuntimeError, match="Conduit state is not initialized"):
        _mk_creations(conduit=conduit)


def test_init_allows_lesser_state(lesser_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=lesser_conduit)
    assert creations._conduit_state == ConduitState.lesser


def test_add_creation_records_disposal_metadata(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-1"
    obj = object()

    creations.add_creation(
        spell_id,
        obj,
        has_disposal_methods=True,
        disposal_methods=["cleanup", "close"],
    )

    creation = creations._creations[spell_id]
    assert creation.has_disposal_methods is True
    assert creation.disposal_method_names == ["cleanup", "close"]


def test_add_many_creations_records_disposal_metadata(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-1"
    obj = object()

    creations.add_many_creations(
        spell_id,
        obj,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creation = creations._creations[spell_id][0]
    assert creation.has_disposal_methods is True
    assert creation.disposal_method_names == ["dispose"]


def test_add_creation_duplicate_key_raises(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-dup"
    creations.add_creation(spell_id, object())
    with pytest.raises(ValueError, match="already exists"):
        creations.add_creation(spell_id, object())


def test_add_many_creations_appends_in_order(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-many"
    a = object()
    b = object()

    creations.add_many_creations(spell_id, a)
    creations.add_many_creations(spell_id, b)

    extracted = creations.extract_spell_creations(spell_id)
    assert [entry["creation"].value for entry in extracted] == [a, b]
    assert {entry["scope"] for entry in extracted} == {"many"}


def test_add_many_creations_non_list_slot_raises(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-collision"
    creations.add_creation(spell_id, object())

    with pytest.raises(ValueError, match="non-list slot"):
        creations.add_many_creations(spell_id, object())


def test_mutations_raise_after_cleanup(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_creation("spell-x", object())
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_many_creations("spell-x", object())
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.register_spellspace_creation("ss", "spell-x", object())


def test_extract_unique_returns_scope_and_is_destructive(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-1"
    obj = object()

    creations.add_creation(spell_id, obj)
    extracted = creations.extract_spell_creations(spell_id)

    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique"
    assert extracted[0]["creation"].value is obj
    assert creations.extract_spell_creations(spell_id) == []


def test_extract_many_returns_all_entries(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-many"
    objs = [object(), object(), object()]

    for obj in objs:
        creations.add_many_creations(spell_id, obj)

    extracted = creations.extract_spell_creations(spell_id)
    assert [entry["creation"].value for entry in extracted] == objs
    assert {entry["scope"] for entry in extracted} == {"many"}


def test_register_spellspace_creation_and_get(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    obj = object()

    creations.register_spellspace_creation("ss-1", "spell-1", obj)

    creation = creations.get_spellspace_creation("ss-1", "spell-1")
    assert creation is not None
    assert creation.value is obj


def test_register_spellspace_duplicate_raises(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.register_spellspace_creation("ss-1", "spell-1", object())
    with pytest.raises(ValueError, match="already exists"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_register_spellspace_creation_non_spellspace_collision_raises(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.add_creation("ss-1", object())

    with pytest.raises(ValueError, match="non-spellspace scope"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_get_spellspace_creation_returns_none_for_non_dict_slot(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.add_creation("ss-1", object())

    assert creations.get_spellspace_creation("ss-1", "spell-1") is None


def test_extract_spell_creations_removes_from_multiple_spellspaces(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-ss"
    creations.register_spellspace_creation("ss-1", spell_id, object())
    creations.register_spellspace_creation("ss-2", spell_id, object())

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 2
    assert {entry["scope"] for entry in extracted} == {"spellspace"}
    assert {entry["spellspace_id"] for entry in extracted} == {"ss-1", "ss-2"}
    assert creations.get_spellspace_creation("ss-1", spell_id) is None
    assert creations.get_spellspace_creation("ss-2", spell_id) is None


def test_extract_can_return_unique_and_spellspace_for_same_spell_id(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-shared"
    creations.add_creation(spell_id, object())
    creations.register_spellspace_creation("ss-1", spell_id, object())

    extracted = creations.extract_spell_creations(spell_id)
    assert {entry["scope"] for entry in extracted} == {"unique", "spellspace"}


def test_restore_spell_creations_restores_unique(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-x"
    obj = object()
    creations.restore_spell_creations(
        spell_id,
        [{"scope": "unique", "creation": Creation(obj)}],
    )

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique"
    assert extracted[0]["creation"].value is obj


def test_restore_spell_creations_unique_replaces_root_and_spellspace_entries(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-replace"
    replacement = object()

    creations.add_creation(spell_id, object())
    creations.register_spellspace_creation("ss-1", spell_id, object())

    creations.restore_spell_creations(
        spell_id,
        [{"scope": "unique", "creation": Creation(replacement)}],
    )

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique"
    assert extracted[0]["creation"].value is replacement
    assert creations.get_spellspace_creation("ss-1", spell_id) is None


def test_restore_spell_creations_restores_many_in_order(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-many"
    a = object()
    b = object()
    creations.restore_spell_creations(
        spell_id,
        [
            {"scope": "many", "creation": Creation(a)},
            {"scope": "many", "creation": Creation(b)},
        ],
    )

    extracted = creations.extract_spell_creations(spell_id)
    assert [entry["creation"].value for entry in extracted] == [a, b]
    assert {entry["scope"] for entry in extracted} == {"many"}


def test_restore_spell_creations_unique_replaces_existing_many_entries(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-many-replace"
    replacement = object()

    creations.add_many_creations(spell_id, object())
    creations.add_many_creations(spell_id, object())

    creations.restore_spell_creations(
        spell_id,
        [{"scope": "unique", "creation": Creation(replacement)}],
    )

    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique"
    assert extracted[0]["creation"].value is replacement


def test_restore_spell_creations_many_into_spellspace_slot_raises_runtimeerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "shared-key"
    creations.register_spellspace_creation(spell_id, "other-spell", object())

    with pytest.raises(RuntimeError, match="non-list slot"):
        creations.restore_spell_creations(
            spell_id,
            [{"scope": "many", "creation": Creation(object())}],
        )


def test_restore_spell_creations_restores_spellspace(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-ss"
    obj = object()
    creations.restore_spell_creations(
        spell_id,
        [{"scope": "spellspace", "spellspace_id": "ss-1", "creation": Creation(obj)}],
    )

    restored = creations.get_spellspace_creation("ss-1", spell_id)
    assert restored is not None
    assert restored.value is obj


def test_restore_spell_creations_spellspace_replaces_root_and_existing_spellspace_entries(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    spell_id = "spell-ss-replace"
    replacement = object()

    creations.add_creation(spell_id, object())
    creations.register_spellspace_creation("ss-old", spell_id, object())

    creations.restore_spell_creations(
        spell_id,
        [{"scope": "spellspace", "spellspace_id": "ss-new", "creation": Creation(replacement)}],
    )

    restored = creations.get_spellspace_creation("ss-new", spell_id)
    assert restored is not None
    assert restored.value is replacement
    assert creations.get_spellspace_creation("ss-old", spell_id) is None
    extracted = creations.extract_spell_creations(spell_id)
    assert len(extracted) == 1
    assert extracted[0]["scope"] == "spellspace"
    assert extracted[0]["spellspace_id"] == "ss-new"
    assert extracted[0]["creation"].value is replacement


def test_restore_spell_creations_spellspace_into_singleton_slot_raises_runtimeerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.add_creation("ss-1", object())

    with pytest.raises(RuntimeError, match="non-dict slot"):
        creations.restore_spell_creations(
            "spell-ss",
            [{"scope": "spellspace", "spellspace_id": "ss-1", "creation": Creation(object())}],
        )


def test_restore_spell_creations_unknown_scope_raises(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    with pytest.raises(RuntimeError, match="Unknown creation scope"):
        creations.restore_spell_creations(
            "spell-x",
            [{"scope": "unknown", "creation": Creation(object())}],
        )


def test_restore_spell_creations_spellspace_missing_id_raises_keyerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    with pytest.raises(KeyError):
        creations.restore_spell_creations(
            "spell-x",
            [{"scope": "spellspace", "creation": Creation(object())}],
        )


def test_restore_spell_creations_invalid_entry_missing_scope_raises_keyerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    with pytest.raises(KeyError):
        creations.restore_spell_creations("spell-x", [{}])


def test_clear_spellspace_instances_noop_for_missing_id(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.clear_spellspace_instances("missing-ss")


def test_clear_spellspace_instances_noop_for_non_dict_slot(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.add_creation("ss-1", object())

    creations.clear_spellspace_instances("ss-1")


def test_clear_spellspace_instances_clears_only_target_bucket(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    a = object()
    b = object()
    creations.register_spellspace_creation("ss-1", "spell-a", a)
    creations.register_spellspace_creation("ss-2", "spell-b", b)

    creations.clear_spellspace_instances("ss-1")

    assert creations.get_spellspace_creation("ss-1", "spell-a") is None
    remaining = creations.get_spellspace_creation("ss-2", "spell-b")
    assert remaining is not None
    assert remaining.value is b


def test_clear_spellspace_instances_raises_exceptiongroup_on_disposal_error(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    bad = ProbeRaises(method="dispose", exc=ValueError("boom"))
    creations.register_spellspace_creation(
        "ss-1",
        "spell-a",
        bad,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    with pytest.raises(ExceptionGroup) as eg:
        creations.clear_spellspace_instances("ss-1")

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)


def test_cleanup_disposes_unique_many_and_spellspace(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    p_unique = Probe()
    p_many_a = Probe()
    p_many_b = Probe()
    p_spellspace = Probe()

    creations.add_creation(
        "spell-u",
        p_unique,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_many_creations(
        "spell-m",
        p_many_a,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_many_creations(
        "spell-m",
        p_many_b,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.register_spellspace_creation(
        "ss-1",
        "spell-s",
        p_spellspace,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creations.cleanup()

    assert p_unique.calls == ["dispose"]
    assert p_many_a.calls == ["dispose"]
    assert p_many_b.calls == ["dispose"]
    assert p_spellspace.calls == ["dispose"]
    assert creations.cleaned is True


def test_cleanup_is_idempotent(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    p = Probe()
    creations.add_creation(
        "spell-1",
        p,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creations.cleanup()
    creations.cleanup()
    assert p.calls == ["dispose"]


def test_cleanup_records_fatal_sequence_error_and_still_tears_down(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)

    def boom() -> list[Exception]:
        raise RuntimeError("boom")

    creations._drain_disposal_stack = boom

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)
    assert creations._creations is None
    assert creations._spellspace_disposal_stacks is None
    assert creations._disposal_stack is None
    assert creations._conduit is None


def test_cleanup_nulls_internal_refs(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.cleanup()
    assert creations._creations is None
    assert creations._spellspace_disposal_stacks is None
    assert creations._disposal_stack is None
    assert creations._conduit is None


def test_cleanup_raises_exceptiongroup_when_disposal_fails(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    bad_unique = ProbeRaises(method="dispose", exc=ValueError("u"))
    bad_many = ProbeRaises(method="dispose", exc=ValueError("m"))
    bad_spellspace = ProbeRaises(method="dispose", exc=ValueError("s"))

    creations.add_creation(
        "spell-u",
        bad_unique,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_many_creations(
        "spell-m",
        bad_many,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.register_spellspace_creation(
        "ss-1",
        "spell-s",
        bad_spellspace,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 3


def test_public_methods_raise_after_cleanup(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.extract_spell_creations("spell-1")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.restore_spell_creations("spell-1", [{"scope": "unique", "creation": Creation(object())}])
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.get_spellspace_creation("ss-1", "spell-1")
    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.clear_spellspace_instances("ss-1")


def test_attempt_cleanup_none_creation_raises_attributeerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    with pytest.raises(AttributeError):
        creations._attempt_cleanup(None)


def test_attempt_cleanup_item_none_returns_none(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creation = Creation(None, has_disposal_methods=True, disposal_methods=["dispose"])
    assert creations._attempt_cleanup(creation) is None


def test_attempt_cleanup_no_methods_returns_none(normal_conduit: FakeConduit) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    probe = Probe()
    creation = Creation(probe, has_disposal_methods=False, disposal_methods=None)
    assert creations._attempt_cleanup(creation) is None
    assert probe.calls == []


def test_attempt_cleanup_missing_method_returns_runtimeerror(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)

    class NoDisposal:
        pass

    creation = Creation(NoDisposal(), has_disposal_methods=True, disposal_methods=["dispose"])
    err = creations._attempt_cleanup(creation)
    assert isinstance(err, RuntimeError)


def test_cleanup_spellspace_instances_drains_and_clears_buckets(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    probe = Probe()
    creations.register_spellspace_creation("ss-1", "spell-a", object())
    creations.register_spellspace_creation(
        "ss-1",
        "spell-b",
        probe,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    non_disposable = creations._creations["ss-1"]["spell-a"]
    disposable = creations._creations["ss-1"]["spell-b"]

    errors = creations._cleanup_spellspace_instances()

    assert errors == []
    assert creations._creations == {}
    assert creations._spellspace_disposal_stacks == {}
    assert non_disposable.cleaned is True
    assert disposable.cleaned is True
    assert probe.calls == ["dispose"]


def test_remove_disposal_creation_removes_only_targeted_entry(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.add_creation(
        "spell-a",
        object(),
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_creation(
        "spell-b",
        object(),
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    target = creations._creations["spell-a"]
    other = creations._creations["spell-b"]

    creations._remove_disposal_creation(target)

    assert list(creations._disposal_stack) == [other]


def test_remove_spellspace_disposal_creation_removes_only_targeted_entry(
    normal_conduit: FakeConduit,
) -> None:
    creations = _mk_creations(conduit=normal_conduit)
    creations.register_spellspace_creation(
        "ss-1",
        "spell-a",
        object(),
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.register_spellspace_creation(
        "ss-1",
        "spell-b",
        object(),
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    target = creations._creations["ss-1"]["spell-a"]
    other = creations._creations["ss-1"]["spell-b"]

    creations._remove_spellspace_disposal_creation("ss-1", target)

    assert list(creations._spellspace_disposal_stacks["ss-1"]) == [other]

