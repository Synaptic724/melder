import inspect
from typing import TYPE_CHECKING, Any, Optional, get_args, get_origin



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
if TYPE_CHECKING:
    from melder.aether.conduit.meld.contracts.spell_map import SpellMap
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import SpellRequirements
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor
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
    - For a set, frozenset, dict or tuple parameter the REQUIRED_HOLE message adds
      that Melder injects collections only as `list[T]`, so such a parameter is
      always supplied by the caller (2026-09-26; the Phase-4 annotation-shape
      guard no longer judges these parameters).
    - Also reports resolved OVERRIDE_REQUIRED sockets from durable local topology.
      Non-resolvable roots have no construction-input obligations.
    - Also reports UNRESOLVED_INPUT sockets (a typed parameter no registered
      spell provides, or a SpellMap default whose address has nothing bound -
      2026-11-16, GitHub #329) with the expected type - for a SpellMap, the
      SpellMap as written - so a forgotten binding is visible at conjure even
      though constructing the spell without the value only fails at meld.
    - Skips an UNRESOLVED_INPUT socket that carries hidden candidates
      (`hidden_spell_ids`, 2026-11-07): its class IS registered, under a
      spellframe or a binding name, and `HiddenProviderStrategy` refuses the
      spell with HIDDEN_PROVIDER naming where - a warning saying no registered
      spell provides it would contradict that error.

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
        via overrides or manual composition; for set/dict/tuple parameters the message adds
        that Melder injects collections only as list[T] - plus OVERRIDE_REQUIRED and UNRESOLVED_INPUT
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
          by the caller; a set/frozenset/dict/tuple annotation adds the
          list-only collection hint (`_container_hint`).
        - Performs reporting only; it does not attempt to synthesize defaults
          or convert the hole into a DI target.
        - Reads reference-only required inputs from SpellSystemStates without
          taking ownership of their topology or changing declaration facts.
        - Emits one `UNRESOLVED_INPUT` warning per unresolved-input socket
          (`_unresolved_input_issue`), naming the expected type from the Phase-1
          annotation, or the SpellMap a SpellMap parameter defaults to - except a
          socket with hidden candidates, which HIDDEN_PROVIDER reports as an error.

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
                        f"{self._container_hint(param.annotation)}"
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
                if socket.hidden_spell_ids:
                    # The class is bound under a spellframe or a binding name:
                    # HiddenProviderStrategy refuses the spell naming where.
                    continue
                context.issues.append(self._unresolved_input_issue(spell, requirements, socket))
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

    def _unresolved_input_issue(
            self,
            spell: Spell,
            requirements: SpellRequirements,
            socket: SpellSocketDescriptor,
    ) -> SpellValidationIssue:
        """
        Build the UNRESOLVED_INPUT warning for one unresolved-input socket without hidden candidates.

        Contract:
            - A parameter whose default is a SpellMap (2026-11-16, GitHub #329: a
              SpellMap that matches nothing waits as an unresolved input) is named
              by that SpellMap as written (`UnresolvedInputError._spellmap_address_name`)
              and the text asks for a spell at that address; `details["expected_type"]`
              is that rendering.
            - Any other parameter keeps the typed text: the expected type from its
              Phase-1 annotation (`_expected_type_for`), unchanged.
            - The details always carry spell_id, parameter_name, position,
              parameter_kind, expected_type and dependency_key.

        Args:
            spell: The spell under validation.
            requirements: Its Phase-1 requirements.
            socket: The UNRESOLVED_INPUT socket.

        Returns:
            SpellValidationIssue: The warning.

        Raises:
            RuntimeError: If the socket has no matching Phase-1 parameter
                (topology and requirements out of step).
        """
        spell_map = self._spell_map_for(requirements, socket.param_name)
        if spell_map is not None:
            expected_type = UnresolvedInputError._spellmap_address_name(spell_map)
            message = (
                f"Parameter {socket.param_name!r} on spell {spell.spell_name!r} asks for the spell its default "
                f"{expected_type} names, but nothing is bound there. Supply it through a meld override (key "
                f"{socket.param_name!r}, or a path key ending in '>{socket.param_name}' when this spell is built as "
                "a dependency) or bind a spell at that address. Constructing this spell without it raises "
                "UnresolvedInputError."
            )
        else:
            expected_type = self._expected_type_for(requirements, socket.param_name)
            message = (
                f"Parameter {socket.param_name!r} on spell {spell.spell_name!r} expects "
                f"{expected_type}, but no registered spell provides it. Supply it through a "
                f"meld override (key {socket.param_name!r}, or a path key ending in "
                f"'>{socket.param_name}' when this spell is built as a dependency) or bind "
                f"a provider for {expected_type}. Constructing this spell without it raises "
                "UnresolvedInputError."
            )
        return SpellValidationIssue(
            severity="warning",
            code="UNRESOLVED_INPUT",
            message=message,
            details={
                "spell_id": spell.spell_id,
                "parameter_name": socket.param_name,
                "position": socket.position,
                "parameter_kind": socket.parameter_kind,
                "expected_type": expected_type,
                "dependency_key": socket.dependency_key,
            },
        )

    @staticmethod
    def _spell_map_for(requirements: SpellRequirements, param_name: str) -> Optional[SpellMap]:
        """
        Return the SpellMap one unresolved-input parameter defaults to, or None.

        Contract:
            - Reads the Phase-1 `spellmap_default` of `param_name`: set only for a
              SPELLMAP_DEFAULT parameter. None for any other parameter, and for a
              name with no Phase-1 parameter (`_expected_type_for` then raises).
            - Pure; reads only the requirements.

        Args:
            requirements: Phase-1 requirements of the spell under validation.
            param_name: Parameter carried by the UNRESOLVED_INPUT socket.

        Returns:
            Optional[SpellMap]: The parameter's SpellMap default, or None.
        """
        for param in requirements.parameters:
            if param.name == param_name:
                spell_map: Optional[SpellMap] = param.spellmap_default
                return spell_map
        return None

    @staticmethod
    def _container_hint(annotation: Any) -> str:
        """
        Return the list-only collection hint for a container-typed required hole.

        Contract:
            - Returns a leading-space sentence when the annotation's origin is set,
              frozenset, dict or tuple (bare generics such as `dict[str, X]` and
              their typing aliases) AND one of its type arguments is a user class,
              where someone may have expected injection; plain data such as
              `dict[str, Any]` gets no hint (2026-09-26). Otherwise an empty string.
            - Pure; reads only the annotation object.

        Args:
            annotation: Phase-1 annotation of the required hole (may be None or a string).

        Returns:
            str: The hint sentence, or "".
        """
        origin = get_origin(annotation)
        if origin not in (set, frozenset, dict, tuple):
            return ""
        if not any(
            inspect.isclass(arg) and arg.__module__ != "builtins" and arg is not Any
            for arg in get_args(annotation)
        ):
            return ""
        return (
            " Melder injects collections only as list[T]; "
            f"a {origin.__name__} parameter is always supplied by the caller."
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
