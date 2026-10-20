"""
S6 part A's graph descriptors (managed_settings_spell_id_2026_10_17): author, normalize, install.

melder_0 (synaptic_python_developer), 2026-10-18.
Usage:
  python s6_graph.py author <descriptor_dir>                     rewrite the old rule, add the rebind (exact checks)
  python s6_graph.py normalize <descriptor_dir>                  re-serialize the seven files as the extractor writes
  python s6_graph.py install <scratch_dir> <repo_dir> [--check]  copy the seven files into the repo graph

The scratch dir is a copy of the repo's descriptors re-extracted on 3.14 with --strict after the notch (0.2.8254), so
its mechanical tier is current and its authored tier is the repo's. `author` replaces four responsibilities and two
edge reasons that state the old rule (the managed settings hashed into the spell_id) and adds two; the walker's
--accept stamps the six class nodes in between, after their source was re-read; `normalize` writes indent=1 + LF as
the extractor does (the walker writes indent=2); `install` refuses a file whose authored fields differ from the
repo's in anything but the edits below and the stamps. The module nodes keep their (unverified) state.
"""
import json
import pathlib
import shutil
import sys

FILES = [
    "melder/__version__.json",
    "melder/aether/spellbook/bind/bind.json",
    "melder/aether/conduit/creations/managed_spell_quantity.json",
    "melder/aether/conduit/creations/creations.json",
    "melder/utilities/caching_system/caching_system.json",
    "melder/aether/spellbook/existence/managed_spell_mode.json",
    "melder/crystallizer/crystals/spell_crystal.json",
]

BIND = "melder.aether.spellbook.bind.bind.Bind"
MSQ = "melder.aether.conduit.creations.managed_spell_quantity.ManagedSpellQuantity"
CREATIONS = "melder.aether.conduit.creations.creations.Creations"
CACHING = "melder.utilities.caching_system.caching_system.CachingSystem"
MODE = "melder.aether.spellbook.existence.managed_spell_mode.ManagedSpellMode"
CRYSTAL = "melder.crystallizer.crystals.spell_crystal.SpellCrystal"
SPELL = "melder.aether.spellbook.spell.Spell"

# (file, node id, responsibility index, old text, new text)
REPLACEMENTS = [
    ("melder/aether/spellbook/bind/bind.json", BIND, 15,
     "validates and normalizes a managed binding's four options once (_normalize_managed_options: classes only, the "
     "mode defaulting to elastic, the limit, the queue-only timeout and callable reset names; every refusal before a "
     "Spell or index exists), appends one managed:<mode>:<limit>:<timeout>:<reset names> part to a managed binding's "
     "fingerprint only, so no other spell id moves, and hands the normalized values to the Spell (0.2.8242)",
     "validates and normalizes a managed binding's four options once (_normalize_managed_options: classes only, the "
     "mode defaulting to elastic, the limit, the queue-only timeout and callable reset names; every refusal before a "
     "Spell or index exists) and hands the normalized values to the Spell as its settings (0.2.8242); the fingerprint "
     "never reads them, so one class bound managed at one address with one disposal list has one spell_id whatever "
     "its settings, and spell_id_inspector checks them as bind does and hashes without them (0.2.8254; 0.2.8242-"
     "0.2.8253 appended a managed:<mode>:<limit>:<timeout>:<reset names> part)"),
    ("melder/aether/conduit/creations/managed_spell_quantity.json", MSQ, 3,
     "is sized by mode: elastic keeps baseline min(20, limit) and at most limit idle with the kernel pools' retention "
     "defaults; limited_quantity and queue are fixed at their limit, so count never exceeds it and nothing is evicted",
     "is sized by mode: elastic keeps baseline min(20, limit) and at most limit idle with the kernel pools' retention "
     "defaults; limited_quantity and queue are fixed at their limit, so count never exceeds it and nothing is evicted "
     "while that limit stands - after a rebind to a lower limit (r9) the objects alive stay counted above it, and each "
     "release that leaves more idle objects than the new limit evicts the oldest one"),
    ("melder/aether/conduit/creations/creations.json", CREATIONS, 9,
     "keeps one ManagedSpellQuantity per managed version a root store owns in _managed_quantities, a map of its own, "
     "so lookups, live probes and purge never meet a pool: ensure_managed_quantity composes it at an owner stamp "
     "(idempotent; a rebind re-points it), get_managed_quantity is a lock-free read, discard_managed_quantity gives "
     "up an identity-checked pool without cleaning it (0.2.8243-0.2.8246)",
     "keeps one ManagedSpellQuantity per managed version a root store owns in _managed_quantities, a map of its own, "
     "so lookups, live probes and purge never meet a pool: ensure_managed_quantity composes it at an owner stamp "
     "(idempotent) and, when a definition bound again under the same spell_id meets the pool its earlier definition "
     "left, hands it the new Spell after releasing the store lock (ManagedSpellQuantity._rebind_spell takes the new "
     "settings, 0.2.8254), get_managed_quantity is a lock-free read, discard_managed_quantity gives up an "
     "identity-checked pool without cleaning it (0.2.8243-0.2.8246)"),
    ("melder/aether/spellbook/existence/managed_spell_mode.json", MODE, 3,
     "identity data: with the limit, the timeout and the reset names it is hashed into a managed spell's id, recorded "
     "by name in its crystal and replayed by restore and graft; __str__ returns the bare name",
     "a setting, not identity: with the limit, the timeout and the reset names it is not part of a managed spell's "
     "spell_id (0.2.8254; 0.2.8242-0.2.8253 hashed them), so changing it is cleanup_spell and a new bind, which keeps "
     "the spell_id and the pool; recorded by name in its crystal and replayed by restore and graft; __str__ returns "
     "the bare name"),
    ("melder/crystallizer/crystals/spell_crystal.json", CRYSTAL, 7,
     "records a managed spell's options as plain values - the mode by name, the limit, the queue timeout and the "
     "reset names - only for managed_spell_quantity, so every other payload is unchanged (record 4.2.0, 0.2.8242); "
     "managed_spell_options returns them, and the static managed_bind_options(payload) is the one reader the restore "
     "and graft lanes replay them through",
     "records a managed spell's options as plain values - the mode by name, the limit, the queue timeout and the "
     "reset names - only for managed_spell_quantity, so every other payload is unchanged (record 4.2.0, 0.2.8242); "
     "managed_spell_options returns them, and the static managed_bind_options(payload) is the one reader the restore "
     "and graft lanes replay them through, as settings: the replayed bind's spell_id does not depend on them "
     "(0.2.8254)"),
]

# (file, node id, expected count before, new responsibility)
ADDITIONS = [
    ("melder/aether/conduit/creations/managed_spell_quantity.json", MSQ, 9,
     "_rebind_spell(spell): a definition bound again under the same spell_id (cleanup_spell, then bind) meets this "
     "pool through Creations.ensure_managed_quantity after the store lock is released; under the pool lock it "
     "re-points the Spell, the class key and the disposal list and, when a setting differs, takes the new mode, "
     "limit, queue timeout and reset names, sizes the retention band as a fresh pool of those settings (elastic: "
     "baseline min(20, limit), ceiling the limit; limited_quantity and queue: both the limit; the target back at the "
     "baseline) and wakes every waiter to re-check; equal settings (an ownership transfer's restamp) only re-point; "
     "nothing is destroyed - the count stays the objects alive (0.2.8254)"),
    ("melder/utilities/caching_system/caching_system.json", CACHING, 11,
     "cache generation 22 retires bundles written while a managed spell's settings were part of its spell_id "
     "(managed_settings_leave_spell_id, 0.2.8254): every managed spell_id moved once, so the ids those bundles were "
     "keyed by are gone"),
]

# (file, from id, to id, old why, new why)
EDGE_REASONS = [
    ("melder/aether/spellbook/bind/bind.json", BIND,
     "melder.aether.spellbook.existence.managed_spell_mode.ManagedSpellMode",
     "Bind normalizes a managed binding's mode to a ManagedSpellMode member before hashing it into the spell id.",
     "Bind normalizes a managed binding's mode to a ManagedSpellMode member and hands it to the Spell as a setting; "
     "the spell_id does not hash it (0.2.8254)."),
    ("melder/aether/conduit/creations/managed_spell_quantity.json", MSQ, SPELL,
     "The pool reads the managed options and the disposal list from its version's Spell at construction and keeps "
     "the Spell borrowed (a rebind under the same id re-points it); it never cleans it.",
     "The pool reads the managed options and the disposal list from its version's Spell at construction and keeps "
     "the Spell borrowed (a rebind under the same spell_id re-points it and gives the pool that Spell's settings, "
     "0.2.8254); it never cleans it."),
]

LEAKS = ("context_compass/", "agent_onboarding/", "tools/system_documents/", "system_docs/", "patches/active/",
         "index_document.py")
AUTHORED = ("role", "responsibilities", "owns_state", "phases", "include")


def dump(path: pathlib.Path, d: dict) -> None:
    """Write a descriptor exactly as extract_graph.py does: indent=1, a final newline, LF."""
    path.write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8", newline="\n")


def check_prose(text: str) -> None:
    """Refuse prose that is not ASCII, leaks a tool path, or calls a SpellIndex a lineage."""
    assert text.isascii(), text
    assert not any(m in text for m in LEAKS), text
    assert "lineage" not in text, text


def find_edge(d: dict, src: str, dst: str) -> dict:
    """Return the one authored edge from `src` to `dst`, refusing none or several."""
    hits = [e for e in d.get("edges_authored") or [] if e["from"] == src and e["to"] == dst]
    if len(hits) != 1:
        raise SystemExit(f"{src} -> {dst}: {len(hits)} authored edges, expected 1 - refusing")
    return hits[0]


def author(root: pathlib.Path) -> None:
    """Apply the replacements, additions and edge reasons; refuse any unexpected starting state."""
    for rel, nid, index, old, new in REPLACEMENTS:
        check_prose(new)
        path = root / rel
        d = json.loads(path.read_text(encoding="utf-8"))
        resp = d["nodes"][nid]["responsibilities"]
        if resp[index] != old:
            raise SystemExit(f"{nid} r{index}: not the expected text - refusing")
        resp[index] = new
        dump(path, d)
        print(f"replaced {nid.rsplit('.', 1)[1]} r{index}")
    for rel, nid, count, text in ADDITIONS:
        check_prose(text)
        path = root / rel
        d = json.loads(path.read_text(encoding="utf-8"))
        resp = d["nodes"][nid]["responsibilities"]
        if text in resp or len(resp) != count:
            raise SystemExit(f"{nid}: {len(resp)} responsibilities, expected {count} and no copy - refusing")
        resp.append(text)
        dump(path, d)
        print(f"added {nid.rsplit('.', 1)[1]} r{count}")
    for rel, src, dst, old, new in EDGE_REASONS:
        check_prose(new)
        path = root / rel
        d = json.loads(path.read_text(encoding="utf-8"))
        edge = find_edge(d, src, dst)
        if edge.get("why") != old:
            raise SystemExit(f"{src} -> {dst}: why is not the expected text - refusing")
        edge["why"] = new
        dump(path, d)
        print(f"edge {src.rsplit('.', 1)[1]} -> {dst.rsplit('.', 1)[1]}: why rewritten")


def normalize(root: pathlib.Path) -> None:
    """Re-serialize the seven files with the extractor's format."""
    for rel in FILES:
        path = root / rel
        dump(path, json.loads(path.read_text(encoding="utf-8")))
    print("normalized", len(FILES))


def expected_responsibilities(nid: str, before: list) -> list:
    """The repo's responsibilities of `nid` with this script's edits applied."""
    expect = list(before)
    for _rel, rid, index, old, new in REPLACEMENTS:
        if rid == nid:
            assert expect[index] == old, (nid, index)
            expect[index] = new
    for _rel, rid, _count, text in ADDITIONS:
        if rid == nid:
            expect.append(text)
    return expect


def expected_edges(rel: str, before: list) -> list:
    """The repo's authored edges of `rel` with this script's reason edits applied."""
    expect = json.loads(json.dumps(before))
    for erel, src, dst, old, new in EDGE_REASONS:
        if erel != rel:
            continue
        for edge in expect:
            if edge["from"] == src and edge["to"] == dst:
                assert edge.get("why") == old, (src, dst)
                edge["why"] = new
    return expect


def install(scratch: pathlib.Path, repo: pathlib.Path, check: bool) -> None:
    """Copy the seven files after proving their authored tier differs from the repo's only as intended."""
    for rel in FILES:
        new = json.loads((scratch / rel).read_text(encoding="utf-8"))
        old = json.loads((repo / rel).read_text(encoding="utf-8"))
        if new.get("edges_authored") != expected_edges(rel, old.get("edges_authored") or []) and not (
                new.get("edges_authored") is None and old.get("edges_authored") is None):
            raise SystemExit(f"{rel}: edges_authored are not the intended edit - refusing")
        if set(new["nodes"]) != set(old["nodes"]):
            raise SystemExit(f"{rel}: node set differs - refusing")
        for nid, node in new["nodes"].items():
            before = old["nodes"][nid]
            for key in AUTHORED:
                a, b = before.get(key), node.get(key)
                if key == "responsibilities":
                    if b != expected_responsibilities(nid, a or []) and not (a is None and b is None):
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
