"""melder_2 P3 apply script: deferred refcounting for Melder's long-lived runtime objects (free-threaded CPython).

usage: python apply_p3.py --root <repo root> [--check]
Anchored, count-checked edits; CRLF preserved; the new utility is copied from --utility (default: next to this script).
"""
import argparse, pathlib, shutil, sys

IMPORT_LINE = "from melder.utilities.helpers.refcount_deferral import RefcountDeferral\n"
ENTRY_OLD = """                    self._fast_meld_doors[fast_door_key] = (
                        target_spell,
                        creation_context,
                        door_epoch_at_entry,
                        # Existing-object flag (2026-09-26): warm hits of a
                        # flagged entry return the bound object. A bool, not
                        # the object, so a stale entry never keeps it alive.
                        target_spell.user_created_object is not None,
                    )
"""
ENTRY_NEW = """                    door_entry = (
                        target_spell,
                        creation_context,
                        door_epoch_at_entry,
                        # Existing-object flag (2026-09-26): warm hits of a
                        # flagged entry return the bound object. A bool, not
                        # the object, so a stale entry never keeps it alive.
                        target_spell.user_created_object is not None,
                    )
                    # Free-threaded builds: every warm hit loads this entry and what it
                    # reaches, from whichever thread melds. Defer it, and any context or
                    # executor built after conjure, so those loads skip refcounting.
                    RefcountDeferral.defer_graph(door_entry)
                    self._fast_meld_doors[fast_door_key] = door_entry
"""
LESSER_OLD = """                new_conduit = Conduit(
                    spellbook=self._spellbook,
                    configuration=self._configuration,
                    conduit_state=ConduitState.lesser,
                    aetheric_frame_name=self._aetheric_frame_name,
                    aetheric_frame=self._aetheric_frame,
                    policy=Policies.default,
                    dynamic=self.__dynamic_environment__,
                    logger=logger,
                    root_conduit_id=root_conduit_id,
                    creation_gate_controller=self._creation_gate_controller,
                    conduit_hooks=root_conduit._conduit_hooks,
                    meld_hooks=root_conduit._meld_hooks,
                )
"""
LESSER_NEW = LESSER_OLD + """                # A new pooled shell is reused by every thread that later leases it:
                # defer its runtime objects (free-threaded builds; see RefcountDeferral).
                RefcountDeferral.defer_graph(new_conduit)
"""
HYDRATE_OLD = """            hydrated_cell[0] = hydrated
"""
HYDRATE_NEW = """            hydrated_cell[0] = hydrated
            # Hot executors are closures, which CPython does not defer itself;
            # every melding thread loads them (free-threaded builds).
            RefcountDeferral.defer_graph(hydrated)
"""
EDITS = {
    "src/melder/aether/spellbook/spellbook.py": [
        ("from melder.utilities.helpers.init_helpers import InitHelpers\n",
         "from melder.utilities.helpers.init_helpers import InitHelpers\n" + IMPORT_LINE, 1),
        ("""        try:
            return self._conjure_within_transaction_window(
                policy=policy,
                dynamic=self._settle_or_inherit_conjure_mode(dynamic),
                name=name,
                conduit_logger=conduit_logger,
                validation_warnings=validation_warnings,
            )
        finally:
            mediator.end_transaction_for_identity(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.CONJURE,
            )
""", """        try:
            conduit = self._conjure_within_transaction_window(
                policy=policy,
                dynamic=self._settle_or_inherit_conjure_mode(dynamic),
                name=name,
                conduit_logger=conduit_logger,
                validation_warnings=validation_warnings,
            )
        finally:
            mediator.end_transaction_for_identity(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.CONJURE,
            )
        # Free-threaded builds: this thread owns the whole kernel it just built, and
        # every other thread's meld reads it. Defer it (see RefcountDeferral).
        RefcountDeferral.defer_graph(self, conduit)
        return conduit
""", 1),
        ("""                    cache_state=cache_state,
                )
                return conduit
        finally:
""", """                    cache_state=cache_state,
                )
                # Free-threaded builds: defer the rebuilt kernel (see RefcountDeferral).
                RefcountDeferral.defer_graph(self, conduit)
                return conduit
        finally:
""", 1),
    ],
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py": [
        ("from melder.utilities.general_base.cleanable import Cleanable\n",
         "from melder.utilities.general_base.cleanable import Cleanable\n" + IMPORT_LINE, 1),
        (HYDRATE_OLD, HYDRATE_NEW, 1),
        ("""        final_door = resolved_cell[0]
        if final_door is not None:
""", """        final_door = resolved_cell[0]
        if final_door is not None:
            # A specialized door is a new closure every thread will load
            # (free-threaded builds; see RefcountDeferral).
            RefcountDeferral.defer_graph(final_door, specialized_hooks_door)
""", 1),
    ],
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/hydration/solo_hydrator.py": [
        ("from melder.utilities.general_base.cleanable import Cleanable\n",
         "from melder.utilities.general_base.cleanable import Cleanable\n" + IMPORT_LINE, 1),
        (HYDRATE_OLD, HYDRATE_NEW, 1),
    ],
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py": [
        ("from melder.utilities.general_base.cleanable import Cleanable\n",
         "from melder.utilities.general_base.cleanable import Cleanable\n" + IMPORT_LINE, 1),
        (HYDRATE_OLD, HYDRATE_NEW, 1),
    ],
    "src/melder/aether/conduit/conduit.py": [
        ("from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration\n",
         "from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration\n" + IMPORT_LINE, 1),
        (LESSER_OLD, LESSER_NEW, 2),
    ],
    "src/melder/aether/conduit/spell_space/spell_space_pool.py": [
        ("from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool\n",
         "from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool\n" + IMPORT_LINE, 1),
        ("""        return SpellSpace(
            owner_conduit_id=self._owner_conduit_id,
            conduit_meld=self._conduit_meld,
            owner_conduit_creations=self._owner_conduit_creations,
            spellspace_registry=self._spellspace_registry,
            spellspace_pool=self,
            spellspace_stack_state=self._spellspace_stack_state,
        )
""", """        space = SpellSpace(
            owner_conduit_id=self._owner_conduit_id,
            conduit_meld=self._conduit_meld,
            owner_conduit_creations=self._owner_conduit_creations,
            spellspace_registry=self._spellspace_registry,
            spellspace_pool=self,
            spellspace_stack_state=self._spellspace_stack_state,
        )
        # A pooled shell is leased by whichever thread enters a scope next:
        # defer its runtime objects (free-threaded builds; see RefcountDeferral).
        RefcountDeferral.defer_graph(space)
        return space
""", 1),
    ],
    "src/melder/aether/conduit/meld/conduit_meld.py": [
        ("from melder.aether.spellbook.existence.existence import Existence\n",
         "from melder.aether.spellbook.existence.existence import Existence\n" + IMPORT_LINE, 1),
        (ENTRY_OLD, ENTRY_NEW, 2),
    ],
    "src/melder/aether/conduit/meld/spellspace_meld.py": [
        ("from melder.aether.spellbook.existence.existence import Existence\n",
         "from melder.aether.spellbook.existence.existence import Existence\n" + IMPORT_LINE, 1),
        (ENTRY_OLD, ENTRY_NEW, 2),
    ],
}
UTILITY_REL = "src/melder/utilities/helpers/refcount_deferral.py"

def _apply_edits(raw: bytes, edits, rel: str):
    """Apply anchored edits line-wise, keeping every untouched line's own ending (files may mix CRLF and LF)."""
    lines = raw.decode("utf-8").splitlines(keepends=True)
    for old, new, count in edits:
        norm = [line.rstrip("\r\n") for line in lines]
        old_lines = old.split("\n")[:-1]
        new_lines = new.split("\n")[:-1]
        hits = [i for i in range(len(norm) - len(old_lines) + 1) if norm[i:i + len(old_lines)] == old_lines]
        if len(hits) != count:
            raise SystemExit(f"ANCHOR MISMATCH {rel}: expected {count}, found {len(hits)}: {old[:70]!r}")
        for i in reversed(hits):
            ending = "\r\n" if lines[i].endswith("\r\n") else "\n"
            lines[i:i + len(old_lines)] = [line + ending for line in new_lines]
    return "".join(lines).encode("utf-8"), b"\r\n" in raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--utility", default=str(pathlib.Path(__file__).with_name("refcount_deferral.py")))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    plans = []
    for rel, edits in EDITS.items():
        path = root / rel
        data, crlf = _apply_edits(path.read_bytes(), edits, rel)
        plans.append((path, data, crlf))
    util_dst = root / UTILITY_REL
    if util_dst.exists():
        print(f"EXISTS {UTILITY_REL}")
        return 1
    print(f"OK: {len(plans)} files + new {UTILITY_REL}" + (" (check only)" if a.check else ""))
    if a.check:
        return 0
    for path, data, crlf in plans:
        path.write_bytes(data)
    util = pathlib.Path(a.utility).read_bytes().decode("utf-8").replace("\r\n", "\n")
    crlf_util = any(p[2] for p in plans)
    util_dst.write_bytes((util.replace("\n", "\r\n") if crlf_util else util).encode("utf-8"))
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
