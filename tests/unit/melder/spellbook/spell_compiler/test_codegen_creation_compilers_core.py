"""Unit tests for direct codegen_creation compiler entrypoints and helpers."""

from types import SimpleNamespace

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation.generalized_no_overrides_codegen_creation_compiler as no_overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation.generalized_overrides_codegen_creation_compiler as overrides_compiler_module
from melder.aether.spellbook.existence.existence import Existence


def test_no_overrides_compiler_requires_ir_payload() -> None:
    """The no-overrides compiler should reject a missing IR payload."""
    with pytest.raises(ValueError, match="codegen_ir must not be None"):
        no_overrides_compiler_module.compile_phase13_no_overrides_executor(
            codegen_ir=None,
        )


def test_no_overrides_compiler_returns_none_when_no_steps_exist() -> None:
    """The no-overrides compiler should no-op when the IR has no step rows."""
    assert no_overrides_compiler_module.compile_phase13_no_overrides_executor(
        codegen_ir={},
        spell_lookup={},
    ) is None


def test_no_overrides_compiler_from_plan_validates_plan_and_empty_steps() -> None:
    """The plan entrypoint should reject None and no-op on empty plans."""
    with pytest.raises(ValueError, match="plan must not be None"):
        no_overrides_compiler_module.compile_phase13_no_overrides_executor_from_plan(
            plan=None,
        )

    assert no_overrides_compiler_module.compile_phase13_no_overrides_executor_from_plan(
        plan=SimpleNamespace(steps=[]),
    ) is None


def test_no_overrides_compiler_resolves_root_instance_key_preferentially() -> None:
    """Root instance resolution should prefer the canonical `(spell_id, None)` row and then fall back."""
    canonical = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("root", None)),
        ),
        root_spell_id="root",
    )
    fallback = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )
    missing = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )

    assert canonical == ("root", None)
    assert fallback == ("root", 5)
    assert missing is None


def test_no_overrides_compiler_supports_transient_unrolled_only_for_many_non_registering_steps() -> None:
    """Transient unrolled support should stay restricted to pure transient-many steps."""
    good = (
        SimpleNamespace(existence=Existence.many, must_register=False),
        SimpleNamespace(existence=Existence.many, must_register=False),
    )
    bad_existence = (
        SimpleNamespace(existence=Existence.unique, must_register=False),
    )
    bad_register = (
        SimpleNamespace(existence=Existence.many, must_register=True),
    )

    assert no_overrides_compiler_module._supports_transient_unrolled_plan(good) is True
    assert no_overrides_compiler_module._supports_transient_unrolled_plan(bad_existence) is False
    assert no_overrides_compiler_module._supports_transient_unrolled_plan(bad_register) is False


def test_no_overrides_compiler_normalizes_transient_schema_and_rejects_bad_lengths() -> None:
    """Transient schema normalization should coerce sequences to tuples and reject bad lengths."""
    normalized = no_overrides_compiler_module._normalize_transient_schema(
        transient_schema={
            "step_count": 1,
            "root_step_index": 0,
            "call_modes": [0],
            "dep1": [-1],
            "dep2a": [-1],
            "dep2b": [-1],
            "dep3a": [-1],
            "dep3b": [-1],
            "dep3c": [-1],
            "dep4a": [-1],
            "dep4b": [-1],
            "dep4c": [-1],
            "dep4d": [-1],
            "dep5a": [-1],
            "dep5b": [-1],
            "dep5c": [-1],
            "dep5d": [-1],
            "dep5e": [-1],
            "dep6a": [-1],
            "dep6b": [-1],
            "dep6c": [-1],
            "dep6d": [-1],
            "dep6e": [-1],
            "dep6f": [-1],
            "dep7a": [-1],
            "dep7b": [-1],
            "dep7c": [-1],
            "dep7d": [-1],
            "dep7e": [-1],
            "dep7f": [-1],
            "dep7g": [-1],
            "dep8a": [-1],
            "dep8b": [-1],
            "dep8c": [-1],
            "dep8d": [-1],
            "dep8e": [-1],
            "dep8f": [-1],
            "dep8g": [-1],
            "dep8h": [-1],
        }
    )

    assert normalized["call_modes"] == (0,)
    assert normalized["dep8h"] == (-1,)

    with pytest.raises(RuntimeError, match="length must equal step_count"):
        no_overrides_compiler_module._normalize_transient_schema(
            transient_schema={
                "step_count": 1,
                "root_step_index": 0,
                "call_modes": [0, 1],
                "dep1": [-1],
                "dep2a": [-1],
                "dep2b": [-1],
                "dep3a": [-1],
                "dep3b": [-1],
                "dep3c": [-1],
                "dep4a": [-1],
                "dep4b": [-1],
                "dep4c": [-1],
                "dep4d": [-1],
                "dep5a": [-1],
                "dep5b": [-1],
                "dep5c": [-1],
                "dep5d": [-1],
                "dep5e": [-1],
                "dep6a": [-1],
                "dep6b": [-1],
                "dep6c": [-1],
                "dep6d": [-1],
                "dep6e": [-1],
                "dep6f": [-1],
                "dep7a": [-1],
                "dep7b": [-1],
                "dep7c": [-1],
                "dep7d": [-1],
                "dep7e": [-1],
                "dep7f": [-1],
                "dep7g": [-1],
                "dep8a": [-1],
                "dep8b": [-1],
                "dep8c": [-1],
                "dep8d": [-1],
                "dep8e": [-1],
                "dep8f": [-1],
                "dep8g": [-1],
                "dep8h": [-1],
            }
        )


def test_overrides_compiler_code_object_entrypoints_validate_and_delegate(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The overrides compiler should validate inputs and delegate through the code-object path cleanly."""
    with pytest.raises(ValueError, match="source must be a non-empty string"):
        overrides_compiler_module.compile_phase13_overrides_executor_code_object(
            source="",
        )

    monkeypatch.setattr(
        overrides_compiler_module,
        "get_or_compile_executor_code",
        lambda source, source_name: ("compiled", source, source_name),
    )
    code_object = overrides_compiler_module.compile_phase13_overrides_executor_code_object(
        source="print('x')",
    )
    assert code_object == (
        "compiled",
        "print('x')",
        "<melder_phase13_overrides_executor>",
    )

    calls = []
    monkeypatch.setattr(
        overrides_compiler_module,
        "_compile_phase13_overrides_executor_core",
        lambda **kwargs: (calls.append(kwargs) or (("executor",), None)),
    )
    result = overrides_compiler_module.compile_phase13_overrides_executor_from_code_object(
        code_object=("compiled",),
        execution_plan=None,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )

    assert result == ("executor",)
    assert calls


def test_overrides_compiler_code_object_entrypoint_requires_code_object() -> None:
    """The overrides code-object entrypoint should reject a missing code object."""
    with pytest.raises(ValueError, match="code_object must not be None"):
        overrides_compiler_module.compile_phase13_overrides_executor_from_code_object(
            code_object=None,
            execution_plan=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )
