"""D3 probe: classification and descent of a package inside a project-local .venv (scratch only)."""
import sys
from pathlib import Path

import app_mod
import probe_pkg
from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer

root = Path.cwd().resolve()
site_roots = CrystalAnalyzer.resolve_site_package_root_paths()
print("python:", sys.version.split()[0], "prefix inside cwd:", Path(sys.prefix).resolve().is_relative_to(root))
print("site roots:", [str(p) for p in site_roots])
pkg_path = Path(probe_pkg.__file__).resolve()
for label, roots in (("cwd", (root,)), ("cwd/src", (root / "src",))):
    for descent in (False, True):
        analyzer = CrystalAnalyzer(
            user_source_root_paths=roots,
            site_package_root_paths=site_roots,
            site_package_dependency_descent=descent,
        )
        try:
            custody = analyzer._match_custody(module_name="probe_pkg", module_obj=probe_pkg, module_path=pkg_path)
            result = analyzer.analyze_spell_root(
                root_module_name="app_mod",
                root_module_obj=app_mod,
                root_module_path=Path(app_mod.__file__).resolve(),
            )
            try:
                kinds = result.module_to_kind
                print(
                    f"roots={label:8} descent={descent!s:5} probe_pkg={custody.kind}/descends={analyzer._custody_descends(custody)}",
                    "| walked:", {k: v for k, v in kinds.items() if k.startswith(("app_mod", "probe"))},
                    "| fingerprinted:", sorted(k for k in result.physical_module_fingerprints if k.startswith("probe")),
                )
            finally:
                result.cleanup()
        finally:
            analyzer.cleanup()
