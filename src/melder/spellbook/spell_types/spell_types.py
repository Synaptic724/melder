from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class SpellType(Enum):
    """
    Canonical runtime binding-family classification for bound spells.

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
    """
    __melder_internal__ = _mrg.sentinel
    # Class-based construction spell families.
    SPELL = auto()
    SPELL_WITH_SPELLFRAME = auto()
    SPELL_WITH_BINDING_NAME = auto()
    SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    # Existing-object spell families. These bind an already-created object
    # rather than planning a new construction DAG for it.
    EXISTING_CREATION = auto()
    EXISTING_CREATION_WITH_SPELLFRAME = auto()
    EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    # Method/function spell families.
    METHOD = auto()
    METHOD_WITH_BINDING_NAME = auto()
    METHOD_WITH_SPELLFRAME = auto()
    METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    # Lambda-style method families.
    LAMBDA_METHOD_WITH_BINDING_NAME = auto()
    LAMBDA_METHOD_WITH_SPELLFRAME = auto()
    LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    def __str__(self):
        """Return the stable enum member name used throughout the runtime."""
        return self.name
