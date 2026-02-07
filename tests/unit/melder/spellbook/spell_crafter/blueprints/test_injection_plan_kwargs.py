"""Unit tests for Phase 9 kwargs assembly helpers."""
from typing import Any, Dict

import pytest

from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionSpec,
    ParamSource,
    build_kwargs_from_injection_spec,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def _make_spec(
    *,
    param_sources: Dict[str, ParamSource],
    contract_payload: Dict[str, Any] | None = None,
    uses_positional_override: bool = False,
) -> InjectionSpec:
    """
    Build a minimal InjectionSpec for tests.
    """
    if contract_payload is None:
        contract_payload = {}
    return InjectionSpec(
        param_sources=param_sources,
        allow_list_aggregation=False,
        uses_positional_override=uses_positional_override,
        contract_payload=contract_payload,
    )


def test_build_kwargs_from_injection_spec_single_dependency() -> None:
    """
    Purpose:
        Validate dependency resolution for a single key.
    Contract:
        - Dependency instance is injected as the param value.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])}
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={},
    )

    assert kwargs["dep"] == "value"


def test_build_kwargs_from_injection_spec_multiple_dependencies() -> None:
    """
    Purpose:
        Validate list aggregation when multiple dependencies exist.
    Contract:
        - Multiple dependency values are injected as a list.
    """
    instance_results = {("a", None): "a", ("b", None): "b"}
    spec = _make_spec(
        param_sources={"deps": ParamSource(kind="dependency", dependency_keys=[("a", None), ("b", None)])}
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={},
    )

    assert kwargs["deps"] == ["a", "b"]


def test_build_kwargs_from_injection_spec_missing_dependency_raises() -> None:
    """
    Purpose:
        Ensure missing dependency keys raise MeldExecutionError.
    Contract:
        - Missing instance keys raise MeldExecutionError.
    """
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])}
    )
    with pytest.raises(KeyError):
        build_kwargs_from_injection_spec(
            instance_key=("root", None),
            occurrence=("root", 0),
            injection_spec=spec,
            instance_results={},
            override_values={},
        )


def test_build_kwargs_from_injection_spec_override_wins() -> None:
    """
    Purpose:
        Ensure override values take precedence over dependencies.
    Contract:
        - Override values replace dependency-resolved values.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])}
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={"dep": "override"},
    )

    assert kwargs["dep"] == "override"


def test_build_kwargs_from_injection_spec_contract_payload_applied() -> None:
    """
    Purpose:
        Validate contract payload values apply when not overridden.
    Contract:
        - Contract payload keys populate kwargs.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload={"extra": "payload"},
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={},
    )

    assert kwargs["extra"] == "payload"


def test_build_kwargs_from_injection_spec_contract_payload_skips_overrides() -> None:
    """
    Purpose:
        Ensure contract payload does not overwrite override values.
    Contract:
        - Override values remain authoritative.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload={"dep": "payload"},
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={"dep": "override"},
    )

    assert kwargs["dep"] == "override"


def test_build_kwargs_from_injection_spec_positional_override() -> None:
    """
    Purpose:
        Validate positional override handling when enabled.
    Contract:
        - __args__ is preserved when uses_positional_override is True.
    """
    instance_results = {("dep", None): "value"}
    contract_payload = {"__args__": [1, 2]}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload=contract_payload,
        uses_positional_override=True,
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={},
    )

    assert kwargs["__args__"] == (1, 2)
    assert contract_payload["__args__"] == [1, 2]


def test_build_kwargs_from_injection_spec_retains_args_when_disabled() -> None:
    """
    Purpose:
        Ensure __args__ payload is retained when positional overrides are disabled.
    Contract:
        - __args__ remains in kwargs when uses_positional_override is False.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload={"__args__": [1, 2]},
        uses_positional_override=False,
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={},
    )

    assert kwargs["__args__"] == [1, 2]


def test_build_kwargs_from_injection_spec_rejects_invalid_positional_override() -> None:
    """
    Purpose:
        Ensure invalid __args__ contract payloads fail fast when positional mode is enabled.
    Contract:
        - Non-list/tuple __args__ raises MeldExecutionError.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload={"__args__": "bad"},
        uses_positional_override=True,
    )
    with pytest.raises(MeldExecutionError, match="Contract payload __args__ must be a list or tuple"):
        build_kwargs_from_injection_spec(
            instance_key=("root", None),
            occurrence=("root", 0),
            injection_spec=spec,
            instance_results=instance_results,
            override_values={},
        )


def test_build_kwargs_from_injection_spec_override_keeps_contract_payload() -> None:
    """
    Purpose:
        Validate overrides do not remove unrelated contract payload keys.
    Contract:
        - Contract payload keys are preserved when not overridden.
    """
    instance_results = {("dep", None): "value"}
    spec = _make_spec(
        param_sources={"dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        contract_payload={"extra": "payload"},
    )
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results=instance_results,
        override_values={"dep": "override"},
    )

    assert kwargs["extra"] == "payload"


def test_build_kwargs_from_injection_spec_includes_unmatched_override_values() -> None:
    """
    Purpose:
        Ensure override values are added even when param_sources is empty.
    Contract:
        - Override values populate kwargs when not already set.
    """
    spec = _make_spec(param_sources={})
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results={},
        override_values={"extra": "override"},
    )

    assert kwargs["extra"] == "override"


def test_build_kwargs_from_injection_spec_empty_when_no_inputs() -> None:
    """
    Purpose:
        Validate kwargs are empty when no sources or overrides exist.
    Contract:
        - Empty inputs yield an empty kwargs mapping.
    """
    spec = _make_spec(param_sources={})
    kwargs = build_kwargs_from_injection_spec(
        instance_key=("root", None),
        occurrence=("root", 0),
        injection_spec=spec,
        instance_results={},
        override_values={},
    )

    assert kwargs == {}
