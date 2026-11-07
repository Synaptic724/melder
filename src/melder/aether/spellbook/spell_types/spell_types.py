from enum import StrEnum
from typing import Optional

class SpellType(StrEnum):
    """
    Canonical runtime binding-family classification for bound spells.

    Values exactly match member names. Historical numeric values 1-14 remain
    readable by value, including in older enum pickle payloads.

    `SpellType` is the normalized runtime label produced by the binding layer
    after `Bind` and the spell-examiner profile machinery inspect what kind of
    callable or object was actually registered. Later phases use this enum to
    decide which resolution-style family a spell belongs to and which runtime
    assumptions are valid for that spell.

    Families:
        - `SPELL*`:
          class-style construction spells. These are the normal "build me by
          planning and calling a constructor/call target" families.
        - `EXISTING_CREATION*`:
          pre-existing objects that already have an instance and therefore skip
          large parts of the creation/execution-plan pipeline.
        - `METHOD*`:
          named method/function bindings that are still first-class spells but
          carry method-style semantics.
        - `LAMBDA_METHOD*`:
          lambda-style callable bindings treated as method-family spells in the
          runtime.

    Suffix signals:
        - `WITH_SPELLFRAME` means the binding carries explicit spellframe
          metadata.
        - `WITH_BINDING_NAME` means the binding carries an explicit binding-name
          dimension for later lookup/disambiguation.
        - combinations of both mean both metadata channels are present.

    Contract:
        - The enum captures binding-family semantics only; it is not itself an
          existence/lifetime policy.
        - Resolution-style policy is derived from this enum together with
          `Existence` and DI shape data in later phases.
        - Method/lambda families remain valid spell registrations, but they
          behave differently from class/existing-object families during Phase 3+
          planning and in the resolution-style matrix.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Produced by the binding
        layer; users read it rather than choosing it.

    Subsystem Context:
        The runtime classification produced by `Bind` plus the spell-examiner
        profile machinery. It pairs with `Existence` (lifetime) and is the input
        `ResolutionStyleMatrix` maps to a support policy.

    System Context:
        This enum is DERIVED, not declared - the binding layer inspects what was
        actually registered and normalizes it. That is why a user never passes a
        `SpellType`: claiming a family the object does not match would put the
        runtime's assumptions at odds with the object it holds.
        The family split drives real pipeline divergence. `EXISTING_CREATION*`
        spells BYPASS the live phase 8-11 group entirely - they have no
        occurrence graph, no analyzer-derived model, and no codegen-creation
        payload, because the object already exists - and
        `CreationContextBuilder` synthesizes their runtime doors locally instead
        of demanding a compiler artifact that will never be produced.
        `METHOD*` and `LAMBDA_METHOD*` carry callable semantics and are
        unique-only for the same reason: there is no per-scope construction to
        vary.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Canonical runtime binding-family classification for bound spells.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """
    # Class-based construction spell families.
    SPELL = "SPELL"
    SPELL_WITH_SPELLFRAME = "SPELL_WITH_SPELLFRAME"
    SPELL_WITH_BINDING_NAME = "SPELL_WITH_BINDING_NAME"
    SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME = "SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME"

    # Existing-object spell families. These bind an already-created object
    # rather than planning a new construction DAG for it.
    EXISTING_CREATION = "EXISTING_CREATION"
    EXISTING_CREATION_WITH_SPELLFRAME = "EXISTING_CREATION_WITH_SPELLFRAME"
    EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME = "EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME"

    # Method/function spell families.
    METHOD = "METHOD"
    METHOD_WITH_BINDING_NAME = "METHOD_WITH_BINDING_NAME"
    METHOD_WITH_SPELLFRAME = "METHOD_WITH_SPELLFRAME"
    METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = "METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME"

    # Lambda-style method families.
    LAMBDA_METHOD_WITH_BINDING_NAME = "LAMBDA_METHOD_WITH_BINDING_NAME"
    LAMBDA_METHOD_WITH_SPELLFRAME = "LAMBDA_METHOD_WITH_SPELLFRAME"
    LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = "LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME"

    def __str__(self) -> str:
        """Return the stable enum member name used throughout the runtime."""
        return self.name

    @classmethod
    def _missing_(cls, value: object) -> Optional[SpellType]:
        """
        Resolve a historical numeric spell type to its original member.

        Current names use ordinary enum lookup. Values equal to the old
        integers remain readable; unknown or unhashable inputs return None
        so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, SpellType] = {
            1: cls.SPELL,
            2: cls.SPELL_WITH_SPELLFRAME,
            3: cls.SPELL_WITH_BINDING_NAME,
            4: cls.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
            5: cls.EXISTING_CREATION,
            6: cls.EXISTING_CREATION_WITH_SPELLFRAME,
            7: cls.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
            8: cls.METHOD,
            9: cls.METHOD_WITH_BINDING_NAME,
            10: cls.METHOD_WITH_SPELLFRAME,
            11: cls.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
            12: cls.LAMBDA_METHOD_WITH_BINDING_NAME,
            13: cls.LAMBDA_METHOD_WITH_SPELLFRAME,
            14: cls.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None