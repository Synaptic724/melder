import annotationlib
import inspect
import types
import typing
from typing import TYPE_CHECKING, Any, Collection, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor


class UnresolvedInputError(MeldExecutionError):
    """

    Purpose:
        Signal that a meld had to construct an object whose typed constructor
        parameter has no registered provider, and the meld did not supply the
        value. Names the consumer, the parameter, the expected type and how to
        supply it, instead of a bare Python missing-argument error.

    Raised When:
        Constructing an object whose Phase-3 topology carries an UNRESOLVED_INPUT
        socket (a single typed dependency no registered spell provides), and the
        constructing call's overrides did not supply that parameter. It fires only
        when that object is actually built: a stored (reused) object never demands
        its unresolved inputs, and conjure succeeds regardless.

    What To Do About It:
        Supply the value in the meld's override payload: the parameter name when
        melding the consumer itself, a path key ending in `>param` (or a broadcast
        `**param`) when the consumer is built as a dependency. Or bind a provider
        for the expected type; the consumer re-resolves into a normal dependency
        on its next meld.

    Contract:
        - A `MeldExecutionError`: code that catches `MeldExecutionError` keeps
          catching it. `node_id` is the consumer's spell id and `param_name` the
          first missing parameter.
        - `expected_type` is the parameter annotation's display name, read from the
          constructor signature on the failure path (Optional and forward references
          unwrapped); the lowercased frame key is used only if that is unreadable.
        - `unresolved_params` lists every missing unresolved parameter of the
          consumer, in signature order.
        - `inner` carries the constructor-call exception that exposed the gap.

    Owned State:
        - Inherited `spell_id`, `spell_name`, `node_id`, `param_name`, `inner`.
        - `expected_type`: display name of the first missing parameter's type.
        - `unresolved_params`: names of all missing unresolved parameters.

    Registration:
        A public exception type; import, raise, and catch freely. Like every
        Melder class it is refused as a spell registration.

    Subsystem Context:
        One of the `utilities/custom_exceptions/` types; the specific form of
        `MeldExecutionError` for the unresolved-input socket contract.

    System Context:
        Fires in the resolution layer on a constructor-failure path only, after
        conjure produced the Conduit. Successful melds never evaluate it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Raised at meld when an object whose typed parameter has no
        registered provider is built without that value; supply it by override
        (root key, `>param` path key or `**param`) or bind a provider for
        expected_type.
    """

    __slots__ = (
        "expected_type",
        "unresolved_params",
    )

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            message: str,
            node_id: Optional[str] = None,
            param_name: Optional[str] = None,
            inner: Optional[BaseException] = None,
            expected_type: str,
            unresolved_params: Tuple[str, ...],
    ) -> None:
        """
        Construct an unresolved-input failure.

        Args:
            spell_id:
                Id of the spell whose construction failed (the consumer).
            spell_name:
                Human-readable name of that spell.
            message:
                Remediation-bearing message naming the parameter, expected type
                and override keys.
            node_id:
                Consumer spell id; kept for `MeldExecutionError` attribution.
            param_name:
                First missing unresolved parameter.
            inner:
                Constructor-call exception that exposed the missing input.
            expected_type:
                Display name of the first missing parameter's expected type.
            unresolved_params:
                Every missing unresolved parameter of the consumer, in signature
                order. Never empty.

        Contract:
            - Preserves every `MeldExecutionError` field unchanged.

        Returns:
            None.
        """
        super().__init__(
            spell_id=spell_id,
            spell_name=spell_name,
            message=message,
            node_id=node_id,
            param_name=param_name,
            inner=inner,
        )
        self.expected_type: str = expected_type
        self.unresolved_params: Tuple[str, ...] = unresolved_params

    @staticmethod
    def expected_type_name(annotation: Any) -> str:
        """
        Render a parameter annotation as the expected-type display name.

        Purpose:
            One naming rule for the Phase-4 UNRESOLVED_INPUT warning and this
            error, so both name the type identically.

        Contract:
            - Unwraps `Optional[T]` / `Union[T, None]` to `T`, and a forward
              reference to its written name, mirroring Phase-3 matching.
            - A class renders as its `__qualname__`; any other annotation object
              as its `repr`.
            - A string renders as itself, minus one layer of matching quotes: a
              quoted annotation in a module using postponed evaluation arrives as
              the source text `'Name'`.
            - Pure: no lookups, no side effects.

        Args:
            annotation:
                The parameter's annotation: Phase-1 requirements at conjure, the
                constructor signature at meld.

        Returns:
            str: Display name of the expected type.
        """
        if isinstance(annotation, typing.ForwardRef):
            return annotation.__forward_arg__
        if isinstance(annotation, str):
            text = annotation.strip()
            if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
                return text[1:-1]
            return text
        origin = typing.get_origin(annotation)
        if origin is typing.Union or origin is types.UnionType:
            members = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
            if len(members) == 1:
                return UnresolvedInputError.expected_type_name(members[0])
        if isinstance(annotation, type):
            return annotation.__qualname__
        return repr(annotation)

    @classmethod
    def from_failed_construction(
            cls,
            spell: Spell,
            exc: BaseException,
            supplied_names: Collection[str] = (),
            supplied_positional_count: int = 0,
    ) -> Optional[UnresolvedInputError]:
        """
        Name the unresolved inputs a failed constructor call did not receive.

        Purpose:
            The single failure-path decision every executor family consults after
            a constructor call raised. INTERIM: once the demand-driven build plan
            exists, the plan decides this error before calling and these
            failure-path hooks are removed.

        Contract:
            - Returns None unless `exc` is a `TypeError`: a missing required
              argument can only fail at call binding, which raises TypeError.
            - Reads the consumer's durable Phase-3 topology and selects its
              UNRESOLVED_INPUT sockets whose name is not in `supplied_names` and,
              for positional-capable parameters, whose position is not below
              `supplied_positional_count`. Returns None when none remain, so any
              other failure keeps its existing error.
            - A required parameter that was not passed makes binding fail, so a
              non-empty selection is exactly the cause of `exc`.
            - Runs only after a call already raised; successful melds never reach it.

        Args:
            spell:
                The spell whose constructor call raised.
            exc:
                The exception raised by that call.
            supplied_names:
                Keyword names actually passed to the call (dependencies, contract
                payload and overrides together).
            supplied_positional_count:
                Number of positional arguments actually passed.

        Returns:
            Optional[UnresolvedInputError]: The error to raise (chain it from
                `exc`), or None when no unresolved input explains the failure.
        """
        if not isinstance(exc, TypeError):
            return None
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        if topology is None:
            return None
        missing: List[SpellSocketDescriptor] = []
        for socket in topology.sockets:
            if socket.socket_kind is not SocketKind.UNRESOLVED_INPUT:
                continue
            if socket.param_name in supplied_names:
                continue
            if (
                    socket.parameter_kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
                    and socket.position < supplied_positional_count
            ):
                continue
            missing.append(socket)
        if not missing:
            return None
        missing.sort(key=lambda socket: socket.position)
        first = missing[0]
        consumer = spell.spell_name
        param_name = first.param_name
        expected_type = cls._constructor_expected_type(spell, first)
        message = (
            f"{consumer}.{param_name} expects {expected_type}, but nothing registered provides it "
            f"and this meld did not supply it. Supply it with override={{{param_name!r}: ...}} when "
            f"melding {consumer}, a path key ending in '>{param_name}' (or '**{param_name}') when "
            f"{consumer} is built as a dependency, or bind a provider for {expected_type}."
        )
        if len(missing) > 1:
            others = ", ".join(repr(socket.param_name) for socket in missing[1:])
            message += f" Also not supplied: {others}."
        spell_id = spell.spell_index.selected_spell_id
        return cls(
            spell_id=spell_id,
            spell_name=consumer,
            message=message,
            node_id=spell_id,
            param_name=param_name,
            inner=exc,
            expected_type=expected_type,
            unresolved_params=tuple(socket.param_name for socket in missing),
        )

    @staticmethod
    def _constructor_expected_type(spell: Spell, socket: SpellSocketDescriptor) -> str:
        """
        Name one unresolved parameter's expected type at meld time.

        Contract:
            - Phase-1 requirements are released after resolution, so this re-reads
              the constructor signature with FORWARDREF annotations (a name that
              only exists under TYPE_CHECKING stays its written name) and applies
              `expected_type_name`.
            - When the signature cannot be read or does not annotate the
              parameter, the socket's watched frame key names the type instead.
            - Failure path only.

        Args:
            spell: The consumer whose construction failed.
            socket: Its first missing UNRESOLVED_INPUT socket.

        Returns:
            str: Display name of the expected type.
        """
        try:
            signature = inspect.signature(
                spell.spell,
                annotation_format=annotationlib.Format.FORWARDREF,
            )
        except (TypeError, ValueError):
            signature = None
        if signature is not None:
            parameter = signature.parameters.get(socket.param_name)
            if parameter is not None and parameter.annotation is not inspect.Parameter.empty:
                return UnresolvedInputError.expected_type_name(parameter.annotation)
        if socket.dependency_key is not None:
            return socket.dependency_key[0]
        return "an unregistered type"
