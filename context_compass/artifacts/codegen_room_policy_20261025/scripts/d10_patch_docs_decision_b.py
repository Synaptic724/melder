"""D-10: record the owner's pathlib answer (B) in the patch docs before the src edit (run from the repo root)."""
import datetime
import pathlib

ROOT = pathlib.Path("context_compass/system_docs/patches/active/codegen_open_builtin_posture_2026_10_25")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of `old`, or stop."""
    assert text.count(old) == 1, (text.count(old), old[:90])
    return text.replace(old, new)


# --- architecture_patch.md ---------------------------------------------------------------------
path = ROOT / "architecture_patch.md"
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "- Status: draft - the `open` change is decided (D2); hybrid's pathlib route waits on the owner (below)\n",
    "- Status: decided - `open` (D2) and hybrid's pathlib route (B; the owner, chat 2026-10-25, \"focus on B\")\n",
)
text = replace_once(text, "- Updated: 2026-10-25T02:10:23Z\n", "- Updated: {}\n".format(NOW))
text = replace_once(
    text,
    "  too and from now on reads the safe tuple itself. Permissive and full_access keep `open` and say so. Every\n"
    "  profile's file posture - `open`, `io.open`, `os.open` and pathlib writes - is pinned by a symptom-named test.\n",
    "  too and from now on reads the safe tuple itself. Permissive and full_access keep `open` and say so. Hybrid's\n"
    "  import list drops `pathlib` (the owner's answer B): it moves from the common root list to the permissive\n"
    "  extras, so hybrid refuses `import pathlib` and permissive keeps it. Every profile's file posture - `open`,\n"
    "  `io.open`, `os.open` and pathlib writes - is pinned by a symptom-named test.\n",
)
text = replace_once(
    text,
    "  (`__import__`) and D-20 (materialize); ProtocolCrafter's writers; any other allow- or deny-list entry, except\n"
    "  hybrid's `pathlib`, which is the owner's call below. Nothing here is protection: the profiles and gates run in\n",
    "  (`__import__`) and D-20 (materialize); ProtocolCrafter's writers; any other allow- or deny-list entry (only\n"
    "  `pathlib` moves, B below). Nothing here is protection: the profiles and gates run in\n",
)
text = replace_once(
    text,
    "| modify | `open` joins the denied-builtin tuple safe, hybrid and precision share; each profile docstring states its file posture | none |\n",
    "| modify | `open` joins the denied-builtin tuple safe, hybrid and precision share; `pathlib` moves from the common import-root list to the permissive extras (B); each profile docstring states its file posture | none |\n",
)
text = replace_once(
    text,
    "- `CompiledFrameACLAccessSurface.denied_builtin_names` for those postures gains \"open\" (the tuple stays sorted).\n",
    "- `CompiledFrameACLAccessSurface.denied_builtin_names` for those postures gains \"open\" (the tuple stays sorted).\n"
    "- Hybrid (B): `import pathlib` is refused by the import gate with \"Import root 'pathlib' is not allowed in this\n"
    "  codegen mode.\"; hybrid's compiled `allowed_import_module_roots` loses \"pathlib\" (`HYBRID_IMPORT_MODULE_ROOTS`\n"
    "  is the common list); `PERMISSIVE_IMPORT_MODULE_ROOTS` - the common list plus the extras - keeps it; precision's\n"
    "  own list never had it.\n",
)
text = replace_once(
    text,
    "2. Add \"open\" to `SAFE_DENIED_BUILTIN_NAMES` (hybrid and precision alias it).\n",
    "2. Add \"open\" to `SAFE_DENIED_BUILTIN_NAMES` (hybrid and precision alias it). After the owner's B: move\n"
    "   \"pathlib\" from `_COMMON_SAFE_IMPORT_MODULE_ROOTS` to `_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS`, the hybrid\n"
    "   pathlib row flipped to refused and seen red first.\n",
)
text = replace_once(
    text,
    "- Rollback steps: remove \"open\" from the tuple; restore the strict xfail; revert the release-note entry. The\n"
    "  default posture can keep reading the safe tuple.\n",
    "- Rollback steps: remove \"open\" from the tuple; restore the strict xfail; move \"pathlib\" back to the common\n"
    "  list and flip the hybrid row back; revert the release-note entries. The default posture can keep reading the\n"
    "  safe tuple.\n",
)
text = replace_once(
    text,
    "- DECISION_REQUEST (the owner; carried from the D2 decision note): hybrid's import allow list includes `pathlib`\n",
    "- DECISION (the owner, chat 2026-10-25: \"yeah do that stuff\", then \"focus on B\"): B. The request it answers,\n"
    "  as it was put - hybrid's import allow list includes `pathlib`\n",
)
text = replace_once(
    text,
    "- UNKNOWN until the red run: the `io.open` and `os.open` refusals under hybrid and precision come from their\n"
    "  allow lists (\"Import root 'io' is not allowed in this codegen mode.\"); measured in the new tests.\n",
    "- Resolved at the red run (2026-10-25T02:16:35Z): the `io.open` and `os.open` refusals under hybrid and\n"
    "  precision come from their allow lists (\"Import root 'io' is not allowed in this codegen mode.\").\n",
)
text = replace_once(
    text,
    "- What changed: nothing yet; this is the plan the ticket links before any src/ edit.\n"
    "- What remains: the owner's pathlib answer; red tests; the fix; docs; notch, release note, closure, rebuild.\n",
    "- What changed: the `open` change, the engine default and the docs landed (ticket Notes of 2026-10-25); the\n"
    "  owner chose B for pathlib.\n"
    "- What remains: B's move and its red/green run; the graph; notch, release note, closure, rebuild.\n",
)
path.write_text(text, encoding="utf-8")

# --- component_patch_codegen_acl_profiles.md -------------------------------------------------
path = ROOT / "component_patch_codegen_acl_profiles.md"
text = path.read_text(encoding="utf-8")
text = replace_once(text, "- Status: draft\n", "- Status: decided (B for hybrid's pathlib)\n")
text = replace_once(text, "- Updated: 2026-10-25T02:10:23Z\n", "- Updated: {}\n".format(NOW))
text = replace_once(
    text,
    "| hybrid | accepted -> refused | refused, not listed | refused, not listed | accepted (A) or refused (B) - owner |\n",
    "| hybrid | accepted -> refused | refused, not listed | refused, not listed | accepted -> refused (B) |\n",
)
text = replace_once(
    text,
    "\"accepted -> refused\" is this patch; every other cell is today's behaviour, pinned by a test (`io`/`os` rows under\n",
    "\"accepted -> refused\" is this patch (hybrid's pathlib cell is the owner's B); every other cell is today's\n"
    "behaviour, pinned by a test (`io`/`os` rows under\n",
)
text = replace_once(
    text,
    "- Outputs: the compiled `denied_builtin_names` of safe, hybrid and precision (and of any chain carrying the\n"
    "  precision overlay) gains \"open\".\n",
    "- Outputs: the compiled `denied_builtin_names` of safe, hybrid and precision (and of any chain carrying the\n"
    "  precision overlay) gains \"open\"; hybrid's compiled `allowed_import_module_roots` loses \"pathlib\" (B).\n",
)
text = replace_once(
    text,
    "- New failure mode: room code that used `open` under safe, hybrid or precision is refused at validation\n"
    "  (Breaking; the release note names it).\n",
    "- New failure mode: room code that used `open` under safe, hybrid or precision is refused at validation\n"
    "  (Breaking; the release note names it); hybrid room code that imports `pathlib` is refused by the import gate\n"
    "  (Breaking, B).\n",
)
text = replace_once(
    text,
    "- Removed failure mode: room code under those postures reading or writing any file the process can reach through\n"
    "  `open` (D-10).\n",
    "- Removed failure mode: room code under those postures reading or writing any file the process can reach through\n"
    "  `open` (D-10), and hybrid code doing so through `pathlib.Path`.\n",
)
text = replace_once(
    text,
    "- DECISION_REQUEST: hybrid's `pathlib` (architecture_patch, options A and B).\n",
    "- DECISION: hybrid's `pathlib` - B (the owner, chat 2026-10-25, \"focus on B\"; architecture_patch).\n",
)
path.write_text(text, encoding="utf-8")
print("patch docs record B at", NOW)
