"""
Test support for one object, one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code).

A spell_id is the SHA256 of the registered object's code - a class's methods, constructor, class-level values and
bases - and nothing from the bind call. Registering one class a second time is therefore refused: under another
binding name, existence or spellframe, in another Book of the frame (under process-wide spell ids), or staged as a
version with `bind_inactive`. A test that needs a second registration of "the same" class binds another version of
it instead, the way an agent stages an edited class.

`version_of` builds that version: a subclass with the same name, qualname and module and the class-level values
given, so its code differs while every lookup by name or class name (`meld(spell=...)`, a class annotation, the
conjure report) still reads the original's name. It is built at runtime and cannot be imported by its qualname, so a
test that restores or grafts the version defines a module-level class instead.
"""
from typing import Any


def version_of(cls: type, **values: Any) -> type:
    """
    Return a new version of `cls`: the same name, qualname and module, with `values` as class-level values.

    Contract:
        - The result is a subclass of `cls`, so it inherits every method, the constructor and its annotations.
        - Its spell_id differs from `cls`'s and from any other version's built with other values: class-level
          values are code. Two calls with equal values build two classes whose code is equal.
        - `__name__`, `__qualname__` and `__module__` are `cls`'s, so a lookup by name resolves the version at the
          address the original used, and a class annotation naming `cls` selects it as a candidate.

    Args:
        cls (type): The class to version.
        **values (Any): The class-level values that make the version new code; at least one.

    Returns:
        type: The new version.

    Raises:
        ValueError: When no value is given - without one the version would be the original's code under its name.
    """
    if not values:
        raise ValueError(
            "version_of needs at least one class-level value: the value is what makes the version new code, "
            "and without one its spell_id would be the original's."
        )
    namespace = {"__module__": cls.__module__, "__qualname__": cls.__qualname__}
    namespace.update(values)
    return type(cls.__name__, (cls,), namespace)
