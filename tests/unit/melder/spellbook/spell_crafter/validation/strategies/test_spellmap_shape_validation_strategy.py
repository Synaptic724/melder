from __future__ import annotations

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.validation.strategies.spellmap_shape_validation_strategy import (
    SpellMapShapeValidationStrategy,
)


class _Cancel:
    @property
    def is_set(self):
        return True

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _ToggleCancel:
    def __init__(self) -> None:
        self._checks = 0

    @property
    def is_set(self):
        self._checks += 1
        return self._checks > 1

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _Param:
    def __init__(self, *, name: str, di_shape: ParameterDIShape, spellmap_default) -> None:
        self.name = name
        self.di_shape = di_shape
        self.spellmap_default = spellmap_default


class _Requirements:
    def __init__(self, parameters) -> None:
        self.parameters = parameters


class _Spell:
    def __init__(self, spell_name: str = "spell") -> None:
        self.spell_name = spell_name


class _Context:
    def __init__(self, *, requirements, cancel_event=None) -> None:
        self.requirements = requirements
        self.cancel_event = cancel_event
        self.spell = _Spell()
        self.issues = []


def test_spellmap_shape_validation_honors_cancellation_before_scan() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(requirements=_Requirements([]), cancel_event=_Cancel())

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_spellmap_shape_validation_honors_cancellation_between_parameters() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Param(name="plain", di_shape=ParameterDIShape.PLAIN, spellmap_default=None),
                _Param(name="map", di_shape=ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=None),
            ]
        ),
        cancel_event=_ToggleCancel(),
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_spellmap_shape_validation_returns_when_requirements_missing() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(requirements=None)

    strategy.validate(context)

    assert context.issues == []


def test_spellmap_shape_validation_skips_non_spellmap_parameters() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Param(name="plain", di_shape=ParameterDIShape.PLAIN, spellmap_default=None),
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_spellmap_shape_validation_flags_missing_default() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Param(name="service", di_shape=ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=None),
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["SPELLMAP_DEFAULT_MISSING"]


def test_spellmap_shape_validation_flags_invalid_default() -> None:
    strategy = SpellMapShapeValidationStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Param(name="service", di_shape=ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=object()),
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["SPELLMAP_DEFAULT_INVALID"]


def test_spellmap_shape_validation_accepts_valid_default_without_binding_warning() -> None:
    class IService:
        pass

    strategy = SpellMapShapeValidationStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Param(
                    name="service",
                    di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                    spellmap_default=SpellMap(spellframe=IService, binding_name="primary"),
                ),
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []
