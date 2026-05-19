from types import SimpleNamespace

import pytest

from melder.nexus.rift.rift_space.workstation import Workstation


def test_workstation_rejects_empty_owner_and_exposes_ids() -> None:
    with pytest.raises(ValueError, match="owner_space_id cannot be empty."):
        Workstation("")

    workstation = Workstation("space-1")

    assert isinstance(workstation.workstation_id, str)
    assert workstation.owner_space_id == "space-1"


def test_workstation_target_and_cleanup_guardrails_work() -> None:
    workstation = Workstation("space-1")

    with pytest.raises(ValueError, match="Workstation has no active target."):
        workstation.get_target()

    workstation.bind_object("thing", object())
    workstation.set_target("thing", store="objects")

    with pytest.raises(ValueError, match="cleanup method names cannot be empty."):
        workstation.cleanup_target("")

    workstation._strong_objects_by_name["thing"] = SimpleNamespace(cleanup="bad")
    with pytest.raises(RuntimeError, match="is not callable"):
        workstation.cleanup_target("cleanup")

    workstation._strong_objects_by_name["thing"] = object()
    with pytest.raises(ValueError, match="No cleanup method was found on the active target."):
        workstation.cleanup_target()

    workstation._strong_objects_by_name["thing"] = object()
    workstation.set_target("thing", store="objects")
    with pytest.raises(RuntimeError, match="Active target is not callable."):
        workstation.call_target()


def test_workstation_success_paths_for_get_release_describe_and_call_target() -> None:
    workstation = Workstation("space-1")

    class _Target:
        def __init__(self) -> None:
            self.cleaned = False

        def cleanup(self) -> None:
            self.cleaned = True

    target = _Target()
    workstation.bind_object("target", target)
    workstation.bind_method("callable", lambda value: value + 1)
    workstation.set_target("callable", store="methods")

    assert workstation.get("target", store="objects") is target
    assert workstation.describe_bindings()["objects"] == ["target"]
    assert workstation.describe_bindings()["methods"] == ["callable"]
    assert workstation.describe_bindings()["target_name"] == ["callable"]

    result = workstation.call_target(2, bind_as_name="result", bind_as_store="attributes")
    assert result == 3
    assert workstation.get("result", store="attributes") == 3

    workstation.bind_object("target", target)
    workstation.set_target("target", store="objects")
    workstation.cleanup_target()
    assert target.cleaned is True

    workstation.bind_object("another", object())
    released = workstation.release("another", store="objects")
    assert released is not None

    workstation.bind_object("selected", object())
    workstation.set_target("selected", store="objects")
    workstation.release("selected", store="objects")
    assert workstation.describe_bindings()["target_name"] == []

    workstation.clear_target()
    assert workstation.describe_bindings()["target_name"] == []


def test_workstation_binding_resolution_and_store_guardrails_work() -> None:
    class _Weakable:
        pass

    workstation = Workstation("space-1")

    with pytest.raises(ValueError, match="binding name cannot be empty."):
        workstation._bind("objects", "", object(), weak_ref=False)

    with pytest.raises(ValueError, match="binding name cannot be empty."):
        workstation._resolve_binding("", store=None)

    with pytest.raises(ValueError, match="Binding 'missing' was not found."):
        workstation._resolve_binding("missing", store=None)

    workstation.bind_object("shared", object())
    workstation.bind_attribute("shared", object())
    with pytest.raises(ValueError, match="Binding 'shared' is ambiguous across workstation stores."):
        workstation._resolve_binding("shared", store=None)

    workstation = Workstation("space-1")
    workstation.bind_object("shared", object())
    weak_value = _Weakable()
    workstation._weak_objects_by_name["shared"] = weak_value
    with pytest.raises(ValueError, match="Binding 'shared' is ambiguous inside 'objects'."):
        workstation._resolve_binding_in_store("objects", "shared")

    with pytest.raises(ValueError, match="Unsupported workstation store 'bad'."):
        workstation._get_store_maps("bad")
    workstation.bind_object("only", object())
    assert workstation._resolve_binding("only", store=None)[0] == "objects"


def test_workstation_weak_binding_and_internal_helpers_work(monkeypatch) -> None:
    class _Weakable:
        pass

    class _WeakStore:
        def __init__(self) -> None:
            self._dict = {}
            self._keys = []
            self.popped = []

        def prune(self) -> None:
            return None

        def __contains__(self, key) -> bool:
            return key in self._keys

        def pop(self, key):
            self.popped.append(key)
            raise RuntimeError("boom")

        def keys(self):
            return list(self._keys)

    workstation = Workstation("space-1")
    callback_calls = []
    monkeypatch_target = _Weakable()

    monkeypatch.setattr(
        Workstation,
        "_register_weak_binding_callback",
        lambda self, store, name, weak_store_map: callback_calls.append((store, name)),
    )
    workstation._bind("objects", "weak_target", monkeypatch_target, weak_ref=True)
    assert callback_calls == [("objects", "weak_target")]

    weak_store = _WeakStore()
    weak_store._keys = ["ghost"]
    monkeypatch.setattr(
        Workstation,
        "_get_store_maps",
        lambda self, store: ({}, weak_store),
    )
    workstation._clear_binding_name_from_store("objects", "ghost")
    assert weak_store.popped == ["ghost"]

    strong_store = {"x": 1}
    weak_pop_calls = []
    monkeypatch.setattr(
        Workstation,
        "_get_store_maps",
        lambda self, store: (
            strong_store,
            SimpleNamespace(pop=lambda name: weak_pop_calls.append(name)),
        ),
    )
    workstation._remove_resolved_binding("objects", "x", False)
    assert strong_store == {}
    workstation._remove_resolved_binding("objects", "y", True)
    assert weak_pop_calls == ["y"]

    workstation._strong_objects_by_name = {"b": object()}
    workstation._strong_attributes_by_name = {"a": object()}
    workstation._strong_methods_by_name = {}
    workstation._weak_objects_by_name = SimpleNamespace(keys=lambda: ["c"])
    workstation._weak_attributes_by_name = SimpleNamespace(keys=lambda: [])
    workstation._weak_methods_by_name = SimpleNamespace(keys=lambda: ["m"])
    monkeypatch.setattr(
        Workstation,
        "_get_store_maps",
        lambda self, store: (
            self._strong_objects_by_name if store == "objects" else (
                self._strong_attributes_by_name if store == "attributes" else self._strong_methods_by_name
            ),
            self._weak_objects_by_name if store == "objects" else (
                self._weak_attributes_by_name if store == "attributes" else self._weak_methods_by_name
            ),
        ),
    )
    assert workstation._describe_store_names("objects") == ["b", "c"]
    assert workstation._describe_store_names("methods") == ["m"]


def test_workstation_cleanup_and_node_none_callback_paths_work(monkeypatch) -> None:
    workstation = Workstation("space-1")
    workstation.bind_object("item", object())
    workstation.bind_attribute("value", 1)
    workstation.bind_method("fn", lambda: None)

    weak_store = SimpleNamespace(_dict={})
    workstation._register_weak_binding_callback("objects", "missing", weak_store)
    workstation._event_publisher = lambda payload: None
    workstation._register_weak_binding_callback("objects", "still_missing", weak_store)

    workstation.cleanup()
    workstation.cleanup()

    assert workstation.cleaned is True
    assert not hasattr(workstation, '_strong_objects_by_name')
    assert not hasattr(workstation, '_strong_attributes_by_name')
    assert not hasattr(workstation, '_strong_methods_by_name')
    assert not hasattr(workstation, '_weak_objects_by_name')
    assert not hasattr(workstation, '_weak_attributes_by_name')
    assert not hasattr(workstation, '_weak_methods_by_name')
    assert not hasattr(workstation, '_event_publisher')
    assert not hasattr(workstation, '_target_name')
    assert not hasattr(workstation, '_target_store')
    assert not hasattr(workstation, '_owner_space_id')
    assert not hasattr(workstation, '_id')


def test_workstation_internal_helpers_cover_weak_binding_callbacks() -> None:
    published = []
    workstation = Workstation("space-1", event_publisher=lambda payload: published.append(payload))

    class _Node:
        def __init__(self) -> None:
            self.callbacks = []
            self.has_fired = True

        def add_callback(self, callback) -> None:
            self.callbacks.append(callback)

    node = _Node()
    weak_store = SimpleNamespace(_dict={"thing": node}, prune=lambda: None, __contains__=lambda self, key: False)

    workstation._register_weak_binding_callback("objects", "thing", weak_store)
    assert len(node.callbacks) == 1

    node.callbacks[0](node)
    assert published[0]["binding_name"] == "thing"

    workstation._event_publisher = None
    workstation._register_weak_binding_callback("objects", "thing", weak_store)
    workstation._publish_weak_binding_event("objects", "thing", node)

    workstation._event_publisher = lambda payload: (_ for _ in ()).throw(RuntimeError("boom"))
    workstation._publish_weak_binding_event("objects", "thing", node)

    node.has_fired = False
    workstation._event_publisher = lambda payload: published.append(payload)
    workstation._publish_weak_binding_event("objects", "thing", node)


def test_workstation_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, workstation: Workstation) -> None:
            self._workstation = workstation

        def __enter__(self):
            self._workstation._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    workstation = Workstation("space-1")
    original_lock = workstation._lock
    workstation._lock = _FlipCleanedOnEnter(workstation)
    try:
        workstation.cleanup()
    finally:
        workstation._lock = original_lock

    assert workstation.cleaned is True
