"""
Fix #1's graph descriptors (find_spell_by_spell_id_2026_10_17): author, normalize, install.

melder_1 (synaptic_python_developer), 2026-10-18.
Usage:
  python graph_fix1.py author <descriptor_dir>              add fix #1's responsibilities (exact checks)
  python graph_fix1.py normalize <descriptor_dir>           re-serialize the twelve files as the extractor writes
  python graph_fix1.py install <scratch_dir> <repo_dir> [--check]   copy the twelve files into the repo graph

The scratch dir is a copy of the repo's descriptors re-extracted on 3.14 with --strict after the notch, so its
mechanical tier is current and its authored tier is the repo's. `author` adds one responsibility each to six class
nodes and renames "version id" in Spellbook r16; the walker's --accept stamps nine nodes in between; `normalize`
writes indent=1 + LF as the extractor does (the walker writes indent=2); `install` refuses a file whose authored
fields differ from the repo's in anything but the additions below and the stamps.
"""
import json
import pathlib
import shutil
import sys

FILES = [
    "melder/__version__.json",
    "melder/aether/spellbook/spellbook.json",
    "melder/aether/conduit/conduit.json",
    "melder/aether/conduit/conduit_ward/conduit_ward.json",
    "melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.json",
    "melder/aether/spellbook/bind/spell_index.json",
    "melder/aether/spellbook/spell.json",
    "melder/crystallizer/crystal_loader_system/graft_runner.json",
    "melder/crystallizer/crystal_loader_system/restore_engine.json",
    "melder/nexus/rift/command_system/command_system.json",
    "melder/nexus/rift/command_system/static_command_system.json",
    "melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.json",
]

# (file, node id, expected count before, new responsibility)
ADDITIONS = [
    ("melder/aether/spellbook/spellbook.json", "melder.aether.spellbook.spellbook.Spellbook", 24,
     "answers a spell_id with exactly the Spell bound under it - one read of _spells_by_id (active), else one of "
     "_inactive_spells (parked), else None - with no lock and no index read; the spell an index has active is a "
     "lookup by the index (find_spell_by_spell_id, renamed from find_spell_by_id with no alias, 0.2.8253)"),
    ("melder/aether/conduit/conduit.json", "melder.aether.conduit.conduit.Conduit", 29,
     "answers get_spell_by_spell_id (renamed from get_spell_by_id with no alias, 0.2.8253) with exactly the spell "
     "the owner Book holds under the spell_id, active or parked, and get_spell_permissions with that version's own "
     "permissions; resolves a transfer's spell_id in two explicit steps - the member, then the spell its index has "
     "active here (_resolve_transfer_spell) - so a transfer still moves the index with its active version"),
    ("melder/aether/conduit/conduit_ward/conduit_ward.json",
     "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard", 11,
     "resolves a grant's or release's spell_id exactly (_check_spell_id_and_spell), so a parked spell_id is granted "
     "or released as itself, and names each granted version's own Spell in the outbound half of a contract listing; "
     "the contract dependency walk and its preflight (_link_spell_dependencies, "
     "_preflight_contract_dependency_collisions) and the transfer's spell_id handle (_transfer_spell_ownership) take "
     "an explicit index step - the spell that owns the spell_id, then the spell its index has active in the owner's "
     "Book (0.2.8253)"),
    ("melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.json",
     "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership", 7,
     "resolves a spell_id in two explicit steps - the spell that owns it, then the spell its index has active in the "
     "source Book (in the member's own Book for the target-side dependency check) - for its own spell handle "
     "(_resolve_spell, RuntimeError when that index has no active spell), the target-side dependency check "
     "(_deps_resolvable_on_target) and the owned-dependency sub-transfers (_transfer_owned_dependencies), so a "
     "parked Spell object never reaches a transfer (0.2.8253)"),
    ("melder/nexus/rift/command_system/command_system.json",
     "melder.nexus.rift.command_system.command_system.CommandSystem", 6,
     "answers get_spell_by_spell_id (renamed from get_spell_by_id, with its command and advertised names, 0.2.8253) "
     "and get_spell_by_source_id with exactly the Spell the spell_id or the published record names, from the owner "
     "Book's find_spell_by_spell_id (_get_spell_by_record_locked for a source id, after the frame gate and the "
     "record's spell-index and owner-conduit ACLs); only get_spell_by_index_id answers the version an index has "
     "active, and a parked version, which Nexus does not publish, is refused"),
    ("melder/nexus/rift/command_system/static_command_system.json",
     "melder.nexus.rift.command_system.static_command_system.StaticCommandSystem", 4,
     "answers get_spell_by_spell_id (renamed from get_spell_by_id, 0.2.8253) and get_spell_by_source_id with the "
     "live object of only the version named - the records published for that spell_id, or the one record the "
     "source id names - each melded by its own spell_id through _meld_live_spell_from_records_locked, the "
     "reuse-only loop the index path shares, whose refusals name what was asked (Spell id '<id>', "
     "Spell '<source_id>', Spell index '<id>')"),
]

R16_OLD = ("answers contracted-spell lookups by key - the active copy by version id, a parked copy through its "
           "index - before walking (0.2.8231)")
R16_NEW = ("answers contracted-spell lookups by key - the active copy by spell_id, a parked copy through its "
           "index - before walking (0.2.8231)")
LEAKS = ("context_compass/", "agent_onboarding/", "tools/system_documents/", "system_docs/", "patches/active/",
         "index_document.py")


def dump(path: pathlib.Path, d: dict) -> None:
    """Write a descriptor exactly as extract_graph.py does: indent=1, a final newline, LF."""
    path.write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8", newline="\n")


def author(root: pathlib.Path) -> None:
    """Add the six responsibilities and rename r16's wording; refuse any unexpected starting state."""
    for rel, nid, count, text in ADDITIONS:
        assert text.isascii() and not any(m in text for m in LEAKS), (rel, "prose must be ASCII and portable")
        path = root / rel
        d = json.loads(path.read_text(encoding="utf-8"))
        resp = d["nodes"][nid]["responsibilities"]
        if text in resp:
            raise SystemExit(f"{nid}: already authored - refusing")
        if len(resp) != count:
            raise SystemExit(f"{nid}: {len(resp)} responsibilities, expected {count} - refusing")
        resp.append(text)
        if nid.endswith(".Spellbook"):
            if resp[16] != R16_OLD:
                raise SystemExit("Spellbook r16 is not the expected text - refusing")
            resp[16] = R16_NEW
        dump(path, d)
        print(f"authored {nid.rsplit('.', 1)[1]}: r{count} added")


def normalize(root: pathlib.Path) -> None:
    """Re-serialize the twelve files with the extractor's format."""
    for rel in FILES:
        path = root / rel
        dump(path, json.loads(path.read_text(encoding="utf-8")))
    print("normalized", len(FILES))


AUTHORED = ("role", "responsibilities", "owns_state", "phases", "include")


def install(scratch: pathlib.Path, repo: pathlib.Path, check: bool) -> None:
    """Copy the twelve files after proving their authored tier differs from the repo's only as intended."""
    added = {nid: text for _rel, nid, _c, text in ADDITIONS}
    for rel in FILES:
        new = json.loads((scratch / rel).read_text(encoding="utf-8"))
        old = json.loads((repo / rel).read_text(encoding="utf-8"))
        if new.get("edges_authored") != old.get("edges_authored"):
            raise SystemExit(f"{rel}: edges_authored differ - refusing")
        if set(new["nodes"]) != set(old["nodes"]):
            raise SystemExit(f"{rel}: node set differs - refusing")
        for nid, node in new["nodes"].items():
            before = old["nodes"][nid]
            for key in AUTHORED:
                a, b = before.get(key), node.get(key)
                if key == "responsibilities" and nid in added:
                    expect = list(a) + [added[nid]]
                    if nid.endswith(".Spellbook"):
                        expect[16] = R16_NEW
                    if b != expect:
                        raise SystemExit(f"{nid}: responsibilities are not the intended edit - refusing")
                elif a != b:
                    raise SystemExit(f"{nid}: authored field {key} differs - refusing")
        raw = (scratch / rel).read_bytes()
        if b"\r" in raw or raw != (json.dumps(new, indent=1) + "\n").encode("utf-8"):
            raise SystemExit(f"{rel}: not in the extractor's format - run normalize")
        print(("would install " if check else "install ") + rel)
        if not check:
            shutil.copyfile(scratch / rel, repo / rel)
    print("check only: nothing written" if check else f"installed {len(FILES)}")


def main() -> None:
    """Dispatch the three modes."""
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "author":
        author(pathlib.Path(args[1]))
    elif len(args) >= 2 and args[0] == "normalize":
        normalize(pathlib.Path(args[1]))
    elif len(args) >= 3 and args[0] == "install":
        install(pathlib.Path(args[1]), pathlib.Path(args[2]), "--check" in args)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
