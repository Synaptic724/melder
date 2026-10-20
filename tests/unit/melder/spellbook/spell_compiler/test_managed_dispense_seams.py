"""Unit contracts for the phase 9-11 seams a managed spell passes through (managed_spell_quantity S5, 2026-10-15).

A managed site is per path like `many` (one lease per injection), the generalized manifest names its route family,
its doors reuse the `many` door templates (`created` is True on every lease) and the opt-in singleton specializer
leaves graphs with a managed row to the site plan.
"""

from types import SimpleNamespace

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_instance_processor_strategy import (
    SpellOccurrenceInstanceProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets import creation_runtime_door_compiler
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    rows_contain_managed_step,
    rows_feed_many_into_non_many_step,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest.generalized_manifest import (
    _resolve_route_key_from_model,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)


@pytest.mark.parametrize("existence", list(Existence))
def test_instance_processor_gives_one_shared_key_only_to_slotted_existences(existence: Existence) -> None:
    """`many` and managed sites get one instance key per path; every slotted existence shares one."""
    expected = existence not in (Existence.many, Existence.managed_spell_quantity)
    assert SpellOccurrenceInstanceProcessorStrategy._is_shared_existence(existence) is expected


@pytest.mark.parametrize("existence", list(Existence))
def test_occurrence_analyzer_collapses_only_slotted_existences(existence: Existence) -> None:
    """The occurrence walk keeps one occurrence per path for `many` and managed spells."""
    expected = existence not in (Existence.many, Existence.managed_spell_quantity)
    assert SpellOccurrenceGraphAnalyzerStrategy._is_shared_existence(existence) is expected


def test_manifest_route_key_accepts_the_managed_family() -> None:
    """A class spell of route family "managed" gets route key "managed"."""
    model = SimpleNamespace(build_kind="class_spell", route_family="managed")
    assert _resolve_route_key_from_model(model) == "managed"


def test_manifest_route_key_still_refuses_an_unknown_family() -> None:
    """Families outside the whitelist keep their refusal."""
    model = SimpleNamespace(build_kind="class_spell", route_family="pooled")
    with pytest.raises(RuntimeError, match="not ready for generalized manifest build"):
        _resolve_route_key_from_model(model)


def test_managed_overrides_doors_reuse_the_many_templates() -> None:
    """Both overrides tables map "managed" onto the `many` template objects."""
    doors = creation_runtime_door_compiler
    assert doors._OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE["managed"] is (
        doors._OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE["many"]
    )
    assert doors._OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE["managed"] is (
        doors._OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE["many"]
    )


@pytest.mark.parametrize("fast", (False, True))
def test_managed_no_overrides_doors_reuse_the_non_fast_many_templates(fast: bool) -> None:
    """Both fast bits of "managed" select the non-fast `many` templates (no fast-transient managed door)."""
    doors = creation_runtime_door_compiler
    assert doors._NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST[("managed", fast)] is (
        doors._NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST[("many", False)]
    )
    assert doors._NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST[("managed", fast)] is (
        doors._NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST[("many", False)]
    )


def test_rows_contain_managed_step_finds_a_managed_row() -> None:
    """One managed row anywhere is enough."""
    rows = ({"existence": "many"}, {"existence": Existence.managed_spell_quantity.name}, {"existence": "unique"})
    assert rows_contain_managed_step(rows) is True


def test_rows_contain_managed_step_is_false_without_a_managed_row() -> None:
    """Graphs of the six other members, and an empty lane, have none."""
    assert rows_contain_managed_step(({"existence": "many"}, {"existence": "unique"})) is False
    assert rows_contain_managed_step(()) is False


def test_many_child_of_a_managed_row_counts_as_feeding_a_holder() -> None:
    """A `many` row feeding a managed row is a holder's child, as for any non-`many` row."""
    rows = (
        {"existence": "many", "instance_key": ("x", 1), "dependency_resolution_order": ()},
        {
            "existence": Existence.managed_spell_quantity.name,
            "instance_key": ("m", None),
            "dependency_resolution_order": (("x", (("x", 1),)),),
        },
    )
    assert rows_feed_many_into_non_many_step(rows) is True
