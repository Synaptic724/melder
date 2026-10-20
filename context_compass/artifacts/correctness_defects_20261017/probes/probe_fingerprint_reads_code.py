"""Probe (melder_0, 2026-10-18; STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): what the
bind fingerprint (the spell_id) reads from the code today, asked by the owner ("methods and init values should be
part of the hash ... did you even read bind?").

  F1  two classes with the same outline whose `run` bodies differ: same spell_id? and does bind refuse the second?
  F2  the same class with a parameter added to a non-init method (`run(self)` -> `run(self, fast=False)`)
  F3  an `__init__` default changed (`retries: int = 1` -> `retries: int = 5`)
  F4  a method renamed (`run` -> `execute`)
  F5  two lambdas with one signature and different bodies: same spell_id? and does bind refuse the second?

Every id is computed the way bind computes it (`Bind.spell_id_inspector` with spell_name=__name__, as
`Bind._bind_logic` passes it, existence unique, no address). Read-only on src/: run from this folder with the
repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_fingerprint_reads_code.py
"""
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import SpellGeneralProfile
from melder.aether.spellbook.spellbook import Spellbook


class Worker:
    """Version 1."""

    def run(self) -> str:
        """Body 1."""
        return "v1"


WorkerV1 = Worker


class Worker:  # noqa-free redefinition on purpose: same name, module and outline
    """Version 2: only the body of run differs."""

    def run(self) -> str:
        """Body 2."""
        total = sum(range(10))
        return f"v2 {total}"


WorkerV2 = Worker


class Worker:
    """Version 3: run takes a new parameter."""

    def run(self, fast: bool = False) -> str:
        """Body 3."""
        return "v3"


WorkerV3 = Worker


class Worker:
    """Version 4: run renamed to execute."""

    def execute(self) -> str:
        """Body 4."""
        return "v4"


WorkerV4 = Worker


class Job:
    """Default 1."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries


JobV1 = Job


class Job:
    """Default 5."""

    def __init__(self, retries: int = 5) -> None:
        self.retries = retries


JobV2 = Job

add_one = lambda x: x + 1  # noqa-free: the owner's case
times_hundred = lambda x: x * 100


def spell_id(target: object) -> str:
    """The spell_id bind would give `target` with no address and existence unique."""
    return Bind.spell_id_inspector(target, spell_name=target.__name__, existence=Existence.unique)


def show_class(label: str, cls: type) -> None:
    """Print what the fingerprint reads from one class profile."""
    profile = SpellGeneralProfile.create_from_target(cls).binding_profile
    print(f"    {label}: name={profile.name} qualname={profile.qualname} bases={profile.bases} "
          f"mro={profile.mro} annotation_keys={sorted(profile.annotations.keys())} "
          f"method_names={sorted(profile.method_names)} init_signature={profile.init_signature!r}")


def show_callable(label: str, fn: object) -> None:
    """Print what the fingerprint reads from one callable profile."""
    profile = SpellGeneralProfile.create_from_target(fn).binding_profile
    params = [(p.name, p.kind, p.default_fingerprint_repr) for p in profile.parameters]
    print(f"    {label}: name={profile.name} qualname={profile.qualname} signature={profile.signature!r} "
          f"params={params} repr={profile.fingerprint_repr!r} type={profile.type_name} "
          f"lambda={profile.lambda_function}")


def fresh_book(frame: str) -> Spellbook:
    """A fresh Aether and one Book on `frame` (automatic, no conjure)."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    return Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())


def try_bind(spellbook: Spellbook, **kwargs: object) -> str:
    """Bind and report the id, or the refusal."""
    try:
        return "bound " + spellbook.bind(permissions="create", **kwargs)[:12]
    except Exception as error:
        return f"REFUSED {type(error).__name__}: {str(error).splitlines()[0]}"


def main() -> None:
    """Run F1-F5."""
    print("F1 same outline, different run body")
    show_class("v1", WorkerV1)
    show_class("v2", WorkerV2)
    a, b = spell_id(WorkerV1), spell_id(WorkerV2)
    print(f"    spell_id v1={a[:12]} v2={b[:12]} equal={a == b}")
    book = fresh_book("f1")
    print(f"    bind v1: {try_bind(book, spell=WorkerV1, existence=Existence.unique)}")
    print(f"    bind v2: {try_bind(book, spell=WorkerV2, existence=Existence.unique)}")

    print("F2 a parameter added to run")
    show_class("v3", WorkerV3)
    c = spell_id(WorkerV3)
    print(f"    spell_id v1={a[:12]} v3={c[:12]} equal={a == c}")

    print("F3 an __init__ default changed")
    show_class("job1", JobV1)
    show_class("job2", JobV2)
    d, e = spell_id(JobV1), spell_id(JobV2)
    print(f"    spell_id job1={d[:12]} job2={e[:12]} equal={d == e}")

    print("F4 run renamed to execute")
    show_class("v4", WorkerV4)
    f = spell_id(WorkerV4)
    print(f"    spell_id v1={a[:12]} v4={f[:12]} equal={a == f}")

    print("F5 two lambdas, one signature, different bodies")
    show_callable("add_one", add_one)
    show_callable("times_hundred", times_hundred)
    g, h = spell_id(add_one), spell_id(times_hundred)
    print(f"    spell_id add_one={g[:12]} times_hundred={h[:12]} equal={g == h}")
    book = fresh_book("f5")
    print(f"    bind add_one as 'op': {try_bind(book, spell=add_one, binding_name='op', existence=Existence.unique)}")
    print(f"    bind times_hundred as 'op2': "
          f"{try_bind(book, spell=times_hundred, binding_name='op2', existence=Existence.unique)}")
    Aether._reset_singleton_for_tests()


if __name__ == "__main__":
    main()
