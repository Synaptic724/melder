import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from melder.crystallizer.synthetic_module import SyntheticModule


PHYSICAL_PACKAGE_PREFIX = "tests.mocks.crystallizer.spell_crystal_demo_pkg"
PHYSICAL_USER_SOURCE_ROOT = (
    Path(__file__).resolve().parent
)
SYNTHETIC_COMPONENT_DEPENDENCY_NAME = "synthetic_spell_crystal_component_dep"


class DummySpell:
    """
    Minimal spell double used by direct `SpellCrystal` tests.
    """

    def __init__(self, spell_id: str, spell: Any) -> None:
        self.spell_id = spell_id
        self.spell = spell
        # Bind-signature fields consumed by SpellCrystal.__init__ (test doubles).
        self.spell_name = spell_id
        self.binding_name = None
        self.spellframe = None
        self.existence = SimpleNamespace(name="present")
        self.permissions = SimpleNamespace(name="default")
        # Capture-gap fields (restore_engine_2026_07_07): SpellCrystal now
        # also reads the disposal contract and the attached profile object
        # (family derived from the profile's TYPE NAME - SimpleNamespace
        # classifies as the "general" fallback, which is what a minimal
        # double should report).
        self.disposal_method_names = []
        self.profile = SimpleNamespace()


def clear_modules(*module_names: str) -> None:
    """
    Remove one or more module names from `sys.modules`.
    """
    for module_name in reversed(module_names):
        sys.modules.pop(module_name, None)


def clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove all loaded modules matching one dotted-name prefix.
    """
    stale_names = [
        module_name
        for module_name in list(sys.modules.keys())
        if module_name == prefix or module_name.startswith(prefix + ".")
    ]
    for module_name in reversed(stale_names):
        sys.modules.pop(module_name, None)


def _module_spec(
        module_name: str,
        source_text: str,
        *,
        parent_name: Optional[str] = None,
        is_package: bool = False,
) -> Dict[str, Any]:
    """
    Build one synthetic module specification record for the harness.
    """
    return {
        "module_name": module_name,
        "source_text": source_text,
        "parent_name": parent_name,
        "is_package": is_package,
    }


def _ensure_package_shell(package_name: str) -> None:
    """
    Ensure one plain package shell exists in `sys.modules`.
    """
    if not package_name or package_name in sys.modules:
        return

    parent_name, _, child_name = package_name.rpartition(".")
    if parent_name:
        _ensure_package_shell(parent_name)

    package_module = ModuleType(package_name)
    package_module.__file__ = "<synthetic:{0}>".format(package_name)
    package_module.__package__ = package_name
    package_module.__path__ = [package_module.__file__]
    sys.modules[package_name] = package_module
    if parent_name:
        parent_module = sys.modules[parent_name]
        setattr(parent_module, child_name, package_module)


def _build_linear_synthetic_case(case_id: str, depth: int) -> Dict[str, Any]:
    """
    Build one linear synthetic dependency chain case.
    """
    package_name = "synthetic_spell_crystal_cases.{0}".format(case_id)
    module_specs: List[Dict[str, Any]] = [
        _module_spec(
            package_name,
            "PACKAGE_NAME = '{0}'\n".format(package_name),
            is_package=True,
        )
    ]
    expected_direct_dependencies: Dict[str, List[str]] = {}
    expected_module_targets: List[str] = []

    for index in range(depth, -1, -1):
        module_name = "{0}.node_{1}".format(package_name, index)
        class_name = "Node{0}".format(index)
        if index == depth:
            source_text = (
                "class {0}:\n"
                "    pass\n"
            ).format(class_name)
            expected_direct_dependencies[module_name] = []
        else:
            dependency_module_name = "{0}.node_{1}".format(package_name, index + 1)
            dependency_class_name = "Node{0}".format(index + 1)
            source_text = (
                "from {0} import {1}\n"
                "class {2}:\n"
                "    dependency_type = {1}\n"
            ).format(
                dependency_module_name,
                dependency_class_name,
                class_name,
            )
            expected_direct_dependencies[module_name] = [dependency_module_name]
        expected_module_targets.append(module_name)
        module_specs.append(
            _module_spec(
                module_name,
                source_text,
                parent_name=package_name,
            )
        )

    expected_module_targets.reverse()
    return {
        "case_id": case_id,
        "root_module_name": "{0}.node_0".format(package_name),
        "root_class_name": "Node0",
        "module_specs": module_specs,
        "cleanup_prefix": package_name,
        "expected_module_targets": expected_module_targets,
        "expected_direct_dependencies": expected_direct_dependencies,
        "expected_kind_by_module": {
            module_name: "synthetic_module"
            for module_name in expected_module_targets
        },
    }


def _build_branch_synthetic_case(case_id: str, width: int) -> Dict[str, Any]:
    """
    Build one branching synthetic dependency graph case.
    """
    package_name = "synthetic_spell_crystal_cases.{0}".format(case_id)
    module_specs: List[Dict[str, Any]] = [
        _module_spec(
            package_name,
            "PACKAGE_NAME = '{0}'\n".format(package_name),
            is_package=True,
        )
    ]
    dependency_module_names: List[str] = []
    expected_direct_dependencies: Dict[str, List[str]] = {}
    expected_module_targets: List[str] = []

    for index in range(width):
        module_name = "{0}.dep_{1}".format(package_name, index)
        class_name = "Dependency{0}".format(index)
        dependency_module_names.append(module_name)
        expected_module_targets.append(module_name)
        expected_direct_dependencies[module_name] = []
        module_specs.append(
            _module_spec(
                module_name,
                "class {0}:\n    pass\n".format(class_name),
                parent_name=package_name,
            )
        )

    import_lines: List[str] = []
    class_lines: List[str] = ["class RootBranch:\n"]
    for index, module_name in enumerate(dependency_module_names):
        class_name = "Dependency{0}".format(index)
        import_lines.append(
            "from {0} import {1}\n".format(module_name, class_name)
        )
        class_lines.append(
            "    dependency_{0} = {1}\n".format(index, class_name)
        )

    root_module_name = "{0}.root".format(package_name)
    expected_module_targets.append(root_module_name)
    expected_direct_dependencies[root_module_name] = dependency_module_names
    module_specs.append(
        _module_spec(
            root_module_name,
            "".join(import_lines + class_lines),
            parent_name=package_name,
        )
    )
    return {
        "case_id": case_id,
        "root_module_name": root_module_name,
        "root_class_name": "RootBranch",
        "module_specs": module_specs,
        "cleanup_prefix": package_name,
        "expected_module_targets": [root_module_name] + dependency_module_names,
        "expected_direct_dependencies": expected_direct_dependencies,
        "expected_kind_by_module": {
            module_name: "synthetic_module"
            for module_name in [root_module_name] + dependency_module_names
        },
    }


def _build_relative_synthetic_case(case_id: str) -> Dict[str, Any]:
    """
    Build one synthetic case using relative imports through nested packages.
    """
    package_name = "synthetic_spell_crystal_cases.{0}".format(case_id)
    layer_package = "{0}.layer".format(package_name)
    deep_package = "{0}.deep".format(layer_package)
    leaf_module_name = "{0}.leaf".format(deep_package)
    helper_module_name = "{0}.helper".format(layer_package)
    root_module_name = "{0}.root".format(layer_package)
    module_specs: List[Dict[str, Any]] = [
        _module_spec(package_name, "PACKAGE_NAME = '{0}'\n".format(package_name), is_package=True),
        _module_spec(layer_package, "LAYER_NAME = 'layer'\n", parent_name=package_name, is_package=True),
        _module_spec(deep_package, "DEEP_NAME = 'deep'\n", parent_name=layer_package, is_package=True),
        _module_spec(
            leaf_module_name,
            "class RelativeLeaf:\n    pass\n",
            parent_name=deep_package,
        ),
        _module_spec(
            helper_module_name,
            "from .deep.leaf import RelativeLeaf\nclass RelativeHelper:\n    dependency_type = RelativeLeaf\n",
            parent_name=layer_package,
        ),
        _module_spec(
            root_module_name,
            "from .helper import RelativeHelper\nclass RelativeRoot:\n    dependency_type = RelativeHelper\n",
            parent_name=layer_package,
        ),
    ]
    expected_direct_dependencies = {
        root_module_name: [helper_module_name],
        helper_module_name: [leaf_module_name],
        leaf_module_name: [],
    }
    expected_module_targets = [root_module_name, helper_module_name, leaf_module_name]
    return {
        "case_id": case_id,
        "root_module_name": root_module_name,
        "root_class_name": "RelativeRoot",
        "module_specs": module_specs,
        "cleanup_prefix": package_name,
        "expected_module_targets": expected_module_targets,
        "expected_direct_dependencies": expected_direct_dependencies,
        "expected_kind_by_module": {
            module_name: "synthetic_module"
            for module_name in expected_module_targets
        },
    }


def _build_reexport_synthetic_case(case_id: str) -> Dict[str, Any]:
    """
    Build one synthetic case where the root depends on a re-export surface.
    """
    package_name = "synthetic_spell_crystal_cases.{0}".format(case_id)
    feature_module_name = "{0}.feature".format(package_name)
    surface_module_name = "{0}.surface".format(package_name)
    root_module_name = "{0}.root".format(package_name)
    module_specs: List[Dict[str, Any]] = [
        _module_spec(package_name, "PACKAGE_NAME = '{0}'\n".format(package_name), is_package=True),
        _module_spec(
            feature_module_name,
            "class FeatureDependency:\n    pass\n",
            parent_name=package_name,
        ),
        _module_spec(
            surface_module_name,
            "from {0} import FeatureDependency\nSurfaceDependency = FeatureDependency\n".format(
                feature_module_name,
            ),
            parent_name=package_name,
        ),
        _module_spec(
            root_module_name,
            "from {0} import SurfaceDependency\nclass ReexportRoot:\n    dependency_type = SurfaceDependency\n".format(
                surface_module_name,
            ),
            parent_name=package_name,
        ),
    ]
    expected_direct_dependencies = {
        root_module_name: [surface_module_name],
        surface_module_name: [feature_module_name],
        feature_module_name: [],
    }
    expected_module_targets = [root_module_name, surface_module_name, feature_module_name]
    return {
        "case_id": case_id,
        "root_module_name": root_module_name,
        "root_class_name": "ReexportRoot",
        "module_specs": module_specs,
        "cleanup_prefix": package_name,
        "expected_module_targets": expected_module_targets,
        "expected_direct_dependencies": expected_direct_dependencies,
        "expected_kind_by_module": {
            module_name: "synthetic_module"
            for module_name in expected_module_targets
        },
    }


def _build_duplicate_import_synthetic_case(case_id: str) -> Dict[str, Any]:
    """
    Build one synthetic case with duplicated import statements.
    """
    package_name = "synthetic_spell_crystal_cases.{0}".format(case_id)
    helper_module_name = "{0}.helper".format(package_name)
    root_module_name = "{0}.root".format(package_name)
    module_specs: List[Dict[str, Any]] = [
        _module_spec(package_name, "PACKAGE_NAME = '{0}'\n".format(package_name), is_package=True),
        _module_spec(
            helper_module_name,
            "class DuplicateHelper:\n    pass\n",
            parent_name=package_name,
        ),
        _module_spec(
            root_module_name,
            (
                "from {0} import DuplicateHelper\n"
                "from {0} import DuplicateHelper as DuplicateHelperAlias\n"
                "import {0} as helper_mod\n"
                "class DuplicateRoot:\n"
                "    helper_type = DuplicateHelper\n"
                "    helper_alias_type = DuplicateHelperAlias\n"
                "    helper_module = helper_mod\n"
            ).format(helper_module_name),
            parent_name=package_name,
        ),
    ]
    expected_direct_dependencies = {
        root_module_name: [helper_module_name],
        helper_module_name: [],
    }
    expected_module_targets = [root_module_name, helper_module_name]
    return {
        "case_id": case_id,
        "root_module_name": root_module_name,
        "root_class_name": "DuplicateRoot",
        "module_specs": module_specs,
        "cleanup_prefix": package_name,
        "expected_module_targets": expected_module_targets,
        "expected_direct_dependencies": expected_direct_dependencies,
        "expected_kind_by_module": {
            module_name: "synthetic_module"
            for module_name in expected_module_targets
        },
    }


SYNTHETIC_CASES: Tuple[Dict[str, Any], ...] = (
    _build_linear_synthetic_case("linear_depth_1", 1),
    _build_linear_synthetic_case("linear_depth_2", 2),
    _build_linear_synthetic_case("linear_depth_3", 3),
    _build_linear_synthetic_case("linear_depth_4", 4),
    _build_linear_synthetic_case("linear_depth_5", 5),
    _build_branch_synthetic_case("branch_width_2", 2),
    _build_branch_synthetic_case("branch_width_3", 3),
    _build_relative_synthetic_case("relative_depth_3"),
    _build_reexport_synthetic_case("reexport_surface"),
    _build_duplicate_import_synthetic_case("duplicate_imports"),
)


PHYSICAL_CASES: Tuple[Dict[str, Any], ...] = (
    {
        "case_id": "physical_root",
        "root_module_name": "{0}.root".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "RootService",
        "expected_module_targets": [
            "{0}.root".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_branch",
        "root_module_name": "{0}.root_branch".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "BranchRootService",
        "expected_module_targets": [
            "{0}.root_branch".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_branch".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_branch".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_deep",
        "root_module_name": "{0}.root_deep".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "DeepRootService",
        "expected_module_targets": [
            "{0}.root_deep".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_deep".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_deep".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_reexport",
        "root_module_name": "{0}.root_reexport".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "ReexportRootService",
        "expected_module_targets": [
            "{0}.root_reexport".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested.reexport".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_reexport".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.nested.reexport".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.nested.reexport".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_reexport".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested.reexport".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_package_import",
        "root_module_name": "{0}.root_package_import".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "PackageImportRootService",
        "expected_module_targets": [
            "{0}.root_package_import".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_package_import".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.nested".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.nested".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_package_import".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_duplicate",
        "root_module_name": "{0}.root_duplicate".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "DuplicateImportRootService",
        "expected_module_targets": [
            "{0}.root_duplicate".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_duplicate".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_duplicate".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_multibranch",
        "root_module_name": "{0}.root_multibranch".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "MultiBranchRootService",
        "expected_module_targets": [
            "{0}.root_multibranch".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_multibranch".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_multibranch".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.nested.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.aggregate".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.leaf_a".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.branch.leaf_b".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_api_surface",
        "root_module_name": "{0}.root_api_surface".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "ApiSurfaceRootService",
        "expected_module_targets": [
            "{0}.root_api_surface".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.api.surface".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_api_surface".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.api.surface".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.api.surface".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_api_surface".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.api.surface".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_api_feature",
        "root_module_name": "{0}.root_api_feature".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "ApiFeatureRootService",
        "expected_module_targets": [
            "{0}.root_api_feature".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
        ],
        "expected_direct_dependencies": {
            "{0}.root_api_feature".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
                "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): [
                "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): [],
        },
        "expected_kind_by_module": {
            "{0}.root_api_feature".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.api.feature".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.deep.level1.level2.provider".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
        },
    },
    {
        "case_id": "physical_with_synthetic",
        "root_module_name": "{0}.root_with_synthetic".format(PHYSICAL_PACKAGE_PREFIX),
        "root_class_name": "MixedRootService",
        "expected_module_targets": [
            "{0}.root_with_synthetic".format(PHYSICAL_PACKAGE_PREFIX),
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            SYNTHETIC_COMPONENT_DEPENDENCY_NAME,
        ],
        "expected_direct_dependencies": {
            "{0}.root_with_synthetic".format(PHYSICAL_PACKAGE_PREFIX): [
                SYNTHETIC_COMPONENT_DEPENDENCY_NAME,
                "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX),
            ],
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): [],
            SYNTHETIC_COMPONENT_DEPENDENCY_NAME: [],
        },
        "expected_kind_by_module": {
            "{0}.root_with_synthetic".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            "{0}.shared".format(PHYSICAL_PACKAGE_PREFIX): "user_source",
            SYNTHETIC_COMPONENT_DEPENDENCY_NAME: "synthetic_module",
        },
        "requires_synthetic_dependency": True,
    },
)


def physical_case_id(case: Mapping[str, Any]) -> str:
    """
    Return the stable pytest id for one physical case.
    """
    return str(case["case_id"])


def synthetic_case_id(case: Mapping[str, Any]) -> str:
    """
    Return the stable pytest id for one synthetic case.
    """
    return str(case["case_id"])


def install_synthetic_case(case: Mapping[str, Any]) -> Tuple[type, List[SyntheticModule]]:
    """
    Materialize one synthetic graph case and return its root class.
    """
    modules_by_name: Dict[str, SyntheticModule] = {}
    cleanup_prefix = str(case["cleanup_prefix"])
    clear_modules_by_prefix(cleanup_prefix)

    for spec in case["module_specs"]:
        module_name = str(spec["module_name"])
        parent_name = spec["parent_name"]
        is_package = bool(spec["is_package"])
        package_parent_name = module_name.rpartition(".")[0]
        if package_parent_name:
            _ensure_package_shell(package_parent_name)
        if parent_name:
            _ensure_package_shell(str(parent_name))
        module = SyntheticModule(
            module_name=module_name,
            spell_crystal_id="{0}-crystal".format(module_name),
            source_text=str(spec["source_text"]),
            source_sha256="{0}-sha".format(module_name),
            binding_signature="{0}-binding".format(module_name),
        )
        module.__file__ = "<synthetic:{0}>".format(module_name)
        if is_package:
            module.__package__ = module_name
            module.__path__ = [module.__file__]
        else:
            module.__package__ = parent_name or module_name.rpartition(".")[0]
        sys.modules[module_name] = module
        if parent_name:
            parent_module = sys.modules[parent_name]
            setattr(parent_module, module_name.rsplit(".", 1)[-1], module)
        exec(module.source_text, module.__dict__, module.__dict__)
        modules_by_name[module_name] = module

    root_module = modules_by_name[str(case["root_module_name"])]
    root_type = getattr(root_module, str(case["root_class_name"]))
    return root_type, list(modules_by_name.values())


def cleanup_synthetic_case(
        case: Mapping[str, Any],
        installed_modules: Sequence[SyntheticModule],
) -> None:
    """
    Cleanup one synthetic graph case.
    """
    for module in reversed(list(installed_modules)):
        module.cleanup()
    clear_modules_by_prefix(str(case["cleanup_prefix"]))


def install_component_synthetic_dependency() -> SyntheticModule:
    """
    Install the mixed physical/synthetic dependency used by physical cases.
    """
    clear_modules(SYNTHETIC_COMPONENT_DEPENDENCY_NAME)
    module = SyntheticModule(
        module_name=SYNTHETIC_COMPONENT_DEPENDENCY_NAME,
        spell_crystal_id="component-synth-crystal",
        source_text=(
            "class SyntheticDependency:\n"
            "    pass\n"
        ),
        source_sha256="component-synth-sha",
        binding_signature="component-synth-binding",
    )
    module.__file__ = "<synthetic:{0}>".format(SYNTHETIC_COMPONENT_DEPENDENCY_NAME)
    module.__package__ = ""
    sys.modules[SYNTHETIC_COMPONENT_DEPENDENCY_NAME] = module
    exec(module.source_text, module.__dict__, module.__dict__)
    return module
