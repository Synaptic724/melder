import sys
from types import ModuleType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from melder.crystallizer.synthetic_module import SyntheticModule


UNIT_CASE_PREFIX = "synthetic_module_unit_cases"


def clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove one dotted-name prefix from `sys.modules`.
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
    Build one synthetic module specification record for unit tests.
    """
    return {
        "module_name": module_name,
        "source_text": source_text,
        "parent_name": parent_name,
        "is_package": is_package,
    }


def _successful_case(
        case_id: str,
        specs: Sequence[Mapping[str, Any]],
        import_target: str,
        expected_marker: str,
        expected_loaded_names: Sequence[str],
) -> Dict[str, Any]:
    """
    Build one successful synthetic-world test case record.
    """
    return {
        "case_id": case_id,
        "specs": list(specs),
        "import_target": import_target,
        "expected_marker": expected_marker,
        "expected_loaded_names": list(expected_loaded_names),
    }


def _build_simple_leaf_case() -> Dict[str, Any]:
    module_name = "{0}.simple_leaf".format(UNIT_CASE_PREFIX)
    return _successful_case(
        "simple_leaf",
        (
            _module_spec(
                module_name,
                "def describe_case() -> str:\n    return 'simple_leaf'\n",
            ),
        ),
        module_name,
        "simple_leaf",
        (module_name,),
    )


def _build_helper_consumer_case() -> Dict[str, Any]:
    package_name = "{0}.helper_consumer".format(UNIT_CASE_PREFIX)
    helper_name = "{0}.helper".format(package_name)
    consumer_name = "{0}.consumer".format(package_name)
    return _successful_case(
        "helper_consumer",
        (
            _module_spec(package_name, "PACKAGE = 'helper_consumer'\n", is_package=True),
            _module_spec(
                helper_name,
                "def answer() -> str:\n    return 'helper_consumer'\n",
                parent_name=package_name,
            ),
            _module_spec(
                consumer_name,
                (
                    "from {0} import answer\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return answer()\n"
                ).format(helper_name),
                parent_name=package_name,
            ),
        ),
        consumer_name,
        "helper_consumer",
        (package_name, helper_name, consumer_name),
    )


def _build_nested_surface_case() -> Dict[str, Any]:
    package_name = "{0}.nested_surface".format(UNIT_CASE_PREFIX)
    api_name = "{0}.api".format(package_name)
    v1_name = "{0}.v1".format(api_name)
    helper_name = "{0}.helper".format(package_name)
    surface_name = "{0}.surface".format(v1_name)
    return _successful_case(
        "nested_surface",
        (
            _module_spec(package_name, "PACKAGE = 'nested_surface'\n", is_package=True),
            _module_spec(api_name, "API = 'api'\n", parent_name=package_name, is_package=True),
            _module_spec(v1_name, "VERSION = 'v1'\n", parent_name=api_name, is_package=True),
            _module_spec(
                helper_name,
                "def answer() -> str:\n    return 'nested_surface'\n",
                parent_name=package_name,
            ),
            _module_spec(
                surface_name,
                (
                    "from {0} import answer\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return answer()\n"
                ).format(helper_name),
                parent_name=v1_name,
            ),
        ),
        surface_name,
        "nested_surface",
        (package_name, api_name, v1_name, helper_name, surface_name),
    )


def _build_branch_case(case_id: str, width: int) -> Dict[str, Any]:
    package_name = "{0}.{1}".format(UNIT_CASE_PREFIX, case_id)
    root_name = "{0}.root".format(package_name)
    specs: List[Mapping[str, Any]] = [
        _module_spec(package_name, "PACKAGE = '{0}'\n".format(case_id), is_package=True)
    ]
    import_lines: List[str] = []
    terms: List[str] = []
    expected_names: List[str] = [package_name]
    for index in range(width):
        child_name = "{0}.dep_{1}".format(package_name, index)
        specs.append(
            _module_spec(
                child_name,
                "def value() -> int:\n    return {0}\n".format(index + 1),
                parent_name=package_name,
            )
        )
        expected_names.append(child_name)
        import_lines.append(
            "from {0} import value as dep_{1}_value\n".format(child_name, index)
        )
        terms.append("str(dep_{0}_value())".format(index))
    specs.append(
        _module_spec(
            root_name,
            "".join(import_lines)
            + "\n"
            + "def describe_case() -> str:\n"
            + "    return '{0}:' + ','.join([{1}])\n".format(
                case_id,
                ", ".join(terms),
            ),
            parent_name=package_name,
        )
    )
    expected_names.append(root_name)
    return _successful_case(
        case_id,
        specs,
        root_name,
        "{0}:{1}".format(
            case_id,
            ",".join(str(index + 1) for index in range(width)),
        ),
        expected_names,
    )


def _build_relative_import_case() -> Dict[str, Any]:
    package_name = "{0}.relative_import".format(UNIT_CASE_PREFIX)
    helper_name = "{0}.helper".format(package_name)
    target_name = "{0}.target".format(package_name)
    return _successful_case(
        "relative_import",
        (
            _module_spec(package_name, "PACKAGE = 'relative_import'\n", is_package=True),
            _module_spec(
                helper_name,
                "def token() -> str:\n    return 'relative_import'\n",
                parent_name=package_name,
            ),
            _module_spec(
                target_name,
                (
                    "from .helper import token\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return token()\n"
                ),
                parent_name=package_name,
            ),
        ),
        target_name,
        "relative_import",
        (package_name, helper_name, target_name),
    )


def _build_reexport_case() -> Dict[str, Any]:
    package_name = "{0}.reexport_surface".format(UNIT_CASE_PREFIX)
    feature_name = "{0}.feature".format(package_name)
    surface_name = "{0}.surface".format(package_name)
    consumer_name = "{0}.consumer".format(package_name)
    return _successful_case(
        "reexport_surface",
        (
            _module_spec(package_name, "PACKAGE = 'reexport_surface'\n", is_package=True),
            _module_spec(
                feature_name,
                "class FeatureTool:\n    pass\n",
                parent_name=package_name,
            ),
            _module_spec(
                surface_name,
                (
                    "from {0} import FeatureTool\n"
                    "AliasTool = FeatureTool\n"
                    "\n"
                    "def build() -> str:\n"
                    "    return 'reexport_surface'\n"
                ).format(feature_name),
                parent_name=package_name,
            ),
            _module_spec(
                consumer_name,
                (
                    "from {0} import AliasTool, build\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return build()\n"
                ).format(surface_name),
                parent_name=package_name,
            ),
        ),
        consumer_name,
        "reexport_surface",
        (package_name, feature_name, surface_name, consumer_name),
    )


def _build_duplicate_import_case() -> Dict[str, Any]:
    package_name = "{0}.duplicate_import".format(UNIT_CASE_PREFIX)
    helper_name = "{0}.helper".format(package_name)
    root_name = "{0}.root".format(package_name)
    return _successful_case(
        "duplicate_import",
        (
            _module_spec(package_name, "PACKAGE = 'duplicate_import'\n", is_package=True),
            _module_spec(
                helper_name,
                "def token() -> str:\n    return 'duplicate_import'\n",
                parent_name=package_name,
            ),
            _module_spec(
                root_name,
                (
                    "from {0} import token\n"
                    "from {0} import token as token_alias\n"
                    "import {0} as helper_mod\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return ':'.join((token(), token_alias(), helper_mod.token()))\n"
                ).format(helper_name),
                parent_name=package_name,
            ),
        ),
        root_name,
        "duplicate_import:duplicate_import:duplicate_import",
        (package_name, helper_name, root_name),
    )


def _build_package_root_import_case() -> Dict[str, Any]:
    package_name = "{0}.package_root_import".format(UNIT_CASE_PREFIX)
    helper_name = "{0}.helper".format(package_name)
    target_name = "{0}.target".format(package_name)
    return _successful_case(
        "package_root_import",
        (
            _module_spec(package_name, "PACKAGE = 'package_root_import'\n", is_package=True),
            _module_spec(
                helper_name,
                "def token() -> str:\n    return 'package_root_import'\n",
                parent_name=package_name,
            ),
            _module_spec(
                target_name,
                (
                    "from . import helper\n"
                    "\n"
                    "def describe_case() -> str:\n"
                    "    return helper.token()\n"
                ),
                parent_name=package_name,
            ),
        ),
        target_name,
        "package_root_import",
        (package_name, helper_name, target_name),
    )


def _build_sibling_modules_case() -> Dict[str, Any]:
    package_name = "{0}.sibling_modules".format(UNIT_CASE_PREFIX)
    shared_name = "{0}.shared".format(package_name)
    left_name = "{0}.left".format(package_name)
    right_name = "{0}.right".format(package_name)
    return _successful_case(
        "sibling_modules",
        (
            _module_spec(package_name, "PACKAGE = 'sibling_modules'\n", is_package=True),
            _module_spec(
                shared_name,
                "def token() -> str:\n    return 'shared'\n",
                parent_name=package_name,
            ),
            _module_spec(
                left_name,
                "from {0} import token\n".format(shared_name)
                + "def describe_case() -> str:\n    return 'left:' + token()\n",
                parent_name=package_name,
            ),
            _module_spec(
                right_name,
                "from {0} import token\n".format(shared_name)
                + "def describe_case() -> str:\n    return 'right:' + token()\n",
                parent_name=package_name,
            ),
        ),
        left_name,
        "left:shared",
        (package_name, shared_name, left_name),
    )


def _build_deep_chain_case(case_id: str, depth: int) -> Dict[str, Any]:
    package_name = "{0}.{1}".format(UNIT_CASE_PREFIX, case_id)
    specs: List[Mapping[str, Any]] = [
        _module_spec(package_name, "PACKAGE = '{0}'\n".format(case_id), is_package=True)
    ]
    expected_names: List[str] = [package_name]
    previous_name = None
    for index in range(depth):
        module_name = "{0}.layer_{1}".format(package_name, index)
        if previous_name is None:
            source_text = (
                "def describe_case() -> str:\n"
                "    return '{0}:0'\n"
            ).format(case_id)
        else:
            source_text = (
                "from {0} import describe_case as previous_describe\n"
                "def describe_case() -> str:\n"
                "    return previous_describe().rsplit(':', 1)[0] + ':{1}'\n"
            ).format(previous_name, index)
        specs.append(
            _module_spec(
                module_name,
                source_text,
                parent_name=package_name,
            )
        )
        expected_names.append(module_name)
        previous_name = module_name
    return _successful_case(
        case_id,
        specs,
        previous_name,
        "{0}:{1}".format(case_id, depth - 1),
        expected_names,
    )


def _build_package_target_case() -> Dict[str, Any]:
    package_name = "{0}.package_target".format(UNIT_CASE_PREFIX)
    child_name = "{0}.child".format(package_name)
    return _successful_case(
        "package_target",
        (
            _module_spec(
                package_name,
                (
                    "from .child import describe_case\n"
                    "PACKAGE_NAME = 'package_target'\n"
                ),
                is_package=True,
            ),
            _module_spec(
                child_name,
                "def describe_case() -> str:\n    return 'package_target'\n",
                parent_name=package_name,
            ),
        ),
        package_name,
        "package_target",
        (package_name, child_name),
    )


def _build_benign_cycle_case() -> Dict[str, Any]:
    package_name = "{0}.benign_cycle".format(UNIT_CASE_PREFIX)
    module_a = "{0}.module_a".format(package_name)
    module_b = "{0}.module_b".format(package_name)
    return _successful_case(
        "benign_cycle",
        (
            _module_spec(package_name, "PACKAGE = 'benign_cycle'\n", is_package=True),
            _module_spec(
                module_a,
                (
                    "from {0} import module_b\n"
                    "VALUE_A = 'A'\n"
                    "def describe_case() -> str:\n"
                    "    return VALUE_A + module_b.VALUE_B\n"
                ).format(package_name),
                parent_name=package_name,
            ),
            _module_spec(
                module_b,
                (
                    "from {0} import module_a\n"
                    "VALUE_B = 'B'\n"
                    "def describe_case() -> str:\n"
                    "    return module_a.VALUE_A + VALUE_B\n"
                ).format(package_name),
                parent_name=package_name,
            ),
        ),
        module_a,
        "AB",
        (package_name, module_a, module_b),
    )


def _build_auto_parent_case() -> Dict[str, Any]:
    module_name = "{0}.auto_parent.a.b.c".format(UNIT_CASE_PREFIX)
    return _successful_case(
        "auto_parent",
        (
            _module_spec(
                module_name,
                "def describe_case() -> str:\n    return 'auto_parent'\n",
                parent_name="{0}.auto_parent.a.b".format(UNIT_CASE_PREFIX),
            ),
        ),
        module_name,
        "auto_parent",
        (
            "{0}.auto_parent".format(UNIT_CASE_PREFIX),
            "{0}.auto_parent.a".format(UNIT_CASE_PREFIX),
            "{0}.auto_parent.a.b".format(UNIT_CASE_PREFIX),
            module_name,
        ),
    )


UNIT_CASES: Tuple[Dict[str, Any], ...] = (
    _build_simple_leaf_case(),
    _build_helper_consumer_case(),
    _build_nested_surface_case(),
    _build_branch_case("branch_two", 2),
    _build_branch_case("branch_three", 3),
    _build_relative_import_case(),
    _build_reexport_case(),
    _build_duplicate_import_case(),
    _build_package_root_import_case(),
    _build_sibling_modules_case(),
    _build_deep_chain_case("deep_chain_3", 3),
    _build_deep_chain_case("deep_chain_4", 4),
    _build_package_target_case(),
    _build_benign_cycle_case(),
    _build_auto_parent_case(),
)


def unit_case_id(case: Mapping[str, Any]) -> str:
    """
    Return the stable pytest id for one unit case.
    """
    return str(case["case_id"])


def install_unit_case(
        case: Mapping[str, Any],
) -> Tuple[ModuleType, Dict[str, SyntheticModule]]:
    """
    Register and import one successful synthetic-world unit case.
    """
    prefix = "{0}.{1}".format(UNIT_CASE_PREFIX, case["case_id"])
    clear_modules_by_prefix(prefix)
    modules_by_name: Dict[str, SyntheticModule] = {}
    for spec in case["specs"]:
        module_name = str(spec["module_name"])
        module = SyntheticModule(
            module_name=module_name,
            spell_crystal_id="{0}-crystal".format(module_name),
            source_text=str(spec["source_text"]),
            source_sha256=SyntheticModule._hash_source_text(str(spec["source_text"])),
            binding_signature="{0}-binding".format(module_name),
            parent_name=spec["parent_name"],
            is_package=bool(spec["is_package"]),
        )
        modules_by_name[module_name] = module
        module.register_in_import_registry()

    SyntheticModule.install_import_hook()
    imported_module = SyntheticModule.import_registered_module(
        str(case["import_target"])
    )
    return imported_module, modules_by_name
