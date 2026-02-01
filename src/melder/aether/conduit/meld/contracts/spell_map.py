from typing import Any, Optional, Union, Tuple
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellMap(Cleanable):
    """
    Declarative DI placeholder used inside user code to tell Melder:

        “At this location, inject *that* spell (or whatever is bound under this
        frame/name), possibly with these overrides.”

    SpellMap is **never** resolved eagerly. It is a *pure intent object*:
    - You put it in your `__init__` defaults or instance attributes.
    - SpellCrafter / the resolution engine inspect it when a `meld(...)` happens.
    - The DI engine replaces it with a real creation (or callable) using the
      normal Spellbook + SpellIndex + Existence pipeline.

    ─────────────────────────────────────────────
    ✅ Do NOT subclass SpellMap.
    ✅ Instantiate it in constructors or as attributes.
    ✅ Treat it as a declarative DI signature, not a real object.
    ─────────────────────────────────────────────

    Typical patterns
    ----------------

        # 1) Concrete-type DI (class as the primary key)
        class MyService:
            def __init__(self, repo = SpellMap(MyRepo)):
                self.repo = repo

        # 2) Protocol / frame DI (frame as the primary key)
        class UsesLogic:
            def __init__(self, logic = SpellMap(ILogic, binding_name="primary")):
                self.logic = logic

        # 3) Override payloads
        class Configured:
            def __init__(self):
                self.db = SpellMap(Postgres, spell_override={"dsn": "localhost"})

        # 4) Frame-only SpellMap (no concrete spell; let the frame+binding decide)
        class UsesConfig:
            def __init__(self, cfg = SpellMap(
                spell=None,
                spellframe=IAppConfig,
                binding_name="primary",
            )):
                self.cfg = cfg

    Supported Shapes
    ----------------
    SpellMap supports four main shapes, all funneled through the same key logic:

        SpellMap(MyService)
            → "concrete-type" DI, spell used as the key when no spellframe is given.

        SpellMap(ILogic)
            → "frame-type" DI, where the Protocol or interface acts as the frame.

        SpellMap(MyService, spellframe=ILogic, binding_name="primary")
            → fully explicit: concrete spell + frame + binding_name.

        SpellMap(spell=None, spellframe=ILogic, binding_name="primary")
            → frame-only: the DI key is derived *only* from `spellframe` and
              `binding_name`. This is the SpellMap equivalent of type-hint DI by
              Protocol / frame with an explicit binding name.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["spell", "spellframe", "binding_name", "spell_override"]

    def __init__(
            self,
            spell: Any | None = None,
            *,
            spellframe: Optional[Any] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> None:
        """
        Create a new SpellMap declarative descriptor.

        Args:
            spell:
                The primary lookup target *or* None for frame-only SpellMaps.

                When not None, this is typically:
                    - the concrete implementation class,
                    - a Protocol used as a frame,
                    - a callable (method/lambda spell),
                    - or any other object your resolver supports.

                Resolution rules (at SpellCrafter / Meld level):

                    - If `spellframe` is provided:
                        `spellframe` is the grouping key and `spell` is treated
                        as the concrete spell implementation (when needed).

                    - If `spellframe` is None:
                        `spell` itself is used as the DI key (type or frame).

                    - If `spell` is None but `spellframe` is provided:
                        This is a **frame-only** SpellMap. The key is derived
                        entirely from `spellframe` + `binding_name`. This matches
                        the "DI by frame type" behavior, but expressed explicitly
                        as a SpellMap instead of a type hint.

            spellframe:
                Optional logical interface / Protocol / string frame key used
                to group spells. If provided, this is the primary key used to
                locate the spell in the Spellbook.

                When `spell` is None, `spellframe` **must** be provided; the
                frame becomes the sole DI identity for this SpellMap.

            binding_name:
                Optional named binding used to disambiguate multiple spells
                under the same frame. None means “use the default binding”.

                When provided, this name is normalized via
                ``SpellInputUtils.normalize_binding_name`` so comparisons are
                case-insensitive. When None, the binding name remains None so
                Spellbook default-binding semantics remain intact.

            spell_override:
                Optional positional/keyword override payload passed through
                into the `meld(...)` pipeline when constructing the target
                creation.

                - dict       → treated as keyword arguments
                - list/tuple → treated as positional arguments

                This payload is **not** interpreted here. It is propagated
                unchanged so that the resolution engine can attach it to
                Spell metadata (e.g. under `"spell_override"`) or feed it
                directly into the constructor / callable.

                When None, no override payload is attached.

        Raises:
            ValueError:
                If both `spell` and `spellframe` are None. At least one of them
                must be provided so we can derive a DI key.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "SpellMap requires at least one of `spell` or `spellframe` "
                "to be provided."
            )
        super().__init__()
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = (
            SpellInputUtils.normalize_binding_name(binding_name)
            if binding_name is not None
            else None
        )
        # Preserve the caller payload; None means no override is attached.
        self.spell_override = spell_override

    def cleanup(self) -> None:
        """
        Explicitly release references and mark this contract as cleaned.

        Notes:
            - Idempotent: safe to call multiple times.
            - After cleanup, any attempt to use this contract should call
              `check_cleaned()` first (e.g., via properties) and will raise.
        """
        if self._cleaned:
            return

        # No internal lock needed; this is a simple intent object.
        self._cleaned = True

        # Clear override payload if it is a container.
        if isinstance(self.spell_override, (list, dict)):
            self.spell_override.clear()

        self.spell_override = None
        self.spell = None
        self.spellframe = None
        self.binding_name = None
    # ------------------------------------------------------------------
    # Raw data for higher-level systems
    # ------------------------------------------------------------------
    @property
    def lookup_triplet(self) -> tuple[Any, Optional[Any], Optional[str]]:
        """
        Raw lookup data:

            (spell, spellframe, binding_name)

        This is what SpellCrafter / the Resolution engine should consume when
        deciding how to locate the underlying Spell in the Spellbook.

        Typical usage:

            frame_key, bind_key = SpellInputUtils.normalize_spell_key(
                spell=sm.spell,
                spellframe=sm.spellframe,
                binding_name=sm.binding_name,
            )

        Notes:
            - For frame-only SpellMaps (`spell is None`), only `spellframe`
              and `binding_name` participate in the key derivation.
            - For fully explicit SpellMaps, both `spell` and `spellframe`
              can be used by higher layers (e.g., to enforce contracts).
            - If a binding name was provided at construction time, it is
              normalized for case-insensitive matching.
        """
        return (self.spell, self.spellframe, self.binding_name)

    # ------------------------------------------------------------------
    # Canonical key (String-based) for Spellbook maps
    # ------------------------------------------------------------------
    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Canonical `(frame_key, binding_key)` for use in Spellbook-style maps.

        This is **exactly** the same shape as used by:
            - SpellInputUtils.make_spell_key_from_parts
            - SpellInputUtils.normalize_spell_key

        It applies all the standard normalization:
            - frame: lowercased frame key (from spellframe or spell name)
            - binding: lowercased name or "__default__"

        Behavior by shape
        -----------------
        - When `spellframe` is provided:
            The frame key is derived from `spellframe` (regardless of whether
            `spell` is None or not).

        - When `spellframe` is None and `spell` is not:
            The frame key is derived from the spell's normalized name.

        - When *both* are None:
            This case is prevented in `__init__` and would otherwise raise
            inside ``SpellInputUtils.normalize_spell_key`` as well.
        """
        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=self.spell,
            spellframe=self.spellframe,
            binding_name=self.binding_name,
        )
        return frame_key, bind_key

    # Backwards-compat alias if you want the old name:
    @property
    def spell_key(self) -> Tuple[str, str]:
        """
        Alias to `canonical_key` for compatibility with older SpellMap usage.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        return (
            f"<SpellMap spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"override={self.spell_override!r}>"
        )
