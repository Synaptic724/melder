"""
Wrapper-mechanics tests for the one-shot singleton specializer.

Purpose:
    Pin `_install_specializing_door` / `build_specialized_no_overrides_executor`
    decline-and-retry contracts from patch lane
    `generalized_singleton_specialization_2026_07_01` that real graphs cannot
    reach deterministically: on a live runtime every post-success capture
    target is live by construction, so the not-yet-live decline, the
    three-attempt pin, and the owner-store-missing decline are only
    observable by driving the wrapper directly with manifest-shaped rows and
    stub spells.

Scope note:
    These are deliberate mechanism tests of internal machinery. The patch's
    Validation Expectations explicitly demand wrapper install/decline/retry
    coverage; the happy-path install/swap is covered on real graphs in
    tests/component/melder/aether/conduit/
    test_conduit_component_singleton_specialization.py and at emitted-factory
    level in test_generalized_emission_contracts.py.
"""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    build_specialized_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator import (
    _install_specializing_door,
)


def _row(
        spell_id: str,
        existence: str,
        deps: Sequence[Tuple[str, Sequence[str]]] = (),
        *,
        callable_spell: bool = True,
        disposal: bool = False,
) -> Dict[str, Any]:
    """
    Build one synthetic manifest step row with the full required field set.
    """
    return {
        "spell_id": spell_id,
        "existence": existence,
        "instance_key": (spell_id, None),
        "dependency_resolution_order": tuple(
            (name, tuple((dep, None) for dep in dep_ids))
            for name, dep_ids in deps
        ),
        "collection_param_names": (),
        "creations_target_kind": 0,
        "use_spell_lock_hint": existence == "unique",
        "has_contract_payload": False,
        "contract_payload_items": (),
        "contract_positional_override": None,
        "uses_positional_override": False,
        "must_register": existence != "many",
        "shared_instance": existence != "many",
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "spell_is_callable": callable_spell,
        "spell_is_existing_creation": False,
        "spell_has_disposal_methods": disposal,
    }


def _stub_spell(
        *,
        door_epoch: int = 1,
        live: Optional[Dict[str, Any]] = None,
        owner_store_missing: bool = False,
) -> SimpleNamespace:
    """
    Build one stub spell exposing exactly the capture-read surface.

    Contract:
        - `_door_epoch` and `_owner_creations._creations` are the only
          attributes the capture pass reads (epoch BEFORE instance).
        - `owner_store_missing=True` models a spell whose owner store is
          unavailable (must decline, never raise).
    """
    owner_creations: Optional[SimpleNamespace] = None
    if not owner_store_missing:
        owner_creations = SimpleNamespace(_creations=dict(live or {}))
    return SimpleNamespace(
        _door_epoch=door_epoch,
        _owner_creations=owner_creations,
    )


def _stub_root_spell() -> SimpleNamespace:
    """
    Build one stub root spell carrying a publishable context slot.
    """
    return SimpleNamespace(
        spell_id="root",
        _creation_context=SimpleNamespace(
            _no_overrides_executor=None,
            _no_overrides_instance_executor=None,
        ),
    )


def _install(
        *,
        rows: Tuple[Dict[str, Any], ...],
        route_key: str,
        plain_door: Any,
        spell_lookup: Dict[str, Any],
        root_spell: SimpleNamespace,
) -> Any:
    """
    Call `_install_specializing_door` with one canonical argument set.

    Note:
        `plain_door` here is the INSTANCE-lane door: the wrapper rides
        `_no_overrides_instance_executor` (the no-hooks meld lanes only
        execute that slot).
    """
    generic_inner_calls: List[Any] = []

    def _generic_inner(meld: Any) -> Any:
        generic_inner_calls.append(meld)
        return ("generic", meld)

    def _plain_hooks_door(caller: Any) -> Any:
        # Tuple-contract hooks twin; only re-published on deopt re-pin.
        return (plain_door(caller), False)

    return _install_specializing_door(
        plain_instance_door=plain_door,
        plain_hooks_door=_plain_hooks_door,
        rows=rows,
        root_instance_key=(rows[-1]["spell_id"], None),
        root_spell_id=rows[-1]["spell_id"],
        spell_lookup=spell_lookup,
        inner_no_overrides_executor=_generic_inner,
        route_key=route_key,
        fast_transient_no_overrides=False,
        root_spell=root_spell,
    )


class TestWrapperInstallRules:
    """
    The wrapper installs only when a specialized body could ever execute.
    """

    def test_zero_capture_returns_plain_door_unchanged(self) -> None:
        """Graphs with no `unique` rows pass the plain door through."""
        def plain_door(caller: Any) -> Any:
            return ("plain", caller)

        rows = (
            _row("m1", "many"),
            _row("root", "many", [("dep", ["m1"])]),
        )
        result = _install(
            rows=rows,
            route_key="many",
            plain_door=plain_door,
            spell_lookup={},
            root_spell=_stub_root_spell(),
        )
        assert result is plain_door

    def test_root_only_capture_on_short_circuit_route_declines(self) -> None:
        """A root-only capture on a non-'many' route is dead code: decline."""
        def plain_door(caller: Any) -> Any:
            return ("plain", caller)

        rows = (
            _row("m1", "many"),
            _row("root", "unique", [("dep", ["m1"])]),
        )
        result = _install(
            rows=rows,
            route_key="unique",
            plain_door=plain_door,
            spell_lookup={},
            root_spell=_stub_root_spell(),
        )
        assert result is plain_door

    def test_capturable_many_route_installs_wrapper(self) -> None:
        """A `unique` dep under a 'many' route yields a wrapper, not the door."""
        def plain_door(caller: Any) -> Any:
            return ("plain", caller)

        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        result = _install(
            rows=rows,
            route_key="many",
            plain_door=plain_door,
            spell_lookup={"u1": _stub_spell()},
            root_spell=_stub_root_spell(),
        )
        assert result is not plain_door
        assert callable(result)


class TestWrapperRetryAndPin:
    """
    Failed attempts decline softly and pin the plain door after three tries.
    """

    def test_dead_capture_target_pins_plain_door_after_three_calls(self) -> None:
        """Not-yet-live capture targets retry twice, then pin the plain door."""
        plain_calls: List[Any] = []

        def plain_door(caller: Any) -> Any:
            plain_calls.append(caller)
            return ("plain", caller)

        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        root_spell = _stub_root_spell()
        # u1 has NO live instance in its owner store: every specialization
        # attempt declines, which is unreachable on a live runtime (post-
        # success all unique targets are live) but must stay soft here.
        wrapper = _install(
            rows=rows,
            route_key="many",
            plain_door=plain_door,
            spell_lookup={"u1": _stub_spell(live={})},
            root_spell=root_spell,
        )
        assert wrapper is not plain_door

        slot = root_spell._creation_context
        assert wrapper("c1") == ("plain", "c1")
        assert slot._no_overrides_instance_executor is None
        assert wrapper("c2") == ("plain", "c2")
        assert slot._no_overrides_instance_executor is None
        assert wrapper("c3") == ("plain", "c3")
        # Third declined attempt pins the plain instance door and publishes
        # it to the INSTANCE slot, so later melds skip the wrapper entirely.
        # The hooks slot is untouched on decline: it already holds the plain
        # hooks door on a live runtime (None in this stub).
        assert slot._no_overrides_instance_executor is plain_door
        assert slot._no_overrides_executor is None
        assert wrapper("c4") == ("plain", "c4")
        assert plain_calls == ["c1", "c2", "c3", "c4"]

    def test_rebuilt_context_sheds_wrapper_after_resolution(self) -> None:
        """A context rebuilt after the pin self-heals on one wrapper call."""
        def plain_door(caller: Any) -> Any:
            return ("plain", caller)

        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        root_spell = _stub_root_spell()
        wrapper = _install(
            rows=rows,
            route_key="many",
            plain_door=plain_door,
            spell_lookup={"u1": _stub_spell(live={})},
            root_spell=root_spell,
        )
        # Drive to the three-attempt pin (resolved = plain instance door).
        for index in range(3):
            assert wrapper(f"c{index}") == ("plain", f"c{index}")
        assert (
            root_spell._creation_context._no_overrides_instance_executor
            is plain_door
        )

        # Model a REBUILT context: hydration re-swaps the container doors,
        # which re-installs the wrapper in the fresh context's instance slot.
        rebuilt_context = SimpleNamespace(
            _no_overrides_executor=None,
            _no_overrides_instance_executor=wrapper,
        )
        root_spell._creation_context = rebuilt_context

        # One call through the wrapper must re-publish the resolved door
        # into the rebuilt context (self-heal) and still return the result.
        assert wrapper("c3") == ("plain", "c3")
        assert rebuilt_context._no_overrides_instance_executor is plain_door
        # Decline-pin resolves never touch the hooks slot.
        assert rebuilt_context._no_overrides_executor is None

    def test_wrapper_never_blocks_the_meld_result_path(self) -> None:
        """Every wrapper call returns the plain door's result unmodified."""
        def plain_door(caller: Any) -> Any:
            return ("plain", caller)

        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        wrapper = _install(
            rows=rows,
            route_key="many",
            plain_door=plain_door,
            spell_lookup={"u1": _stub_spell(owner_store_missing=True)},
            root_spell=_stub_root_spell(),
        )
        for index in range(6):
            assert wrapper(index) == ("plain", index)


class TestBuilderDeclineContract:
    """
    `build_specialized_no_overrides_executor` declines with None, never raises.
    """

    def test_missing_spell_in_lookup_declines(self) -> None:
        """A capture row whose spell is unresolved declines with None."""
        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        assert build_specialized_no_overrides_executor(
            rows=rows,
            root_instance_key=("root", None),
            root_spell_id="root",
            spell_lookup={},
            generic_inner_executor=lambda meld: meld,
        ) is None

    def test_missing_owner_store_declines(self) -> None:
        """A captured spell without an owner store declines with None."""
        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        assert build_specialized_no_overrides_executor(
            rows=rows,
            root_instance_key=("root", None),
            root_spell_id="root",
            spell_lookup={"u1": _stub_spell(owner_store_missing=True)},
            generic_inner_executor=lambda meld: meld,
        ) is None

    def test_not_yet_live_instance_declines(self) -> None:
        """A captured spell with an empty owner store declines with None."""
        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("dep", ["u1"])]),
        )
        assert build_specialized_no_overrides_executor(
            rows=rows,
            root_instance_key=("root", None),
            root_spell_id="root",
            spell_lookup={"u1": _stub_spell(live={})},
            generic_inner_executor=lambda meld: meld,
        ) is None

    def test_all_many_rows_decline(self) -> None:
        """Zero `unique` rows decline before any capture read happens."""
        rows = (
            _row("m1", "many"),
            _row("root", "many", [("dep", ["m1"])]),
        )
        assert build_specialized_no_overrides_executor(
            rows=rows,
            root_instance_key=("root", None),
            root_spell_id="root",
            spell_lookup={},
            generic_inner_executor=lambda meld: meld,
        ) is None
