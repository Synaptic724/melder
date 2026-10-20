"""Probe (melder_0, 2026-10-18; STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): does the
code-hash prototype (probe_code_hash_prototype.py) read the code INSIDE a method - the owner's question ("the internal
code inside the methods not just the superficial shit ... is that part of your equation?").

One method, `Saver.handle`, holds a constant, a call, a branch, a lambda, a nested function and a comprehension; each
case changes one thing inside it and nothing else (method names, signatures and the constructor stay the same):
  I1 a constant (x * 2 -> x * 3)          I2 the method called (self.save -> self.store)
  I3 a comparison (x > 0 -> x >= 0)       I4 inside the lambda (y + 1 -> y + 2)
  I5 inside the nested def (z - 1 -> z - 2)   I6 inside the comprehension (v + 1 -> v * 2)
  I7 two statements swapped               I8 a local variable renamed (total -> amount)
  I9 a comment inside the nested def (must not count)
Prints "today" (bind's spell_id) and the prototype per case, then the start of the instruction stream the prototype
hashes for `handle`. Run from this folder:
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_code_hash_internals.py
"""
import dis

import probe_code_hash_prototype as proto


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


Base = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 3
        if x > 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I1 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.store(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I2 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x >= 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I3 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        helper = lambda y: y + 2
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I4 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 2
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I5 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v * 2 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I6 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        def inner(z: int) -> int:
            return z - 1
        helper = lambda y: y + 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I7 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        amount = x * 2
        if x > 0:
            self.save(amount)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(amount), inner(amount), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I8 = Saver


class Saver:
    def handle(self, x: int) -> tuple:
        total = x * 2
        if x > 0:
            self.save(total)
        helper = lambda y: y + 1
        def inner(z: int) -> int:
            # a comment deep inside the nested function
            return z - 1
        values = [v + 1 for v in range(x)]
        return helper(total), inner(total), values

    def save(self, value: int) -> None:
        self.last = value

    def store(self, value: int) -> None:
        self.kept = value


I9 = Saver


def main() -> None:
    """Print each case against the base, then the start of what is hashed for handle."""
    cases = [
        ("I1 constant x*2 -> x*3", I1), ("I2 call save -> store", I2), ("I3 compare > -> >=", I3),
        ("I4 inside the lambda", I4), ("I5 inside the nested def", I5), ("I6 inside the comprehension", I6),
        ("I7 two statements swapped", I7), ("I8 local renamed total -> amount", I8),
        ("I9 comment inside the nested def", I9),
    ]
    base_today, base_code = proto.today_spell_id(Base), proto.code_spell_id(Base)
    for label, variant in cases:
        today = "same" if proto.today_spell_id(variant) == base_today else "different"
        code = "same" if proto.code_spell_id(variant) == base_code else "different"
        print(f"{label:<36} today: {today:<9} code hash: {code}")
    print("hashed for Base.handle (first 12 instructions, operands resolved):")
    for instruction in list(dis.get_instructions(Base.handle.__code__))[:12]:
        print(f"    {instruction.opname} {proto.canonical(instruction.argval)}")


if __name__ == "__main__":
    main()
