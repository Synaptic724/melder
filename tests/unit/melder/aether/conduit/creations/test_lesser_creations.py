# tests/aether/conduit/creations/test_lesser_creations.py

import threading
from typing import Any, List, Optional

import pytest

from melder.aether.conduit.creations.creation import Creation
from melder.aether.conduit.creations.lesser_creations import LesserCreations


class _DummyLogger:
    """Minimal logger shim used by unit tests.

    LesserCreations calls logger.debug/error with a `message` plus various keyword args.
    This shim records calls and never raises.
    """

    def __init__(self) -> None:
        self.debug_calls: List[tuple[str, dict]] = []
        self.error_calls: List[tuple[str, dict]] = []

    def debug(self, message: str, **kwargs: Any) -> None:
        self.debug_calls.append((message, kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self.error_calls.append((message, kwargs))


class _ConduitStateStub:
    """ConduitState stand-in.

    LesserCreations currently validates state via `conduit._conduit_state.__str__() == "lesser"`.
    """

    def __init__(self, state_name: str) -> None:
        self._state_name = state_name

    def __str__(self) -> str:
        return self._state_name


class _ConduitStub:
    """Minimal conduit stub satisfying LesserCreations' attribute contract."""

    def __init__(self, *, conduit_id: str, logger: _DummyLogger, state: Optional[_ConduitStateStub]) -> None:
        self._id = conduit_id
        self._logger = logger
        self._conduit_state = state


class _RecordingItem:
    """Disposable test object that records disposal calls and can be configured to raise."""

    def __init__(self, calls: List[str], name: str, *, raises: bool = False) -> None:
        self._calls = calls
        self._name = name
        self._raises = raises

    def cleanup(self) -> None:
        self._calls.append(f"{self._name}.cleanup")
        if self._raises:
            raise ValueError(f"{self._name} boom")

    def close(self) -> None:
        self._calls.append(f"{self._name}.close")
        if self._raises:
            raise ValueError(f"{self._name} boom")

    def dispose(self) -> None:
        self._calls.append(f"{self._name}.dispose")
        if self._raises:
            raise ValueError(f"{self._name} boom")


class _NonCallableAttrItem:
    """Has a non-callable attribute matching a disposal method name."""

    cleanup = "not callable"


@pytest.fixture
def make_lesser_creations():
    """Factory fixture returning (LesserCreations, logger)."""

    def _make(
            *,
            disposal_enabled: bool = True,
            disposal_method_names: Optional[List[str]] = None,
            conduit_state: Optional[_ConduitStateStub] = None,
    ) -> tuple[LesserCreations, _DummyLogger]:
        logger = _DummyLogger()
        state = conduit_state if conduit_state is not None else _ConduitStateStub("lesser")
        conduit = _ConduitStub(conduit_id="c-1", logger=logger, state=state)
        creations = LesserCreations(
            disposal_enabled=disposal_enabled,
            disposal_method_names=disposal_method_names,
            conduit=conduit,
            parent_creations=None,
        )
        return creations, logger

    return _make


# -----------------
# Initialization
# -----------------

def test_init_raises_when_conduit_state_is_none():
    logger = _DummyLogger()
    conduit = _ConduitStub(conduit_id="c-1", logger=logger, state=None)
    with pytest.raises(RuntimeError, match="no state"):
        LesserCreations(disposal_enabled=True, disposal_method_names=["cleanup"], conduit=conduit, parent_creations=None)


def test_init_raises_when_conduit_state_is_not_lesser():
    logger = _DummyLogger()
    conduit = _ConduitStub(conduit_id="c-1", logger=logger, state=_ConduitStateStub("normal"))
    with pytest.raises(RuntimeError, match="LesserCreations can only be initialized"):
        LesserCreations(disposal_enabled=True, disposal_method_names=["cleanup"], conduit=conduit, parent_creations=None)


def test_init_accepts_lesser_conduit_state_str(make_lesser_creations):
    creations, _ = make_lesser_creations()
    # Public signal: can operate without raising.
    creations.add_unique_per_scope("spell-1", object())


def test_init_defaults_disposal_methods_to_empty_list_when_none(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=None)
    calls: List[str] = []
    creations.add_unique_per_scope("spell-1", _RecordingItem(calls, "x"))
    creations.cleanup()
    # No disposal methods configured => should not call item's cleanup.
    assert calls == []


# -----------------
# Disposal helper (_attempt_cleanup)
# -----------------

def test_attempt_cleanup_returns_none_when_item_none(make_lesser_creations):
    creations, _ = make_lesser_creations()
    assert creations._attempt_cleanup(None) is None


def test_attempt_cleanup_skips_when_disposal_disabled(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_enabled=False, disposal_method_names=["cleanup"])
    calls: List[str] = []
    item = _RecordingItem(calls, "x")
    assert creations._attempt_cleanup(item) is None
    assert calls == []


def test_attempt_cleanup_returns_none_when_no_method_matches(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])

    class _NoMethods:
        pass

    assert creations._attempt_cleanup(_NoMethods()) is None


def test_attempt_cleanup_calls_first_matching_method_in_order(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["close", "cleanup"])
    calls: List[str] = []
    item = _RecordingItem(calls, "x")
    creations._attempt_cleanup(item)
    assert calls == ["x.close"]


def test_attempt_cleanup_skips_noncallable_attribute(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup", "close"])
    calls: List[str] = []

    item = _NonCallableAttrItem()
    # Provide a callable close so the second option works.
    setattr(item, "close", _RecordingItem(calls, "x").close)

    creations._attempt_cleanup(item)
    assert calls == ["x.close"]


def test_attempt_cleanup_wraps_exception_in_runtimeerror(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []
    item = _RecordingItem(calls, "x", raises=True)

    err = creations._attempt_cleanup(item)

    assert isinstance(err, RuntimeError)
    assert "cleanup" in str(err)
    assert calls == ["x.cleanup"]


# -----------------
# Unique-per-scope
# -----------------

def test_add_unique_per_scope_stores_and_cleanup_calls_disposal(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_unique_per_scope("spell-1", _RecordingItem(calls, "a"))
    creations.cleanup()

    assert calls == ["a.cleanup"]


def test_add_unique_per_scope_duplicate_key_raises_valueerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.add_unique_per_scope("spell-1", object())

    with pytest.raises(ValueError, match="already exists"):
        creations.add_unique_per_scope("spell-1", object())


def test_add_unique_per_scope_after_cleanup_raises_runtimeerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_unique_per_scope("spell-1", object())


def test_unique_per_scope_cleanup_calls_disposal_once_per_item(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_unique_per_scope("spell-1", _RecordingItem(calls, "a"))
    creations.cleanup()

    assert calls.count("a.cleanup") == 1


def test_cleanup_disposes_unique_per_scope_multiple_items(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_unique_per_scope("spell-1", _RecordingItem(calls, "a"))
    creations.add_unique_per_scope("spell-2", _RecordingItem(calls, "b"))
    creations.cleanup()

    assert sorted(calls) == ["a.cleanup", "b.cleanup"]


def test_cleanup_collects_errors_from_unique_per_scope_disposal_failures(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.add_unique_per_scope("spell-1", _RecordingItem([], "a", raises=True))

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)


def test_cleanup_continues_after_unique_per_scope_error(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_unique_per_scope("spell-1", _RecordingItem(calls, "a", raises=True))
    creations.add_unique_per_scope("spell-2", _RecordingItem(calls, "b"))

    with pytest.raises(ExceptionGroup):
        creations.cleanup()

    assert "b.cleanup" in calls


def test_cleanup_nulls_wrapped_creation_value_for_unique_per_scope(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.add_unique_per_scope("spell-1", object())

    # No public accessor exists; validate lifecycle safety by holding the wrapper reference.
    wrapper: Creation = creations._unique_per_scope["spell-1"]

    creations.cleanup()

    assert wrapper.value is None


# -----------------
# Many
# -----------------

def test_add_many_disposes_on_cleanup_single_item(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_many("spell-1", _RecordingItem(calls, "a"))
    creations.cleanup()

    assert calls == ["a.cleanup"]


def test_add_many_multiple_items_same_key_disposed_all(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_many("spell-1", _RecordingItem(calls, "a"))
    creations.add_many("spell-1", _RecordingItem(calls, "b"))
    creations.cleanup()

    assert sorted(calls) == ["a.cleanup", "b.cleanup"]


def test_add_many_multiple_keys_disposed_all(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_many("spell-1", _RecordingItem(calls, "a"))
    creations.add_many("spell-2", _RecordingItem(calls, "b"))
    creations.cleanup()

    assert sorted(calls) == ["a.cleanup", "b.cleanup"]


def test_add_many_after_cleanup_raises_runtimeerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_many("spell-1", object())


def test_add_many_disposal_disabled_does_not_call_underlying_methods(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_enabled=False, disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_many("spell-1", _RecordingItem(calls, "a"))
    creations.cleanup()

    assert calls == []


def test_add_many_cleanup_collects_errors_for_raising_item(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.add_many("spell-1", _RecordingItem([], "a", raises=True))

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 1


def test_add_many_cleanup_disposes_other_items_even_if_one_raises(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_many("spell-1", _RecordingItem(calls, "a", raises=True))
    creations.add_many("spell-1", _RecordingItem(calls, "b"))

    with pytest.raises(ExceptionGroup):
        creations.cleanup()

    assert "b.cleanup" in calls


def test_cleanup_nulls_wrapped_creation_value_for_many(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.add_many("spell-1", object())

    # No public accessor exists; validate lifecycle safety by holding the wrapper reference.
    wrapper: Creation = creations._many["spell-1"][0]

    creations.cleanup()

    assert wrapper.value is None


# -----------------
# Spellspace creations
# -----------------

def test_get_spellspace_creation_returns_none_when_spellspace_missing(make_lesser_creations):
    creations, _ = make_lesser_creations()
    assert creations.get_spellspace_creation("ss-1", "spell-1") is None


def test_get_spellspace_creation_returns_none_when_spell_missing(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())
    assert creations.get_spellspace_creation("ss-1", "spell-2") is None


def test_register_spellspace_creation_adds_and_get_returns_creation_value(make_lesser_creations):
    creations, _ = make_lesser_creations()
    item = object()

    creations.register_spellspace_creation("ss-1", "spell-1", item)
    creation = creations.get_spellspace_creation("ss-1", "spell-1")

    assert creation is not None
    assert creation.value is item


def test_register_spellspace_creation_duplicate_spell_id_raises_valueerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())

    with pytest.raises(ValueError, match="already exists"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_register_spellspace_creation_creates_new_bucket_when_missing(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())
    creations.register_spellspace_creation("ss-2", "spell-1", object())

    assert creations.get_spellspace_creation("ss-1", "spell-1") is not None
    assert creations.get_spellspace_creation("ss-2", "spell-1") is not None


def test_register_spellspace_creation_after_cleanup_raises_runtimeerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.register_spellspace_creation("ss-1", "spell-1", object())


def test_clear_spellspace_instances_noop_when_spellspace_missing(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.clear_spellspace_instances("missing")


def test_clear_spellspace_instances_removes_bucket_and_future_get_returns_none(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())

    creations.clear_spellspace_instances("ss-1")

    assert creations.get_spellspace_creation("ss-1", "spell-1") is None


def test_clear_spellspace_instances_preserves_other_buckets(make_lesser_creations):
    """
    Purpose:
        Ensure clearing one spellspace bucket leaves others intact.
    Contract:
        - The targeted bucket is removed.
        - Other buckets remain accessible.
    Returns:
        None.
    Raises:
        AssertionError: If unrelated buckets are cleared.
    """
    creations, _ = make_lesser_creations()
    obj_a = object()
    obj_b = object()

    creations.register_spellspace_creation("ss-1", "spell-a", obj_a)
    creations.register_spellspace_creation("ss-2", "spell-b", obj_b)

    creations.clear_spellspace_instances("ss-1")

    assert creations.get_spellspace_creation("ss-1", "spell-a") is None
    preserved = creations.get_spellspace_creation("ss-2", "spell-b")
    assert preserved is not None
    assert preserved.value is obj_b


def test_clear_spellspace_instances_calls_disposal_on_all_spells_in_bucket(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.register_spellspace_creation("ss-1", "spell-1", _RecordingItem(calls, "a"))
    creations.register_spellspace_creation("ss-1", "spell-2", _RecordingItem(calls, "b"))

    creations.clear_spellspace_instances("ss-1")

    assert sorted(calls) == ["a.cleanup", "b.cleanup"]


def test_clear_spellspace_instances_calls_creation_cleanup_value_becomes_none(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    item = object()

    creations.register_spellspace_creation("ss-1", "spell-1", item)
    creation = creations.get_spellspace_creation("ss-1", "spell-1")

    assert creation is not None

    creations.clear_spellspace_instances("ss-1")

    assert creation.value is None


def test_clear_spellspace_instances_disposal_disabled_skips_underlying_disposal(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_enabled=False, disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.register_spellspace_creation("ss-1", "spell-1", _RecordingItem(calls, "a"))
    creations.clear_spellspace_instances("ss-1")

    assert calls == []


def test_clear_spellspace_instances_raises_exceptiongroup_when_any_disposal_fails(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.register_spellspace_creation("ss-1", "spell-1", _RecordingItem([], "a", raises=True))

    with pytest.raises(ExceptionGroup) as eg:
        creations.clear_spellspace_instances("ss-1")

    assert len(eg.value.exceptions) == 1
    assert isinstance(eg.value.exceptions[0], RuntimeError)


def test_clear_spellspace_instances_exceptiongroup_contains_all_errors(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.register_spellspace_creation("ss-1", "spell-1", _RecordingItem([], "a", raises=True))
    creations.register_spellspace_creation("ss-1", "spell-2", _RecordingItem([], "b", raises=True))

    with pytest.raises(ExceptionGroup) as eg:
        creations.clear_spellspace_instances("ss-1")

    assert len(eg.value.exceptions) == 2


def test_clear_spellspace_instances_deletes_bucket_even_when_errors(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    creations.register_spellspace_creation("ss-1", "spell-1", _RecordingItem([], "a", raises=True))

    with pytest.raises(ExceptionGroup):
        creations.clear_spellspace_instances("ss-1")

    assert creations.get_spellspace_creation("ss-1", "spell-1") is None


def test_clear_spellspace_instances_after_cleanup_raises_runtimeerror(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.clear_spellspace_instances("ss-1")


def test_get_spellspace_creation_returns_same_object_instance(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())

    c1 = creations.get_spellspace_creation("ss-1", "spell-1")
    c2 = creations.get_spellspace_creation("ss-1", "spell-1")

    assert c1 is c2


def test_register_spellspace_creation_allows_reuse_after_clear(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.register_spellspace_creation("ss-1", "spell-1", object())

    creations.clear_spellspace_instances("ss-1")

    creations.register_spellspace_creation("ss-1", "spell-1", object())

    assert creations.get_spellspace_creation("ss-1", "spell-1") is not None


def test_get_spellspace_creation_after_cleanup_raises_runtimeerror(make_lesser_creations):
    """Verify get_spellspace_creation rejects access after cleanup."""
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.get_spellspace_creation("ss-1", "spell-1")


# -----------------
# Cleanup behavior
# -----------------

def test_cleanup_idempotent_no_objects(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()
    creations.cleanup()


def test_cleanup_marks_cleaned_and_blocks_adds(make_lesser_creations):
    creations, _ = make_lesser_creations()
    creations.cleanup()

    with pytest.raises(RuntimeError):
        creations.add_unique_per_scope("spell-1", object())

    with pytest.raises(RuntimeError):
        creations.add_many("spell-1", object())


def test_cleanup_nulls_internal_refs_and_logger_fields(make_lesser_creations):
    """
    Purpose:
        Validate cleanup nulls internal references for lifecycle safety.
    Contract:
        - Managed collections are nulled after cleanup.
        - Logger and log metadata are nulled after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If references remain after cleanup.
    """
    creations, _ = make_lesser_creations()

    creations.cleanup()

    assert creations._unique_per_scope is None
    assert creations._many is None
    assert creations._spellspace_instances is None
    assert creations._conduit is None
    assert creations._parent_creations is None
    assert creations._disposal_method_names is None
    assert creations._logger is None
    assert creations._log_groups is None
    assert creations._log_sysgroups is None


def test_cleanup_disposes_across_scopes_unique_many_spellspace(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []

    creations.add_unique_per_scope("u1", _RecordingItem(calls, "u1"))
    creations.add_many("m1", _RecordingItem(calls, "m1a"))
    creations.add_many("m1", _RecordingItem(calls, "m1b"))
    creations.register_spellspace_creation("ss-1", "s1", _RecordingItem(calls, "ss1"))

    creations.cleanup()

    assert sorted(calls) == ["m1a.cleanup", "m1b.cleanup", "ss1.cleanup", "u1.cleanup"]


def test_cleanup_raises_exceptiongroup_for_multiple_failures_across_scopes(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])

    creations.add_unique_per_scope("u1", _RecordingItem([], "u1", raises=True))
    creations.add_many("m1", _RecordingItem([], "m1", raises=True))
    creations.register_spellspace_creation("ss-1", "s1", _RecordingItem([], "s1", raises=True))

    with pytest.raises(ExceptionGroup) as eg:
        creations.cleanup()

    assert len(eg.value.exceptions) == 3


def test_cleanup_when_exceptiongroup_still_marks_cleaned(make_lesser_creations):
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])

    creations.add_unique_per_scope("u1", _RecordingItem([], "u1", raises=True))

    with pytest.raises(ExceptionGroup):
        creations.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_many("m1", object())


def test_cleanup_is_thread_safe_for_concurrent_calls(make_lesser_creations):
    creations, _ = make_lesser_creations()
    exceptions: List[BaseException] = []

    def _worker() -> None:
        try:
            creations.cleanup()
        except BaseException as exc:
            exceptions.append(exc)

    t1 = threading.Thread(target=_worker)
    t2 = threading.Thread(target=_worker)

    t1.start()
    t2.start()

    t1.join(timeout=2)
    t2.join(timeout=2)

    assert not exceptions


# -----------------
# transfer_data_and_clear
# -----------------


def test_transfer_data_and_clear_should_return_snapshot_and_clean_when_fixed(make_lesser_creations):
    """Verify transfer_data_and_clear returns snapshot data and cleans the manager."""
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    obj_u = object()
    obj_m = object()

    creations.add_unique_per_scope("u1", obj_u)
    creations.add_many("m1", obj_m)

    data = creations.transfer_data_and_clear()

    assert set(data.keys()) == {"unique_per_scope", "many"}

    u = data["unique_per_scope"]
    m = data["many"]

    assert "u1" in u
    assert isinstance(u["u1"], Creation)
    assert u["u1"].value is obj_u

    assert "m1" in m
    assert len(m["m1"]) == 1
    assert isinstance(m["m1"][0], Creation)
    assert m["m1"][0].value is obj_m

    with pytest.raises(RuntimeError, match="already been cleaned"):
        creations.add_unique_per_scope("u2", object())


def test_transfer_data_and_clear_skips_disposal_for_transferred_entries(make_lesser_creations):
    """
    Purpose:
        Verify transfer_data_and_clear skips disposal for transferred entries.
    Contract:
        - No disposal calls occur for transferred objects.
        - The manager is marked cleaned after transfer.
    Returns:
        None.
    Raises:
        AssertionError: If disposal is invoked or the manager remains active.
    """
    creations, _ = make_lesser_creations(disposal_method_names=["cleanup"])
    calls: List[str] = []
    item = _RecordingItem(calls, "u1", raises=True)
    creations.add_unique_per_scope("u1", item)

    data = creations.transfer_data_and_clear()

    assert calls == []
    assert data["unique_per_scope"]["u1"].value is item
    assert creations.cleaned is True
    assert creations._unique_per_scope is None
    assert creations._many is None
