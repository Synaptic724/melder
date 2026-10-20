import hashlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


#region BindingManifest


class BindingManifest:
    """
    How one spell version is kept - its address, lifetime, teardown, capability and managed settings - as a value
    record with its own SHA256, the binding hash.

    Purpose:
        A spell_id is the registered object's code (`SpellCodeDigest`); the bind call that registered it is not part
        of it (the owner, 2026-10-18: "bind signature can get its own hash signature we could put into a manifest
        associated with an object"). This record is that bind call: every Spell builds one from its own arguments,
        and its `binding_hash` tells the creation cache, the record and (later) revalidation exactly when a spell's
        binding changed while its code did not.

    Contract:
        - Fields, in hash order: `frame_key` and `binding_key` (the address, as `Spell.key` normalizes it),
          `spellframe` (the bind call's spellframe as text: "" for none, a category as written, `<module>.<qualname>`
          of a Protocol contract), `spellframe_kind` (the `SpellframeKind` name), `binding_name` (as written, or None),
          `existence` (the `Existence` name), `disposal_method_names` (the resolved names in execution order),
          `resolvable`, `managed_spell_mode` (the `ManagedSpellMode` name, or None), `managed_spell_limit`,
          `managed_spell_timeout_seconds` (a float, or None) and `managed_spell_reset_methods`.
        - `binding_hash` is the SHA256 hex digest of `TAG` ("v1-binding") and one `<field>=<repr(value)>` line per
          field, in that order, newline-joined. Every value is None, a bool, an int, a float, a str or a tuple of str,
          so the text, and the hash, are the same in every process and GIL mode.
        - Not in it: permissions, hooks, application metadata and the aetheric frame - no compiled plan, structural
          row or verdict reads them - and the object's code, which is the spell_id.
        - Immutable: computed once at construction, holds no live reference, exposes read-only properties.

    Threading / Concurrency:
        Immutable after construction, so it is safe to read from any thread without a lock.

    Lifecycle / Cleanup:
        A value record: it owns nothing and needs no cleanup. A Spell keeps it after its own cleanup, like its
        spell_id.

    Registration:
        MELDER KERNEL - guarded. Built by `Spell.__init__` (`BindingManifest.build`); never bound as a spell.

    Subsystem Context:
        EPIC-2026-10-18-spell_identity_is_the_code, S2. Consumers: the creation cache keys every structural payload
        and the world stamp on it, the SpellCrystal records it, and a restore reports a binding it rebuilt with
        another hash.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. How a spell is bound - address, existence, disposal order, resolvable, managed settings - with
        its own SHA256 (`binding_hash`), separate from the spell_id, which is the object's code. Read it from
        `spell.binding_manifest`; `describe()` gives the fields and the hash as plain data.
    """

    __slots__ = (
        "_frame_key",
        "_binding_key",
        "_spellframe",
        "_spellframe_kind",
        "_binding_name",
        "_existence",
        "_disposal_method_names",
        "_resolvable",
        "_managed_spell_mode",
        "_managed_spell_limit",
        "_managed_spell_timeout_seconds",
        "_managed_spell_reset_methods",
        "_binding_hash",
    )

    # The hash domain. Change it whenever the field set or the line format changes meaning.
    TAG: ClassVar[str] = "v1-binding"

    def __init__(
            self,
            *,
            frame_key: str,
            binding_key: str,
            spellframe: str,
            spellframe_kind: str,
            binding_name: Optional[str],
            existence: str,
            disposal_method_names: Tuple[str, ...],
            resolvable: bool,
            managed_spell_mode: Optional[str],
            managed_spell_limit: Optional[int],
            managed_spell_timeout_seconds: Optional[float],
            managed_spell_reset_methods: Tuple[str, ...],
    ) -> None:
        """
        Record one binding's fields as plain values and compute its binding hash.

        Args:
            frame_key: The address's frame key (`Spell.key[0]`).
            binding_key: The address's binding key (`Spell.key[1]`).
            spellframe: The spellframe as text ("" for none).
            spellframe_kind: The `SpellframeKind` name.
            binding_name: The binding name as written, or None.
            existence: The `Existence` name.
            disposal_method_names: The resolved disposal names in execution order.
            resolvable: The per-version resolution capability.
            managed_spell_mode: The `ManagedSpellMode` name, or None.
            managed_spell_limit: The managed limit, or None.
            managed_spell_timeout_seconds: The queue wait in seconds, or None.
            managed_spell_reset_methods: The reset method names, in order.

        Contract:
            - Stores the values as given (`build` converts a Spell's arguments to them) and hashes them once.

        Returns:
            None.
        """
        self._frame_key: str = frame_key
        self._binding_key: str = binding_key
        self._spellframe: str = spellframe
        self._spellframe_kind: str = spellframe_kind
        self._binding_name: Optional[str] = binding_name
        self._existence: str = existence
        self._disposal_method_names: Tuple[str, ...] = disposal_method_names
        self._resolvable: bool = resolvable
        self._managed_spell_mode: Optional[str] = managed_spell_mode
        self._managed_spell_limit: Optional[int] = managed_spell_limit
        self._managed_spell_timeout_seconds: Optional[float] = managed_spell_timeout_seconds
        self._managed_spell_reset_methods: Tuple[str, ...] = managed_spell_reset_methods
        lines = "\n".join(name + "=" + repr(value) for name, value in self.fields())
        self._binding_hash: str = hashlib.sha256(
            (self.TAG + "\n" + lines).encode("utf-8", "surrogatepass")
        ).hexdigest()

    @classmethod
    def build(
            cls,
            *,
            key: Tuple[str, str],
            spellframe: Any,
            spellframe_kind: SpellframeKind,
            binding_name: Optional[str],
            existence: Existence,
            disposal_method_names: Sequence[str],
            resolvable: bool,
            managed_spell_mode: Optional[ManagedSpellMode],
            managed_spell_limit: Optional[int],
            managed_spell_timeout_seconds: Optional[float],
            managed_spell_reset_methods: Sequence[str],
    ) -> BindingManifest:
        """
        Build the manifest of a Spell from the arguments it was constructed with.

        Contract:
            - Converts each argument to its plain value: the enums to their names, the spellframe to text
              (`spellframe_text`), the name sequences to tuples and the queue timeout to a float, so equal settings
              written differently (a list or a tuple, `5` or `5.0`) give one hash.

        Args:
            key: The Spell's normalized `(frame_key, binding_key)` address.
            spellframe: The bind call's spellframe: None, a category string or a Protocol class.
            spellframe_kind: How Bind classified the spellframe.
            binding_name: The binding name as written, or None.
            existence: The spell's existence.
            disposal_method_names: The resolved disposal names in execution order.
            resolvable: The per-version resolution capability.
            managed_spell_mode: The managed pool policy, or None.
            managed_spell_limit: The managed limit, or None.
            managed_spell_timeout_seconds: The queue wait, or None.
            managed_spell_reset_methods: The reset method names, in order.

        Returns:
            BindingManifest: The manifest.
        """
        frame_key, binding_key = key
        return cls(
            frame_key=frame_key,
            binding_key=binding_key,
            spellframe=cls.spellframe_text(spellframe),
            spellframe_kind=spellframe_kind.name,
            binding_name=binding_name,
            existence=existence.name,
            disposal_method_names=tuple(disposal_method_names),
            resolvable=resolvable,
            managed_spell_mode=None if managed_spell_mode is None else managed_spell_mode.name,
            managed_spell_limit=managed_spell_limit,
            managed_spell_timeout_seconds=(
                None if managed_spell_timeout_seconds is None else float(managed_spell_timeout_seconds)
            ),
            managed_spell_reset_methods=tuple(managed_spell_reset_methods),
        )

    @staticmethod
    def spellframe_text(spellframe: Any) -> str:
        """
        Return a spellframe as text, without running its code.

        Args:
            spellframe: None, a category string or a Protocol class (Bind refuses anything else).

        Returns:
            str: "" for None, the string as written, `<module>.<qualname>` for a class, or `<module>.<qualname>` of its
            type in angle brackets for any other object.
        """
        if spellframe is None:
            return ""
        if isinstance(spellframe, str):
            return spellframe
        klass = spellframe if isinstance(spellframe, type) else type(spellframe)
        text = BindingManifest._class_text(klass, "__module__") + "." + BindingManifest._class_text(klass, "__qualname__")
        return text if isinstance(spellframe, type) else "<" + text + ">"

    @staticmethod
    def _class_text(klass: type, name: str) -> str:
        """
        Read a string attribute of a class through `type.__getattribute__`.

        Args:
            klass: The class.
            name: `__module__` or `__qualname__`.

        Returns:
            str: The value, or "?" when it is absent or not a string.
        """
        try:
            value = type.__getattribute__(klass, name)
        except AttributeError:
            return "?"
        return value if isinstance(value, str) else "?"

    def fields(self) -> Tuple[Tuple[str, Any], ...]:
        """
        Return the fields as `(name, value)` pairs, in hash order.

        Returns:
            Tuple[Tuple[str, Any], ...]: The twelve fields.
        """
        return (
            ("frame_key", self._frame_key),
            ("binding_key", self._binding_key),
            ("spellframe", self._spellframe),
            ("spellframe_kind", self._spellframe_kind),
            ("binding_name", self._binding_name),
            ("existence", self._existence),
            ("disposal_method_names", self._disposal_method_names),
            ("resolvable", self._resolvable),
            ("managed_spell_mode", self._managed_spell_mode),
            ("managed_spell_limit", self._managed_spell_limit),
            ("managed_spell_timeout_seconds", self._managed_spell_timeout_seconds),
            ("managed_spell_reset_methods", self._managed_spell_reset_methods),
        )

    @property
    def binding_hash(self) -> str:
        """
        Return the binding hash: the SHA256 of the fields (see the class contract).

        Returns:
            str: 64 hex characters.
        """
        return self._binding_hash

    @property
    def frame_key(self) -> str:
        """
        Return the address's frame key.

        Returns:
            str: The normalized frame key.
        """
        return self._frame_key

    @property
    def binding_key(self) -> str:
        """
        Return the address's binding key.

        Returns:
            str: The normalized binding key ("__default__" for an unnamed binding).
        """
        return self._binding_key

    @property
    def spellframe(self) -> str:
        """
        Return the spellframe as text.

        Returns:
            str: "" for none, a category as written, or `<module>.<qualname>` of a Protocol contract.
        """
        return self._spellframe

    @property
    def spellframe_kind(self) -> str:
        """
        Return the spellframe's kind.

        Returns:
            str: The `SpellframeKind` name: "none", "category" or "contract".
        """
        return self._spellframe_kind

    @property
    def binding_name(self) -> Optional[str]:
        """
        Return the binding name as written.

        Returns:
            Optional[str]: The binding name, or None.
        """
        return self._binding_name

    @property
    def existence(self) -> str:
        """
        Return the existence.

        Returns:
            str: The `Existence` name.
        """
        return self._existence

    @property
    def disposal_method_names(self) -> Tuple[str, ...]:
        """
        Return the resolved disposal method names.

        Returns:
            Tuple[str, ...]: The names, in execution order.
        """
        return self._disposal_method_names

    @property
    def resolvable(self) -> bool:
        """
        Return the resolution capability.

        Returns:
            bool: Whether the version can be resolved by a meld.
        """
        return self._resolvable

    @property
    def managed_spell_mode(self) -> Optional[str]:
        """
        Return the managed pool policy.

        Returns:
            Optional[str]: The `ManagedSpellMode` name, or None for any other existence.
        """
        return self._managed_spell_mode

    @property
    def managed_spell_limit(self) -> Optional[int]:
        """
        Return the managed limit.

        Returns:
            Optional[int]: The limit, or None.
        """
        return self._managed_spell_limit

    @property
    def managed_spell_timeout_seconds(self) -> Optional[float]:
        """
        Return the queue wait.

        Returns:
            Optional[float]: Seconds, or None.
        """
        return self._managed_spell_timeout_seconds

    @property
    def managed_spell_reset_methods(self) -> Tuple[str, ...]:
        """
        Return the managed reset method names.

        Returns:
            Tuple[str, ...]: The names, in order (empty when none).
        """
        return self._managed_spell_reset_methods

    def describe(self) -> Dict[str, Any]:
        """
        Return the fields and the binding hash as plain, JSON- and marshal-safe data.

        Returns:
            Dict[str, Any]: `binding_hash` and the twelve fields; the two name tuples as lists.
        """
        payload: Dict[str, Any] = {"binding_hash": self._binding_hash}
        for name, value in self.fields():
            payload[name] = list(value) if isinstance(value, tuple) else value
        return payload

    def __repr__(self) -> str:
        """
        Return a short diagnostic text.

        Returns:
            str: The hash's first twelve characters, the address and the existence.
        """
        return (
            f"BindingManifest(binding_hash={self._binding_hash[:12]!r}, frame_key={self._frame_key!r}, "
            f"binding_key={self._binding_key!r}, existence={self._existence!r})"
        )
