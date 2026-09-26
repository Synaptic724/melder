"""S2a: key-set plans read their constants as globals of their own namespace, not as default arguments.

Usage: python apply_s2a_edits.py <tree_root> [--check]

Each anchor must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"

EDITS = {
    LOWERING: [
        ("replace",
         "        Hold the cold-path helpers a plan binds as default arguments: the\n",
         "        Hold the cold-path helpers a plan reads from its namespace: the\n"),
        ("replace",
         "        Emit one key-set plan: `def _site_plan_executor(meld, ov, <constants>) -> instance`.\n",
         "        Emit one key-set plan: `def _site_plan_executor(meld, ov) -> instance`.\n"
         "\n"
         "        The plan reads its constants (spells, ids, helpers) as globals of the\n"
         "        returned namespace, so the caller must exec the code into that namespace.\n"),
        ("replace",
         "        - Local `v{n}` holds kept step n's value; step constants and helpers are\n"
         "          bound as default arguments (fast locals) on the plan function. Spells\n"
         "          ride one `spells` tuple read only on cold paths (errors, shared-site\n"
         "          routing for `unique`, locks), keeping the default count low on deep\n"
         "          graphs.\n",
         "        - Local `v{n}` holds kept step n's value; step constants and helpers are\n"
         "          globals of the plan's own namespace (the plan is exec'd into it), as\n"
         "          the inner no-overrides executor reads module globals. Default\n"
         "          arguments were used until 2026-09-26: they cost one fill per constant\n"
         "          on every call, hundreds on deep graphs. Spells ride one `spells`\n"
         "          tuple read only on cold paths (errors, shared-site routing for\n"
         "          `unique`, locks). No namespace name is assigned in the plan body.\n"),
        ("replace",
         "        defaults = \"\".join(f\", {name}={name}\" for name in self._namespace)\n"
         "        source_lines = [f\"def {SitePlanLowering.PLAN_FUNCTION_NAME}(meld, ov{defaults}):\"]\n",
         "        # Constants are read as globals of the plan's namespace; see the class contract.\n"
         "        source_lines = [f\"def {SitePlanLowering.PLAN_FUNCTION_NAME}(meld, ov):\"]\n"),
        ("replace",
         "        Bind one plan constant into the namespace (and so as a default argument).\n",
         "        Bind one plan constant into the namespace, which is the plan's globals.\n"),
    ],
}


def main() -> None:
    """Check every edit, then write (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        data = (root / rel).read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[root / rel] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
