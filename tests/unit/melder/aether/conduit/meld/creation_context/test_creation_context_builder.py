"""CreationContextBuilder policy and routing contract tests."""
from types import SimpleNamespace
from typing import Any, Optional

import pytest

import melder.aether.conduit.meld.creation_context.creation_context_builder as builder_module
from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.existence.existence import Existence


def _make_crafter(
        *,
        fast_transient_plan: Optional[Any] = None,
        phase12_no_overrides_executor: Optional[Any] = None,
        override_patch_map_phase10: Optional[Any] = None,
        codegen_ir: Optional[Any] = None,
        root_blueprint_phase5: Optional[Any] = None,
) -> Any:
    """Build a minimal compiler-artifact stub for CreationContextBuilder tests."""
    return SimpleNamespace(
        _execution_plan_phase11_no_overrides=SimpleNamespace(
            fast_transient_plan=fast_transient_plan,
        ),
        _phase12_no_overrides_executor=phase12_no_overrides_executor,
        _override_patch_map_phase10=override_patch_map_phase10,
        _codegen_ir=codegen_ir,
        _root_blueprint_phase5=root_blueprint_phase5,
        _phase8_11_codegen_ir_dirty=False,
    )


_DEFAULT_ARTIFACT = object()


def _make_spell(
        *,
        is_existing_creation: bool = False,
        crafter: Optional[Any] = None,
        existence: Any = None,
        execution_plan_dispatch_route: Optional[str] = None,
        has_mutation_override: bool = False,
        spellbook: Optional[Any] = None,
) -> Any:
    """Build a minimal spell stub for CreationContextBuilder tests."""
    if existence is None:
        existence = Existence.unique
    if spellbook is None:
        spellbook = SimpleNamespace(_spell_id_pool={"s1": object()})
    return SimpleNamespace(
        spell_id="s1",
        is_existing_creation=is_existing_creation,
        _compiler_artifact=_make_crafter() if crafter is _DEFAULT_ARTIFACT else crafter,
        existence=existence,
        execution_plan_dispatch_route=execution_plan_dispatch_route,
        has_mutation_override=has_mutation_override,
        _spellbook=spellbook,
    )

def test_build_requires_crafter_for_non_existing_spells() -> None:
    """Verify build rejects non-existing spells without compiler artifacts."""
    builder = CreationContextBuilder()
    spell = _make_spell(is_existing_creation=False, crafter=SimpleNamespace(_execution_plan_phase11_no_overrides=None, _override_patch_map_phase10=None, _codegen_ir=None, _phase8_11_codegen_ir_dirty=False))

    with pytest.raises(RuntimeError, match="Cannot build CreationContext"):
        builder.build(spell)


def test_build_passes_resolved_policy_into_creation_context(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify build forwards resolved builder policy into CreationContext construction."""
    builder = CreationContextBuilder()
    spell = _make_spell(is_existing_creation=False, crafter=_make_crafter())
    captured: dict[str, Any] = {}

    def _fake_creation_context(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return "context"

    monkeypatch.setattr(builder_module, "CreationContext", _fake_creation_context)
    monkeypatch.setattr(
        CreationContextBuilder,
        "_resolve_route_key",
        staticmethod(lambda _spell: CreationContext.ROUTE_MANY),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_resolve_fast_transient_no_overrides_enabled",
        staticmethod(lambda _spell: True),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_coerce_fast_transient_route_eligibility",
        staticmethod(
            lambda *, resolve_route_key, fast_transient_no_overrides_enabled: (
                resolve_route_key == CreationContext.ROUTE_MANY
                and fast_transient_no_overrides_enabled
            )
        ),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_resolve_no_overrides_executor",
        staticmethod(lambda _spell: "executor"),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_resolve_override_patch_map_phase10",
        staticmethod(lambda _spell: "patch-map"),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_build_override_route_config",
        staticmethod(lambda **kwargs: "no-mutation-config"),
    )
    monkeypatch.setattr(
        CreationContextBuilder,
        "_build_mutation_override_route_config",
        staticmethod(lambda *, spell: "mutation-config"),
    )

    result = builder.build(
        spell,
        dynamic_environment=True,
        creation_gate="gate",
        creation_gate_index_id="index",
    )

    assert result == "context"
    assert captured == {
        "spell": spell,
        "dynamic_environment": True,
        "creation_gate": "gate",
        "creation_gate_index_id": "index",
        "resolve_route_key": CreationContext.ROUTE_MANY,
        "fast_transient_no_overrides_enabled": True,
        "no_overrides_executor": "executor",
        "override_patch_map_phase10": "patch-map",
        "override_route_config_no_mutation": "no-mutation-config",
        "override_route_config_mutation": "mutation-config",
    }


@pytest.mark.parametrize(
    ("spell", "expected"),
    [
        (_make_spell(is_existing_creation=True), CreationContext.ROUTE_EXISTING_CREATION),
        (_make_spell(existence=Existence.unique_per_spell_space), CreationContext.ROUTE_SPELLSPACE),
        (_make_spell(existence=Existence.unique_per_conduit), CreationContext.ROUTE_UNIQUE_PER_CONDUIT),
        (_make_spell(existence=Existence.many), CreationContext.ROUTE_MANY),
        (_make_spell(existence=Existence.unique), CreationContext.ROUTE_SHARED),
    ],
)
def test_resolve_route_key_selects_expected_route(spell: Any, expected: str) -> None:
    """Verify route-key resolution matches spell existence policy."""
    assert CreationContextBuilder._resolve_route_key(spell) == expected


@pytest.mark.parametrize(
    ("route_key", "enabled", "expected"),
    [
        (CreationContext.ROUTE_MANY, True, True),
        (CreationContext.ROUTE_MANY, False, False),
        (CreationContext.ROUTE_SHARED, True, False),
    ],
)
def test_coerce_fast_transient_route_eligibility_only_allows_many(
        route_key: str,
        enabled: bool,
        expected: bool,
) -> None:
    """Verify fast transient eligibility is limited to the many route."""
    assert (
        CreationContextBuilder._coerce_fast_transient_route_eligibility(
            resolve_route_key=route_key,
            fast_transient_no_overrides_enabled=enabled,
        )
        is expected
    )


def test_resolve_fast_transient_returns_false_for_existing_creation() -> None:
    """Verify existing-creation spells never use fast transient dispatch."""
    spell = _make_spell(is_existing_creation=True, crafter=_make_crafter())
    assert CreationContextBuilder._resolve_fast_transient_no_overrides_enabled(spell) is False


def test_resolve_fast_transient_uses_dispatch_route_prefix() -> None:
    """Verify FAST_TRANSIENT dispatch routes enable the fast transient lane."""
    spell = _make_spell(
        crafter=_make_crafter(fast_transient_plan=None),
        execution_plan_dispatch_route="FAST_TRANSIENT_PLAN",
    )
    assert CreationContextBuilder._resolve_fast_transient_no_overrides_enabled(spell) is True


def test_resolve_fast_transient_uses_phase11_plan_when_present() -> None:
    """Verify phase11 fast transient plans enable the fast transient lane."""
    spell = _make_spell(
        crafter=_make_crafter(fast_transient_plan=object()),
        execution_plan_dispatch_route=None,
    )
    assert CreationContextBuilder._resolve_fast_transient_no_overrides_enabled(spell) is True


def test_resolve_fast_transient_returns_false_when_plan_missing() -> None:
    """Verify missing phase11 plans disable fast transient dispatch."""
    spell = _make_spell(
        crafter=SimpleNamespace(_execution_plan_phase11_no_overrides=None),
        execution_plan_dispatch_route=None,
    )
    assert CreationContextBuilder._resolve_fast_transient_no_overrides_enabled(spell) is False


def test_resolve_no_overrides_executor_returns_none_for_existing_creation() -> None:
    """Verify existing-creation spells do not expose a no-overrides executor."""
    spell = _make_spell(is_existing_creation=True, crafter=_make_crafter())
    assert CreationContextBuilder._resolve_no_overrides_executor(spell) is None


def test_resolve_no_overrides_executor_returns_crafter_executor() -> None:
    """Verify no-overrides executor comes from the crafter payload."""
    executor = object()
    spell = _make_spell(crafter=_make_crafter(phase12_no_overrides_executor=executor))
    assert CreationContextBuilder._resolve_no_overrides_executor(spell) is executor


def test_resolve_override_patch_map_returns_none_for_existing_creation() -> None:
    """Verify existing-creation spells do not expose phase10 override patch maps."""
    spell = _make_spell(is_existing_creation=True, crafter=_make_crafter())
    assert CreationContextBuilder._resolve_override_patch_map_phase10(spell) is None


def test_resolve_override_patch_map_returns_crafter_patch_map() -> None:
    """Verify phase10 override patch maps come from the crafter payload."""
    patch_map = object()
    spell = _make_spell(crafter=_make_crafter(override_patch_map_phase10=patch_map))
    assert CreationContextBuilder._resolve_override_patch_map_phase10(spell) is patch_map


def test_build_override_route_config_returns_none_for_existing_creation() -> None:
    """Verify existing-creation spells do not build override route config payloads."""
    spell = _make_spell(is_existing_creation=True, crafter=_make_crafter())
    assert (
        CreationContextBuilder._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides",
        )
        is None
    )


def test_build_override_route_config_returns_none_when_codegen_ir_missing() -> None:
    """Verify missing codegen IR disables override route config creation."""
    spell = _make_spell(crafter=_make_crafter(codegen_ir=None))
    assert (
        CreationContextBuilder._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides",
        )
        is None
    )


def test_build_override_route_config_returns_none_when_execution_variant_missing() -> None:
    """Verify missing override execution variants disable route config creation."""
    crafter = _make_crafter(
        codegen_ir={"phase8_11": {"execution": {}}},
        root_blueprint_phase5=None,
    )
    spell = _make_spell(crafter=crafter)
    assert (
        CreationContextBuilder._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides",
        )
        is None
    )


def test_build_override_route_config_builds_static_payload() -> None:
    """Verify override route config is built from crafter/static spell payload."""
    path_registry = object()
    crafter = _make_crafter(
        codegen_ir={
            "phase8_11": {
                "execution": {
                    "overrides": {
                        "signature": ("variant", "sig"),
                        "steps_rows_signature": ("rows",),
                        "steps_rows": ({"row": 1},),
                        "root_spell_id": "root-spell",
                    }
                }
            }
        },
        root_blueprint_phase5=SimpleNamespace(path_registry=path_registry),
    )
    spellbook = SimpleNamespace(_spell_id_pool={"root-spell": object()})
    spell = _make_spell(crafter=crafter, spellbook=spellbook)

    config = CreationContextBuilder._build_override_route_config(
        spell=spell,
        execution_ir_key="overrides",
    )

    assert config is not None
    assert config.plan_signature == (
        "phase11_overrides_ir",
        ("variant", "sig"),
        ("rows",),
    )
    assert config.path_registry is path_registry
    assert config.plan_rows == ({"row": 1},)
    assert config.root_spell_id == "root-spell"
    assert config.spell_lookup is spellbook._spell_id_pool
    assert config.empty_shape_key == (
        config.plan_signature,
        (),
        -1,
    )
    assert config.baseline_executor is None


def test_build_mutation_override_route_config_returns_none_without_mutation_override() -> None:
    """Verify mutation override configs are omitted when the spell has no mutation overlay."""
    spell = _make_spell(has_mutation_override=False, crafter=_make_crafter())
    assert (
        CreationContextBuilder._build_mutation_override_route_config(spell=spell)
        is None
    )


def test_build_mutation_override_route_config_delegates_when_mutation_enabled(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify mutation override configs delegate to the generic override-config builder."""
    spell = _make_spell(has_mutation_override=True, crafter=_make_crafter())
    sentinel = object()

    monkeypatch.setattr(
        CreationContextBuilder,
        "_build_override_route_config",
        staticmethod(lambda **kwargs: sentinel),
    )

    assert (
        CreationContextBuilder._build_mutation_override_route_config(spell=spell)
        is sentinel
    )


