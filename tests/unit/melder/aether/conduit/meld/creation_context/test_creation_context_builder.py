"""CreationContextBuilder current-surface contract tests."""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

import melder.aether.conduit.meld.creation_context.creation_context_builder as builder_module
from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.spellbook.existence.existence import Existence


def _make_creation_artifact(
        *,
        resolve_route_key: Optional[str] = CreationContext.ROUTE_SHARED,
        fast_transient_no_overrides_enabled: bool = False,
        no_overrides_executor: Optional[Any] = None,
        override_targeting: Optional[Any] = None,
        override_no_mutation_plan_signature: Optional[tuple[Any, ...]] = None,
        override_no_mutation_path_registry: Optional[Any] = None,
        override_no_mutation_plan_rows: Optional[Any] = None,
        override_no_mutation_root_spell_id: Optional[str] = None,
        override_no_mutation_spell_lookup: Optional[Any] = None,
        override_no_mutation_empty_shape_key: Optional[tuple[Any, ...]] = None,
        override_no_mutation_baseline_executor: Optional[Any] = None,
        override_mutation_plan_signature: Optional[tuple[Any, ...]] = None,
        override_mutation_path_registry: Optional[Any] = None,
        override_mutation_plan_rows: Optional[Any] = None,
        override_mutation_root_spell_id: Optional[str] = None,
        override_mutation_spell_lookup: Optional[Any] = None,
        override_mutation_empty_shape_key: Optional[tuple[Any, ...]] = None,
        override_mutation_baseline_executor: Optional[Any] = None,
) -> Any:
    """Build a minimal `SpellCodegenCreation`-shaped stub for builder tests."""
    return SimpleNamespace(
        resolve_route_key=resolve_route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        no_overrides_executor=no_overrides_executor,
        override_targeting=override_targeting,
        override_no_mutation_plan_signature=override_no_mutation_plan_signature,
        override_no_mutation_path_registry=override_no_mutation_path_registry,
        override_no_mutation_plan_rows=override_no_mutation_plan_rows,
        override_no_mutation_root_spell_id=override_no_mutation_root_spell_id,
        override_no_mutation_spell_lookup=override_no_mutation_spell_lookup,
        override_no_mutation_empty_shape_key=override_no_mutation_empty_shape_key,
        override_no_mutation_baseline_executor=override_no_mutation_baseline_executor,
        override_mutation_plan_signature=override_mutation_plan_signature,
        override_mutation_path_registry=override_mutation_path_registry,
        override_mutation_plan_rows=override_mutation_plan_rows,
        override_mutation_root_spell_id=override_mutation_root_spell_id,
        override_mutation_spell_lookup=override_mutation_spell_lookup,
        override_mutation_empty_shape_key=override_mutation_empty_shape_key,
        override_mutation_baseline_executor=override_mutation_baseline_executor,
    )


def _make_spell(
        *,
        is_existing_creation: bool = False,
        existence: Existence = Existence.unique,
        has_mutation_override: bool = False,
        creation_artifact: Optional[Any] = None,
) -> Any:
    """Build a minimal spell stub for `CreationContextBuilder` tests."""
    compiler_artifact = SimpleNamespace(
        _spell_codegen_creation=creation_artifact,
    )
    return SimpleNamespace(
        spell_id="spell-1",
        spell_name="spell-1",
        spell_index=SimpleNamespace(current="spell-1", id="lineage-spell-1"),
        existence=existence,
        is_existing_creation=is_existing_creation,
        has_mutation_override=has_mutation_override,
        _owner_creations=object(),
        _compiler_artifact=compiler_artifact,
        _spellbook=SimpleNamespace(_spell_id_pool={"spell-1": object()}),
    )


def test_build_requires_spell_codegen_creation_for_constructed_spell() -> None:
    """Constructed spells should not build contexts before codegen creation exists."""
    spell = _make_spell(is_existing_creation=False, creation_artifact=None)

    with pytest.raises(RuntimeError, match="spell_codegen_creation"):
        CreationContextBuilder.build(spell)


def test_build_allows_existing_creation_without_codegen_creation(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing-creation spells should still build through the dedicated existing route."""
    spell = _make_spell(is_existing_creation=True, creation_artifact=None)
    captured: dict[str, Any] = {}

    def _fake_creation_context(**kwargs: Any) -> Any:
        """Capture constructor kwargs without building a real context."""
        captured.update(kwargs)
        return "context"

    monkeypatch.setattr(builder_module, "CreationContext", _fake_creation_context)

    result = CreationContextBuilder.build(spell)

    assert result == "context"
    assert captured["resolve_route_key"] == CreationContext.ROUTE_EXISTING_CREATION
    assert captured["no_overrides_executor"] is None
    assert captured["override_targeting"] is None
    assert captured["override_route_config_no_mutation"] is None
    assert captured["override_route_config_mutation"] is None


def test_build_forwards_creation_artifact_fields_into_creation_context(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Builder should forward the flattened `SpellCodegenCreation` contract into `CreationContext`."""
    spell = _make_spell(
        creation_artifact=_make_creation_artifact(
            resolve_route_key=CreationContext.ROUTE_MANY,
            fast_transient_no_overrides_enabled=True,
            no_overrides_executor="executor",
            override_targeting="targeting",
            override_no_mutation_plan_signature=("no-mutation",),
            override_no_mutation_path_registry="path-registry",
            override_no_mutation_plan_rows=("rows",),
            override_no_mutation_root_spell_id="spell-1",
            override_no_mutation_spell_lookup={"spell-1": object()},
            override_no_mutation_empty_shape_key=("empty",),
            override_no_mutation_baseline_executor="baseline",
            override_mutation_plan_signature=("mutation",),
            override_mutation_path_registry="mutation-path-registry",
            override_mutation_plan_rows=("mutation-rows",),
            override_mutation_root_spell_id="spell-1",
            override_mutation_spell_lookup={"spell-1": object()},
            override_mutation_empty_shape_key=("mutation-empty",),
            override_mutation_baseline_executor="mutation-baseline",
        ),
        has_mutation_override=True,
    )
    captured: dict[str, Any] = {}

    def _fake_creation_context(**kwargs: Any) -> Any:
        """Capture constructor kwargs without building a real context."""
        captured.update(kwargs)
        return "context"

    monkeypatch.setattr(builder_module, "CreationContext", _fake_creation_context)

    result = CreationContextBuilder.build(
        spell,
        dynamic_environment=True,
        creation_gate="gate",
        creation_gate_index_id="index",
    )

    assert result == "context"
    assert captured["spell"] is spell
    assert captured["dynamic_environment"] is True
    assert captured["creation_gate"] == "gate"
    assert captured["creation_gate_index_id"] == "index"
    assert captured["resolve_route_key"] == CreationContext.ROUTE_MANY
    assert captured["fast_transient_no_overrides_enabled"] is True
    assert captured["no_overrides_executor"] == "executor"
    assert captured["override_targeting"] == "targeting"
    assert isinstance(captured["override_route_config_no_mutation"], OverrideRouteConfig)
    assert isinstance(captured["override_route_config_mutation"], OverrideRouteConfig)
    assert captured["override_route_config_no_mutation"].plan_signature == ("no-mutation",)
    assert captured["override_route_config_mutation"].plan_signature == ("mutation",)


def test_resolve_route_key_uses_existing_creation_shortcut() -> None:
    """Existing-creation spells should always resolve to the existing route."""
    spell = _make_spell(is_existing_creation=True, creation_artifact=None)

    assert CreationContextBuilder._resolve_route_key(
        spell=spell,
        spell_codegen_creation=None,
    ) == CreationContext.ROUTE_EXISTING_CREATION


def test_resolve_route_key_requires_creation_artifact_route_for_constructed_spell() -> None:
    """Constructed spells should resolve their route from the creation artifact."""
    spell = _make_spell(
        is_existing_creation=False,
        creation_artifact=_make_creation_artifact(
            resolve_route_key=CreationContext.ROUTE_UNIQUE_PER_CONDUIT,
        ),
    )

    assert CreationContextBuilder._resolve_route_key(
        spell=spell,
        spell_codegen_creation=spell._compiler_artifact._spell_codegen_creation,
    ) == CreationContext.ROUTE_UNIQUE_PER_CONDUIT


def test_build_override_route_config_from_creation_returns_none_when_all_fields_missing() -> None:
    """Route-config rehydration should no-op when the flattened payload is completely absent."""
    assert CreationContextBuilder._build_override_route_config_from_creation(
        plan_signature=None,
        path_registry=None,
        plan_rows=None,
        root_spell_id=None,
        spell_lookup=None,
        empty_shape_key=None,
        baseline_executor=None,
    ) is None


def test_build_override_route_config_from_creation_rehydrates_runtime_config() -> None:
    """Route-config rehydration should rebuild the runtime `OverrideRouteConfig` carrier."""
    config = CreationContextBuilder._build_override_route_config_from_creation(
        plan_signature=("sig",),
        path_registry="path-registry",
        plan_rows=("rows",),
        root_spell_id="spell-1",
        spell_lookup={"spell-1": object()},
        empty_shape_key=("empty",),
        baseline_executor="baseline",
    )

    assert config is not None
    assert config.plan_signature == ("sig",)
    assert config.path_registry == "path-registry"
    assert config.plan_rows == ("rows",)
    assert config.root_spell_id == "spell-1"
    assert config.empty_shape_key == ("empty",)
    assert config.baseline_executor == "baseline"
