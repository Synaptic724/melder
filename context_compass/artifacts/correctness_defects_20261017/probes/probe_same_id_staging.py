"""Probe (melder_0, 2026-10-17; STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): what staging a
version whose spell_id the index already holds does today - the case every settings-only version becomes once the
managed settings leave the spell_id.

  S1  bind Worker managed (limit 1), conjure, then bind_inactive the same class with the same settings on its index
      (the same spell_id): what is raised, and is anything left registered?
  S2  the same through a fresh Book where the first version was disposed with cleanup_spell before the re-stage.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_same_id_staging.py
"""
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Worker:
    """The managed class."""

    def reset(self) -> None:
        """The reset a release runs."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def options(limit: int) -> dict:
    """The bind options both versions use."""
    return dict(spell=Worker, spellframe="workers", binding_name="worker",
                existence=Existence.managed_spell_quantity, permissions="create",
                managed_spell_mode="limited_quantity", managed_spell_limit=limit,
                managed_spell_reset_methods=["reset"])


def world(frame: str):
    """One dynamic Book on `frame` with Worker bound managed (limit 1), conjured."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)
    spell_id = spellbook.bind(**options(1))
    conduit = spellbook.conjure(dynamic=True, name="root")
    return spellbook, conduit, spell_id


def s1() -> None:
    """Re-stage the same spell_id onto its own index."""
    print("S1 bind_inactive of the same class with the same settings (the same spell_id) on its index")
    spellbook, conduit, a = world("s1")
    index = spellbook.find_spell_by_spell_id(a).spell_index
    try:
        b = conduit.bind_inactive(spell_index=index, **options(1))
        print(f"    returned {b[:12]}; same id: {b == a}")
    except Exception as error:
        print(f"    raised {type(error).__name__}: {' '.join(str(error).split())}")
    print(f"    parked versions in the Book: {len(spellbook._inactive_spells)}; "
          f"the id still names the active version: {spellbook.find_spell_by_spell_id(a) is not None}")


def s2() -> None:
    """Dispose the only version, then bind the same class with other settings (the same spell_id once settings leave it)."""
    print("S2 cleanup_spell of the only version, then bind the same class again with limit 2")
    spellbook, conduit, a = world("s2")
    conduit.cleanup_spell(spell=spellbook.find_spell_by_spell_id(a))
    b = conduit.bind(**options(2))
    print(f"    rebound: same id today: {b == a} (the managed part differs, so a new id today)")


if __name__ == "__main__":
    for case in (s1, s2):
        fresh_aether()
        case()
        print()
