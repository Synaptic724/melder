from enum import Enum


class SpellframeKind(Enum):
    """
    What kind of thing a spell's `spellframe` is.

    Purpose:
        A spellframe is the category half of a spell's address, and a binding
        may declare it in exactly two forms: a string, which is a plain
        category label, or a `typing.Protocol` class, which is a label AND a
        contract that bind checked the spell against. The kind is recorded on
        the `Spell` at bind so Phase 3 reads it instead of inferring a meaning
        from the frame's name (a category named like a class is not a provider
        of that class).

    Contract:
        - `none`: bound without a spellframe; the address label is the spell's
          own name. The spell answers to its type and, in a collection, to its
          own name as a label.
        - `category`: a string spellframe. A pure label: reached by explicit
          addressing (`meld(spellframe=..., binding_name=...)`, `SpellMap`,
          `SpellContract`) and by collection annotations naming the label; it
          never satisfies a single annotation, whatever its spelling.
        - `contract`: a Protocol spellframe. Bind verified the spell's directly
          declared public members against it; a parameter annotated with that
          Protocol (as a class or as a `TYPE_CHECKING` string) resolves to the
          spells recorded under it, and a collection of it gathers them.
        - Any other object offered as a spellframe is refused at bind
          (TypeError); there is no fourth kind.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Users read it off a
        `Spell` (`spell.spellframe_kind`); they never pass it to `bind`.

    Subsystem Context:
        The vocabulary `Bind` writes and `CompilerPhase3` reads; the
        crystallizer records the member's name so a restore rebinds the frame
        as the kind it was.
    """

    none = "none"
    category = "category"
    contract = "contract"
