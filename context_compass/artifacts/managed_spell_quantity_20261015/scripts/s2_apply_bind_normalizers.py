"""S2: the managed-option normalizers and the fingerprint part in bind.py. Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/bind/bind.py")
text = path.read_text(encoding="utf-8")
anchor = "    @staticmethod\n    def _validate_binding(\n"
assert text.count(anchor) == 1
block = '''    @staticmethod
    def _managed_fingerprint_part(
            managed_spell_mode: ManagedSpellMode,
            managed_spell_limit: Optional[int],
            managed_spell_timeout_seconds: Optional[float],
            managed_spell_reset_methods: Sequence[str],
    ) -> str:
        """
        Render the fingerprint part of a managed binding's normalized options.

        Contract:
            - `managed:<mode>:<limit>:<timeout>:<reset names>`: the mode's name, the limit as an int, the
              timeout as the repr of its float, the reset names joined by "," in their order; an absent limit
              or timeout renders as empty text.
            - Pure: equal normalized options always render equal text, so `2` and `2.0` seconds hash alike
              (bind stores both as `2.0`).

        Args:
            managed_spell_mode: The normalized mode.
            managed_spell_limit: The normalized limit, or None.
            managed_spell_timeout_seconds: The normalized timeout in seconds, or None.
            managed_spell_reset_methods: The normalized reset names, in order.

        Returns:
            str: The part `sha256_profile` appends to a managed binding's key.
        """
        limit_text = "" if managed_spell_limit is None else str(managed_spell_limit)
        timeout_text = "" if managed_spell_timeout_seconds is None else repr(float(managed_spell_timeout_seconds))
        return "managed:{0}:{1}:{2}:{3}".format(
            managed_spell_mode.name,
            limit_text,
            timeout_text,
            ",".join(managed_spell_reset_methods),
        )

    @staticmethod
    def _normalize_managed_options(
            spell: Any,
            binding_profile: SpellBindingProfile,
            spell_name: str,
            existence: Existence,
            managed_spell_mode: Optional[Union[ManagedSpellMode, str]],
            managed_spell_limit: Optional[int],
            managed_spell_timeout_seconds: Optional[float],
            managed_spell_reset_methods: Optional[Sequence[str]],
    ) -> Tuple[Optional[ManagedSpellMode], Optional[int], Optional[float], Tuple[str, ...]]:
        """
        Validate and normalize the four managed options of one binding.

        Purpose:
            The one place the options of `Existence.managed_spell_quantity` are checked, so a malformed binding
            fails at bind, next to the mistake, and the fingerprint, the Spell and the crystal all read the same
            normalized values.

        Contract:
            - Any other existence: every option must be None (an empty reset list counts as set); the result is
              (None, None, None, ()).
            - Managed: the target must be a class - its pool builds and reuses instances of it. The mode defaults
              to elastic; the limit, timeout and reset names follow `_normalize_managed_limit`,
              `_normalize_managed_timeout` and `_normalize_managed_reset_methods`, checked in that order.
            - Reads the target class to check reset names and changes nothing.

        Args:
            spell: The binding target (the class for a managed binding).
            binding_profile: Its binding profile; a `ClassBindingProfile` for a class.
            spell_name: The target's name, used in error messages only.
            existence: The binding's existence.
            managed_spell_mode: A `ManagedSpellMode`, its name, or None.
            managed_spell_limit: An int, or None.
            managed_spell_timeout_seconds: A number of seconds, or None.
            managed_spell_reset_methods: A list or tuple of method names, or None.

        Returns:
            Tuple[Optional[ManagedSpellMode], Optional[int], Optional[float], Tuple[str, ...]]:
                The normalized mode, limit, timeout and reset names.

        Raises:
            ValueError: An option on another existence, or a malformed option (see the three helpers).
            TypeError: A managed binding of a function, method, lambda or existing object, or an option of the
                wrong type.
        """
        if existence is not Existence.managed_spell_quantity:
            supplied = [
                option_name
                for option_name, option_value in zip(
                    Bind._MANAGED_OPTION_NAMES,
                    (
                        managed_spell_mode,
                        managed_spell_limit,
                        managed_spell_timeout_seconds,
                        managed_spell_reset_methods,
                    ),
                )
                if option_value is not None
            ]
            if supplied:
                existence_text = (
                    f"Existence.{existence.name}" if isinstance(existence, Existence) else repr(existence)
                )
                raise ValueError(
                    f"{', '.join(supplied)} only apply to Existence.managed_spell_quantity, but '{spell_name}' is "
                    f"bound as {existence_text}. Remove {'it' if len(supplied) == 1 else 'them'}, or bind "
                    f"'{spell_name}' with existence=Existence.managed_spell_quantity."
                )
            return None, None, None, ()
        if not isinstance(binding_profile, ClassBindingProfile):
            target_kind = (
                "an existing object"
                if isinstance(binding_profile, (InstanceBindingProfile, OtherBindingProfile))
                else "a function or method"
            )
            raise TypeError(
                "Existence.managed_spell_quantity binds classes only: its pool builds and reuses instances of a "
                f"class, and '{spell_name}' is {target_kind}. Bind the class itself as managed, or bind "
                f"'{spell_name}' with Existence.unique."
            )
        mode = Bind._normalize_managed_mode(managed_spell_mode)
        limit = Bind._normalize_managed_limit(mode, managed_spell_limit, spell_name)
        timeout = Bind._normalize_managed_timeout(mode, managed_spell_timeout_seconds, spell_name)
        reset_methods = Bind._normalize_managed_reset_methods(spell, managed_spell_reset_methods, spell_name)
        return mode, limit, timeout, reset_methods

    @staticmethod
    def _normalize_managed_mode(
            managed_spell_mode: Optional[Union[ManagedSpellMode, str]],
    ) -> ManagedSpellMode:
        """
        Resolve a managed binding's mode.

        Contract:
            - None -> `ManagedSpellMode.elastic`; a member -> itself; a string -> the member of that name,
              matched lowercased (as Existence and Permissions names are).

        Args:
            managed_spell_mode: A `ManagedSpellMode`, its name, or None.

        Returns:
            ManagedSpellMode: The mode.

        Raises:
            ValueError: A string that names no mode (the message lists the three).
            TypeError: Any other type, an Existence member included.
        """
        if managed_spell_mode is None:
            return ManagedSpellMode.elastic
        if isinstance(managed_spell_mode, ManagedSpellMode):
            return managed_spell_mode
        if isinstance(managed_spell_mode, str):
            mode = ManagedSpellMode.__members__.get(managed_spell_mode.lower())
            if mode is None:
                raise ValueError(
                    f"Unknown managed_spell_mode {managed_spell_mode!r}. Use 'elastic', 'limited_quantity' or "
                    "'queue' (or a ManagedSpellMode member)."
                )
            return mode
        raise TypeError(
            "managed_spell_mode must be a ManagedSpellMode member or its name ('elastic', 'limited_quantity', "
            f"'queue'), got {type(managed_spell_mode).__name__}."
        )

    @staticmethod
    def _normalize_managed_limit(
            mode: ManagedSpellMode,
            managed_spell_limit: Optional[int],
            spell_name: str,
    ) -> int:
        """
        Resolve a managed binding's limit.

        Contract:
            - elastic: the most idle objects the pool keeps; None -> 256 (`_MANAGED_ELASTIC_DEFAULT_LIMIT`).
            - limited_quantity and queue: the most objects alive at once (idle plus out); required.
            - An int >= 1 (int subclasses are stored as plain ints); a bool is refused.

        Args:
            mode: The resolved mode.
            managed_spell_limit: The supplied limit, or None.
            spell_name: The target's name, for messages.

        Returns:
            int: The limit.

        Raises:
            ValueError: Missing for limited_quantity or queue, or below 1.
            TypeError: Not an int, or a bool.
        """
        if managed_spell_limit is None:
            if mode is ManagedSpellMode.elastic:
                return Bind._MANAGED_ELASTIC_DEFAULT_LIMIT
            raise ValueError(
                f"managed_spell_mode '{mode}' needs managed_spell_limit: the most objects of '{spell_name}' alive "
                "at once (an int >= 1)."
            )
        if isinstance(managed_spell_limit, bool) or not isinstance(managed_spell_limit, int):
            raise TypeError(f"managed_spell_limit must be an int, got {type(managed_spell_limit).__name__}.")
        if managed_spell_limit < 1:
            raise ValueError(f"managed_spell_limit must be at least 1, got {managed_spell_limit}.")
        return int(managed_spell_limit)

    @staticmethod
    def _normalize_managed_timeout(
            mode: ManagedSpellMode,
            managed_spell_timeout_seconds: Optional[float],
            spell_name: str,
    ) -> Optional[float]:
        """
        Resolve a managed binding's queue timeout.

        Contract:
            - queue: required; an int or float (not a bool), finite and > 0; stored as a float.
            - elastic and limited_quantity never wait: the timeout must be None, and None is returned.

        Args:
            mode: The resolved mode.
            managed_spell_timeout_seconds: The supplied timeout in seconds, or None.
            spell_name: The target's name, for messages.

        Returns:
            Optional[float]: The timeout in seconds for a queue, else None.

        Raises:
            ValueError: Given outside the queue mode, missing for a queue, or not finite and > 0.
            TypeError: Not an int or float, or a bool.
        """
        if mode is not ManagedSpellMode.queue:
            if managed_spell_timeout_seconds is not None:
                raise ValueError(
                    f"managed_spell_timeout_seconds applies only to managed_spell_mode 'queue'; '{mode}' never "
                    f"waits for a release. Remove it, or bind '{spell_name}' with managed_spell_mode='queue'."
                )
            return None
        if managed_spell_timeout_seconds is None:
            raise ValueError(
                "managed_spell_mode 'queue' needs managed_spell_timeout_seconds: how long a lease of "
                f"'{spell_name}' waits for a release before it raises (a number of seconds > 0)."
            )
        if isinstance(managed_spell_timeout_seconds, bool) or not isinstance(
                managed_spell_timeout_seconds, (int, float)
        ):
            raise TypeError(
                "managed_spell_timeout_seconds must be a number of seconds (int or float), got "
                f"{type(managed_spell_timeout_seconds).__name__}."
            )
        seconds = float(managed_spell_timeout_seconds)
        if not math.isfinite(seconds) or seconds <= 0.0:
            raise ValueError(
                "managed_spell_timeout_seconds must be a finite number of seconds > 0, got "
                f"{managed_spell_timeout_seconds!r}."
            )
        return seconds

    @staticmethod
    def _normalize_managed_reset_methods(
            spell: Any,
            managed_spell_reset_methods: Optional[Sequence[str]],
            spell_name: str,
    ) -> Tuple[str, ...]:
        """
        Resolve a managed binding's reset method names.

        Contract:
            - None -> (). Otherwise a list or tuple (a bare string is refused: it would be read per character)
              of non-empty strings, each naming a callable attribute of the class; kept in the order given,
              duplicates included, as a tuple. The pool calls them, in that order, on every release.
            - The names are caller-supplied, so the lookup is dynamic: `getattr` on the class with a default is
              the documented exception. A property or a plain attribute is not callable and is refused.

        Args:
            spell: The managed class.
            managed_spell_reset_methods: The supplied names, or None.
            spell_name: The class's name, for messages.

        Returns:
            Tuple[str, ...]: The reset names.

        Raises:
            TypeError: Not a list or tuple, or an element that is not a string.
            ValueError: An empty name, or a name that is not a callable attribute of the class.
        """
        if managed_spell_reset_methods is None:
            return ()
        if not isinstance(managed_spell_reset_methods, (list, tuple)):
            raise TypeError(
                "managed_spell_reset_methods must be a list or tuple of method names, got "
                f"{type(managed_spell_reset_methods).__name__}. Wrap a single name in a list: ['reset']."
            )
        for method_name in managed_spell_reset_methods:
            if not isinstance(method_name, str):
                raise TypeError(
                    "managed_spell_reset_methods must hold method-name strings; found an element of type "
                    f"{type(method_name).__name__}."
                )
            if not method_name:
                raise ValueError(
                    f"managed_spell_reset_methods holds an empty name; give the name of a method of '{spell_name}'."
                )
            if not callable(getattr(spell, method_name, None)):
                raise ValueError(
                    f"managed_spell_reset_methods names '{method_name}', which is not a method of '{spell_name}'. "
                    "A reset method is a zero-argument method the pool calls on every release, before the object "
                    "is leased again."
                )
        return tuple(managed_spell_reset_methods)

'''
text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8", newline="\n")
print("normalizers added")
