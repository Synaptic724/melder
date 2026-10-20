"""The identity landing's graph leftovers (melder_0, 2026-10-19): retired-fingerprint prose rewritten, nodes re-read.

S1 and S2 (0.2.8257-0.2.8258) left the authored tier of their graph descriptors behind the source: four descriptors
still describe the retired bind fingerprint (binding_profile, binding_profile_strategy, inspector_utility,
signature_reflection), Bind's prose names the fingerprint and an inspector rule it no longer has, and the classes the
landing changed (SpellbookCreationSystem, RestoreReport, GraftRunner, SpellCrystal, RecordVersion, CachingSystem) do
not mention the binding hash. Each node below was re-read against its source (whole file, or the landing's diff of a
node accepted before it) before this prose was written. Spellbook and Spell are left to melder_1's S4 landing: their
files carry its in-progress edits. All-or-nothing: every anchor must match once; `--write` writes the descriptors.
"""
import json
import pathlib
import sys
from typing import Any, Dict, List

GRAPH = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
BP = "melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile."
BPS = "melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy.BindingProfileStrategy"
IU = "melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility.InspectorUtility"
SR = "melder.utilities.helpers.signature_reflection.SignatureReflection"
BIND = "melder.aether.spellbook.bind.bind.Bind"
SCD = "melder.aether.spellbook.bind.spell_code_digest.SpellCodeDigest"
BM = "melder.aether.spellbook.bind.binding_manifest.BindingManifest"
MODE = "melder.aether.spellbook.existence.managed_spell_mode.ManagedSpellMode"

# (file, op, node or edge key, payload)
OPS: List[tuple] = [
    # binding_profile.py - read whole: the profiles keep display data only; fingerprint_repr is gone.
    ("aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.json", "set", BP + "ClassBindingProfile", {
        "role": "Binding-time view of a class candidate - enough to reason about protocol compatibility and produce "
                "diagnostics; the spell_id is the class's code digest (SpellCodeDigest), never read from it.",
        "responsibilities": [
            "record name, qualname, module, bases, MRO, annotations, origin file and line, the dataclass and "
            "decorated flags, and the method names",
            "keep the address-free constructor signature text (init_signature) for descriptors and diagnostics beside "
            "the live inspect.Signature the requirements finder reuses",
            "keep the per-method view shallow (names only); deep inspection belongs to later phases",
            "read the source preview lazily on first access, so the bind path never reads a source file",
            "feed nothing to the spell_id (0.2.8257): the code digest reads the class's code itself",
        ],
        "owns_state": ["name", "qualname", "module", "bases", "mro", "annotations", "origin_file", "origin_line",
                       "init_signature", "init_signature_object", "method_names"],
        "phases": ["bind", "cleanup"],
    }),
    ("aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.json", "set",
     BP + "CallableParameterBindingSummary", {
        "role": "The minimal binding-time view of one callable parameter, for diagnostics.",
        "responsibilities": [
            "record the parameter's name, kind, default repr and annotation repr (truncated display text)",
            "feed nothing to the spell_id (0.2.8257; default_fingerprint_repr is gone): the code digest reads a "
            "function's defaults itself",
        ],
        "owns_state": ["name", "kind", "default_repr", "annotation_repr"],
    }),
    ("aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.json", "set",
     BP + "CallableBindingProfile", {
        "responsibilities": [
            "store callable identity, signature and the shallow parameter summaries",
            "avoid deeper runtime-resolution detail, which belongs to later profile phases",
            "keep repr_string as truncated display text; nothing here feeds the spell_id, which the code digest takes "
            "from the callable's code (0.2.8257; fingerprint_repr is gone)",
        ],
        "owns_state": ["name", "qualname", "module", "object_id", "type_name", "repr_string", "signature",
                       "parameters"],
    }),
    ("aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.json", "set",
     BP + "InstanceBindingProfile", {
        "responsibilities": [
            "record the instance's type name, module and truncated repr",
            "feed nothing to the spell_id (0.2.8257; fingerprint_repr is gone): an existing object's spell_id is its "
            "class's code plus its data, encoded by SpellCodeDigest",
        ],
        "owns_state": ["type_name", "module", "repr_string"],
    }),
    ("aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.json", "set",
     BP + "OtherBindingProfile", {
        "responsibilities": [
            "store only the minimum detached identity and representation surface",
            "feed nothing to the spell_id, as the instance profile (0.2.8257)",
        ],
        "owns_state": ["type_name", "module", "repr_string"],
    }),
    # binding_profile_strategy.py - read whole.
    ("aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.json", "set", BPS, {
        "responsibilities": [
            "builds the correct binding-profile variant from a raw candidate surface: class, callable, instance or "
            "other",
            "captures Python 3.14 signatures with unresolved annotation names retained as ForwardRefs",
            "renders init_signature and callable signature text with unresolved names as source text "
            "(SignatureReflection.stabilize_signature), so descriptor and diagnostic text carries no ForwardRef "
            "owner or memory address",
            "keeps only truncated display reprs (InspectorUtility.safe_repr); no profile text feeds the spell_id, "
            "which SpellCodeDigest takes from the target's code (0.2.8257)",
            "reads class-level annotations evaluated where every name resolves, otherwise without evaluating the "
            "unavailable names (kept as source text, the ClassInspector read), so every annotated field reaches the "
            "published descriptor; any other read failure yields an empty mapping",
            "reads no source file at bind: the origin line comes from __firstlineno__ and the class profile reads "
            "its source preview lazily",
        ],
    }),
    ("aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.json", "edge_why",
     (BPS, SR), "BindingProfileStrategy stabilizes init_signature and callable signature text through "
                "SignatureReflection, so descriptor and diagnostic text carries no ForwardRef owner or memory "
                "address."),
    ("aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.json", "edge_add", None, {
        "from": BPS, "to": IU, "relation": "uses",
        "why": "BindingProfileStrategy takes truncated display reprs, callable unwrapping and extension-module "
               "detection from InspectorUtility's static helpers.",
        "cardinality": "many_to_one", "phase": ["validation"], "strength": "borrowed",
    }),
    # inspector_utility.py - read whole.
    ("aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.json", "set", IU, {
        "responsibilities": [
            "provides safe repr, extension-module detection, and best-effort callable unwrapping",
            "provides stable_repr and strip_memory_addresses: the full repr text with CPython ' at 0x<hex>' fragments "
            "removed, which SpellCodeDigest encodes for a target with no readable state, a value type's object, an "
            "installed third-party object, a typing object and a constant it cannot otherwise name (0.2.8257)",
        ],
    }),
    # signature_reflection.py - read whole; the node is current, one statement named the retired fingerprint.
    ("utilities/helpers/signature_reflection.json", "resp_prefix", SR, (
        "stabilizes an existing FORWARDREF signature for fingerprint text",
        "stabilizes an existing FORWARDREF signature for display and descriptor text (the binding profiles' "
        "signature text): no ForwardRef owner or memory address, unchanged when nothing is unresolved")),
    # bind.py - the landing's diff of a node accepted at 0.2.8256.
    ("aether/spellbook/bind/bind.json", "resp_prefix", BIND, (
        "takes each spell_id from SpellCodeDigest.spell_id(target)",
        "takes each spell_id from SpellCodeDigest.spell_id(target) - the SHA256 of the target's code and, for an "
        "existing object, its data - and nothing from the bind call; spell_id_inspector(spell) answers the same id "
        "from the target alone, through a fresh SpellCodeDigest per call, and checks no binding rule")),
    ("aether/spellbook/bind/bind.json", "resp_prefix", BIND, (
        "matches requested inherited disposal through first-definition MRO namespaces",
        "matches requested inherited disposal through first-definition MRO namespaces without invoking descriptors "
        "or expanding the shallow profile")),
    ("aether/spellbook/bind/bind.json", "resp_prefix", BIND, (
        "validates and normalizes a managed binding's four options once",
        "validates and normalizes a managed binding's four options once (_normalize_managed_options: classes only, "
        "the mode defaulting to elastic, the limit, the queue-only timeout and callable reset names; every refusal "
        "before a Spell or index exists) and hands the normalized values to the Spell as its settings, "
        "binding-manifest fields (0.2.8242, 0.2.8258); the spell_id never reads them (0.2.8254, and since 0.2.8257 "
        "nothing from the bind call does)")),
    ("aether/spellbook/bind/bind.json", "owns_append", BIND, "_spell_code_digest"),
    ("aether/spellbook/bind/bind.json", "edge_why", (BIND, MODE),
     "Bind normalizes a managed binding's mode to a ManagedSpellMode member and hands it to the Spell as a setting, "
     "a binding-manifest field; the spell_id never reads it (0.2.8254, 0.2.8257)."),
    ("aether/spellbook/bind/bind.json", "edge_add", None, {
        "from": BIND, "to": SCD, "relation": "owns_lifecycle_of",
        "why": "Bind builds one SpellCodeDigest at init, asks it for every spell_id under its own lock (the "
               "code-object memo lives as long as Bind) and cleans it in cleanup; spell_id_inspector builds and "
               "cleans its own per call.",
        "cardinality": "one_to_one", "phase": ["init", "runtime", "cleanup"], "strength": "hard",
    }),
    # spell_code_digest.py - read whole.
    ("aether/spellbook/bind/spell_code_digest.json", "resp_append", SCD,
     "runs no target code but repr() of a target with no readable state, of a value type's object and of an "
     "installed third-party object, reading through type and object __getattribute__ and builtin container bases; "
     "never raises for a target (opaque:<type>, a repr placeholder, a type-and-repr fallback for data nested past "
     "the recursion limit)"),
    ("aether/spellbook/bind/spell_code_digest.json", "resp_append", SCD,
     "holds no lock: its memos serve one caller at a time (Bind calls it under its lock; spell_id_inspector builds "
     "a fresh one), and cleanup clears and deletes them"),
    ("aether/spellbook/bind/spell_code_digest.json", "owns_append", SCD, "_site_roots"),
    ("aether/spellbook/bind/spell_code_digest.json", "edge_add", None, {
        "from": SCD, "to": IU, "relation": "uses",
        "why": "SpellCodeDigest encodes a target with no readable state, a value type's object, an installed "
               "third-party object, a typing object and an otherwise unnamed constant through "
               "InspectorUtility.stable_repr, the address-free full repr.",
        "cardinality": "many_to_one", "phase": ["runtime"], "strength": "borrowed",
    }),
    # binding_manifest.py - read whole.
    ("aether/spellbook/bind/binding_manifest.json", "set", BM, {
        "responsibilities": [
            "build(...) records the address (frame and binding keys), the spellframe as text and its kind, the "
            "binding name as written, existence, the ordered disposal names, resolvable and the managed settings, "
            "equal settings written alike (enum names, tuples, a float timeout)",
            "binding_hash: the SHA256 of 'v1-binding' and one <field>=<repr> line per field in order; it keys the "
            "creation caches beside the spell_id and rides the SpellCrystal (record 4.3.0)",
            "leaves out permissions, hooks, application metadata, the aetheric frame and the object's code (the "
            "spell_id)",
            "is an immutable value record: hashed once at construction, read-only properties, owning nothing and "
            "needing no cleanup",
            "describe() gives the hash and the fields as plain data",
        ],
    }),
    # The landing's diffs of nodes accepted at 0.2.8256.
    ("aether/spellbook/spellbook_creation_system.json", "resp_prefix",
     "melder.aether.spellbook.spellbook_creation_system.SpellbookCreationSystem", (
        "admits an executor-cache full hit only when the bundle's recorded world stamp",
        "admits an executor-cache full hit only when the bundle's recorded world stamp equals the live structural "
        "world stamp (generation 19); a world that differs by an existing creation or a non-resolvable definition "
        "recompiles phases 8-11 and re-stages the bundle under the new stamp; since generation 23 the stamp carries "
        "each pool and borrowed spell's binding hash beside its spell_id, so a binding changed under one spell_id is "
        "another world (0.2.8258)")),
    ("crystallizer/crystal_loader_system/restore_engine.json", "resp_prefix",
     "melder.crystallizer.crystal_loader_system.restore_engine.RestoreReport", (
        "carry structural identity translations and changed bind-SHA translations",
        "carry structural identity translations and changed spell_id translations (a replayed bind whose target's "
        "code moved since the record) in one locked report map")),
    ("crystallizer/crystal_loader_system/restore_engine.json", "resp_append",
     "melder.crystallizer.crystal_loader_system.restore_engine.RestoreReport",
     "carry binding changes by custody key - the recorded and live binding hashes of each binding the receiving "
     "Book rebuilt differently - as information, never a shortfall (record 4.3.0)"),
    ("crystallizer/crystal_loader_system/restore_engine.json", "owns_append",
     "melder.crystallizer.crystal_loader_system.restore_engine.RestoreReport", "_binding_changes"),
    ("crystallizer/crystal_loader_system/graft_runner.json", "resp_append",
     "melder.crystallizer.crystal_loader_system.graft_runner.GraftRunner",
     "lets receiving-Book policy decide each member's binding, never its spell_id: a live spell_id differs from the "
     "recorded one only when the member's code moved since the record (0.2.8257)"),
    ("crystallizer/crystals/spell_crystal.json", "resp_append", "melder.crystallizer.crystals.spell_crystal.SpellCrystal",
     "records the spell's binding hash (record 4.3.0) - the SHA256 of its binding manifest, written for every spell - "
     "which a restore compares with the binding it rebuilds"),
    ("crystallizer/crystals/spell_crystal.json", "owns_append", "melder.crystallizer.crystals.spell_crystal.SpellCrystal",
     "_binding_hash (record 4.3.0)"),
    ("crystallizer/persistence/record_version.json", "set",
     "melder.crystallizer.persistence.record_version.RecordVersion", {
        "role": "Static record-schema version authority (stamp 4.3.0; readers gate on MAJOR; absent stamps read "
                "0.0.0).",
    }),
    ("crystallizer/persistence/record_version.json", "resp_append",
     "melder.crystallizer.persistence.record_version.RecordVersion",
     "uses minor 4.3.0 for the spell crystal's binding_hash, written for every spell (0.2.8258); 4.2 readers ignore "
     "it and a 4.2 record compares no binding"),
    ("utilities/caching_system/caching_system.json", "resp_append",
     "melder.utilities.caching_system.caching_system.CachingSystem",
     "cache generation 23 retires bundles keyed by the spell_id before it became the code digest; the structural key "
     "(payload format 2) and the world stamp carry each spell's binding hash beside its spell_id, so a binding "
     "changed under one spell_id misses both tiers (binding_manifest_keys, 0.2.8258)"),
]


def apply(data: Dict[str, Any], op: str, key: Any, payload: Any, label: str) -> None:
    """Apply one operation to a loaded descriptor; exit on any anchor that does not match exactly once."""
    if op in ("set", "resp_prefix", "resp_append", "owns_append"):
        node = data["nodes"].get(key)
        if node is None:
            sys.exit(f"NODE {label}: {key}")
        if op == "set":
            node.update(payload)
        elif op == "resp_prefix":
            prefix, new = payload
            hits = [i for i, item in enumerate(node["responsibilities"]) if item.startswith(prefix)]
            if len(hits) != 1:
                sys.exit(f"RESP {label}: {prefix[:60]}: {len(hits)}")
            node["responsibilities"][hits[0]] = new
        elif op == "resp_append":
            if payload in node["responsibilities"]:
                sys.exit(f"RESP EXISTS {label}")
            node["responsibilities"].append(payload)
        else:
            owns = node.get("owns_state") or []
            if payload in owns:
                sys.exit(f"OWNS EXISTS {label}: {payload}")
            node["owns_state"] = list(owns) + [payload]
    elif op == "edge_why":
        source, target = key
        hits = [e for e in data.get("edges_authored", []) if e["from"] == source and e["to"] == target]
        if len(hits) != 1:
            sys.exit(f"EDGE {label}: {source} -> {target}: {len(hits)}")
        hits[0]["why"] = payload
    elif op == "edge_add":
        edges = data.setdefault("edges_authored", [])
        if any(e["from"] == payload["from"] and e["to"] == payload["to"] for e in edges):
            sys.exit(f"EDGE EXISTS {label}: {payload['to']}")
        edges.append(payload)
    else:
        sys.exit(f"OP {op}")


def main() -> None:
    loaded: Dict[str, Dict[str, Any]] = {}
    for index, (rel, op, key, payload) in enumerate(OPS):
        if rel not in loaded:
            loaded[rel] = json.loads((GRAPH / rel).read_text(encoding="utf-8"))
        apply(loaded[rel], op, key, payload, f"op {index} {rel}")
    texts = {rel: json.dumps(data, indent=1, ensure_ascii=False) + "\n" for rel, data in loaded.items()}
    for rel, text in texts.items():
        if "\r" in text:
            sys.exit(f"CR {rel}")
        json.loads(text)
    if "--write" not in sys.argv:
        print("CHECK OK", len(OPS), "ops over", sorted(texts))
        return
    for rel, text in texts.items():
        (GRAPH / rel).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", rel)


if __name__ == "__main__":
    main()
