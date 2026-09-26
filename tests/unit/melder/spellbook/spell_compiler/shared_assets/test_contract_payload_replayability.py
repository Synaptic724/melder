"""
Unit tests for the creation-cache replayability gate (owner option B, 2026-09-26).

The persisted phase-11 step rows carry contract payload values in their frozen form and the
cache-load path hydrates plan steps from those rows, so only values that survive
`freeze_phase11_schema_value` unchanged - `None`, exact `bool`/`int`/`float`/`str`, and tuples
of those - construct identically after a cache hit. `CodegenCreationSchemaHelpers` owns the
predicate; both package builders refuse plans that fail it.
"""

import enum
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation import (
    spell_codegen_creation_cache,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets import (
    manifest_creation_cache,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)


class _Existence(enum.Enum):
    """Plain enum probe: its `repr` is stable but it is not a replayable value."""

    UNIQUE = "unique"


class _Priority(enum.IntEnum):
    """IntEnum probe: passes through freeze as an `int` subclass but cannot be marshalled."""

    HIGH = 1


class _Label(str):
    """`str` subclass probe: same reasoning as `_Priority`."""


class _DefaultReprObject:
    """Instance whose `repr` is `object.__repr__` (freezes to a marker tuple)."""


def _payload_function() -> None:
    """Function probe (freezes to a `__callable__` tuple)."""


def _step(contract_payload: Optional[Dict[str, Any]]) -> SimpleNamespace:
    """Build one plan-step probe carrying a raw contract payload."""
    return SimpleNamespace(contract_payload=contract_payload)


def _lane_plan(*payloads: Optional[Dict[str, Any]]) -> SimpleNamespace:
    """Build one lane-plan probe from per-step payloads."""
    return SimpleNamespace(steps=tuple(_step(payload) for payload in payloads))


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        0,
        -7,
        1.5,
        "",
        "marker",
        (),
        (1, "a", None),
        (("nested", 2), (3.5,)),
    ],
)
def test_replayable_values_are_the_freeze_fixed_points(value: Any) -> None:
    """Every accepted value freezes to itself, so the cache path hands it back unchanged."""
    assert CodegenCreationSchemaHelpers.is_replayable_contract_payload_value(value) is True
    assert CodegenCreationSchemaHelpers.freeze_phase11_schema_value(value) == value


@pytest.mark.parametrize(
    "value",
    [
        [1, 2],
        {"a": 1},
        {1, 2},
        frozenset({1}),
        b"bytes",
        bytearray(b"x"),
        _Existence.UNIQUE,
        _Priority.HIGH,
        _Label("x"),
        _DefaultReprObject,
        _DefaultReprObject(),
        _payload_function,
        len,
        (1, [2]),
        ("ok", {"nested": "dict"}),
    ],
)
def test_non_replayable_values_are_refused(value: Any) -> None:
    """Containers other than tuples, scalar subclasses, enums, classes, callables and objects are refused."""
    assert CodegenCreationSchemaHelpers.is_replayable_contract_payload_value(value) is False


def test_plan_without_payloads_is_replayable() -> None:
    """Steps with no payload, an empty payload or scalar/tuple payloads keep the lane cacheable."""
    plan = _lane_plan(None, {}, {"marker": "override"}, {"__args__": (1, "two", None)})

    assert CodegenCreationSchemaHelpers.plan_contract_payloads_are_replayable(plan) is True
    assert CodegenCreationSchemaHelpers.plan_contract_payloads_are_replayable(_lane_plan()) is True


def test_plan_with_one_non_replayable_value_is_refused() -> None:
    """A single offending value anywhere in the lane refuses the whole lane."""
    plan = _lane_plan({"marker": "override"}, {"hook": _payload_function})
    positional = _lane_plan({"__args__": (1, [2])})

    assert CodegenCreationSchemaHelpers.plan_contract_payloads_are_replayable(plan) is False
    assert CodegenCreationSchemaHelpers.plan_contract_payloads_are_replayable(positional) is False


def test_spell_plan_verdict_covers_both_lanes_and_refuses_a_missing_plan() -> None:
    """No plan means no verdict (refused); a missing lane does not count; either bad lane refuses."""
    good = SimpleNamespace(no_overrides_plan=_lane_plan({"a": 1}), overrides_plan=None)
    bad_overrides = SimpleNamespace(
        no_overrides_plan=_lane_plan({"a": 1}),
        overrides_plan=_lane_plan({"b": _DefaultReprObject()}),
    )
    bad_no_overrides = SimpleNamespace(
        no_overrides_plan=_lane_plan({"a": [1]}),
        overrides_plan=None,
    )

    assert CodegenCreationSchemaHelpers.spell_codegen_plan_is_replayable(None) is False
    assert CodegenCreationSchemaHelpers.spell_codegen_plan_is_replayable(good) is True
    assert CodegenCreationSchemaHelpers.spell_codegen_plan_is_replayable(bad_overrides) is False
    assert CodegenCreationSchemaHelpers.spell_codegen_plan_is_replayable(bad_no_overrides) is False


def _manifest_spell(spell_codegen_plan: Optional[SimpleNamespace]) -> SimpleNamespace:
    """Build a manifest-first spell probe whose artifact carries a manifest and the given plan."""
    manifest = {"family_id": "generalized_codegen_creation", "no_overrides": {}}
    return SimpleNamespace(
        spell_id="spell-1",
        _compiler_artifact=SimpleNamespace(
            _spell_codegen_creation=SimpleNamespace(
                metadata={manifest_creation_cache.MANIFEST_METADATA_KEY: manifest},
            ),
            _spell_codegen_plan=spell_codegen_plan,
            _spell_codegen_model=SimpleNamespace(),
        ),
    )


def test_manifest_package_is_built_for_a_replayable_plan() -> None:
    """A replayable plan is exported as the family manifest envelope, unchanged."""
    plan = SimpleNamespace(no_overrides_plan=_lane_plan({"marker": "override"}), overrides_plan=None)

    package = manifest_creation_cache.build_package(_manifest_spell(plan))

    assert package is not None
    assert package["family_id"] == "generalized_codegen_creation"
    assert package["spell_id"] == "spell-1"
    assert package["package_version"] == manifest_creation_cache.PACKAGE_VERSION
    assert manifest_creation_cache.is_manifest_package(package) is True


@pytest.mark.parametrize(
    "spell_codegen_plan",
    [
        None,
        SimpleNamespace(no_overrides_plan=_lane_plan({"marker": _DefaultReprObject()}), overrides_plan=None),
        SimpleNamespace(no_overrides_plan=_lane_plan({"a": 1}), overrides_plan=_lane_plan({"b": [1]})),
    ],
)
def test_manifest_package_is_refused_for_a_non_replayable_or_missing_plan(
        spell_codegen_plan: Optional[SimpleNamespace],
) -> None:
    """The envelope builder returns None instead of a package that would hydrate wrong values."""
    assert manifest_creation_cache.build_package(_manifest_spell(spell_codegen_plan)) is None


def test_manifest_package_still_raises_without_phase11_output() -> None:
    """The gate does not soften the existing hard failures for missing phase-11 output."""
    with pytest.raises(RuntimeError, match="compiler artifact"):
        manifest_creation_cache.build_package(SimpleNamespace(spell_id="x", _compiler_artifact=None))


def test_legacy_package_is_refused_before_any_subpackage_is_built(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The both-lane builder refuses a non-replayable plan after the phase-11 presence checks and
    before it touches the subpackage builders, so no executor source is compiled for it.
    """
    calls: List[str] = []

    def _forbidden(**kwargs: Any) -> Dict[str, Any]:
        """Record an unexpected subpackage build."""
        calls.append("built")
        return {}

    monkeypatch.setattr(
        spell_codegen_creation_cache, "_build_no_overrides_subpackage", _forbidden, raising=True,
    )
    monkeypatch.setattr(
        spell_codegen_creation_cache, "_build_overrides_subpackage", _forbidden, raising=True,
    )
    spell = SimpleNamespace(
        spell_id="spell-1",
        _compiler_artifact=SimpleNamespace(
            _spell_codegen_creation=SimpleNamespace(metadata={}),
            _spell_codegen_plan=SimpleNamespace(
                no_overrides_plan=_lane_plan({"marker": _payload_function}),
                overrides_plan=None,
            ),
            _spell_codegen_model=SimpleNamespace(),
        ),
    )

    assert spell_codegen_creation_cache.build_package(spell) is None
    assert calls == []


def test_legacy_package_builds_subpackages_for_a_replayable_plan(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A replayable plan reaches both subpackage builders and is wrapped in the versioned envelope."""
    seen: List[Tuple[str, Any]] = []

    def _no_overrides(*, no_overrides_plan: Any) -> Dict[str, Any]:
        """Record the no-overrides subpackage build."""
        seen.append(("no_overrides", no_overrides_plan))
        return {"lane": "no_overrides"}

    def _overrides(*, spell_codegen_plan: Any, spell_codegen_model: Any) -> Optional[Dict[str, Any]]:
        """Record the overrides subpackage build."""
        seen.append(("overrides", spell_codegen_plan))
        return None

    monkeypatch.setattr(
        spell_codegen_creation_cache, "_build_no_overrides_subpackage", _no_overrides, raising=True,
    )
    monkeypatch.setattr(
        spell_codegen_creation_cache, "_build_overrides_subpackage", _overrides, raising=True,
    )
    plan = SimpleNamespace(no_overrides_plan=_lane_plan({"marker": "override"}), overrides_plan=None)
    spell = SimpleNamespace(
        spell_id="spell-1",
        _compiler_artifact=SimpleNamespace(
            _spell_codegen_creation=SimpleNamespace(metadata={}),
            _spell_codegen_plan=plan,
            _spell_codegen_model=SimpleNamespace(),
        ),
    )

    package = spell_codegen_creation_cache.build_package(spell)

    assert package is not None
    assert package["spell_id"] == "spell-1"
    assert package["no_overrides"] == {"lane": "no_overrides"}
    assert package["overrides"] is None
    assert [label for label, _plan in seen] == ["no_overrides", "overrides"]
