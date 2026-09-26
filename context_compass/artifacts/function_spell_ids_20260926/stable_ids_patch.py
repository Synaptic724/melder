"""Apply the stable-callable-spell-id + conjure-cache-restage change to a repository root.

Usage: stable_ids_patch.py <root>. Each anchor is matched with CRLF first, then LF, and the replacement
uses the newline style of the matched anchor, so mixed-EOL files keep their per-line style.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
BASE = "src/melder/aether/spellbook/"


def _variant(text: str, nl: str) -> str:
    return text.replace("\n", nl)


def rep(t: str, old: str, new: str, count: int = 1) -> str:
    for nl in ("\r\n", "\n"):
        o = _variant(old, nl)
        n = t.count(o)
        if n:
            assert n == count, (old[:70], n, count)
            return t.replace(o, _variant(new, nl))
    raise AssertionError(("anchor not found", old[:90]))


def edit(rel: str, fn) -> None:
    p = ROOT / rel
    t = p.read_bytes().decode("utf-8")
    t2 = fn(t)
    assert t2 != t, rel
    p.write_bytes(t2.encode("utf-8"))
    print("ok", rel)


# ---------------------------------------------------------------- InspectorUtility
def inspector(t: str) -> str:
    t = rep(t, "import inspect\nfrom typing import Any, Optional, ClassVar\n",
            "import inspect\nimport re\nfrom typing import Any, Optional, ClassVar\n")
    t = rep(t, "          causes inspection to fail.\n        - The utility does not own any mutable runtime state.\n    \"\"\"\n    __slots__ = ()\n",
            "          causes inspection to fail.\n        - The utility does not own any mutable runtime state.\n    \"\"\"\n    __slots__ = ()\n"
            "    # CPython's default reprs embed the object's address as \" at 0x<hex>\"; it changes per process.\n"
            "    _MEMORY_ADDRESS_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r\" at 0x[0-9a-fA-F]+\")\n\n")
    t = rep(t, "            # If repr() fails for any reason, return a placeholder indicating the type\n"
               "            return f\"<unrepr-able {type(obj).__name__}>\"\n\n    @staticmethod\n    def is_extension_module(",
            "            # If repr() fails for any reason, return a placeholder indicating the type\n"
            "            return f\"<unrepr-able {type(obj).__name__}>\"\n\n"
            "    @staticmethod\n"
            "    def stable_repr(obj: Any) -> str:\n"
            "        \"\"\"\n"
            "        Return the complete repr() of an object with every CPython memory address removed.\n\n"
            "        Purpose:\n"
            "            Give the bind fingerprint a representation that is identical in every process for the\n"
            "            same object content. CPython's default reprs embed the object's address\n"
            "            (`<function f at 0x...>`, `<C object at 0x...>`, `functools.partial(<function f at\n"
            "            0x...>, ...)`), which differs between processes and would give the same spell a new id\n"
            "            every run.\n\n"
            "        Contract:\n"
            "            - Removes every \" at 0x<hex>\" fragment from the full repr() text.\n"
            "            - Never truncates: cutting after the removal would still depend on how many digits\n"
            "              the removed addresses had, so the whole text is kept.\n"
            "            - Never raises; a failing repr() yields the same placeholder as `safe_repr`.\n"
            "            - Addresses printed in any other form (a custom __repr__ showing hex ids) are left\n"
            "              untouched; they are that object's own identity text.\n\n"
            "        Args:\n"
            "            obj: Object to represent.\n\n"
            "        Returns:\n"
            "            str: Address-free, untruncated representation text.\n"
            "        \"\"\"\n"
            "        try:\n"
            "            text = repr(obj)\n"
            "        except Exception:\n"
            "            # Same best-effort placeholder as safe_repr: a broken repr must not fail binding.\n"
            "            return f\"<unrepr-able {type(obj).__name__}>\"\n"
            "        return InspectorUtility.strip_memory_addresses(text)\n\n"
            "    @staticmethod\n"
            "    def strip_memory_addresses(text: str) -> str:\n"
            "        \"\"\"\n"
            "        Remove every CPython \" at 0x<hex>\" memory-address fragment from a representation text.\n\n"
            "        Contract:\n"
            "            - Pure and deterministic; only the fragment is removed, the rest of the text is kept.\n\n"
            "        Args:\n"
            "            text: Representation text, possibly containing addresses.\n\n"
            "        Returns:\n"
            "            str: The text without memory addresses.\n"
            "        \"\"\"\n"
            "        return InspectorUtility._MEMORY_ADDRESS_PATTERN.sub(\"\", text)\n\n"
            "    @staticmethod\n    def is_extension_module(")
    return t


# ---------------------------------------------------------------- binding profiles
FP_DOC = ("            fingerprint_repr:\n"
          "                Optional address-free, untruncated repr used only by the bind fingerprint\n"
          "                (`InspectorUtility.stable_repr`). None means the fingerprint derives the text\n"
          "                from `repr_string` with memory addresses removed.\n")


def profiles(t: str) -> str:
    i_sum = t.index("class CallableParameterBindingSummary")
    i_call = t.index("class CallableBindingProfile")
    i_inst = t.index("class InstanceBindingProfile")
    i_other = t.index("class OtherBindingProfile")
    head, summ, call, inst, other = t[:i_sum], t[i_sum:i_call], t[i_call:i_inst], t[i_inst:i_other], t[i_other:]
    summ = rep(summ, '    __slots__ = ["name", "kind", "default_repr", "annotation_repr"]\n',
               '    __slots__ = ["name", "kind", "default_repr", "annotation_repr", "default_fingerprint_repr"]\n')
    summ = rep(summ, "            annotation_repr: Optional[str],\n    ) -> None:\n",
               "            annotation_repr: Optional[str],\n            default_fingerprint_repr: Optional[str] = None,\n    ) -> None:\n")
    summ = rep(summ, "            annotation_repr:\n                Optional annotation representation.\n",
               "            annotation_repr:\n                Optional annotation representation.\n"
               "            default_fingerprint_repr:\n"
               "                Optional address-free, untruncated default repr used only by the bind\n"
               "                fingerprint. None means the fingerprint derives it from `default_repr`.\n")
    summ = rep(summ, "        self.annotation_repr: Optional[str] = annotation_repr\n",
               "        self.annotation_repr: Optional[str] = annotation_repr\n"
               "        self.default_fingerprint_repr: Optional[str] = default_fingerprint_repr\n")
    call = rep(call, '        "repr_string",\n        "signature",\n', '        "repr_string",\n        "fingerprint_repr",\n        "signature",\n')
    call = rep(call, "            abstract: bool = False,\n    ) -> None:\n",
               "            abstract: bool = False,\n            fingerprint_repr: Optional[str] = None,\n    ) -> None:\n")
    call = rep(call, "            abstract:\n                Whether the callable appears abstract.\n",
               "            abstract:\n                Whether the callable appears abstract.\n" + FP_DOC)
    call = rep(call, "        self.abstract: bool = abstract\n",
               "        self.abstract: bool = abstract\n        self.fingerprint_repr: Optional[str] = fingerprint_repr\n")
    call = rep(call, "        del self.abstract\n", "        del self.abstract\n        del self.fingerprint_repr\n")
    out = []
    for seg in (inst, other):
        seg = rep(seg, '        "repr_string",\n    ]\n', '        "repr_string",\n        "fingerprint_repr",\n    ]\n')
        seg = rep(seg, "            repr_string: str,\n    ) -> None:\n",
                  "            repr_string: str,\n            fingerprint_repr: Optional[str] = None,\n    ) -> None:\n")
        seg = rep(seg, "            repr_string:\n                Detached representation string.\n",
                  "            repr_string:\n                Detached representation string.\n" + FP_DOC)
        seg = rep(seg, "        self.repr_string: str = repr_string\n",
                  "        self.repr_string: str = repr_string\n        self.fingerprint_repr: Optional[str] = fingerprint_repr\n")
        seg = rep(seg, "        del self.repr_string\n", "        del self.repr_string\n        del self.fingerprint_repr\n")
        out.append(seg)
    return head + summ + call + out[0] + out[1]


# ---------------------------------------------------------------- strategy
def strategy(t: str) -> str:
    t = rep(t, "        signature text and annotation reprs render those names as source text so\n        they never embed an object address.\n",
            "        signature text and annotation reprs render those names as source text so\n        they never embed an object address.\n"
            "        `fingerprint_repr` and each parameter's `default_fingerprint_repr` carry the\n"
            "        address-free, untruncated repr the bind fingerprint hashes; `repr_string` and\n"
            "        `default_repr` stay the truncated display text.\n")
    t = rep(t, "                default_repr = None\n                if parameter.default is not inspect.Parameter.empty:\n"
               "                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)\n",
            "                default_repr = None\n                default_fingerprint_repr = None\n"
            "                if parameter.default is not inspect.Parameter.empty:\n"
            "                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)\n"
            "                    default_fingerprint_repr = InspectorUtility.stable_repr(parameter.default)\n")
    t = rep(t, "                        annotation_repr=annotation_repr,\n",
            "                        annotation_repr=annotation_repr,\n                        default_fingerprint_repr=default_fingerprint_repr,\n")
    t = rep(t, "            repr_string=InspectorUtility.safe_repr(effective, self.max_repr),\n",
            "            repr_string=InspectorUtility.safe_repr(effective, self.max_repr),\n"
            "            fingerprint_repr=InspectorUtility.stable_repr(effective),\n")
    t = rep(t, "            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),\n        )\n",
            "            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),\n"
            "            fingerprint_repr=InspectorUtility.stable_repr(obj),\n        )\n", count=2)
    t = rep(t, "        Build the binding-time profile for one existing instance candidate.\n",
            "        Build the binding-time profile for one existing instance candidate.\n\n"
            "        The display `repr_string` is truncated; `fingerprint_repr` is the full repr with memory\n"
            "        addresses removed, so a default-repr object gets the same spell id in every process.\n")
    t = rep(t, "        Build the fallback binding profile for unsupported candidate shapes.\n",
            "        Build the fallback binding profile for unsupported candidate shapes.\n\n"
            "        Carries the same address-free `fingerprint_repr` as the instance profile.\n")
    return t


# ---------------------------------------------------------------- bind
def bind(t: str) -> str:
    t = rep(t, "from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (\n"
               "    ClassBindingProfile,\n    CallableBindingProfile,\n    InstanceBindingProfile,\n    OtherBindingProfile,\n)\n",
            "from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (\n"
            "    ClassBindingProfile,\n    CallableBindingProfile,\n    CallableParameterBindingSummary,\n"
            "    InstanceBindingProfile,\n    OtherBindingProfile,\n)\n"
            "from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility\n")
    t = rep(t, "        Contract:\n            - Fingerprints normalized bind-time metadata only, not transient\n              runtime object identity.\n",
            "        Contract:\n            - Fingerprints normalized bind-time metadata only, not transient\n              runtime object identity.\n"
            "            - Repr-derived inputs (callable/instance/other repr and callable parameter\n"
            "              defaults) are address-free: the profile's `fingerprint_repr` /\n"
            "              `default_fingerprint_repr` when present, otherwise the display text with every\n"
            "              \" at 0x<hex>\" removed. The same object content therefore gets the same id in\n"
            "              every process (2026-09-26). The class init_signature and callable\n"
            "              signature texts are hashed with addresses removed too (a default such as\n"
            "              object() renders its address inside the signature).\n")
    t = rep(t, "                profile.init_signature or \"\",\n",
            "                InspectorUtility.strip_memory_addresses(profile.init_signature or \"\"),\n")
    t = rep(t, "                profile.signature or \"\",\n",
            "                InspectorUtility.strip_memory_addresses(profile.signature or \"\"),\n")
    t = rep(t, "                f\"{p.name}:{p.kind}={p.default_repr}\"\n",
            "                f\"{p.name}:{p.kind}={Bind._fingerprint_default_text(p)}\"\n")
    t = rep(t, "                (profile.repr_string or \"\").strip(),\n", "                Bind._fingerprint_repr_text(profile),\n", count=3)
    t = rep(t, "    @staticmethod\n    def _validate_resolvable(resolvable: bool) -> None:\n",
            "    @staticmethod\n"
            "    def _fingerprint_repr_text(\n"
            "            profile: Union[CallableBindingProfile, InstanceBindingProfile, OtherBindingProfile],\n"
            "    ) -> str:\n"
            "        \"\"\"\n"
            "        Return the address-free representation text a binding profile contributes to its fingerprint.\n\n"
            "        Contract:\n"
            "            - Prefers `fingerprint_repr` (full repr, addresses removed, built by the binding\n"
            "              strategy); strips surrounding whitespace like the display text always was.\n"
            "            - Falls back to `repr_string` with memory addresses removed for profiles built without\n"
            "              it (direct constructions); that text may still be truncated display text.\n\n"
            "        Args:\n"
            "            profile: Callable, instance or other binding profile.\n\n"
            "        Returns:\n"
            "            str: Text hashed into the fingerprint.\n"
            "        \"\"\"\n"
            "        if profile.fingerprint_repr is not None:\n"
            "            return profile.fingerprint_repr.strip()\n"
            "        return InspectorUtility.strip_memory_addresses((profile.repr_string or \"\").strip())\n\n"
            "    @staticmethod\n"
            "    def _fingerprint_default_text(parameter: CallableParameterBindingSummary) -> Optional[str]:\n"
            "        \"\"\"\n"
            "        Return the address-free default-value text one callable parameter contributes to the fingerprint.\n\n"
            "        Contract:\n"
            "            - Prefers `default_fingerprint_repr`; otherwise `default_repr` with memory addresses\n"
            "              removed; None when the parameter has no default (rendered as \"None\", unchanged).\n\n"
            "        Args:\n"
            "            parameter: Parameter summary from a callable binding profile.\n\n"
            "        Returns:\n"
            "            Optional[str]: Default text hashed into the fingerprint, or None.\n"
            "        \"\"\"\n"
            "        if parameter.default_fingerprint_repr is not None:\n"
            "            return parameter.default_fingerprint_repr\n"
            "        if parameter.default_repr is None:\n"
            "            return None\n"
            "        return InspectorUtility.strip_memory_addresses(parameter.default_repr)\n\n"
            "    @staticmethod\n    def _validate_resolvable(resolvable: bool) -> None:\n")
    return t


# ---------------------------------------------------------------- creation system
STAGE = '''    @staticmethod
    def _stage_spell_payloads_at_conjure_end(
            *,
            spellbook: Spellbook,
            cache_state: dict[str, Any],
    ) -> None:
        """
        Rebuild the conduit cache bundle from this conjure's compile.

        Purpose:
            Make conjure the staging boundary for every constructed spell so a
            cache full hit does not depend on each spell being melded directly
            at least once. Dependency-only spells never receive their own
            `CreationContextFactory` publish, so meld-time staging alone leaves
            them permanently missing from the bundle and locks the conduit
            cache into the mixed path, recompiling phases 8-11 on every
            conjure.
            Re-staging EVERY live spell, not only the missing ones, keeps the
            bundle one consistent world: a consumer's cached manifest names its
            providers' spell ids, so when a provider's id changes, a consumer
            payload kept from the previous world would make the next full hit
            fail at hydration ("generalized manifest references unknown
            spell_id"). Stale ids are dropped for the same reason and so the
            bundle cannot grow without bound (2026-09-26, generation 12).

        Contract:
            - Runs only on non-full-hit conjures, after phases 8-11 have built
              the compiler artifact for every constructed spell; staging is a
              metadata read for manifest-first families.
            - Removes every payload in the bundle, then stages every live
              payload-eligible spell in sorted id order through
              `Spellbook._emit_spell_cache` (unchanged: it skips spells with
              caching disabled, refuses non-replayable plans and flags the
              conjure-end file emit on success).
            - Flags the conjure-end emit when anything was removed, so a pruned
              bundle is persisted even if nothing re-staged.
            - Payload eligibility is enforced upstream: `live_spell_ids`
              derives from `_build_conjure_cache_state`, which already excludes
              existing-creation and non-resolvable spells.
            - Best-effort per spell: a staging miss leaves that spell out of
              the bundle, so it compiles on the next conjure instead of
              hydrating a plan from another world.
            - No-op when caching is disabled (no cache utility in the state).

        Args:
            spellbook:
                Owning Spellbook whose bundle should be rebuilt.
            cache_state:
                Conjure cache-state summary built by
                `_build_conjure_cache_state`.

        Returns:
            None.
        """
        caching_system = cache_state["caching_system"]
        if caching_system is None:
            return
        # The cached-id view is live and this loop removes from the store it
        # views, so iterate over a detached copy (required for correctness).
        removed_any = False
        for cached_spell_id in tuple(caching_system.cached_spell_ids):
            if caching_system.remove_spell_payload(cached_spell_id):
                removed_any = True
        for spell_id in sorted(cache_state["live_spell_ids"]):
            spellbook._emit_spell_cache(spellbook._spell_id_pool[spell_id])
        if removed_any:
            spellbook._cache_emit_required = True

'''


def creation(t: str) -> str:
    nl = "\r\n" if "\r\n" in t[t.index("def _stage_spell_payloads_at_conjure_end"):t.index("def _emit_conduit_cache_file_at_conjure_end")] else "\n"
    start = t.index("    @staticmethod" + nl + "    def _stage_spell_payloads_at_conjure_end(")
    end = t.index("    @staticmethod" + nl + "    def _emit_conduit_cache_file_at_conjure_end(")
    old = t[start:end]
    assert "missing_spell_ids" in old and old.count("def ") == 1
    return t[:start] + STAGE.replace("\n", nl) + t[end:]


# ---------------------------------------------------------------- caching system
def caching(t: str) -> str:
    t = rep(t, "    # Version 11: a typed parameter with no registered provider compiles as an\n",
            "    # Version 12: a non-full-hit conjure rebuilds the whole bundle from its own\n"
            "    # compile and drops ids that are no longer live (2026-09-26). Earlier\n"
            "    # bundles can hold a consumer plan naming a provider spell id from an older\n"
            "    # world, which fails hydration on the next full hit, so they cold-reset.\n"
            "    # Version 11: a typed parameter with no registered provider compiles as an\n")
    t = rep(t, '        11: "unresolved_input_sockets",\n',
            '        11: "unresolved_input_sockets",\n        12: "complete_bundle_restage",\n')
    return t


edit(BASE + "spell_compiler/spell_examiner/inspectors/inspector_utility.py", inspector)
edit(BASE + "spell_compiler/spell_examiner/profiles/binding_profile.py", profiles)
edit(BASE + "spell_compiler/spell_examiner/strategies/binding_profile_strategy.py", strategy)
edit(BASE + "bind/bind.py", bind)
edit(BASE + "spellbook_creation_system.py", creation)
edit("src/melder/utilities/caching_system/caching_system.py", caching)
