import traceback
from typing import Any, Dict, List, Optional

import pytest
from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.creations.creations import Creations
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cross_clear_repro() -> None:
    """
    Purpose:
        Ensure this forensic repro starts with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a non-dynamic Spellbook matching the failing component test.
    Contract:
        - Non-dynamic posture (the fast meld lane's only build posture).
        - phase_scheduler_workers_per_spellbook is set to 1 for determinism.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=False,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class _SpaceMarker:
    """
    Purpose:
        unique_per_spell_space marker service for the cross-clear repro.
    Contract:
        - Instances are distinguishable by identity.
        - Carries no disposal methods so spellspace recycle takes the
          lock-free reset lane (the lane under investigation).
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _TracingDict(dict):
    """
    Purpose:
        Inner-storage dict that records a stack trace for every mutation so
        the caller that empties a spellspace store names itself.
    Contract:
        - Behaves exactly like the dict it replaces (subclass, contents
          copied on install) so runtime behavior is unchanged.
        - Records `clear`, `pop`, `popitem`, `__delitem__`, and
          `__setitem__` events into the shared event list with a full
          formatted stack, then delegates to the real dict operation.
        - Never raises from instrumentation.
    """

    def __init__(
            self,
            label: str,
            events: List[Dict[str, Any]],
            initial: Dict[str, Any],
    ) -> None:
        """
        Purpose:
            Build one tracing dict seeded with the store's current contents.
        Args:
            label: Human-readable store label (e.g. "scope_c").
            events: Shared mutation-event sink owned by the test.
            initial: Current inner-dict contents to copy in.
        Returns:
            None.
        """
        super().__init__(initial)
        self._label = label
        self._events = events

    def _record(self, op: str, key: Optional[str]) -> None:
        """
        Purpose:
            Append one mutation event with the caller's formatted stack.
        Args:
            op: Mutation operation name.
            key: Affected key when the operation is key-targeted.
        Returns:
            None.
        """
        self._events.append(
            {
                "store": self._label,
                "op": op,
                "key": key,
                "stack": "".join(traceback.format_stack()[:-2]),
            }
        )

    def clear(self) -> None:
        self._record("clear", None)
        super().clear()

    def pop(self, *args: Any) -> Any:
        self._record("pop", args[0] if args else None)
        return super().pop(*args)

    def popitem(self) -> Any:
        self._record("popitem", None)
        return super().popitem()

    def __delitem__(self, key: Any) -> None:
        self._record("delitem", key)
        super().__delitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._record("setitem", key)
        super().__setitem__(key, value)


def _install_tracer(
        store: Creations,
        label: str,
        events: List[Dict[str, Any]],
) -> _TracingDict:
    """
    Purpose:
        Replace one Creations inner dict with a tracing dict in place.
    Contract:
        - Copies current contents so reads stay identical.
        - Returns the tracer so the test can later detect rebinds
          (clear_all/cleanup paths rebind `_creations` to a fresh dict,
          which bypasses in-place tracing but is caught by identity check).
    Args:
        store: Live Creations wrapper to instrument.
        label: Store label recorded on each event.
        events: Shared mutation-event sink.
    Returns:
        _TracingDict: The installed tracer.
    """
    tracer = _TracingDict(label, events, store._creations)
    store._creations = tracer
    return tracer


def _format_report(
        events: List[Dict[str, Any]],
        scope_c_rebound: bool,
        scope_d_rebound: bool,
) -> str:
    """
    Purpose:
        Render every captured mutation event plus rebind verdicts.
    Args:
        events: Captured mutation events.
        scope_c_rebound: True when scope_c's inner dict was rebound
            (clear_all/cleanup ran against scope_c's wrapper).
        scope_d_rebound: True when scope_d's inner dict was rebound.
    Returns:
        str: Multi-line forensic report.
    """
    lines = [
        "NESTED SPELLSPACE CROSS-CLEAR FORENSICS",
        f"scope_c inner dict rebound (clear_all/cleanup on c): {scope_c_rebound}",
        f"scope_d inner dict rebound (clear_all/cleanup on d): {scope_d_rebound}",
        f"captured mutation events: {len(events)}",
    ]
    for index, event in enumerate(events):
        lines.append(
            f"--- event {index}: store={event['store']} op={event['op']} "
            f"key={event['key']} ---"
        )
        lines.append(event["stack"])
    return "\n".join(lines)


def test_repro_nested_spellspace_cross_clear() -> None:
    """
    Purpose:
        Reproduce the nested-spellspace store cross-clear with forensic
        instrumentation that names the code path mutating scope_c's store.
    Contract:
        - Mirrors the failing component flow: A -> B -> C melds, then a D
          cycle (meld, warm re-meld, exit).
        - scope_c and scope_d inner dicts are tracing dicts during the D
          cycle; every destructive mutation records a full stack.
        - On marker loss, the test fails with the complete forensic report
          (also printed), pinpointing the guilty caller.
        - On no loss, the test passes: the repro then no longer reproduces
          and the component failure needs a wider net.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarker,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    events: List[Dict[str, Any]] = []
    try:
        with conduit.enter_spellspace() as scope_a:
            marker_a = scope_a.meld(spell=marker_id)
            with conduit.enter_spellspace() as scope_b:
                marker_b = scope_b.meld(spell=marker_id)
                assert marker_b is not marker_a
                with conduit.enter_spellspace() as scope_c:
                    marker_c = scope_c.meld(spell=marker_id)
                    assert marker_c is not marker_b
                    # Instrument C before the D cycle: every later mutation
                    # of c's storage is captured with the caller's stack.
                    tracer_c = _install_tracer(scope_c._creations, "scope_c", events)
                    assert tracer_c.get(marker_id) is marker_c
                    with conduit.enter_spellspace() as scope_d:
                        # Instrument D before its first meld so its expected
                        # store/clear traffic is captured for contrast.
                        tracer_d = _install_tracer(
                            scope_d._creations, "scope_d", events
                        )
                        marker_d = scope_d.meld(spell=marker_id)
                        assert marker_d is not marker_c
                        assert scope_d.meld(spell=marker_id) is marker_d
                    # D exited. Forensics on C's storage.
                    scope_c_rebound = scope_c._creations._creations is not tracer_c
                    scope_d_rebound = scope_d._creations._creations is not tracer_d
                    survived = (
                        scope_c._creations.get_creation(marker_id) is marker_c
                    )
                    if not survived:
                        report = _format_report(
                            events, scope_c_rebound, scope_d_rebound
                        )
                        print(report)
                        raise AssertionError(report)
                    assert scope_c.meld(spell=marker_id) is marker_c
                assert scope_b.meld(spell=marker_id) is marker_b
            assert scope_a.meld(spell=marker_id) is marker_a
    finally:
        conduit.permanent_cleanup()
