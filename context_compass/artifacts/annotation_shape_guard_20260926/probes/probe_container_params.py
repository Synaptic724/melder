"""Does a dict/set/tuple constructor parameter of user classes (or Any) break conjure? One case per process.

PROBE_CASE selects the consumer shape. Each case binds Operation plus one consumer, conjures, and melds the
consumer with the container supplied through override. Run each case in a fresh process.
"""
import os
from typing import Any

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Operation:
    """A user class Melder could inject on its own."""


def consumer_for(case: str) -> type:
    """Return the consumer class for one probe case."""
    if case == "dict_of_class":
        class Consumer:
            """dict of a user class, no default."""
            def __init__(self, ops: dict[str, Operation]) -> None:
                self.value = ops
    elif case == "dict_of_any":
        class Consumer:
            """dict[str, Any], no default."""
            def __init__(self, meta: dict[str, Any]) -> None:
                self.value = meta
    elif case == "set_of_class":
        class Consumer:
            """set of a user class, no default."""
            def __init__(self, items: set[Operation]) -> None:
                self.value = items
    elif case == "tuple_of_class":
        class Consumer:
            """variadic tuple of a user class, no default."""
            def __init__(self, parts: tuple[Operation, ...]) -> None:
                self.value = parts
    elif case == "dict_of_class_defaulted":
        class Consumer:
            """dict of a user class with an ordinary default (PLAIN, no REQUIRED_HOLE)."""
            def __init__(self, ops: dict[str, Operation] = {}) -> None:
                self.value = ops
    elif case == "dict_of_int":
        class Consumer:
            """control: dict of a builtin."""
            def __init__(self, counts: dict[str, int]) -> None:
                self.value = counts
    else:
        raise ValueError(case)
    return Consumer


def supplied_value(case: str) -> dict:
    """Return the override mapping that supplies the container parameter."""
    names = {"dict_of_class": "ops", "dict_of_any": "meta", "set_of_class": "items",
             "tuple_of_class": "parts", "dict_of_class_defaulted": "ops", "dict_of_int": "counts"}
    values = {"dict_of_class": {"a": Operation()}, "dict_of_any": {"k": 1}, "set_of_class": {Operation()},
              "tuple_of_class": (Operation(),), "dict_of_class_defaulted": {"a": Operation()},
              "dict_of_int": {"k": 1}}
    return {names[case]: values[case]}


def main() -> None:
    """Bind, conjure and meld one case; print the outcome on one line."""
    case = os.environ["PROBE_CASE"]
    consumer = consumer_for(case)
    book = Spellbook(aetheric_frame=f"asg-{case}")
    book.bind(spell=Operation, existence=Existence.many, permissions="create")
    book.bind(spell=consumer, existence=Existence.many, permissions="create")
    try:
        conduit = book.conjure(name=f"asg-{case}", validation_warnings=True)
    except Exception as exc:
        print(f"{case}: CONJURE FAILED {type(exc).__name__}: {str(exc).splitlines()[0][:150]}")
        return
    override = supplied_value(case)
    obj = conduit.meld(spell=consumer, override=override)
    same = obj.value is next(iter(override.values()))
    print(f"{case}: conjure ok; meld ok; supplied value passed through by identity: {same}")


if __name__ == "__main__":
    main()
