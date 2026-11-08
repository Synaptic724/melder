from typing import TYPE_CHECKING, Dict, List, Optional

# Melder imports
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import ParameterDIShape
from melder.aether.spellbook.spell_compiler.validation.hidden_provider_report import HiddenProviderReport
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
        SpellParameterRequirement,
    )
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext
    from melder.aether.spellbook.spellbook import Spellbook


class HiddenProviderStrategy(SpellValidationStrategy):
    """
    Refuse a spell whose class lookup finds its class only where the lookup cannot reach it, and say where it is bound.

    A class lookup - a class annotation, a single string annotation's type part, `Optional[Class]` without a
    default, `SpellMap(spell=Class)` without a spellframe - reaches a spell only when it is bound bare, with no
    spellframe and the default binding (2026-11-07). The owner's rule for TASK-2026-11-07-spellframe_ambiguity_
    validation_check part (a): a consumer whose class is bound only under a spellframe or only under a binding name is
    refused at conjure by a Phase 4 error that names where the class is bound and the lookup to use (patch
    hidden_provider_2026_11_07, approved 2026-11-07). Phase 3 records such a parameter as an UNRESOLVED_INPUT socket
    carrying the hidden candidates (`SpellSocketDescriptor.hidden_spell_ids`); this strategy turns each into one
    HIDDEN_PROVIDER error. A class also bound bare is found by Phase 3, so its socket carries no candidates and this
    strategy says nothing.

    Contract:
    - One `HIDDEN_PROVIDER` error per UNRESOLVED_INPUT socket with `hidden_spell_ids`; every other socket is ignored.
    - The annotation form (`HiddenProviderReport.annotation_message`) names the parameter, the expected type
      (rendered as `UnresolvedInputError.expected_type_name` renders it), each candidate's address with the
      `SpellMap` that reaches it, and a Protocol annotation where one applies; the SpellMap form
      (`HiddenProviderReport.spellmap_message`) is used when the parameter's Phase-1 shape is SPELLMAP_DEFAULT.
      Neither offers a meld override: a refused spell's melds are refused, override or not.
    - Candidates are found with `context.spellbook.find_spell_by_spell_id`, which searches the Book's own active and
      parked spells, and then among the copies the Book borrows from peer conduits
      (`Spellbook._find_contracted_spell_by_id`), so a borrowed candidate renders as an owned one does (STEP 3 of the
      patch, 0.2.8281); an id neither finds (removed between phases) renders as `spell id <id>` and never raises, and
      when no candidate is found at all the report's remedy names no SpellMap.
    - `details` carries `spell_id`, `parameter_name`, `lookup` ("annotation" or "spellmap"), `expected_type` or
      `spellmap`, `dependency_key` and `candidates` (the `HiddenProviderReport.describe` dicts in address order, each
      with its `use`), so tooling can act without parsing text.
    - Emits into the supplied context; mutates no graph, topology or spell.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        One built-in of the `validation/strategies` family, registered into `SpellValidationSystem` right after
        `AmbiguousProviderStrategy`; `RequiredHolesStrategy` skips the sockets this strategy reports, so they are not
        also listed as UNRESOLVED_INPUT warnings.

    System Context:
        Phase 4 (validation) of the conjure pipeline. Its error marks the spell broken: conjure refuses through
        `SpellbookValidationError`; a consumer late-bound into a dynamic world is refused at that bind and stays
        registered and invalid, so every meld after it raises the same report, as AMBIGUOUS_PROVIDER does.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: emits one HIDDEN_PROVIDER error per UNRESOLVED_INPUT socket whose class
        is bound only under a spellframe or a binding name, naming each address and the SpellMap that reaches it.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the hidden-provider strategy.

        Contract:
            Seeds the stable strategy name/description published through the validation pipeline.
        """
        super().__init__(
            name="hidden_provider",
            description="Refuses a class lookup whose class is bound only under a spellframe or a binding name, "
                        "and says where.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Emit one HIDDEN_PROVIDER error per UNRESOLVED_INPUT socket that recorded hidden candidates.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Reads the spell's Phase-3 topology through the spell's `SpellSystemStates`; a spell with no topology
          (stand-ins, or validation without Phase 3) yields nothing.
        - Never raises for a candidate id the spellbook cannot resolve; the entry is rendered by id.

        Args:
            context: Validation context of the spell under validation.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        if topology is None:
            return
        for socket in topology.iter_sockets():
            if socket.socket_kind is not SocketKind.UNRESOLVED_INPUT or not socket.hidden_spell_ids:
                continue
            context.issues.append(self._issue_for(context, socket))

    def _issue_for(self, context: SpellValidationContext, socket: SpellSocketDescriptor) -> SpellValidationIssue:
        """
        Build the HIDDEN_PROVIDER issue for one socket, in the annotation or the SpellMap form.

        Contract:
            - The SpellMap form when the parameter's Phase-1 shape is SPELLMAP_DEFAULT with a captured SpellMap;
              the annotation form otherwise (a missing requirement renders the parameter name as the type, so the
              report never fails on a rendering detail).

        Args:
            context: Validation context of the spell under validation.
            socket: An UNRESOLVED_INPUT socket with hidden candidates.

        Returns:
            SpellValidationIssue: The error.
        """
        spell = context.spell
        candidates = self._describe_candidates(context, socket)
        param = self._requirement_for(context, socket.param_name)
        details: Dict[str, object] = {
            "spell_id": spell.spell_id,
            "parameter_name": socket.param_name,
            "dependency_key": socket.dependency_key,
        }
        spellmap = (
            param.spellmap_default
            if param is not None and param.di_shape is ParameterDIShape.SPELLMAP_DEFAULT
            else None
        )
        if spellmap is not None:
            class_name = HiddenProviderReport.spell_display_name(spellmap.spell)
            message = HiddenProviderReport.spellmap_message(
                param_name=socket.param_name,
                consumer_name=spell.spell_name,
                class_name=class_name,
                binding_name=spellmap.binding_name,
                candidates=candidates,
            )
            details["lookup"] = "spellmap"
            details["spellmap"] = HiddenProviderReport.spellmap_text(class_name, spellmap.binding_name)
            details["candidates"] = HiddenProviderReport.with_uses(
                candidates, shape=HiddenProviderReport.SHAPE_SPELLMAP, class_name=class_name,
            )
        else:
            expected_type = (
                socket.param_name if param is None else UnresolvedInputError.expected_type_name(param.annotation)
            )
            message = HiddenProviderReport.annotation_message(
                param_name=socket.param_name,
                consumer_name=spell.spell_name,
                expected_type=expected_type,
                candidates=candidates,
            )
            details["lookup"] = "annotation"
            details["expected_type"] = expected_type
            details["candidates"] = HiddenProviderReport.with_uses(candidates, shape=HiddenProviderReport.SHAPE_SINGLE)
        return SpellValidationIssue(severity="error", code="HIDDEN_PROVIDER", message=message, details=details)

    @staticmethod
    def _requirement_for(context: SpellValidationContext, param_name: str) -> Optional[SpellParameterRequirement]:
        """
        Return the Phase-1 requirement of one parameter, or None.

        Contract:
            None when the context carries no requirements or they do not list the parameter.

        Args:
            context: Validation context of the spell under validation.
            param_name: The socket's parameter.

        Returns:
            Optional[SpellParameterRequirement]: The requirement.
        """
        requirements = context.requirements
        if requirements is None:
            return None
        for param in requirements.parameters:
            if param.name == param_name:
                return param
        return None

    @classmethod
    def _describe_candidates(
            cls,
            context: SpellValidationContext,
            socket: SpellSocketDescriptor,
    ) -> List[Dict[str, Optional[str]]]:
        """
        Describe each hidden candidate the socket recorded.

        Contract:
            - One `HiddenProviderReport.describe` dict per id, in recorded order (the report orders by address).
            - Each id is found by `_find_candidate`: an own spell of the Book or a copy it borrows, so a borrowed
              candidate is described - and rendered - as an owned one is.
            - A candidate found nowhere (removed between phases) is described by id only.

        Args:
            context: Validation context of the spell under validation.
            socket: The UNRESOLVED_INPUT socket.

        Returns:
            List[Dict[str, Optional[str]]]: The candidate descriptions.
        """
        spellbook = context.spellbook
        return [
            HiddenProviderReport.describe(candidate_id, cls._find_candidate(spellbook, candidate_id))
            for candidate_id in socket.hidden_spell_ids
        ]

    @staticmethod
    def _find_candidate(spellbook: Optional[Spellbook], candidate_id: str) -> Optional[Spell]:
        """
        Find one hidden candidate: an own spell of the Book, else a copy the Book borrows from a peer conduit.

        Purpose:
            Phase 3 finds hidden candidates in the Book's spell_id pool, which holds the copies a peer granted by
            contract as well as the Book's own spells, so a hidden candidate can be a borrowed copy.
            `Spellbook.find_spell_by_spell_id` answers for own spells only; a borrowed candidate rendered as
            `spell id <id>`, with no address and no SpellMap (finding c of patch hidden_provider_2026_11_07, fixed in
            its STEP 3, 0.2.8281).

        Contract:
            - `Spellbook.find_spell_by_spell_id` first: the Book's own active and parked spells.
            - Then the Book's borrowed copies, peer by peer, through `Spellbook._find_contracted_spell_by_id` - the
              walk `Conduit.find_contracted_spell` makes over the same maps; no lookup surface is added.
            - Lock-free, as both lookups are: Phase 4 runs while conjure holds the Book lock. The peer ids are copied
              with one `list(...)` call, exact under a concurrent link or sever on 3.14t; a peer linked or severed
              meanwhile may be missed or still answered, and is then rendered by id.
            - None for a stand-in context without a Book, and for an id neither lookup finds (a spell removed
              between phases); never raises for a missing spell.

        Args:
            spellbook: The Book under validation, or None for a stand-in context.
            candidate_id: A hidden candidate's spell_id as Phase 3 recorded it.

        Returns:
            Optional[Spell]: The candidate, or None.
        """
        if spellbook is None:
            return None
        own = spellbook.find_spell_by_spell_id(candidate_id)
        if own is not None:
            return own
        for conduit_id in list(spellbook._contracted_spells):
            borrowed = spellbook._find_contracted_spell_by_id(candidate_id, conduit_id)
            if borrowed is not None:
                return borrowed
        return None
