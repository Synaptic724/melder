"""Focused contract tests for CreationContextBuilder."""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def _make_creation_artifact(
        *,
        no_overrides_executor: Optional[Any] = None,
        overrides_executor: Optional[Any] = None,
) -> Any:
    """Build a minimal `SpellCodegenCreation`-shaped stub for builder tests."""
    return SimpleNamespace(
        no_overrides_executor=no_overrides_executor,
        overrides_executor=overrides_executor,
    )


def _make_spell(
        *,
        is_existing_creation: bool = False,
        existence: Existence = Existence.unique,
        creation_artifact: Optional[Any] = None,
        user_created_object: Any = None,
) -> Any:
    """Build a minimal spell stub for CreationContextBuilder tests."""
    compiler_artifact = SimpleNamespace(
        _spell_codegen_creation=creation_artifact,
    )
    return SimpleNamespace(
        spell_id="spell-1",
        spell_name="spell-1",
        spell_index=SimpleNamespace(current="spell-1", id="lineage-spell-1"),
        existence=existence,
        is_existing_creation=is_existing_creation,
        user_created_object=user_created_object,
        _owner_creations=object(),
        _compiler_artifact=compiler_artifact,
        _spellbook=SimpleNamespace(_spell_id_pool={"spell-1": object()}),
    )


def test_build_requires_codegen_creation_for_constructed_spell() -> None:
    """Constructed spells should not build contexts before codegen creation exists."""
    spell = _make_spell(is_existing_creation=False, creation_artifact=None)

    with pytest.raises(RuntimeError, match="spell_codegen_creation"):
        CreationContextBuilder.build(spell)


def test_build_requires_both_runtime_executors_for_constructed_spell() -> None:
    """Constructed spells should fail hard if phase 11 omitted one of the 2 runtime doors."""
    spell_missing_no_overrides = _make_spell(
        creation_artifact=_make_creation_artifact(
            no_overrides_executor=None,
            overrides_executor=lambda creations, overrides: ("value", True),
        ),
    )
    spell_missing_overrides = _make_spell(
        creation_artifact=_make_creation_artifact(
            no_overrides_executor=lambda creations: ("value", True),
            overrides_executor=None,
        ),
    )

    with pytest.raises(RuntimeError, match="no_overrides_executor"):
        CreationContextBuilder.build(spell_missing_no_overrides)
    with pytest.raises(RuntimeError, match="overrides_executor"):
        CreationContextBuilder.build(spell_missing_overrides)


def test_build_existing_creation_without_codegen_creation_uses_local_runtime_doors() -> None:
    """Existing-creation spells should still build a context without phase-11 codegen output."""
    spell = _make_spell(
        is_existing_creation=True,
        creation_artifact=None,
        user_created_object="existing-root",
    )
    caller_creations = object()

    context = CreationContextBuilder.build(spell)

    assert context.execute_no_hooks(caller_creations) == "existing-root"
    assert context.execute(caller_creations) == ("existing-root", False)


def test_existing_creation_overrides_raise_contract_error() -> None:
    """Existing creations must still reject override payloads."""
    spell = _make_spell(
        is_existing_creation=True,
        creation_artifact=None,
        user_created_object="existing-root",
    )
    context = CreationContextBuilder.build(spell)

    with pytest.raises(MeldExecutionError, match="already exists"):
        context.execute(object(), {"dep": "value"})


def test_build_constructed_spell_uses_phase11_runtime_doors() -> None:
    """Builder should pass through the two final phase-11 runtime doors for constructed spells."""
    no_overrides_calls = []
    overrides_calls = []

    def _no_overrides_executor(caller_creations: Any) -> tuple[str, bool]:
        no_overrides_calls.append(caller_creations)
        return "plain", True

    def _overrides_executor(
            caller_creations: Any,
            overrides: dict[str, Any],
    ) -> tuple[str, bool]:
        overrides_calls.append((caller_creations, overrides))
        return "override", False

    spell = _make_spell(
        creation_artifact=_make_creation_artifact(
            no_overrides_executor=_no_overrides_executor,
            overrides_executor=_overrides_executor,
        ),
    )
    caller_creations = object()

    context = CreationContextBuilder.build(spell)

    assert context.execute(caller_creations) == ("plain", True)
    assert context.execute(caller_creations, {"dep": "value"}) == ("override", False)
    assert no_overrides_calls == [caller_creations]
    assert overrides_calls == [(caller_creations, {"dep": "value"})]
