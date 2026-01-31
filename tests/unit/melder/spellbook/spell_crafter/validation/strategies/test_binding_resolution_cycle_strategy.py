from typing import Dict, List, Optional

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.strategies.binding_resolution_cycle_strategy import (
    BindingResolutionCycleStrategy,
)


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
        self._crafter = _CrafterStub(requirements)


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
