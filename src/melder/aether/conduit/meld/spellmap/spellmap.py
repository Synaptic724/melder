from typing import Any, Optional, Union, Tuple

from melder.spellbook.spell_input_utils import SpellInputUtils


class SpellMap:
    """
    Declarative DI placeholder used inside user code to tell Melder:

        “At this location, inject *that* spell (or whatever is bound under this
        frame/name), possibly with these overrides.”

    SpellMap is **never** resolved eagerly. It is a *pure intent object*:
    - You put it in your `__init__` defaults or instance attributes.
    - SpellCrafter / ResolutionFrame inspect it when a `meld(...)` happens.
    - The DI engine replaces it with a real creation (or callable) using the
      normal spellbook + SpellIndex + existence pipeline.

    ─────────────────────────────────────────────
    ✅ Do NOT subclass SpellMap.
    ✅ Instantiate it in constructors or as attributes.
    ✅ Treat it as a declarative DI signature, not a real object.
    ─────────────────────────────────────────────

    Typical patterns
    ----------------

        class MyService:
            def __init__(self, repo = SpellMap(MyRepo)):
                self.repo = repo

        class UsesLogic:
            def __init__(self, logic = SpellMap(ILogic, binding_name="primary")):
                self.logic = logic

        class Configured:
            def __init__(self):
                self.db = SpellMap(Postgres, spell_override={"dsn": "localhost"})
    """

    __slots__ = ("spell", "spellframe", "binding_name", "spell_override")

    def __init__(
            self,
            spell: Any,
            *,
            spellframe: Optional[Any] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> None:
        """
        Create a new SpellMap declarative descriptor.

        Args:
            spell:
                The primary lookup target. This may be:
                - the concrete implementation class,
                - a Protocol used as a frame,
                - a callable (method/lambda spell),
                - or any other object your resolver supports.

                Resolution rules (at SpellCrafter / Meld level):
                    - If `spellframe` is provided, `spellframe` is the
                      grouping key and `spell` is treated as the concrete
                      spell implementation (when needed).
                    - If `spellframe` is None, `spell` itself is used as the
                      DI key (type or frame).

            spellframe:
                Optional logical interface / Protocol / string frame key used
                to group spells. If provided, this is the primary key used to
                locate the spell in the spellbook.

            binding_name:
                Optional named binding used to disambiguate multiple spells
                under the same frame. None means “use the default binding”.

            spell_override:
                Optional positional/keyword override payload passed through
                into the `meld(...)` pipeline when constructing the target
                creation.

                - dict       → treated as keyword arguments
                - list/tuple → treated as positional arguments
        """
        if spell is None:
            raise ValueError("SpellMap requires `spell` to be provided.")

        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.spell_override = spell_override if spell_override is not None else {}

    # ------------------------------------------------------------------
    # Raw data for higher-level systems
    # ------------------------------------------------------------------
    @property
    def lookup_triplet(self) -> tuple[Any, Optional[Any], Optional[str]]:
        """
        Raw lookup data:

            (spell, spellframe, binding_name)

        This is what SpellCrafter / ResolutionFrame should consume when
        deciding how to locate the underlying Spell in the Spellbook.

        Typical usage:

            frame_key, bind_key = SpellInputUtils.normalize_spell_key(
                spell=sm.spell, spellframe=sm.spellframe, binding_name=sm.binding_name
            )
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
