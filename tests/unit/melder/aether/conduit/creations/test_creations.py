from unittest.mock import patch

import pytest

from melder.aether.conduit.creations.creations import Creations


class Probe:
    """
    Minimal disposable object used to verify cleanup ordering.
    """

    def __init__(self) -> None:
        """
        Initialize one empty call log.
        """
        self.calls: list[str] = []

    def cleanup(self) -> None:
        """
        Record one cleanup call.
        """
        self.calls.append("cleanup")

    def close(self) -> None:
        """
        Record one close call.
        """
        self.calls.append("close")

    def dispose(self) -> None:
        """
        Record one dispose call.
        """
        self.calls.append("dispose")


class ProbeRaises:
    """
    Disposable probe that fails on one configured disposal method.
    """

    def __init__(self, *, method: str, exc: Exception) -> None:
        """
        Configure which disposal method should raise.
        """
        self.calls: list[str] = []
        self._method: str = method
        self._exc: Exception = exc

    def cleanup(self) -> None:
        """
        Record cleanup and optionally raise.
        """
        self.calls.append("cleanup")
        if self._method == "cleanup":
            raise self._exc

    def close(self) -> None:
        """
        Record close and optionally raise.
        """
        self.calls.append("close")
        if self._method == "close":
            raise self._exc

    def dispose(self) -> None:
        """
        Record dispose and optionally raise.
        """
        self.calls.append("dispose")
        if self._method == "dispose":
            raise self._exc


@pytest.fixture()
def creations() -> Creations:
    """
    Build one base scoped creations registry for direct unit checks.
    """
    return Creations(
        owner_conduit_id="conduit-normal",
        id="scope-a",
    )


def _disposable_entry(value: object, *methods: str) -> tuple[object, list[str]]:
    """
    Build one expected disposal metadata tuple.
    """
    return value, list(methods)


def test_init_exposes_owner_and_scope_ids(creations: Creations) -> None:
    """
    Verify base creations exposes the injected owner and scope ids.
    """
    assert creations.owner_conduit_id == "conduit-normal"
    assert creations.id == "scope-a"


def test_add_creation_records_disposal_metadata(creations: Creations) -> None:
    """
    Verify singleton creation registration mirrors disposal metadata.
    """
    obj = object()

    creations.add_creation(
        "spell-1",
        obj,
        has_disposal_methods=True,
        disposal_methods=["cleanup", "close"],
    )

    assert creations.get_creation("spell-1") is obj
    assert creations._disposable_creations["spell-1"] == _disposable_entry(
        obj,
        "cleanup",
        "close",
    )


def test_add_many_creations_records_disposal_metadata(creations: Creations) -> None:
    """
    Verify many-scope registration stores live and disposal entries in order.
    """
    obj = object()

    creations.add_many_creations(
        "spell-many",
        obj,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    assert creations._creations["spell-many"] == [obj]
    assert creations._disposable_creations["spell-many"][0] == _disposable_entry(
        obj,
        "dispose",
    )


def test_add_creation_duplicate_key_raises(creations: Creations) -> None:
    """
    Verify singleton registration rejects duplicate keys.
    """
    creations.add_creation("spell-dup", object())

    with pytest.raises(ValueError, match="already exists"):
        creations.add_creation("spell-dup", object())


def test_add_many_creations_non_list_slot_raises(creations: Creations) -> None:
    """
    Verify many registration rejects collisions with singleton slots.
    """
    creations.add_creation("spell-collision", object())

    with pytest.raises(ValueError, match="non-list slot"):
        creations.add_many_creations("spell-collision", object())


def test_extract_unique_returns_scope_and_is_destructive(creations: Creations) -> None:
    """
    Verify unique extraction returns one local payload and removes it.
    """
    obj = object()
    creations.add_creation("spell-1", obj)

    extracted = creations.extract_spell_creations("spell-1")

    assert extracted == [
        {
            "scope": "unique",
            "disposable": False,
            "stored": obj,
        }
    ]
    assert creations.extract_spell_creations("spell-1") == []


def test_extract_many_returns_all_entries_in_order(creations: Creations) -> None:
    """
    Verify many extraction preserves insertion order.
    """
    first = object()
    second = object()
    third = object()

    creations.add_many_creations("spell-many", first)
    creations.add_many_creations("spell-many", second)
    creations.add_many_creations("spell-many", third)

    extracted = creations.extract_spell_creations("spell-many")

    assert [entry["stored"] for entry in extracted] == [first, second, third]
    assert {entry["scope"] for entry in extracted} == {"many"}


def test_restore_unique_replaces_existing_many_entries(creations: Creations) -> None:
    """
    Verify restoring a unique entry replaces current many-scope state.
    """
    replacement = object()
    creations.add_many_creations("spell-x", object())
    creations.add_many_creations("spell-x", object())

    creations.restore_spell_creations(
        "spell-x",
        [{"scope": "unique", "disposable": False, "stored": replacement}],
    )

    extracted = creations.extract_spell_creations("spell-x")

    assert len(extracted) == 1
    assert extracted[0]["scope"] == "unique"
    assert extracted[0]["stored"] is replacement


def test_restore_many_rebuilds_values_in_order(creations: Creations) -> None:
    """
    Verify restoring many-scope entries preserves payload order.
    """
    first = object()
    second = object()

    creations.restore_spell_creations(
        "spell-many",
        [
            {"scope": "many", "disposable": False, "stored": first},
            {"scope": "many", "disposable": False, "stored": second},
        ],
    )

    extracted = creations.extract_spell_creations("spell-many")

    assert [entry["stored"] for entry in extracted] == [first, second]
    assert {entry["scope"] for entry in extracted} == {"many"}


def test_restore_unknown_scope_raises(creations: Creations) -> None:
    """
    Verify unknown restore payload scopes are rejected.
    """
    with pytest.raises(RuntimeError, match="Unknown creation scope"):
        creations.restore_spell_creations(
            "spell-x",
            [{"scope": "unknown", "disposable": False, "stored": object()}],
        )


def test_clear_all_disposes_unique_and_many(creations: Creations) -> None:
    """
    Verify reusable clear disposes tracked entries and preserves the object.
    """
    unique_obj = Probe()
    many_a = Probe()
    many_b = Probe()

    creations.add_creation(
        "spell-u",
        unique_obj,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_many_creations(
        "spell-m",
        many_a,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )
    creations.add_many_creations(
        "spell-m",
        many_b,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creations.clear_all()

    assert unique_obj.calls == ["dispose"]
    assert many_a.calls == ["dispose"]
    assert many_b.calls == ["dispose"]
    assert creations._creations == {}
    assert creations._disposable_creations == {}


def test_reset_for_pool_aliases_clear_all(creations: Creations) -> None:
    """
    Verify reset_for_pool uses the same reusable clear semantics.
    """
    obj = Probe()
    creations.add_creation(
        "spell-u",
        obj,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creations.reset_for_pool()

    assert obj.calls == ["dispose"]
    assert creations._creations == {}
    assert creations._disposable_creations == {}


def test_cleanup_is_idempotent(creations: Creations) -> None:
    """
    Verify cleanup only disposes tracked entries once.
    """
    obj = Probe()
    creations.add_creation(
        "spell-1",
        obj,
        has_disposal_methods=True,
        disposal_methods=["dispose"],
    )

    creations.cleanup()
    creations.cleanup()

    assert obj.calls == ["dispose"]


def test_cleanup_records_fatal_sequence_error_and_tears_down(
        creations: Creations,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify cleanup still tears down fields when disposal aggregation crashes.
    """

    def boom(self: Creations, registry: dict[str, object]) -> list[Exception]:
        del registry
        raise RuntimeError("boom")

    monkeypatch.setattr(Creations, "_dispose_disposable_registry", boom)

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)
    assert not hasattr(creations, "_creations")
    assert not hasattr(creations, "_owner_conduit_id")


def test_cleanup_raises_exceptiongroup_when_disposal_fails(
        creations: Creations,
) -> None:
    """
    Verify cleanup aggregates disposal failures after best-effort teardown.
    """
    bad_unique = ProbeRaises(method="dispose", exc=ValueError("u"))
    bad_many = ProbeRaises(method="dispose", exc=ValueError("m"))

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

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 2
    assert all(isinstance(exc, RuntimeError) for exc in eg.value.exceptions)


def test_public_methods_fail_after_cleanup(creations: Creations) -> None:
    """
    Verify post-clean access now fails through deleted-field runtime errors.
    """
    creations.cleanup()

    assert not hasattr(creations, "_creations")
    with pytest.raises(AttributeError):
        creations.add_creation("spell-x", object())
    with pytest.raises(AttributeError):
        creations.add_many_creations("spell-x", object())
    with pytest.raises(AttributeError):
        creations.get_creation("spell-x")


def test_attempt_cleanup_missing_method_returns_runtimeerror(
        creations: Creations,
) -> None:
    """
    Verify disposal failures are wrapped when a method cannot be resolved.
    """
    result = creations._attempt_cleanup((object(), ["dispose"]))

    assert isinstance(result, RuntimeError)
    assert "Failed to dispose object" in str(result)


def test_attempt_cleanup_no_methods_returns_none(creations: Creations) -> None:
    """
    Verify empty disposal method lists are treated as no-op.
    """
    probe = Probe()

    assert creations._attempt_cleanup((probe, [])) is None


def test_attempt_cleanup_uses_first_successful_method_only(creations: Creations) -> None:
    """
    Verify disposal stops after the first successful method call.
    """
    probe = Probe()

    assert creations._attempt_cleanup((probe, ["cleanup", "dispose"])) is None
    assert probe.calls == ["cleanup"]
