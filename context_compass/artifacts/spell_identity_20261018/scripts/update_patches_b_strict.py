"""Update the spell_identity_is_the_code patch docs for the owner's decisions of 2026-10-18.

Architecture, Binding Pipeline and code-description patches: approved by the owner's word to land S1 with
S2's cache keys; decision B (installed third-party code named by distribution version); strict uniqueness
(S6 parked; the refusals name no duplicate option); the S2 binding manifest. Writes the new creation-cache
component patch. Every anchor must occur once; new prose lines stay within 120 characters.
"""
import datetime
import pathlib
import shutil
import sys


class PatchUpdate:
    """One read-modify-write pass over the patch folder."""

    FOLDER = (pathlib.Path.home()
              / "mnt/melder_private/context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18")
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t4")

    def __init__(self) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.BACKUP.mkdir(parents=True, exist_ok=True)
        self.pending: list = []

    def read(self, name: str) -> str:
        return (self.FOLDER / name).read_text(encoding="utf-8")

    def write(self, name: str, text: str, new: bool = False) -> None:
        """Stage one file; nothing is written until every edit of the pass has matched its anchor."""
        self.pending.append((name, text, new))

    def flush(self, name: str, text: str, new: bool = False) -> None:
        if "\r" in text:
            sys.exit(f"CR in {name}")
        path = self.FOLDER / name
        if new:
            if path.exists():
                sys.exit(f"exists: {name}")
        else:
            shutil.copy2(path, self.BACKUP / name)
        path.write_text(text, encoding="utf-8", newline="\n")

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        count = text.count(old)
        if count != 1:
            sys.exit(f"ANCHOR {label}: found {count}")
        PatchUpdate.width(new, label)
        return text.replace(old, new)

    @staticmethod
    def width(block: str, label: str) -> None:
        for line in block.split("\n"):
            if len(line) > 120 and "`src/" not in line and not line.startswith("|"):
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    def architecture(self) -> None:
        t = self.read("architecture_patch.md")
        t = self.once(t,
            "- Status: draft - for the owner's approval before any src/ edit. S1's component and code-description patches are\n"
            "  in this folder; S2-S5 add theirs before their code.\n",
            "- Status: approved - the owner's word to land S1 with S2's cache keys (chat 2026-10-18; the epic's DECISION note\n"
            "  of 2026-10-18T15:01:53Z) approves this patch; updated for his decisions of 2026-10-18. S1's and S2's component\n"
            "  patches and S1's code-description patch are in this folder; S3-S5 add theirs before their code.\n", "a status")
        t = self.once(t, "- Updated: 2026-10-18T13:21:00Z\n", f"- Updated: {self.now}\n", "a updated")
        t = self.once(t,
            "  counts; (5) the scope of a registration stays the existing spell-id regime.\n",
            "  counts; (5) the scope of a registration stays the existing spell-id regime.\n"
            "- The owner's decisions (chat 2026-10-18): the \"conduit manifest\" reading confirmed (S2 keys the creation cache on\n"
            "  each spell's binding hash, S3 revalidates on a change); installed third-party code and objects named by\n"
            "  qualified name and distribution version (decision B; a configurable later); a record holding one object twice\n"
            "  restores the first and files a shortfall per dropped duplicate (S5); one object is strictly one spell for now -\n"
            "  the explicit duplicate bind (S6) is parked - and S1 lands now with S2's cache keys.\n", "a decisions")
        t = self.once(t,
            "  - The spell-id regime itself (call 5): unique per process by default, per frame under per-frame ids.\n",
            "  - The spell-id regime itself (call 5): unique per process by default, per frame under per-frame ids.\n"
            "  - An explicit duplicate bind (S6, parked by the owner) and binding or caching patterns users choose\n"
            "    (EPIC-2026-10-18-identity_and_caching_configurables, parked).\n", "a nongoals")
        t = self.once(t,
            "| SpellCodeDigest (new: `src/melder/aether/spellbook/bind/spell_code_digest.py`) | add | the canonical code and "
            "data encoding and the spell_id (code_description_patch_spell_code_digest.md) | none |\n",
            "| SpellCodeDigest (new: `src/melder/aether/spellbook/bind/spell_code_digest.py`) | add | the canonical code and "
            "data encoding and the spell_id; installed third-party code named by distribution version (decision B) "
            "(code_description_patch_spell_code_digest.md) | none |\n", "a matrix digest")
        t = self.once(t,
            "| Creation cache (structural key, world stamp, the generalized manifest's disposal fact, generation 23) and the "
            "binding manifest (S2) | modify / add | they rely on the spell_id covering the binding | S1 (same landing) |\n",
            "| Binding manifest (S2, new: `src/melder/aether/spellbook/bind/binding_manifest.py`; `Spell` builds, carries "
            "and describes it) | add | the bind call as a value record with its own SHA256, the binding hash "
            "(component_patch_binding_pipeline.md, S2 section) | S1 (same landing) |\n"
            "| Creation cache (S2): the structural key and the world stamp carry the binding hash; generation 23; the "
            "docstrings that trust the spell_id to cover the binding | modify | they rely on the spell_id covering the "
            "binding (component_patch_creation_cache.md) | Binding manifest |\n", "a matrix cache")
        t = self.once(t,
            "| Bind-guard manifest (generated) | modify | SpellCodeDigest joins it: 628 -> 629 entries | SpellCodeDigest |\n",
            "| Bind-guard manifest (generated) | modify | SpellCodeDigest and BindingManifest join it: 628 -> 630 entries | "
            "SpellCodeDigest, Binding manifest |\n", "a matrix guard")
        t = self.once(t,
            "  instead of binding it again. Two lambdas with the same code and defaults, and two existing objects of one class\n"
            "  with equal data (D10), are one spell.\n",
            "  instead of binding it again. Two lambdas with the same code and defaults, and two existing objects of one class\n"
            "  with equal data (D10), are one spell. This holds strictly for now (the owner, 2026-10-18): no option registers\n"
            "  one object twice, and the corrected refusals name none (S6 parked).\n"
            "- Binding (S2, same landing): every Spell carries `binding_manifest` - its spellframe and kind, address,\n"
            "  existence, disposal names, resolvable and managed settings - and `binding_hash`, their SHA256; `Spell.describe`\n"
            "  shows both, and both creation-cache tiers key on the binding hash beside the spell_id.\n", "a interface")
        t = self.once(t,
            "   and `inspect.getattr_static`. The only call into an object is `repr()` of a target with no Python-visible state,\n"
            "   today's rule (`InspectorUtility.stable_repr`). An object with neither Python-visible state nor an informative\n"
            "   repr cannot be told from another of its type, today as after (D6).\n",
            "   and `inspect.getattr_static`. The only calls into objects are `repr()` (`InspectorUtility.stable_repr`) of a\n"
            "   target with no Python-visible state, today's rule, and of an object of an installed third-party class\n"
            "   (invariant 8). An object with neither Python-visible state nor an informative repr cannot be told from another\n"
            "   of its type, today as after (D6).\n", "a inv4")
        t = self.once(t,
            "7. (S2, same landing) No cache tier or emitted fact keyed by spell_id is read without the binding hash, so a binding\n"
            "   changed under one spell_id never replays a plan or a row built for another binding.\n",
            "7. (S2, same landing) No cache tier or emitted fact keyed by spell_id is read without the binding hash: the\n"
            "   structural key carries the spell's binding hash and the world stamp every pool and borrowed spell's, so a\n"
            "   binding changed under one spell_id never replays a plan or a row built for another binding.\n"
            "8. Installed third-party code (decision B): a class, metaclass or function whose module file lies under an\n"
            "   installed site-packages directory, and is not standard library, is named by qualified name and distribution\n"
            "   version, never digested; an object of such a class is named by its type, that version and its address-free\n"
            "   repr. Application code - the project's own modules, `__main__`, editable installs - is digested. A package\n"
            "   upgrade moves the ids of the spells that inherit from or hold its code; nothing else of the package enters an\n"
            "   id.\n", "a inv7")
        t = self.once(t,
            "1. This patch, S1's component patches (Binding Pipeline, Spell Examination Profiles) and S1's code-description\n"
            "   patch; the owner's approval; S1's section -> implementation -> validation mapping note.\n",
            "1. This patch, S1's component patches (Binding Pipeline, Spell Examination Profiles) and S1's code-description\n"
            "   patch, approved by the owner's word to land (2026-10-18T15:01:53Z) and updated for his decisions; S1's\n"
            "   section -> implementation -> validation mapping note.\n", "a step1")
        t = self.once(t,
            "3. S2's component patches (the binding manifest, the cache keys, generation 23) and the owner's word on the \"conduit\n"
            "   manifest\" reading.\n"
            "4. spellbook.py back from melder_1 by message (M1-31), after S8 lands if it is still open.\n",
            "3. S2's component patches - the binding manifest (component_patch_binding_pipeline.md, S2 section) and the cache\n"
            "   keys with generation 23 (component_patch_creation_cache.md); the \"conduit manifest\" reading is confirmed.\n"
            "4. spell.py and spellbook.py back from melder_1 by message (M0-196): S9 holds them (M1-33, M1-35); S8 is on hold.\n",
            "a step3")
        t = self.once(t,
            "| `structural_snapshot.py:264-268`, `generalized_manifest_no_overrides_compiler.py:99-101`, "
            "`generalized_manifest.py:190-193` | \"the spell id covers existence / disposal\" | S2 |\n",
            "| `structural_snapshot.py:264-268`, `generalized_manifest_no_overrides_compiler.py:99-101`, "
            "`generalized_manifest.py:190-193` | \"the spell id covers existence / disposal\" | S2 |\n"
            "| `spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`, `caching_system.py:CachingSystem` "
            "(class docstring) | the world stamp is \"pool ids, posture, borrowed ids\" | S2 |\n"
            "| `meld.py:2080-2080`, `:2161-2161`, `contract/details.py:198-198`, `:434-434`, `inspector_utility.py:72-72` | "
            "\"SHA256 fingerprint\", \"the bind fingerprint\" (a full sweep of src/ for \"fingerprint\" at landing) | S1 |\n",
            "a statements")
        old_unknowns = t[t.index("- DECISION_REQUEST (owner; S2): the \"conduit manifest\""):
                         t.index("- Derived from the calls, for the owner to know")]
        if "refuse the restore\n  whole, as any replay failure does today.\n" not in old_unknowns:
            sys.exit("unknowns block shape")
        new_unknowns = (
            "- DECIDED (owner, 2026-10-18; S2): the \"conduit manifest\" - each spell's binding hash is recorded in what the\n"
            "  conduit builds and caches that spell from, and a changed hash revalidates and rebuilds that spell (S2 keys the\n"
            "  cache on it; S3 revalidates).\n"
            "- DECIDED (owner, 2026-10-18; S1): B - installed third-party code and objects are named by qualified name and\n"
            "  distribution version (invariant 8); a configurable for it waits in\n"
            "  EPIC-2026-10-18-identity_and_caching_configurables. Applied to a third-party object as its type, that version\n"
            "  and its address-free repr - today's rule for an object, plus the version - because type and version alone\n"
            "  would make two differently configured library objects (two engines, two clients) one spell, and strict\n"
            "  uniqueness would then refuse the second; the owner can narrow it to type and version.\n"
            "- DECIDED (owner, 2026-10-18; S5): a record holding one object twice restores the first registration and files a\n"
            "  shortfall per dropped duplicate.\n"
            "- DECIDED (owner, 2026-10-18): one object is strictly one spell for now; the explicit duplicate bind (S6) is\n"
            "  parked in the backlog and the refusals name no duplicate option.\n")
        self.width(new_unknowns, "a unknowns")
        t = t.replace(old_unknowns, new_unknowns)
        t = self.once(t,
            "- What remains: the owner's approval and his three decisions above; the blast-radius run; S2's patches; spellbook.py\n"
            "  back from melder_1.\n"
            "- Next entrypoint: component_patch_binding_pipeline.md, then code_description_patch_spell_code_digest.md.\n",
            f"- What changed since ({self.now}): the owner's word to land S1 with S2's cache keys and his decisions\n"
            "  (Unknowns and Decision Requests); S2's patches written (the binding manifest, the creation cache).\n"
            "- What remains: the blast-radius run (step 2); spell.py and spellbook.py back from melder_1 (M0-196); the landing\n"
            "  pass (step 5).\n"
            "- Next entrypoint: component_patch_binding_pipeline.md, component_patch_creation_cache.md, then\n"
            "  code_description_patch_spell_code_digest.md.\n", "a handoff")
        self.write("architecture_patch.md", t)

    def binding_pipeline(self) -> None:
        t = self.read("component_patch_binding_pipeline.md")
        t = self.once(t,
            "  Today\", rows marked S1)\n"
            "- Status: draft - for the owner's approval\n",
            "  Today\", rows marked S1); for S2, in the same landing, the new `BindingManifest`, built and carried by `Spell`\n"
            "- Status: approved by the owner's word to land S1 with S2 (2026-10-18T15:01:53Z); updated for decision B and\n"
            "  strict uniqueness\n", "b status")
        t = self.once(t, "- Updated: 2026-10-18T13:21:00Z\n", f"- Updated: {self.now}\n", "b updated")
        t = self.once(t,
            "  refusals keep their logic; their remedy text changes in this landing - \"differentiate the binding with a distinct\n"
            "  spellframe or binding_name\" stops working once the binding leaves the id - and S4 makes them name the existing\n"
            "  registration.\n",
            "  refusals keep their logic; their remedy text changes in this landing - \"differentiate the binding with a distinct\n"
            "  spellframe or binding_name\" stops working once the binding leaves the id - and S4 makes them name the existing\n"
            "  registration. One object is strictly one spell (the owner, 2026-10-18), so no text names a duplicate option.\n"
            "  - bind and bind_inactive: \"Spell ID collision detected: this object is already registered as spell_id <id>. A\n"
            "    spell_id is the SHA256 of the object's code (its methods, constructor, class-level values and base classes,\n"
            "    or an existing object's class and data), and one object is one spell: registering it again - under another\n"
            "    binding name, existence or spellframe, or in another Spellbook where spell_ids are unique (the process by\n"
            "    default, the frame under per-frame spell ids) - is refused. Use the spell already registered (another conduit\n"
            "    shares it through a link or a contract), or cleanup_spell it and bind it again to change how it is bound. A\n"
            "    changed method, constructor, class-level value or base class is a new spell_id: stage it with bind_inactive\n"
            "    and notch to it.\"\n"
            "  - conjure's integrity check keeps its head and SCOPE lines; its explanation becomes \"A spell_id is the SHA256 of\n"
            "    the registered object's code (its methods, constructor, class-level values and base classes, or an existing\n"
            "    object's class and data) and includes neither the frame nor the bind call, so two Spellbooks binding the same\n"
            "    object mint the same id\", its fix \"bind the object in one Spellbook and share it with the others (a link or\n"
            "    a contract); one object is one spell\", and its last sentence ends \"the id follows the code, and the code has\n"
            "    no frame in it\".\n", "b refusals")
        t = self.once(t,
            "2. The spellbook.py edits (inspect_spell's text, the three refusal texts) wait for spellbook.py to come back from\n"
            "   melder_1 (M1-31, S8's landing).\n",
            "2. The spellbook.py edits (inspect_spell's text, the three refusal texts) and the spell.py edits (the spell_id\n"
            "   docstrings, the S2 manifest) wait for both files to come back from melder_1 (M0-196; S9 holds them, M1-33).\n",
            "b ordering")
        s2 = (
            "## S2 (same landing): the binding manifest\n"
            "- Purpose: once the spell_id is the object's code, how a spell is kept needs an identity of its own (the owner,\n"
            "  chat 2026-10-18: \"bind signature can get its own hash signature we could put into a manifest associated with an\n"
            "  object\"). `BindingManifest` (new: `src/melder/aether/spellbook/bind/binding_manifest.py`) is that record: a\n"
            "  value object holding no live reference, built once per Spell.\n"
            "- Fields, in hash order: `frame_key` and `binding_key` (the address, `Spell._key`, normalized as bind claims it);\n"
            "  `spellframe` (the bind call's spellframe as text: \"\" for none, the category as written, `<module>.<qualname>`\n"
            "  of a Protocol contract); `spellframe_kind` (the `SpellframeKind` name); `binding_name` (as written, or None);\n"
            "  `existence` (the `Existence` name); `disposal_method_names` (the resolved list in execution order, a tuple);\n"
            "  `resolvable`; `managed_spell_mode` (the `ManagedSpellMode` name, or None), `managed_spell_limit`,\n"
            "  `managed_spell_timeout_seconds` and `managed_spell_reset_methods` (a tuple).\n"
            "- `binding_hash` is the SHA256 hex digest of `\"v1-binding\\n\"` and one `<field>=<repr(value)>` line per field, in\n"
            "  that order, newline-joined. Every value is None, a bool, an int, a float, a str or a tuple of str, so the text\n"
            "  is the same in every process and GIL mode.\n"
            "- Not in it: permissions, hooks, application metadata and the aetheric frame - no compiled plan, structural row\n"
            "  or verdict reads them (searched: `aether/spellbook/spell_compiler`, `aether/conduit/meld`) - and the object's\n"
            "  code, which is its spell_id.\n"
            "- `Spell.__init__` builds it last, from its own arguments (`BindingManifest.build(...)`), so every Spell - bound,\n"
            "  staged, restored or grafted - carries one, computed once; Bind passes nothing new. `Spell.binding_manifest` is\n"
            "  public and read-only by contract, `Spell.binding_hash` returns its hash, `Spell.describe()` adds both, and both\n"
            "  survive cleanup like `spell_id` (value data). No lock: the constructor runs before the Spell is reachable.\n"
            "- `BindingManifest.describe()` returns the fields and the hash as a marshal- and JSON-safe dict.\n"
            "- Consumers in this landing: the creation cache (component_patch_creation_cache.md). Later: S3 revalidates a\n"
            "  spell whose binding hash changes; S5 adds the hash to the SpellCrystal with the record's other changes (the\n"
            "  crystal already records every field, and a restore replays them through bind, which rebuilds the same hash).\n"
            "- Validation: each field moves the hash and nothing else does; equal arguments give equal hashes in two processes\n"
            "  and with the GIL off and on; `describe()`; a bound, a staged and a restored Spell carry the manifest their bind\n"
            "  call implies; `Spell.binding_hash` after cleanup.\n\n")
        self.width(s2, "b s2")
        t = self.once(t, "## Unknowns and Open Decisions\n", s2 + "## Unknowns and Open Decisions\n", "b s2 insert")
        t = self.once(t,
            "- DECISION_REQUEST (owner): third-party code and objects (architecture patch).\n",
            "- DECIDED (owner, 2026-10-18): installed third-party code and objects are named by distribution version (B;\n"
            "  architecture patch, invariant 8).\n", "b decided")
        t = self.once(t,
            "- Next entrypoint: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic` (the fingerprint call at 795-803).\n",
            "- Next entrypoint: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic` (the fingerprint call at 795-803);\n"
            "  for S2, `src/melder/aether/spellbook/spell.py:Spell.__init__` (its last lines, 569-576).\n", "b next")
        self.write("component_patch_binding_pipeline.md", t)

    def code_description(self) -> None:
        t = self.read("code_description_patch_spell_code_digest.md")
        t = self.once(t, "- Status: draft - for the owner's approval\n",
                      "- Status: approved by the owner's word to land S1 (2026-10-18T15:01:53Z); updated for decision B\n",
                      "c status")
        t = self.once(t, "- Updated: 2026-10-18T13:42:22Z\n", f"- Updated: {self.now}\n", "c updated")
        t = self.once(t,
            "   a. a class: `\"class \" + class_digest(target)`;\n"
            "   b. a plain Python function (`types.FunctionType`): `\"function \" + module + \" \" + qualname + \" \" +\n"
            "      function_digest(target)`;\n",
            "   a. a class: `\"class \" + class_digest(target)`, or `\"class \" + named(target)` when it is installed third-party;\n"
            "   b. a plain Python function (`types.FunctionType`): `\"function \" + module + \" \" + qualname + \" \" +\n"
            "      function_digest(target)`, or `\"function \" + named(target)` when it is installed third-party;\n",
            "c rule ab")
        t = self.once(t,
            "   d. an object with Python-visible state - an instance `__dict__`, or a `__slots__` entry on a class of its MRO -\n"
            "      whose type is neither standard library nor Melder: `\"object \" + class_digest(type(target)) + data(target)`;\n",
            "   d. an object with Python-visible state - an instance `__dict__`, or a `__slots__` entry on a class of its MRO -\n"
            "      whose type is application code (not standard library, Melder or installed third-party):\n"
            "      `\"object \" + class_digest(type(target)) + data(target)`;\n"
            "   d2. an object of an installed third-party class other than Melder's: `\"object \" + external(target)` (the\n"
            "      value table's `ext:` row);\n",
            "c rule d")
        t = self.once(t,
            "3. `class_digest(cls)`: the lines `module <module>`, `qualname <qualname>`, `meta <metaclass>` (its qualified name\n"
            "   when it is standard library, else its qualified name and its class digest), `bases <qualified names of\n"
            "   __bases__, comma-joined>`, then one line per class of `cls.__mro__`, in order: `own <namespace_digest(cls)>` for\n"
            "   cls itself; `mro <qualified>` for a standard-library or builtin class; `mro <qualified> <namespace_digest>` for any\n"
            "   other. The SHA256 of the lines joined by newlines.\n",
            "3. `class_digest(cls)`: the lines `module <module>`, `qualname <qualname>`, `meta <metaclass>` (its qualified name\n"
            "   when it is standard library, its qualified name and distribution version when it is installed third-party,\n"
            "   else its qualified name and its class digest), `bases <qualified names of __bases__, comma-joined>`, then one\n"
            "   line per class of `cls.__mro__`, in order: `own <namespace_digest(cls)>` for cls itself; `mro <qualified>` for\n"
            "   a standard-library or builtin class; `mro <qualified> <dist>==<version>` for an installed third-party class;\n"
            "   `mro <qualified> <namespace_digest>` for any other. The SHA256 of the lines joined by newlines.\n",
            "c rule3")
        t = self.once(t,
            "| a plain function | `fn:<function_digest>` |\n",
            "| a plain function | `fn:<function_digest>`; an installed third-party one `fn:<qualified> <dist>==<version>` |\n",
            "c fn row")
        t = self.once(t,
            "| an object with Python-visible state | `obj:<qualified type>{<data>}` |\n",
            "| an object of an installed third-party class | `ext:<qualified type> <dist>==<version> <stable_repr>` |\n"
            "| an object with Python-visible state (application code) | `obj:<qualified type>{<data>}` |\n", "c ext row")
        old_std = t[t.index("- Standard library: a module whose top-level name"):t.index("- `qualified(x)` is")]
        if "(decision A); under decision B" not in old_std:
            sys.exit("std paragraph shape")
        new_std = (
            "- Standard library: a module whose top-level name is in `sys.stdlib_module_names` or is `builtins`, or no module.\n"
            "  Installed third-party (decision B): a module, not standard library, whose `__file__` lies under one of the\n"
            "  interpreter's site-packages directories (`sysconfig` purelib and platlib, `site.getsitepackages()`,\n"
            "  `site.getusersitepackages()`). `named(x)` is `<qualified> <dist>==<version>`: the distribution that installs\n"
            "  its top-level package - `importlib.metadata.version(top)` first, `importlib.metadata.packages_distributions()`\n"
            "  once per SpellCodeDigest when the import name is not a distribution name - or `?==?` when none is found;\n"
            "  `external(obj)` is `ext:` + `named(type(obj))` + its `stable_repr`. Module locations and versions are memoized\n"
            "  per SpellCodeDigest. Application code: everything else - the project's modules, `__main__`, editable installs,\n"
            "  a module that cannot be located. Melder: `melder` and `melder.*`, for objects only (`ref:`); a Melder class in\n"
            "  an MRO is code like any other - digested when Melder runs from source, named by version when it is installed.\n")
        self.width(new_std, "c std")
        t = t.replace(old_std, new_std)
        t = self.once(t,
            "  (the prototype's `melder-code-digest/v2`); the RecursionError fallback.\n",
            "  (the prototype's `melder-code-digest/v2`); the RecursionError fallback; decision B (the prototype digested\n"
            "  installed packages like the application).\n", "c changed")
        t = self.once(t,
            "- No lock: the owner serializes calls (Bind holds its lock around `_bind_logic`; `spell_id_inspector` uses its own\n"
            "  instance). No target code runs, except `repr()` in rule 2e.\n",
            "- No lock: the owner serializes calls (Bind holds its lock around `_bind_logic`; `spell_id_inspector` uses its own\n"
            "  instance). No target code runs, except `repr()` in rule 2e and for an installed third-party object (`ext:`).\n",
            "c nolock")
        t = self.once(t,
            "  runtime class state E25, E25b, E25c, E33; monitoring and tracing E34, E34b; module and qualname E14, E15.\n",
            "  runtime class state E25, E25b, E25c, E33; monitoring and tracing E34, E34b; module and qualname E14, E15;\n"
            "  decision B: a class over an installed third-party base (D9's pygments lexer) named by version, an installed\n"
            "  third-party object by type, version and repr, an application or `__main__` class digested.\n", "c focus")
        t = self.once(t,
            "- Remaining unknowns: decision A or B for third-party code (architecture patch); GIL versus free-threaded\n"
            "  instructions for one Python version.\n",
            "- Remaining unknowns: GIL versus free-threaded instructions for one Python version. Decision B is made (the\n"
            "  owner, 2026-10-18).\n", "c unknowns")
        self.write("code_description_patch_spell_code_digest.md", t)

    def creation_cache(self) -> None:
        now = self.now
        text = "\n".join([
            "# Component patch: Spellbook Core - the creation cache keys on the binding hash (spell_identity_is_the_code_2026_10_18)",
            "",
            "## Metadata",
            "- Patch ID: spell_identity_is_the_code_2026_10_18",
            "- Component: Spellbook Core (Binding and Conjure) - its creation cache: `StructuralSnapshot.PAYLOAD_FORMAT`,",
            "  `structural_key`, `world_stamp` and `payload_well_formed`",
            "  (`src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py`);",
            "  `CachingSystem.CACHE_VERSION_HISTORY` and the class docstring (`src/melder/utilities/caching_system/caching_system.py`);",
            "  the docstring and comment of `SpellbookCreationSystem._build_conjure_cache_state`",
            "  (`src/melder/aether/spellbook/spellbook_creation_system.py`); the generalized family's comment and docstring",
            "  that trust the spell_id to cover the binding (`generalized_manifest_no_overrides_compiler.py`,",
            "  `generalized_manifest.py`, under `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/`)",
            "- Story: STORY-2026-10-18-binding_manifest_hash (S2), landing with STORY-2026-10-18-spell_id_hashes_the_object_code",
            "  (S1)",
            "- Status: approved - the owner's word to land S1 with S2's cache keys (chat 2026-10-18; the epic's DECISION note",
            "  of 2026-10-18T15:01:53Z) and his confirmation of the \"conduit manifest\" reading (DECISION note of",
            "  2026-10-18T14:14:10Z)",
            "- Owner: user; melder_0 (synaptic_python_developer)",
            f"- Created: {now}",
            f"- Updated: {now}",
            "",
            "## Component Purpose and Boundary",
            "- Current boundary, read whole on 0.2.8255: one `.meldercache` bundle per root conduit holds two tiers, both keyed",
            "  by spell_id.",
            "  - Structural tier: one payload per owned spell, keyed `{format, spell_id, annotation_refs}` and carrying the",
            "    world stamp, a SHA256 over the sorted pool ids, the frame posture and the sorted borrowed ids. A conjure",
            "    replays phases 3-4 when every owned spell's payload carries its live key, the live stamp and a replayable",
            "    verdict, and captures fresh payloads at its end on every cache path (`StructuralSnapshot.structural_key`,",
            "    `world_stamp`, `classify`, `capture_at_conjure_end`).",
            "  - Executor tier: one manifest package per payload-eligible spell. A conjure skips phases 8-11 and loads every",
            "    context from its package when every live id is cached and the envelope's recorded stamp equals the live one;",
            "    any other conjure compiles, removes every package, restages every live spell and records the stamp",
            "    (`SpellbookCreationSystem._build_conjure_cache_state`, `_load_cached_creation_contexts_for_conjure`,",
            "    `_stage_spell_payloads_at_conjure_end`). A meld stages a package only for an id the bundle lacks",
            "    (`Spellbook._emit_spell_cache`).",
            "  - Both rest on the spell_id covering the binding. The key's docstring says \"the spell id already covers the",
            "    spell's own signature, names, existence and resolvability\", and the generalized family stamps each step's",
            "    existence and disposal flag into the rows a cached plan is emitted from, trusting that \"disposal facts",
            "    compose into the spell fingerprint\".",
            "- Target boundary: the same tiers and rules with each spell's binding hash beside its spell_id. The structural key",
            "  gains `binding_hash`, and the world stamp hashes every pool id and every borrowed id with its spell's binding",
            "  hash. One stamp feeds both tiers, so a binding changed under one spell_id - existence, disposal names, address,",
            "  spellframe, resolvable or managed settings - misses both tiers for the Book, as a changed spell_id does today.",
            "",
            "## Before/After Behavior Summary",
            "- Without this patch, S1 would let a stale plan through: `Greeter` cached as `unique`, then bound as `many` in the",
            "  next process, keeps one spell_id and one pool, so both tiers would hit and its consumers would replay plans",
            "  emitted for a `unique` provider.",
            "- With it, that world's stamp differs, so both tiers miss once, recompile and restage; a repeat world is a",
            "  byte-identical full hit as today, and worlds whose bindings did not change hit exactly as today.",
            "",
            "## Interface Deltas",
            "- Inputs: none new. `StructuralSnapshot.world_stamp(spellbook)` and `structural_key(spell)` keep their signatures",
            "  and read `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section).",
            "- Outputs: the structural key is `{\"format\": 2, \"spell_id\", \"binding_hash\", \"annotation_refs\"}` (`PAYLOAD_FORMAT`",
            "  1 -> 2, checked by `payload_well_formed`); the stamp's lines are `pool:<id>=<binding_hash>,...` (sorted by id),",
            "  `posture:<name>` and `borrowed:<id>=<binding_hash>,...` (sorted); the envelope format is unchanged.",
            "- `CachingSystem.CACHE_VERSION_HISTORY` gains 23: \"binding_manifest_keys\"; a generation-22 bundle is cold once.",
            "- Error semantics: unchanged - a malformed or older payload is a miss, an older bundle a cold cache.",
            "",
            "## State and Lifecycle Deltas",
            "- Owned state changes: none. Both values are computed from the Book's Spells at classification and capture, as",
            "  the stamp is today; `Spell.binding_hash` is computed once at bind.",
            "- Lifecycle/cleanup changes: none.",
            "",
            "## Failure Mode Deltas",
            "- New failure mode: none. Removed: the stale replay S1 alone would allow (above).",
            "- Changed: none visible. A binding change changed the spell_id and missed both tiers; it now keeps the spell_id",
            "  and still misses both.",
            "- Residual, unchanged (RISK, low): a package staged at a meld for an id the bundle lacked - possible only after",
            "  that spell's conjure-end staging failed, which is logged - is replayed by a later full hit of the stamped world",
            "  even when the spell was rebound in between; the restaging that follows any miss replaces it.",
            "",
            "## Dependency and Ordering Constraints",
            "1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py",
            "   (M0-196).",
            "2. Lands with S1 in one pass: the cache never sees S1's spell_id without the binding hash (architecture patch,",
            "   invariant 7).",
            "3. The generation bump is in the same change set as the key and stamp change.",
            "",
            "## Validation Expectations",
            "- Unit: the key carries the binding hash and `payload_well_formed` refuses format 1; the stamp moves when one pool",
            "  spell's binding hash moves (existence, disposal names, resolvable, managed settings) and when a borrowed",
            "  spell's does, and is byte-identical for one world across two processes and with the GIL off and on.",
            "- Integration: bind a class as `unique`, conjure and emit; a fresh Aether binds it as `many` (one spell_id) and",
            "  conjures - the structural path is a miss, the executor path mixed, and the consumer builds a new provider per",
            "  meld; the same world twice is a full hit on both tiers.",
            "- `CachingSystem`: a generation-22 bundle loads cold.",
            "- The existing structural-snapshot and executor-cache suites pass, the format assertions moved to 2.",
            "",
            "## Unknowns and Open Decisions",
            "- UNKNOWN: none in the code paths read.",
            "- RISK (low): the residual under Failure Mode Deltas; closing it needs a per-package record of the world it was",
            "  staged in, which no reachable path but a logged staging failure exercises.",
            "",
            "## Context / Handoff Summary",
            "- What changed: nothing in `src/`.",
            "- Remaining risks: the residual above.",
            "- Next entrypoint:",
            "  `src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:StructuralSnapshot.world_stamp`.",
            "",
        ])
        self.width(text, "creation cache")
        self.write("component_patch_creation_cache.md", text, new=True)

    def exam_profiles(self) -> None:
        t = self.read("component_patch_spell_examination_profiles.md")
        t = self.once(t,
            "- Status: draft - for the owner's approval (he may keep the fields; then this patch is dropped and they stay unused)\n",
            "- Status: approved - the owner's word to land S1 (2026-10-18T15:01:53Z) approves it with its recommendation:\n"
            "  the fields are removed\n", "e status")
        t = self.once(t, "- Updated: 2026-10-18T13:21:00Z\n", f"- Updated: {self.now}\n", "e updated")
        t = self.once(t,
            "  that fill them are removed. The display fields stay; `InspectorUtility.stable_repr` stays, because SpellCodeDigest\n"
            "  uses it for a target with no Python-visible state (code-description patch).\n",
            "  that fill them are removed. The display fields stay; `InspectorUtility.stable_repr` stays, because SpellCodeDigest\n"
            "  uses it for a target with no Python-visible state and for an object of an installed third-party class\n"
            "  (decision B; code-description patch).\n", "e boundary")
        t = self.once(t,
            "- The owner may keep the fields (no reader would remain); recommended: remove them, since a field nothing reads is\n"
            "  a second, stale description of identity.\n",
            "- DECIDED (the owner's word to land S1, 2026-10-18): the fields are removed, as recommended - a field nothing\n"
            "  reads is a second, stale description of identity.\n", "e decided")
        self.write("component_patch_spell_examination_profiles.md", t)

    def run(self) -> None:
        self.architecture()
        self.binding_pipeline()
        self.code_description()
        self.exam_profiles()
        self.creation_cache()
        for item in self.pending:
            self.flush(*item)
        print("OK", self.now, [item[0] for item in self.pending])


if __name__ == "__main__":
    PatchUpdate().run()
