from typing import TYPE_CHECKING, Any, Dict, List



# Melder imports
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import SpellRequirements
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class AmbiguousProviderStrategy(SpellValidationStrategy):
    """
    Refuse a spell whose single typed parameter has several registered providers, and say which.

    Ambiguity is a configuration error, never an input the meld could pick for the caller (owner
    ruling 2026-10-04: a hard error, no warning). Phase 3 records such a parameter as an
    `AMBIGUOUS_INPUT` socket instead of raising, so this strategy is what refuses the spell - through
    the readable validation report, with every candidate's address and the remedies, where the
    former Phase-3 `RuntimeError` surfaced as a compiler trace.

    Contract:
    - One `AMBIGUOUS_PROVIDER` error per `AMBIGUOUS_INPUT` socket of the spell's Phase-3 topology.
    - The message names the parameter, the expected type (rendered as the meld-time
      `UnresolvedInputError` renders it), each candidate as `<spell_name> at (spellframe=...,
      binding_name=...)` ordered by address, and the three ways out: a `SpellMap`
      default on the parameter, a meld override, or a single provider of the type.
    - `details` carries `spell_id`, `parameter_name`, `expected_type` and `candidates` (a list of
      `{spell_id, spell_name, spellframe, binding_name}`), so tooling can act without parsing text.
    - A candidate the spellbook can no longer find (removed between phases) is rendered by id only.
    - Emits into the supplied context; mutates no graph, topology or spell.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        One built-in of the `validation/strategies` family, registered into `SpellValidationSystem`
        after `RequiredHolesStrategy` (which reports the sibling UNRESOLVED_INPUT sockets as warnings).

    System Context:
        Phase 4 (validation) of the conjure pipeline. Its error marks the spell broken: conjure refuses
        through `SpellbookValidationError`, and a consumer late-bound into a dynamic world is refused at
        its first meld by the meld-time validation gate.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: emits one AMBIGUOUS_PROVIDER error per AMBIGUOUS_INPUT
        socket, naming the parameter, the expected type, every candidate's address and the remedies.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the ambiguous-provider strategy.

        Contract:
            Seeds the stable strategy name/description published through the validation pipeline.
        """
        super().__init__(
            name="ambiguous_provider",
            description="Refuses a single typed parameter that several registered spells provide.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Emit one AMBIGUOUS_PROVIDER error per ambiguous socket of the spell.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Reads the spell's Phase-3 topology through the spell's `SpellSystemStates`; a spell with no
          topology (stand-ins, or validation without Phase 3) yields nothing.
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
            if socket.socket_kind is not SocketKind.AMBIGUOUS_INPUT:
                continue
            expected_type = self._expected_type_for(context.requirements, socket.param_name)
            candidates = self._describe_candidates(context, socket)
            rendered = "; ".join(self._render_candidate(candidate) for candidate in candidates)
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="AMBIGUOUS_PROVIDER",
                    message=(
                        f"Parameter {socket.param_name!r} on spell {spell.spell_name!r} expects "
                        f"{expected_type}, but {len(candidates)} registered spells provide it: {rendered}. "
                        f"Select one with a SpellMap default on the parameter "
                        f"(SpellMap(spellframe=..., binding_name=...)), supply it at meld with "
                        f"override={{{socket.param_name!r}: ...}}, or bind only one provider of this type."
                    ),
                    details={
                        "spell_id": spell.spell_id,
                        "parameter_name": socket.param_name,
                        "expected_type": expected_type,
                        "candidates": candidates,
                    },
                )
            )

    @staticmethod
    def _expected_type_for(requirements: "SpellRequirements | None", param_name: str) -> str:
        """
        Name the expected type of the ambiguous parameter.

        Contract:
            - Renders the Phase-1 annotation of `param_name` with
              `UnresolvedInputError.expected_type_name`, the rule the meld-time errors use.
            - Returns the parameter name itself when requirements are absent or do not carry the
              parameter, so the report never fails on a rendering detail.

        Args:
            requirements: Phase-1 requirements of the spell under validation, when available.
            param_name: Parameter carried by the AMBIGUOUS_INPUT socket.

        Returns:
            str: Display name of the expected type.
        """
        if requirements is not None:
            for param in requirements.parameters:
                if param.name == param_name:
                    return UnresolvedInputError.expected_type_name(param.annotation)
        return param_name

    @staticmethod
    def _describe_candidates(context: SpellValidationContext, socket: SpellSocketDescriptor) -> List[Dict[str, Any]]:
        """
        Describe each candidate the socket recorded with its address.

        Contract:
            - One entry per `referenced_spell_ids` id, ordered by address (spellframe, binding_name,
              spell_name; None sorts first): `{spell_id, spell_name, spellframe, binding_name}`;
              `spellframe` is the frame's display name (a string category as itself, a Protocol by
              `__name__`) or None, `binding_name` the bound name or None.
            - A candidate the spellbook cannot find renders with `spell_name` None and no address.

        Args:
            context: Validation context of the spell under validation.
            socket: The AMBIGUOUS_INPUT socket.

        Returns:
            List[Dict[str, Any]]: The candidate descriptions.
        """
        described: List[Dict[str, Any]] = []
        spellbook = context.spellbook
        for candidate_id in socket.referenced_spell_ids:
            candidate: "Spell | None" = spellbook.find_spell_by_id(candidate_id) if spellbook is not None else None
            if candidate is None:
                described.append({"spell_id": candidate_id, "spell_name": None, "spellframe": None, "binding_name": None})
                continue
            frame = candidate.spellframe
            described.append({
                "spell_id": candidate_id,
                "spell_name": candidate.spell_name,
                "spellframe": None if frame is None else getattr(frame, "__name__", str(frame)),
                "binding_name": candidate.binding_name,
            })
        described.sort(key=lambda entry: (entry["spellframe"] or "", entry["binding_name"] or "", entry["spell_name"] or ""))
        return described

    @staticmethod
    def _render_candidate(candidate: Dict[str, Any]) -> str:
        """
        Render one candidate as `<spell_name> at (spellframe=..., binding_name=...)`.

        Args:
            candidate: One entry of `_describe_candidates`.

        Returns:
            str: The rendered candidate; an unresolvable one renders as `spell id <id>`.
        """
        if candidate["spell_name"] is None:
            return f"spell id {candidate['spell_id']}"
        return (
            f"{candidate['spell_name']} at (spellframe={candidate['spellframe']!r}, "
            f"binding_name={candidate['binding_name']!r})"
        )
