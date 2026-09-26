from typing import TYPE_CHECKING



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import SpellRequirements
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class RequiredHolesStrategy(SpellValidationStrategy):
    """
    Surface any **required holes** discovered in Phase 1.

    Required holes are parameters that:

        * Are classified as PLAIN (no DI).
        * Have **no default value**.
        * Therefore must be satisfied by the caller (e.g. via spell overrides,
          manual composition, or root-level parameters in meld()).

    Contract:
    - Reports caller-required parameters that Melder DI will never satisfy.
    - Emits warnings rather than hard errors because the caller may still
      provide these values at invocation time.
    - Also reports resolved OVERRIDE_REQUIRED sockets from durable local topology.
      Non-resolvable roots have no construction-input obligations.
    - Also reports UNRESOLVED_INPUT sockets (a typed parameter no registered
      spell provides) with the expected type, so a forgotten binding is visible
      at conjure even though constructing the spell without the value only fails
      at meld.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; it consumes the Phase-1
        `SpellRequirements.iter_required_holes()` view.

    System Context:
        Phase 4 (validation) of the conjure pipeline. It emits warnings only - they
        ride along without breaking the build.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: emits a REQUIRED_HOLE warning per PLAIN,
        default-less parameter - a hole Melder DI will never fill, so the caller must supply it
        via overrides or manual composition - plus OVERRIDE_REQUIRED and UNRESOLVED_INPUT
        warnings for supplied-input sockets. Reporting only.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the required-holes strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="required_holes",
            description="Flags parameters that DI will never satisfy and that lack defaults.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Emit warnings for required holes discovered in the requirements model.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits one `REQUIRED_HOLE` warning per parameter that must be supplied
          by the caller.
        - Performs reporting only; it does not attempt to synthesize defaults
          or convert the hole into a DI target.
        - Reads reference-only required inputs from SpellSystemStates without
          taking ownership of their topology or changing declaration facts.
        - Emits one `UNRESOLVED_INPUT` warning per unresolved-input socket,
          naming the expected type from the Phase-1 annotation.

        Raises:
            RuntimeError: If an UNRESOLVED_INPUT socket has no matching Phase-1
                parameter (topology and requirements out of step).
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        requirements = context.requirements
        if requirements is None:
            return

        spell = context.spell
        if not spell.resolvable:
            return

        for param in requirements.iter_required_holes():
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="REQUIRED_HOLE",
                    message=(
                        f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                        "cannot be satisfied by Melder DI and has no default. "
                        "The caller must supply a value (e.g. via spell overrides "
                        "or manual composition)."
                    ),
                    details={
                        "parameter_name": param.name,
                        "position": param.position,
                        "annotation": param.annotation,
                    },
                )
            )

        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        if topology is None:
            return
        for socket in topology.sockets:
            if socket.socket_kind is SocketKind.UNRESOLVED_INPUT:
                expected_type = self._expected_type_for(requirements, socket.param_name)
                context.issues.append(
                    SpellValidationIssue(
                        severity="warning",
                        code="UNRESOLVED_INPUT",
                        message=(
                            f"Parameter {socket.param_name!r} on spell {spell.spell_name!r} expects "
                            f"{expected_type}, but no registered spell provides it. Supply it through a "
                            f"meld override (key {socket.param_name!r}, or a path key ending in "
                            f"'>{socket.param_name}' when this spell is built as a dependency) or bind "
                            f"a provider for {expected_type}. Constructing this spell without it raises "
                            "UnresolvedInputError."
                        ),
                        details={
                            "spell_id": spell.spell_id,
                            "parameter_name": socket.param_name,
                            "position": socket.position,
                            "parameter_kind": socket.parameter_kind,
                            "expected_type": expected_type,
                            "dependency_key": socket.dependency_key,
                        },
                    )
                )
                continue
            if socket.socket_kind is not SocketKind.OVERRIDE_REQUIRED:
                continue
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="OVERRIDE_REQUIRED",
                    message=(
                        f"Parameter {socket.param_name!r} on spell {spell.spell_name!r} "
                        "references a non-resolvable definition. Supply its value through "
                        "a meld override when constructing this consumer."
                    ),
                    details={
                        "spell_id": spell.spell_id,
                        "parameter_name": socket.param_name,
                        "position": socket.position,
                        "parameter_kind": socket.parameter_kind,
                        "referenced_spell_ids": socket.referenced_spell_ids,
                    },
                )
            )

    @staticmethod
    def _expected_type_for(requirements: SpellRequirements, param_name: str) -> str:
        """
        Name the expected type of one unresolved-input parameter.

        Contract:
            - Reads the Phase-1 annotation of `param_name` and renders it with
              `UnresolvedInputError.expected_type_name`, the rule the meld-time
              error also uses.

        Args:
            requirements: Phase-1 requirements of the spell under validation.
            param_name: Parameter carried by the UNRESOLVED_INPUT socket.

        Returns:
            str: Display name of the expected type.

        Raises:
            RuntimeError: If `param_name` is not a Phase-1 parameter.
        """
        for param in requirements.parameters:
            if param.name == param_name:
                return UnresolvedInputError.expected_type_name(param.annotation)
        raise RuntimeError(
            f"UNRESOLVED_INPUT socket {param_name!r} has no Phase-1 parameter. "
            "Re-run the structural phases for this spell."
        )
