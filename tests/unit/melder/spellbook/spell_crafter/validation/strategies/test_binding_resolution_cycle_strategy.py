from typing import Dict, List, Optional

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.binding_resolution_cycle_strategy import (
    BindingResolutionCycleStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils


class _SpellIndexStub:
    """
    Purpose:
        Provide a spell index stub with current id tracking.
    Contract:
        Exposes a current id value without validation.
    """

    def __init__(self, current: str) -> None:
        """
        Purpose:
            Initialize the index stub with a current id.
        Contract:
            Stores the provided id as current.
        Args:
            current: Spell id string.
        Returns:
            None.
        """
        self.current = current


class _RequirementStub:
    """
    Purpose:
        Provide a lightweight parameter requirement stub.
    Contract:
        Exposes attributes used for binding key derivation.
    """

    def __init__(
        self,
        *,
        name: str,
        di_shape: ParameterDIShape,
        spellmap_default: SpellMap,
    ) -> None:
        """
        Purpose:
            Initialize the requirement stub.
        Contract:
            Stores DI shape and SpellMap defaults for binding resolution.
        Args:
            name: Parameter name.
            di_shape: DI shape for the parameter.
            spellmap_default: SpellMap default instance.
        Returns:
            None.
        """
        self.name = name
        self.di_shape = di_shape
        self.spellmap_default = spellmap_default
        self.annotation = None
        self.collection_element_annotation = None
        self.default_value = spellmap_default


class _RequirementsStub:
    """
    Purpose:
        Provide a requirements stub with parameter access.
    Contract:
        Returns parameters in insertion order.
        Exposes a cleaned flag for strategy guards.
    """

    def __init__(
        self,
        parameters: list[_RequirementStub],
        *,
        cleaned: bool = False,
    ) -> None:
        """
        Purpose:
            Initialize the requirements stub.
        Contract:
            Stores the provided parameters and cleaned flag.
        Args:
            parameters: List of requirement stubs.
            cleaned: Whether this requirements artifact should appear cleaned.
        Returns:
            None.
        """
        self._parameters = list(parameters)
        self.cleaned = cleaned

    @property
    def parameters(self) -> tuple[_RequirementStub, ...]:
        """
        Purpose:
            Return parameters as a stable tuple.
        Contract:
            Preserves insertion order.
        Returns:
            tuple[_RequirementStub, ...]: Stored parameter list.
        """
        return tuple(self._parameters)


class _RaisingRequirementsStub(_RequirementsStub):
    @property
    def parameters(self):
        raise RuntimeError("requirements unavailable")


class _CrafterStub:
    """
    Purpose:
        Provide a crafter stub that exposes requirements.
    Contract:
        Stores requirements as provided.
    """

    def __init__(self, requirements: Optional[_RequirementsStub]) -> None:
        """
        Purpose:
            Initialize the stub with requirements.
        Contract:
            Stores requirements without mutation.
        Args:
            requirements: Requirements stub or None.
        Returns:
            None.
        """
        self.requirements = requirements


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with binding metadata.
    Contract:
        Exposes spellframe, spell_name, binding_name, and spell_index.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spellframe: object,
        spell_name: str,
        binding_name: Optional[str],
        requirements: Optional[_RequirementsStub],
    ) -> None:
        """
        Purpose:
            Initialize the spell stub and attach a crafter when needed.
        Contract:
            Sets spell_index.current and binding attributes.
        Args:
            spell_id: Spell id for spell_index.current.
            spellframe: Frame/interface identifier.
            spell_name: Spell name string.
            binding_name: Optional binding name.
            requirements: Requirements stub or None.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spellframe = spellframe
        self.spell_name = spell_name
        self.binding_name = binding_name
        self.requirements = requirements
        self._crafter = _CrafterStub(requirements)
        # Mirror the live Spell contract: `key` is the bind-time precomputed
        # canonical (frame_key, binding_key) tuple the strategy reads directly.
        self.key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub with local and contracted spell maps.
    Contract:
        Stores visible spells and a spell_id pool for validation strategies.
    """

    def __init__(
        self,
        *,
        spells: List[_SpellStub],
        contracted: Optional[List[_SpellStub]] = None,
    ) -> None:
        """
        Purpose:
            Initialize the spellbook stub with visible spells.
        Contract:
            Builds local and contracted spell maps without copies of spell objects.
        Args:
            spells: Local spell instances.
            contracted: Optional contracted spell instances.
        Returns:
            None.
        """
        self._spells: Dict[_SpellIndexStub, _SpellStub] = {
            spell.spell_index: spell for spell in spells
        }
        self._contracted_spells: Dict[str, Dict[_SpellIndexStub, _SpellStub]] = {}
        self._spell_id_pool: Dict[str, _SpellStub] = {
            spell.spell_index.current: spell for spell in spells
        }
        if contracted:
            self._contracted_spells["contracted"] = {
                spell.spell_index: spell for spell in contracted
            }
            for spell in contracted:
                self._spell_id_pool[spell.spell_index.current] = spell


def _spellmap_requirement(*, name: str, spellframe: object) -> _RequirementStub:
    """
    Purpose:
        Build a requirement stub for a SpellMap dependency.
    Contract:
        Creates a SPELLMAP_DEFAULT requirement targeting the spellframe.
    Args:
        name: Parameter name.
        spellframe: Target spellframe for the SpellMap.
    Returns:
        _RequirementStub: Requirement stub instance.
    """
    spellmap = SpellMap(spellframe=spellframe)
    return _RequirementStub(
        name=name,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=spellmap,
    )


class _CancelAfter:
    def __init__(self, threshold: int) -> None:
        self._checks = 0
        self._threshold = threshold

    @property
    def is_set(self):
        self._checks += 1
        return self._checks > self._threshold

    def throw_if_set(self):
        raise RuntimeError("cancelled")


def _make_context(
    spell: _SpellStub,
    *,
    spellbook: Optional[_SpellbookStub],
) -> tuple[SpellValidationContext, list]:
    """
    Purpose:
        Build a SpellValidationContext for binding cycle tests.
    Contract:
        Returns the context and the shared issues list.
    Args:
        spell: Root spell under validation.
        spellbook: Spellbook stub for spell iteration.
    Returns:
        tuple[SpellValidationContext, list]: Context and issues list.
    """
    issues: list = []
    context = SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=issues,
    )
    return context, issues


def test_binding_resolution_cycle_emits_issue() -> None:
    """
    Purpose:
        Verify binding cycles reachable from the root emit errors.
    Contract:
        Emits BINDING_RESOLUTION_CYCLE when a cycle is present.
    Returns:
        None.
    Raises:
        AssertionError: If the cycle diagnostic is missing.
    """
    class FrameA:
        """
        Purpose:
            Dummy frame for spell A.
        Contract:
            Acts as a stable spellframe identifier.
        """

    class FrameB:
        """
        Purpose:
            Dummy frame for spell B.
        Contract:
            Acts as a stable spellframe identifier.
        """

    req_a = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameB)])
    req_b = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameA)])

    spell_a = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=req_a,
    )
    spell_b = _SpellStub(
        spell_id="b",
        spellframe=FrameB,
        spell_name="spell-b",
        binding_name=None,
        requirements=req_b,
    )

    spellbook = _SpellbookStub(spells=[spell_a, spell_b])
    context, issues = _make_context(spell_a, spellbook=spellbook)

    BindingResolutionCycleStrategy().validate(context)

    assert issues
    assert issues[0].code == "BINDING_RESOLUTION_CYCLE"
    assert issues[0].severity == "error"


def test_binding_resolution_cycle_skips_when_acyclic() -> None:
    """
    Purpose:
        Verify no diagnostics are emitted for acyclic bindings.
    Contract:
        Leaves issues empty when no cycles are reachable.
    Returns:
        None.
    Raises:
        AssertionError: If any issues are emitted.
    """
    class FrameA:
        """
        Purpose:
            Dummy frame for the root spell.
        Contract:
            Acts as a stable spellframe identifier.
        """

    class FrameB:
        """
        Purpose:
            Dummy frame for the dependency spell.
        Contract:
            Acts as a stable spellframe identifier.
        """

    req_a = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameB)])
    req_b = _RequirementsStub([])

    spell_a = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=req_a,
    )
    spell_b = _SpellStub(
        spell_id="b",
        spellframe=FrameB,
        spell_name="spell-b",
        binding_name=None,
        requirements=req_b,
    )

    spellbook = _SpellbookStub(spells=[spell_a, spell_b])
    context, issues = _make_context(spell_a, spellbook=spellbook)

    BindingResolutionCycleStrategy().validate(context)

    assert issues == []


def test_binding_resolution_cycle_returns_when_spell_or_spellbook_missing() -> None:
    class FrameA:
        pass

    spell = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=None,
    )
    context, issues = _make_context(spell, spellbook=None)

    BindingResolutionCycleStrategy().validate(context)
    assert issues == []

    context.spell = None
    BindingResolutionCycleStrategy().validate(context)
    assert issues == []


def test_binding_resolution_cycle_honors_cancellation_before_scan() -> None:
    class FrameA:
        pass

    spell = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=None,
    )
    spellbook = _SpellbookStub(spells=[spell])
    context, _ = _make_context(spell, spellbook=spellbook)
    context.cancel_event = _CancelAfter(0)

    with pytest.raises(RuntimeError, match="cancelled"):
        BindingResolutionCycleStrategy().validate(context)


def test_binding_resolution_cycle_honors_cancellation_during_spellbook_scan() -> None:
    class FrameA:
        pass

    class FrameB:
        pass

    req_a = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameB)])
    spell_a = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=req_a,
    )
    spell_b = _SpellStub(
        spell_id="b",
        spellframe=FrameB,
        spell_name="spell-b",
        binding_name=None,
        requirements=None,
    )
    spellbook = _SpellbookStub(spells=[spell_a, spell_b])
    context, _ = _make_context(spell_a, spellbook=spellbook)
    context.cancel_event = _CancelAfter(1)

    with pytest.raises(RuntimeError, match="cancelled"):
        BindingResolutionCycleStrategy().validate(context)


def test_binding_resolution_cycle_skips_unusable_spellbook_entries() -> None:
    class FrameA:
        pass

    class FrameB:
        pass

    plain_requirement = _RequirementStub(
        name="plain",
        di_shape=ParameterDIShape.PLAIN,
        spellmap_default=SpellMap(spellframe=FrameB),
    )
    root_requirements = _RequirementsStub([plain_requirement])
    cleaned_requirements = _RequirementsStub([], cleaned=True)
    raising_requirements = _RaisingRequirementsStub([])

    root_spell = _SpellStub(
        spell_id="root",
        spellframe=FrameA,
        spell_name="root-spell",
        binding_name=None,
        requirements=root_requirements,
    )
    no_crafter_spell = _SpellStub(
        spell_id="no-crafter",
        spellframe=FrameB,
        spell_name="no-crafter",
        binding_name=None,
        requirements=None,
    )
    no_crafter_spell.requirements = None
    no_requirements_spell = _SpellStub(
        spell_id="no-req",
        spellframe=FrameB,
        spell_name="no-req",
        binding_name=None,
        requirements=None,
    )
    cleaned_spell = _SpellStub(
        spell_id="cleaned",
        spellframe=FrameB,
        spell_name="cleaned",
        binding_name=None,
        requirements=cleaned_requirements,
    )
    raising_spell = _SpellStub(
        spell_id="raising",
        spellframe=FrameB,
        spell_name="raising",
        binding_name=None,
        requirements=raising_requirements,
    )

    spellbook = _SpellbookStub(
        spells=[
            root_spell,
            no_crafter_spell,
            no_requirements_spell,
            cleaned_spell,
            raising_spell,
        ]
    )
    context, issues = _make_context(root_spell, spellbook=spellbook)

    BindingResolutionCycleStrategy().validate(context)

    assert issues == []


def test_binding_resolution_cycle_collects_duplicate_spells_per_binding_key() -> None:
    class FrameA:
        pass

    class FrameB:
        pass

    req_a = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameB)])
    req_b = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameA)])
    root_spell = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=req_a,
    )
    dep_spell = _SpellStub(
        spell_id="b",
        spellframe=FrameB,
        spell_name="spell-b",
        binding_name=None,
        requirements=req_b,
    )
    duplicate_root = _SpellStub(
        spell_id="a-copy",
        spellframe=FrameA,
        spell_name="spell-a-copy",
        binding_name=None,
        requirements=None,
    )
    unrelated = _SpellStub(
        spell_id="other",
        spellframe=str,
        spell_name="other",
        binding_name="x",
        requirements=None,
    )

    spellbook = _SpellbookStub(spells=[root_spell, dep_spell, unrelated], contracted=[duplicate_root])
    context, issues = _make_context(root_spell, spellbook=spellbook)

    strategy = BindingResolutionCycleStrategy()
    strategy.validate(context)

    assert len(issues) == 1
    cycle_spells = issues[0].details["cycle_spells"]
    root_key = strategy._format_key(root_spell.key)  # noqa: SLF001
    assert cycle_spells[root_key] == ["a", "a-copy"]
    assert "str:x" not in cycle_spells


def test_binding_resolution_cycle_honors_cancellation_during_cycle_spell_collection() -> None:
    class FrameA:
        pass

    class FrameB:
        pass

    req_a = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameB)])
    req_b = _RequirementsStub([_spellmap_requirement(name="dep", spellframe=FrameA)])
    spell_a = _SpellStub(
        spell_id="a",
        spellframe=FrameA,
        spell_name="spell-a",
        binding_name=None,
        requirements=req_a,
    )
    spell_b = _SpellStub(
        spell_id="b",
        spellframe=FrameB,
        spell_name="spell-b",
        binding_name=None,
        requirements=req_b,
    )
    spellbook = _SpellbookStub(spells=[spell_a, spell_b])
    context, _ = _make_context(spell_a, spellbook=spellbook)
    context.cancel_event = _CancelAfter(6)

    with pytest.raises(RuntimeError, match="cancelled"):
        BindingResolutionCycleStrategy().validate(context)


def test_binding_key_for_requirement_covers_supported_shapes() -> None:
    strategy = BindingResolutionCycleStrategy()

    class FrameA:
        pass

    assert strategy._binding_key_for_requirement(  # noqa: SLF001
        _RequirementStub(
            name="single-none",
            di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
            spellmap_default=SpellMap(spellframe=FrameA),
        )
    ) is None

    single_requirement = _RequirementStub(
        name="single",
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        spellmap_default=SpellMap(spellframe=FrameA),
    )
    single_requirement.annotation = FrameA
    assert strategy._binding_key_for_requirement(single_requirement) == ("framea", "__default__")  # noqa: SLF001

    collection_requirement = _RequirementStub(
        name="collection",
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        spellmap_default=SpellMap(spellframe=FrameA),
    )
    assert strategy._binding_key_for_requirement(collection_requirement) is None  # noqa: SLF001
    collection_requirement.collection_element_annotation = FrameA
    assert strategy._binding_key_for_requirement(collection_requirement) == ("framea", "__default__")  # noqa: SLF001

    spellmap_requirement = _RequirementStub(
        name="map",
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=None,
    )
    assert strategy._binding_key_for_requirement(spellmap_requirement) is None  # noqa: SLF001
    spellmap_requirement.spellmap_default = SpellMap(spellframe=FrameA, binding_name="named")
    assert strategy._binding_key_for_requirement(spellmap_requirement) == ("framea", "named")  # noqa: SLF001

    contract_requirement = _RequirementStub(
        name="contract",
        di_shape=ParameterDIShape.SPELL_CONTRACT,
        spellmap_default=None,
    )
    contract_requirement.default_value = None
    assert strategy._binding_key_for_requirement(contract_requirement) is None  # noqa: SLF001
    contract_requirement.default_value = SpellContract(spellframe=FrameA, binding_name="contract")
    assert strategy._binding_key_for_requirement(contract_requirement) == ("framea", "contract")  # noqa: SLF001

    plain_requirement = _RequirementStub(
        name="plain",
        di_shape=ParameterDIShape.PLAIN,
        spellmap_default=None,
    )
    assert strategy._binding_key_for_requirement(plain_requirement) is None  # noqa: SLF001


def test_binding_resolution_cycle_helper_methods_cover_fallbacks() -> None:
    strategy = BindingResolutionCycleStrategy()

    class FrameA:
        pass

    # Node keys now come from the bind-time `Spell.key` contract; the strategy
    # no longer owns a per-spell key normalization helper.
    assert SpellInputUtils.make_spell_key_from_parts(
        spellframe=FrameA,
        spell_name="SpellA",
        binding_name=None,
    ) == ("framea", "__default__")

    assert strategy._normalize_cycle([]) == ()  # noqa: SLF001
    assert strategy._normalize_cycle(  # noqa: SLF001
        [("z", "z"), ("a", "a"), ("m", "m"), ("z", "z")]
    ) == (("a", "a"), ("m", "m"), ("z", "z"), ("a", "a"))

    graph = {
        ("A", "__default__"): {("B", "__default__"), ("C", "__default__")},
        ("B", "__default__"): {("D", "__default__")},
        ("C", "__default__"): {("D", "__default__")},
    }
    assert strategy._detect_cycles(("A", "__default__"), graph, None) == []  # noqa: SLF001


def test_binding_resolution_cycle_detect_cycles_honors_cancellation() -> None:
    strategy = BindingResolutionCycleStrategy()
    graph = {
        ("A", "__default__"): {("B", "__default__")},
        ("B", "__default__"): {("A", "__default__")},
    }

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy._detect_cycles(  # noqa: SLF001
            ("A", "__default__"),
            graph,
            _CancelAfter(0),
        )
