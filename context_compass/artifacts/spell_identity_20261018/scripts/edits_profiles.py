"""melder_0, 2026-10-18: S1's Spell Examination Profiles edits (component_patch_spell_examination_profiles.md): the
four fingerprint-only fields, their keywords, assignments and cleanup deletions, and the `stable_repr` calls that
filled them, removed; the docstrings that said the profile feeds the spell_id corrected."""
from typing import List, Tuple

from apply_common import Applier

PROFILE = "src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py"
STRATEGY = "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py"

FINGERPRINT_DOC = (
    "            fingerprint_repr:\n"
    "                Optional address-free, untruncated repr used only by the bind fingerprint\n"
    "                (`InspectorUtility.stable_repr`). None means the fingerprint derives the text\n"
    "                from `repr_string` with memory addresses removed.\n")


def scoped(applier: Applier, rel: str, start: str, end: str, pairs: List[Tuple[str, str]], label: str) -> None:
    """Apply `pairs` inside the region from `start` (exactly once) to `end` (exactly once after it, or the file's
    end when `end` is empty); each `old` must occur exactly once in that region."""
    text = applier._load(rel)
    if text.count(start) != 1:
        applier.errors.append(f"SCOPE {label} start in {rel}: {text.count(start)}")
        return
    begin = text.index(start)
    finish = len(text)
    if end:
        if text.count(end) != 1 or text.index(end) <= begin:
            applier.errors.append(f"SCOPE {label} end in {rel}: {text.count(end)}")
            return
        finish = text.index(end)
    region = text[begin:finish]
    for index, (old, new) in enumerate(pairs):
        count = region.count(old)
        if count != 1:
            applier.errors.append(f"ANCHOR {label}#{index} in {rel}: found {count}: {old[:70]!r}")
            continue
        region = region.replace(old, new)
        applier.counts[rel] = applier.counts.get(rel, 0) + 1
    applier.texts[rel] = text[:begin] + region + text[finish:]


def profile_fields(applier: Applier, cls: str, end: str) -> None:
    """Remove `fingerprint_repr` from one of the three profile classes."""
    scoped(applier, PROFILE, f"class {cls}(SpellBindingProfile):", end, [
        ("        \"fingerprint_repr\",\n", ""),
        ("            fingerprint_repr: Optional[str] = None,\n", ""),
        (FINGERPRINT_DOC, ""),
        ("        self.fingerprint_repr: Optional[str] = fingerprint_repr\n", ""),
        ("        del self.fingerprint_repr\n", ""),
    ], cls)


def apply(applier: Applier) -> None:
    """Stage every binding_profile.py and binding_profile_strategy.py edit."""
    # The working tree mixes CRLF (244 lines) and LF (77) in the strategy; git stores it LF and reports no diff.
    # It is written back all CRLF, as binding_profile.py is.
    applier.normalize_mixed[STRATEGY] = "\r\n"
    applier.edit(PROFILE, [
        ("    Enough to fingerprint, reason about protocol compatibility, and produce diagnostics.\n"
         "    Very shallow per-method view (names only), no deep inspection.\n",
         "    Enough to reason about protocol compatibility and produce diagnostics. Very shallow\n"
         "    per-method view (names only), no deep inspection; the spell_id is the class's code\n"
         "    digest (`SpellCodeDigest`), never read from this profile.\n"),
        ("                Optional constructor signature string (`str(inspect.signature(cls))`).\n"
         "                Part of the v4 fingerprint: constructor-shape changes must\n"
         "                change the spell id so stale cache bundles cannot full-hit.\n",
         "                Optional constructor signature string (`str(inspect.signature(cls))`),\n"
         "                address-free, for descriptors and diagnostics. It does not feed the\n"
         "                spell_id: the code digest reads the constructor's code itself.\n"),
    ], "profile docs")
    scoped(applier, PROFILE, "class CallableParameterBindingSummary:", "class CallableBindingProfile(", [
        ("    Minimal binding-time view of a single callable parameter (for fingerprint/diagnostics).\n",
         "    Minimal binding-time view of a single callable parameter (for diagnostics).\n"),
        ("    __slots__ = [\"name\", \"kind\", \"default_repr\", \"annotation_repr\", \"default_fingerprint_repr\"]\n",
         "    __slots__ = [\"name\", \"kind\", \"default_repr\", \"annotation_repr\"]\n"),
        ("            default_fingerprint_repr: Optional[str] = None,\n", ""),
        ("            default_fingerprint_repr:\n"
         "                Optional address-free, untruncated default repr used only by the bind\n"
         "                fingerprint. None means the fingerprint derives it from `default_repr`.\n", ""),
        ("        self.default_fingerprint_repr: Optional[str] = default_fingerprint_repr\n", ""),
    ], "parameter summary")
    profile_fields(applier, "CallableBindingProfile", "class InstanceBindingProfile(")
    profile_fields(applier, "InstanceBindingProfile", "class OtherBindingProfile(")
    profile_fields(applier, "OtherBindingProfile", "")
    applier.edit(STRATEGY, [
        ("        The `init_signature` text feeds the bind fingerprint (spell id). A\n"
         "        ForwardRef's repr embeds its owner, including a memory address, so the\n"
         "        text renders those names as source text\n",
         "        The `init_signature` text is descriptor and diagnostic data; the spell_id\n"
         "        is the class's code digest (`SpellCodeDigest`), which reads the\n"
         "        constructor's code, not this text. A ForwardRef's repr embeds its owner,\n"
         "        including a memory address, so the text renders those names as source text\n"),
        ("        unavailable names, which stay as their source text (2026-09-26). The\n"
         "        bind fingerprint hashes their keys, so every annotated field counts.\n",
         "        unavailable names, which stay as their source text (2026-09-26), so every\n"
         "        annotated field reaches the published spell descriptor.\n"),
        ("        # No source-file read here: the v4 fingerprint hashes the constructor\n"
         "        # signature instead of a source preview, and the preview itself is\n",
         "        # No source-file read here: the spell_id is the class's code digest\n"
         "        # (SpellCodeDigest reads code objects, never files), and the preview itself is\n"),
        ("            - Keys are always the class's own annotation names, so the bind\n"
         "              fingerprint (which hashes the sorted keys) sees every annotated field.\n",
         "            - Keys are always the class's own annotation names, so the profile (and\n"
         "              the spell descriptor Nexus publishes from it) lists every annotated field.\n"),
        ("        they never embed an object address.\n"
         "        `fingerprint_repr` and each parameter's `default_fingerprint_repr` carry the\n"
         "        address-free, untruncated repr the bind fingerprint hashes; `repr_string` and\n"
         "        `default_repr` stay the truncated display text.\n",
         "        they never embed an object address. `repr_string` and each parameter's\n"
         "        `default_repr` are the truncated display text; the spell_id is the callable's\n"
         "        code digest (`SpellCodeDigest`), so no full repr is kept here.\n"),
        ("                default_repr = None\n"
         "                default_fingerprint_repr = None\n",
         "                default_repr = None\n"),
        ("                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)\n"
         "                    default_fingerprint_repr = InspectorUtility.stable_repr(parameter.default)\n",
         "                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)\n"),
        ("                        annotation_repr=annotation_repr,\n"
         "                        default_fingerprint_repr=default_fingerprint_repr,\n",
         "                        annotation_repr=annotation_repr,\n"),
        ("            fingerprint_repr=InspectorUtility.stable_repr(effective),\n", ""),
        ("        The display `repr_string` is truncated; `fingerprint_repr` is the full repr with memory\n"
         "        addresses removed, so a default-repr object gets the same spell id in every process.\n",
         "        The display `repr_string` is truncated. The spell_id is the object's digest\n"
         "        (`SpellCodeDigest`: its class's code plus its slots and `__dict__`), not a repr.\n"),
        ("        Carries the same address-free `fingerprint_repr` as the instance profile.\n",
         "        Carries the same display surface as the instance profile; the spell_id is the\n"
         "        candidate's digest (`SpellCodeDigest`).\n"),
    ], "strategy")
    scoped(applier, STRATEGY, "    def _build_instance_profile(", "    def _build_other_profile(", [
        ("            fingerprint_repr=InspectorUtility.stable_repr(obj),\n", ""),
    ], "instance builder")
    scoped(applier, STRATEGY, "    def _build_other_profile(", "    def _is_probably_decorated_class(", [
        ("            fingerprint_repr=InspectorUtility.stable_repr(obj),\n", ""),
    ], "other builder")
