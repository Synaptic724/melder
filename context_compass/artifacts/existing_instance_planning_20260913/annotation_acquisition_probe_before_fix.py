"""Isolate Python 3.14 annotation acquisition using real class providers.

Three acquisition modes distinguish the initial signature failure from the
subsequent raw-annotation failure. Only test-process references are replaced;
the existing-instance planners, validation and production files are unchanged.
"""

import annotationlib
import inspect
import json
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.spellbook.spell_compiler.spell_examiner.strategies import (
    binding_profile_strategy,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder import (
    spell_requirements_finder,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.experimentation.test_existing_instance_gap_experiment import (
    DisposableValue as RuntimeValue,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)

if TYPE_CHECKING:
    from tests.experimentation.test_existing_instance_gap_experiment import (
        DisposableValue,
    )


class DeferredConsumer:
    """Require a provider whose annotation is deliberately unavailable at runtime."""

    def __init__(self, value: DisposableValue) -> None:
        """Retain the actual injected class-created provider."""
        self.value = value


class DeferredCollectionConsumer:
    """Keep an unresolved name inside a real collection annotation."""

    def __init__(self, values: list[DisposableValue]) -> None:
        """Retain all matching class-created providers in order."""
        self.values = values


class DeferredDefaultConsumer:
    """Preserve an ordinary default even when its type name cannot be evaluated."""

    def __init__(self, value: Optional[DisposableValue] = None) -> None:
        """Retain the selected None rather than inferring a provider edge."""
        self.value = value


def deferred_factory(value: DisposableValue) -> DeferredConsumer:
    """Require the same annotation through a callable binding rather than a class."""
    return DeferredConsumer(value)


class ForwardSignatureInspection:
    """Test-only inspect facade changing signature format at two acquisition owners."""

    @staticmethod
    def signature(target: object, **kwargs: object) -> inspect.Signature:
        """Request partial annotation evaluation while preserving the original signature."""
        kwargs.setdefault("annotation_format", annotationlib.Format.FORWARDREF)
        return inspect.signature(target, **kwargs)

    def __getattr__(self, name: str) -> object:
        """Delegate other dynamic inspect-module capabilities without changing them."""
        return getattr(inspect, name)


def forward_annotations(finder: SpellRequirementsFinder, call_target: object) -> dict[str, object]:
    """Prototype acquisition with unresolved references, retaining Melder's existing normalizer."""
    target = call_target.__init__ if inspect.isclass(call_target) else call_target
    raw = annotationlib.get_annotations(target, format=annotationlib.Format.FORWARDREF)
    module = inspect.getmodule(call_target)
    globalns = vars(module) if module is not None else {}
    localns = dict(vars(call_target)) if inspect.isclass(call_target) else {}
    return {
        name: finder._normalize_annotation(annotation=value, globalns=globalns, localns=localns)
        for name, value in raw.items()
    }


@pytest.fixture(params=("stock", "signature_only", "forward_acquisition"))
def acquisition_mode(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """Patch only acquisition owners for this case and restore them automatically afterward."""
    mode: str = request.param
    if mode != "stock":
        facade = ForwardSignatureInspection()
        monkeypatch.setattr(binding_profile_strategy, "inspect", facade)
        monkeypatch.setattr(spell_requirements_finder, "inspect", facade)
    if mode == "forward_acquisition":
        monkeypatch.setattr(SpellRequirementsFinder, "_resolve_parameter_annotations", forward_annotations)
    return mode


@pytest.mark.parametrize("kind", ("class", "function", "collection", "default"))
def test_deferred_annotation_acquisition(
        instance_book: Spellbook, acquisition_mode: str, kind: str,
) -> None:
    """Compare both failure boundaries and verify actual resolution after acquisition succeeds."""
    provider_id = instance_book.bind(spell=RuntimeValue, existence="unique")
    target = {"class": DeferredConsumer, "function": deferred_factory,
              "collection": DeferredCollectionConsumer, "default": DeferredDefaultConsumer}[kind]
    report = {"kind": kind, "acquisition": acquisition_mode}
    if acquisition_mode != "forward_acquisition":
        with pytest.raises(NameError, match="DisposableValue") as error:
            instance_book.bind(spell=target, existence="unique")
        report["outcome"] = "signature_nameerror" if acquisition_mode == "stock" else "raw_annotations_nameerror"
        report["error"] = str(error.value)
    else:
        target_id = instance_book.bind(spell=target, existence="unique")
        root = instance_book.conjure(dynamic=True)
        consumer = root.meld(spell_id=target_id)
        if kind == "default":
            assert consumer.value is None
        else:
            expected = root.meld(spell_id=provider_id)
            value = consumer.values[0] if kind == "collection" else consumer.value
            assert value is expected
            assert value.read() == "created"
            if kind == "collection":
                assert len(consumer.values) == 1
        report["outcome"] = "resolved_with_default_and_identity_preserved"
    print("ANNOTATION " + json.dumps(report, sort_keys=True))


def test_forward_format_preserves_known_signature() -> None:
    """A known constructor retains the same signature objects and fingerprint text."""
    original = inspect.signature(RuntimeValue)
    partial = ForwardSignatureInspection.signature(RuntimeValue)
    assert partial == original
    assert str(partial) == str(original)


@pytest.mark.parametrize("acquisition_mode", ("forward_acquisition",), indirect=True)
def test_forward_acquisition_still_requires_provider(
        instance_book: Spellbook, acquisition_mode: str,
) -> None:
    """Partial annotation acquisition must not turn an unresolved required dependency into no DI."""
    assert acquisition_mode == "forward_acquisition"
    instance_book.bind(spell=DeferredConsumer, existence="unique")
    with pytest.raises(RuntimeError, match="no DI candidate found"):
        instance_book.conjure(dynamic=True)
