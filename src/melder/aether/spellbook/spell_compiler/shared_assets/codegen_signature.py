import hashlib
import pickle
import types
from typing import Any, Dict, Optional, Tuple, Union


class CodegenSignature:
    """
    Single implementation of the compiler's codegen signature path.

    Purpose:
        Own the three helpers that turn phase-exported IR parts into
        deterministic bytes and SHA256 digests - `serialize_codegen_signature_part`,
        `hash_codegen_signature` and `freeze_phase11_schema_value` - in ONE place.
        `SharedCompilerExecutions` (phase-side facade) and
        `CodegenCreationSchemaHelpers` (phase-11 facade) delegate here, so the two
        surfaces can no longer drift apart and silently produce different cache keys.

    Contract:
        - Slot-only static helper surface with no `__init__`; owns no state.
        - Imports the standard library only: this module sits BELOW both facades
          and never reaches into `melder.aether`, so the phase-11 subsystem's rule
          of not importing the phase helper surface holds unchanged.
        - Byte-compatibility: for every input whose bytes were already
          deterministic across interpreter processes before this module existed,
          the bytes are unchanged. Only inputs that were process-local before
          (hash-seed-ordered sets, `repr` values carrying memory addresses) are
          rendered differently, and those are rendered canonically.
        - Determinism: the same logical inputs yield the same digest in two
          interpreter processes regardless of `PYTHONHASHSEED` and object
          identity, for every value shape this module canonicalizes (see
          `freeze_phase11_schema_value` for the exact rule and its limits).

    Threading:
        Pure functions over their arguments; safe to call from any phase worker.

    Lifecycle / Cleanup:
        None. Nothing is owned.

    Registration:
        MELDER KERNEL - internal helper surface; never bound as a spell.

    Subsystem Context:
        The leaf of the compiler's signature path under `spell_compiler/shared_assets/`.
        Consumed through the two facades by phase 8 (occurrence-analysis input
        signature), the phase-11 step-row builders, the generalized manifest and
        codegen-creation steps, and the phase 8-11 IR export digest.
        Also owns the contract-override reference shape and the row projection rule
        for override payload entries, used directly by every family's row builder.

    System Context:
        Every creation-cache key and every executor signature in the `.melc`
        bundle passes through `hash_codegen_signature`, so a non-deterministic byte
        here is a cache miss per process, and a byte that drifts between the two
        facades is a stale full-hit cache: on a full hit no fresh signature is
        computed to detect it.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One deterministic serializer/hash/freeze implementation for
        codegen signatures; both compiler facades delegate here. Byte-compatible with the
        previous facade bodies for every input that was already deterministic.
    """

    __slots__ = ()

    @staticmethod
    def build_contract_override_ref(
            consumer_spell_id: str,
            param_name: str,
            key: Union[str, int],
    ) -> Tuple[str, str, str, Union[str, int]]:
        """
        Build the value-only reference to one entry of a consumer's override payload.

        Purpose:
            A `SpellContract` / `SpellMap` override payload may hold any Python
            object. The compiled plan and the creation cache never carry such a
            value; phase 9 records this reference instead and the codegen
            hydration reads the live value back from the consumer's descriptor
            (`CodegenCreationSchemaHelpers.resolve_contract_override_ref`).

        Contract:
            - Returns `("__contract_override__", consumer_spell_id, param_name, key)`,
              a tuple of `str`/`int` only, so it is a fixed point of
              `freeze_phase11_schema_value`, marshal-safe and byte-deterministic.
            - `key` is the keyword name (`str`) for a dict payload entry, or the
              positional index (`int`) for a list/tuple payload entry (including
              the `__args__` entry of a dict payload).
            - Pure; no validation of the consumer beyond typing.

        Args:
            consumer_spell_id: Selected spell id of the consumer declaring the descriptor.
            param_name: The consumer's constructor parameter carrying the descriptor.
            key: Keyword name or positional index inside the payload.

        Returns:
            Tuple[str, str, str, Union[str, int]]: The reference tuple.
        """
        return ("__contract_override__", consumer_spell_id, param_name, key)

    @staticmethod
    def is_contract_override_ref(value: Any) -> bool:
        """
        Report whether a row value is a contract override reference.

        Contract:
            - True exactly for a 4-tuple whose first item is the string
              `"__contract_override__"` (the shape `build_contract_override_ref`
              emits); every other value, including subclasses of `tuple`, is False.
            - Pure and allocation-free; safe on every row read.

        Args:
            value: Any row or payload value.

        Returns:
            bool: Whether `value` is a reference to a live override payload entry.
        """
        return (
            type(value) is tuple
            and len(value) == 4
            and value[0] == "__contract_override__"
        )

    @staticmethod
    def is_replayable_contract_payload_value(value: Any) -> bool:
        """
        Return whether one contract payload value survives a phase-11 row unchanged.

        Purpose:
            The row builders' classifier shared by every codegen family (2026-09-26):
            a value that passes is written into the row exactly as it is; any other
            value is replaced by its reference (`build_contract_override_ref`) and
            read back live at hydration, so no row ever carries a value the marshal
            envelope or a freeze projection would mangle.

        Contract:
            - True for `None`, for values whose EXACT type is `bool`, `int`, `float`
              or `str`, and for an exact `tuple` whose items are all replayable:
              these are the values `freeze_phase11_schema_value` and the many-only
              `freeze_value` return unchanged, the row hydration passes through
              as-is, and `marshal` persists.
            - False for everything else. `list` and `set` thaw as tuples, `dict` as
              a sorted tuple of pairs, plain enum members and classes as `repr`
              text, callables and default-`repr` instances as marker tuples - none
              of them is the value the descriptor carried; subclasses of the scalar
              types (an `IntEnum` member, a `str` subclass) pass through a freeze
              but are not marshallable, so they are refused as well.
            - Pure; never raises.

        Args:
            value: Raw payload value taken from a plan step.

        Returns:
            bool: True when a row reproduces `value` exactly.
        """
        if value is None:
            return True
        value_type = type(value)
        if value_type is bool or value_type is int or value_type is float or value_type is str:
            return True
        if value_type is tuple:
            for item in value:
                if not CodegenSignature.is_replayable_contract_payload_value(item):
                    return False
            return True
        return False

    @staticmethod
    def project_contract_payload_entry(
            param_name: str,
            value: Any,
            payload_refs: Optional[Dict[str, Any]],
    ) -> Any:
        """
        Project one contract payload entry into its row form: the value itself or its reference.

        Purpose:
            The one rule every family's row builder applies to `step.contract_payload`
            and `step.contract_positional_override` (2026-09-26), so the generalized,
            many-only and solo rows agree on what a payload entry looks like.

        Contract:
            - A replayable value (`is_replayable_contract_payload_value`) is returned
              as it is; it is a fixed point of every freeze in the compiler, so the
              row bytes equal the previous frozen bytes.
            - Any other value is replaced by its reference from `payload_refs`; the
              value itself never enters a row.
            - `param_name == "__args__"` projects a positional list/tuple element by
              element against the tuple of references stored under that key, so a
              scalar element stays a value while an object element becomes a
              reference; the result is always a `tuple`. A `None` positional
              payload projects to `None`.
            - Pure over its arguments.

        Args:
            param_name: Payload key, or `"__args__"` for the positional payload.
            value: Raw payload value from the plan step.
            payload_refs: The step's `contract_payload_refs` map, or None.

        Returns:
            Any: The value, its reference, or the projected positional tuple.

        Raises:
            RuntimeError: When a non-replayable value has no reference to stand in
                for it (a plan step built without `contract_payload_refs`), or a
                positional payload is neither a list/tuple nor replayable; rows must
                never fall back to writing such a value.
        """
        if param_name == "__args__":
            if value is None:
                return None
            if not isinstance(value, (list, tuple)):
                if CodegenSignature.is_replayable_contract_payload_value(value):
                    return value
                raise RuntimeError(
                    "Phase-11 row build: the positional contract payload is neither a "
                    f"list/tuple nor a scalar ({type(value).__name__})."
                )
            positional_refs = None
            if payload_refs is not None:
                positional_refs = payload_refs.get("__args__")
            projected = []
            for index, item in enumerate(value):
                if CodegenSignature.is_replayable_contract_payload_value(item):
                    projected.append(item)
                    continue
                if positional_refs is None or index >= len(positional_refs):
                    raise RuntimeError(
                        "Phase-11 row build: positional contract payload item "
                        f"{index} is not a scalar and carries no reference."
                    )
                projected.append(positional_refs[index])
            return tuple(projected)
        if CodegenSignature.is_replayable_contract_payload_value(value):
            return value
        ref = None if payload_refs is None else payload_refs.get(param_name)
        if ref is None:
            raise RuntimeError(
                "Phase-11 row build: contract payload value for parameter "
                f"{param_name!r} is not a scalar and carries no reference."
            )
        return ref

    @staticmethod
    def serialize_codegen_signature_part(part: Any) -> bytes:
        """
        Serialize one signature part into deterministic bytes.

        Purpose:
            Avoid expensive mega-`repr(...)` materialization on large nested IR
            payloads while preserving deterministic signature behaviour.

        Contract:
            - Typed one-byte fastpaths for scalars: `N` (None), `B1`/`B0` (bool),
              `I` (int), `F` (float `repr`), `S` (str UTF-8), `Y` (bytes/bytearray),
              so distinct types never collide on the same payload.
            - `dict`, `tuple` and `list` parts are pickled as they are (protocol 5).
              Their bytes are identical to the previous facade bodies; callers keep
              the responsibility of pre-freezing nested dict/set content through
              `freeze_phase11_schema_value` when canonical ordering matters,
              because rebuilding containers here would change pickle memo bytes
              for inputs that were already deterministic.
            - A top-level `set` or `frozenset` part is frozen (sorted) before
              pickling. The previous bodies pickled it in iteration order, which is
              hash-seed dependent for `str` members, so this is a new byte layout
              only for inputs that were never deterministic.
            - Any other object is pickled; when pickling raises, the encoding falls
              back to `repr(part).encode("utf-8")`, exactly as before.

        Args:
            part:
                One primitive/tuple/dict/set signature segment.

        Returns:
            bytes:
                Deterministic encoded bytes for hashing.
        """
        part_type = type(part)
        if part_type is set or part_type is frozenset:
            frozen_part: Any = CodegenSignature.freeze_phase11_schema_value(part)
            return CodegenSignature._pickle_or_repr(frozen_part)
        if part_type is dict or part_type is tuple or part_type is list:
            return CodegenSignature._pickle_or_repr(part)
        if part is None:
            return b"N"
        if part_type is bool:
            return b"B1" if part else b"B0"
        if part_type is int:
            return b"I" + str(part).encode("ascii")
        if part_type is float:
            return b"F" + repr(part).encode("ascii")
        if part_type is str:
            part_str: str = part
            return b"S" + part_str.encode("utf-8")
        if part_type is bytes:
            part_bytes: bytes = part
            return b"Y" + part_bytes
        if part_type is bytearray:
            return b"Y" + bytes(part)
        return CodegenSignature._pickle_or_repr(part)

    @staticmethod
    def _pickle_or_repr(part: Any) -> bytes:
        """
        Pickle one part with protocol 5, falling back to its `repr` bytes.

        Contract:
            - The fallback triggers only on `PickleError`, `TypeError` or
              `AttributeError`, the same set the previous facade bodies caught.
            - Not a canonicalization step: the part is encoded as given.

        Args:
            part:
                Container or object to encode.

        Returns:
            bytes:
                Pickle bytes, or `repr(part)` encoded as UTF-8 when pickling fails.
        """
        try:
            encoded_part: bytes = pickle.dumps(part, protocol=5)
            return encoded_part
        except (pickle.PickleError, TypeError, AttributeError):
            return repr(part).encode("utf-8")

    @staticmethod
    def hash_codegen_signature(*parts: Any) -> str:
        """
        Build a deterministic SHA256 signature over ordered IR parts.

        Purpose:
            Produce stable fingerprints for phase-exported IR slices so
            codegen-creation compilation can skip unchanged payloads and the
            creation cache can match executors across processes.

        Contract:
            - Each part is encoded via `serialize_codegen_signature_part` and
              followed by a `|` separator byte, so ordering and grouping are
              significant: two different partitions of the same values never
              collide.
            - Deterministic for equal-ordered inputs; independent of
              process-randomized object identity for every shape
              `freeze_phase11_schema_value` canonicalizes.

        Args:
            *parts:
                Ordered signature components.

        Returns:
            str:
                Hex SHA256 digest over the encoded parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(CodegenSignature.serialize_codegen_signature_part(part))
            digest.update(b"|")
        return digest.hexdigest()

    @staticmethod
    def freeze_phase11_schema_value(value: Any) -> Any:
        """
        Normalize an arbitrary value into a deterministic schema-safe form.

        Purpose:
            Give step rows, contract payloads and signature parts one canonical,
            hashable projection whose bytes do not depend on the process that
            produced them.

        Contract:
            - `None`, `bool`, `int`, `float` and `str` pass through unchanged.
            - `dict` -> tuple of `(key, frozen value)` pairs sorted by key.
            - `list` / `tuple` -> order-preserving tuple of frozen items.
            - `set` / `frozenset` -> tuple of frozen items sorted by `repr`.
              (`frozenset` previously fell through to `repr`, which is
              iteration-ordered and therefore hash-seed dependent.)
            - Functions, methods and builtin callables -> the tuple
              `("__callable__", module, qualname)`. Their `repr` carries a memory
              address, so the previous rendering was process-local.
            - Instances whose type does not override `object.__repr__` -> the
              tuple `("__object__", module, qualname of the type)`, for the same
              reason. Two distinct instances of such a type therefore freeze to the
              SAME value: the signature deliberately does not distinguish
              identity-only objects, because identity was never reproducible
              across processes in the first place.
            - Anything else -> `repr(value)`, byte-for-byte as before. Classes,
              enum members, dataclasses and every type with an address-free
              `repr` keep their previous bytes; a user type whose custom `repr`
              embeds an address stays process-local and is out of this rule's
              reach (the determinism test is the guard).
            - Recurses into nested containers, so the whole structure is
              order-canonical and hashable.
            - Deterministic, not lossless: the phase-11 row builder stores the
              frozen payload values in the step rows, and every manifest-first
              executor - hydrated in-process at first meld or from a cache hit
              - binds those row values as constructor arguments (only the
              legacy plan compiler binds the raw values). A contract payload
              value that is not `None`, `bool`, `int`, `float`, `str` or a
              tuple of those therefore reaches the constructor as its frozen
              projection. The creation cache refuses such spells (owner option
              B, 2026-09-26); the in-process projection is an open owner
              decision recorded on the tranche's tickets.

        Args:
            value:
                Value to freeze.

        Returns:
            Any:
                A deterministic, hashable projection of `value`.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        CodegenSignature.freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                CodegenSignature.freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, (set, frozenset)):
            return tuple(
                sorted(
                    (
                        CodegenSignature.freeze_phase11_schema_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        if isinstance(
                value,
                (
                    types.FunctionType,
                    types.MethodType,
                    types.BuiltinFunctionType,
                    types.BuiltinMethodType,
                ),
        ):
            return CodegenSignature._freeze_callable(value)
        if type(value).__repr__ is object.__repr__:
            value_type = type(value)
            return ("__object__", value_type.__module__, value_type.__qualname__)
        return repr(value)

    @staticmethod
    def _freeze_callable(value: Any) -> Tuple[str, str, str]:
        """
        Render a callable as a process-independent `(marker, module, qualname)` tuple.

        Contract:
            - Bound methods are rendered through their underlying function, so
              the instance's identity never enters the signature.
            - A callable without a module (some builtins) renders its module as
              the empty string rather than raising.
            - Never invokes the callable.

        Args:
            value:
                Function, method or builtin callable.

        Returns:
            Tuple[str, str, str]:
                `("__callable__", module, qualname)`.
        """
        target: Any = value
        if isinstance(value, types.MethodType):
            target = value.__func__
        module_name = target.__module__
        if module_name is None:
            module_name = ""
        return ("__callable__", module_name, target.__qualname__)
