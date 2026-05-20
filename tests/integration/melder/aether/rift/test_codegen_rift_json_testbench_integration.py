import json
from typing import Any, Dict, List

import pytest

from tests.integration.melder.aether.rift.codegen_rift_json_testbench_support import (
    CodegenRiftJsonBench,
)
from tests._codegen_system_support import reset_runtime_singletons


@pytest.fixture(autouse=True)
def _reset_singletons_per_test() -> None:
    reset_runtime_singletons()
    yield
    reset_runtime_singletons()


def _build_validation_scenarios() -> List[Dict[str, object]]:
    scenarios: List[Dict[str, object]] = [
        {
            "name": "safe_validate_local_accept",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["result = 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": True,
        },
        {
            "name": "safe_validate_import_reject",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["import json\nresult = 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Import statements are not allowed",
        },
        {
            "name": "safe_validate_dunder_reject",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["result = command.__dict__"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Dunder attribute access '__dict__'",
        },
        {
            "name": "safe_validate_recursive_reject",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["result = codegen.execute_codegen('result = 1')"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Recursive codegen call 'codegen.execute_codegen'",
        },
        {
            "name": "safe_validate_unknown_name_reject",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["result = mystery_name"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Name 'mystery_name' is not available",
        },
        {
            "name": "hybrid_validate_json_import_accept",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["import json\nresult = 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": True,
        },
        {
            "name": "hybrid_validate_inspect_import_accept",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["import inspect\nresult = 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": True,
        },
        {
            "name": "hybrid_validate_type_builtin_reject",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["result = type(command)"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Reflection helper 'type'",
        },
        {
            "name": "precision_validate_inspect_reject",
            "profile_name": "hybrid",
            "precision_profile_name": "precision",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["import inspect\nresult = 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": False,
            "message_fragment": "Import root 'inspect' is not allowed",
        },
        {
            "name": "permissive_validate_eval_socket_accept",
            "profile_name": "permissive",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "validate_codegen",
                        "args": ["import socket\nresult = eval('1 + 1')"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "validation",
                    }
                ]
            },
            "kind": "validation",
            "accepted": True,
        },
    ]
    return scenarios


def _build_execution_scenarios() -> List[Dict[str, object]]:
    return [
        {
            "name": "safe_execute_local_result",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["result = 1 + 1"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": 2,
        },
        {
            "name": "safe_execute_missing_result",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["value = 7"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": None,
        },
        {
            "name": "safe_execute_runtime_failure",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["raise ValueError('boom')"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": False,
            "runtime_error_fragment": "ValueError: boom",
        },
        {
            "name": "hybrid_execute_json_import",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["import json\nresult = 3"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": 3,
        },
        {
            "name": "hybrid_execute_viewer_names",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["result = viewer.list_nexus_frame_names()"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": ["finance", "ops"],
        },
        {
            "name": "hybrid_execute_link_finance_then_list_linked",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "command.link_frame('finance')\nresult = viewer.list_linked_frame_names()"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": ["finance", "ops"],
        },
        {
            "name": "precision_execute_math",
            "profile_name": "hybrid",
            "precision_profile_name": "precision",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["import math\nresult = math.sqrt(9)"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": 3.0,
        },
        {
            "name": "permissive_execute_eval_socket",
            "profile_name": "permissive",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["import socket\nresult = eval('2 + 2')"],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": 4,
        },
        {
            "name": "permissive_execute_recursive_codegen",
            "profile_name": "permissive",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ['result = codegen.execute_codegen("result = 4")["result"]'],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": 4,
        },
        {
            "name": "full_access_execute_importlib_recursive",
            "profile_name": "full_access",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            'import importlib\nresult = codegen.execute_codegen("import importlib\\nresult = importlib.__name__")["result"]'
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    }
                ]
            },
            "kind": "execution",
            "accepted": True,
            "expected_result": "importlib",
        },
    ]


def _build_workspace_frame_scenarios() -> List[Dict[str, object]]:
    return [
        {
            "name": "local_class_bind_object_then_target_method",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "class Helper:\n"
                            "    value: int\n"
                            "    def __init__(self, value: int) -> None:\n"
                            "        self.value = value\n"
                            "    def run(self, prefix: str = 'ok') -> str:\n"
                            "        return '{0}:{1}'.format(prefix, self.value)\n"
                            "helper = Helper(7)\n"
                            "workstation.bind_object('helper', helper, weak_ref=False)\n"
                            "result = helper.run('created')"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["helper"],
                        "kwargs": {"store": "objects"},
                    },
                    {
                        "surface": "command",
                        "method": "execute_target_method",
                        "args": ["run", "later"],
                        "save_as": "executed",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
            "kind": "workspace_object_method",
            "created_result": "created:7",
            "executed_result": "later:7",
            "binding_name": "helper",
        },
        {
            "name": "local_linked_objects_chain",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "class Right:\n"
                            "    def __init__(self, value: int) -> None:\n"
                            "        self.value = value\n"
                            "class Left:\n"
                            "    def __init__(self, right: Right) -> None:\n"
                            "        self.right = right\n"
                            "    def read(self) -> int:\n"
                            "        return self.right.value\n"
                            "right = Right(11)\n"
                            "left = Left(right)\n"
                            "workstation.bind_object('left', left, weak_ref=False)\n"
                            "workstation.bind_object('right', right, weak_ref=False)\n"
                            "result = left.read()"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["left"],
                        "kwargs": {"store": "objects"},
                    },
                    {
                        "surface": "command",
                        "method": "execute_target_method",
                        "args": ["read"],
                        "save_as": "executed",
                    },
                ]
            },
            "kind": "workspace_linked_objects",
            "created_result": 11,
            "executed_result": 11,
        },
        {
            "name": "bind_attribute_payload_then_fetch",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "payload = {'kind': 'payload', 'value': 3}\n"
                            "workstation.bind_attribute('payload', payload, weak_ref=False)\n"
                            "result = payload['value']"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "get",
                        "args": ["payload"],
                        "kwargs": {"store": "attributes"},
                        "save_as": "payload",
                    },
                ]
            },
            "kind": "workspace_attribute_binding",
            "created_result": 3,
            "payload_value": 3,
        },
        {
            "name": "bind_method_runner_then_call_target",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "def make_runner(prefix: str):\n"
                            "    def _runner(suffix: str = 'tail') -> str:\n"
                            "        return '{0}:{1}'.format(prefix, suffix)\n"
                            "    return _runner\n"
                            "runner = make_runner('cg')\n"
                            "workstation.bind_method('runner', runner, weak_ref=False)\n"
                            "result = 'bound'"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["runner"],
                        "kwargs": {"store": "methods"},
                    },
                    {
                        "surface": "workstation",
                        "method": "call_target",
                        "args": ["tail"],
                        "save_as": "called",
                    },
                ]
            },
            "kind": "workspace_method_binding",
            "called_result": "cg:tail",
        },
        {
            "name": "local_inheritance_object_chain",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "class Base:\n"
                            "    def read(self) -> str:\n"
                            "        return 'base'\n"
                            "class Child(Base):\n"
                            "    def read(self) -> str:\n"
                            "        return 'child'\n"
                            "child = Child()\n"
                            "workstation.bind_object('child', child, weak_ref=False)\n"
                            "result = child.read()"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["child"],
                        "kwargs": {"store": "objects"},
                    },
                    {
                        "surface": "command",
                        "method": "execute_target_method",
                        "args": ["read"],
                        "save_as": "executed",
                    },
                ]
            },
            "kind": "workspace_inheritance",
            "created_result": "child",
            "executed_result": "child",
        },
        {
            "name": "bind_finance_conduit_then_get_target_attribute",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "link_frame",
                        "args": ["@manifest.frames.finance.frame_name"],
                    },
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "finance_root = command.get_nexus_frame('finance')\n"
                            "workstation.bind_object('finance_root', finance_root, weak_ref=False)\n"
                            "result = finance_root._aetheric_frame_name"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "created",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["finance_root"],
                        "kwargs": {"store": "objects"},
                    },
                    {
                        "surface": "command",
                        "method": "get_target_attribute",
                        "args": ["_aetheric_frame_name"],
                        "save_as": "frame_name",
                    },
                ]
            },
            "kind": "finance_root_binding",
            "expected_frame_name": "finance",
        },
        {
            "name": "list_linked_frames_before_and_after_finance_link",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "viewer",
                        "method": "list_linked_frame_names",
                        "save_as": "before",
                    },
                    {
                        "surface": "command",
                        "method": "link_frame",
                        "args": ["@manifest.frames.finance.frame_name"],
                    },
                    {
                        "surface": "viewer",
                        "method": "list_linked_frame_names",
                        "save_as": "after",
                    },
                ]
            },
            "kind": "linked_frame_transition",
        },
        {
            "name": "execute_on_finance_after_link",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "link_frame",
                        "args": ["@manifest.frames.finance.frame_name"],
                    },
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": ["result = 2 + 2"],
                        "kwargs": {"frame_name": "@manifest.frames.finance.frame_name"},
                        "save_as": "execution",
                    },
                ]
            },
            "kind": "finance_execution",
            "expected_result": 4,
        },
        {
            "name": "create_multiple_objects_and_describe_bindings",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "class Alpha:\n"
                            "    pass\n"
                            "alpha = Alpha()\n"
                            "beta = {'kind': 'beta'}\n"
                            "workstation.bind_object('alpha', alpha, weak_ref=False)\n"
                            "workstation.bind_attribute('beta', beta, weak_ref=False)\n"
                            "result = 'ok'"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
            "kind": "binding_inventory",
        },
        {
            "name": "bind_object_then_clear_target",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "execute_codegen",
                        "args": [
                            "class Holder:\n"
                            "    pass\n"
                            "holder = Holder()\n"
                            "workstation.bind_object('holder', holder, weak_ref=False)\n"
                            "result = 'bound'"
                        ],
                        "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"},
                        "save_as": "execution",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["holder"],
                        "kwargs": {"store": "objects"},
                    },
                    {
                        "surface": "workstation",
                        "method": "clear_target",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
            "kind": "clear_target",
        },
    ]


def _build_hook_scenarios() -> List[Dict[str, object]]:
    return [
        {
            "name": "codegen_category_hooks_validate",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["codegen", "cg-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["codegen", "cg-category-post"]},
                    {"surface": "command", "method": "validate_codegen", "args": ["result = 1"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "validation"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cg-category-pre", "cg-category-post"],
        },
        {
            "name": "codegen_action_hooks_validate",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_action_pre_hook", "args": ["codegen", "validate_codegen", "cg-action-pre"]},
                    {"surface": "bench", "method": "register_action_post_hook", "args": ["codegen", "validate_codegen", "cg-action-post"]},
                    {"surface": "command", "method": "validate_codegen", "args": ["result = 1"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "validation"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cg-action-pre", "cg-action-post"],
        },
        {
            "name": "codegen_category_hooks_execute",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["codegen", "cg-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["codegen", "cg-category-post"]},
                    {"surface": "command", "method": "execute_codegen", "args": ["result = 1"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "execution"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cg-category-pre", "cg-category-post"],
        },
        {
            "name": "codegen_action_hooks_execute",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_action_pre_hook", "args": ["codegen", "execute_codegen", "cg-action-pre"]},
                    {"surface": "bench", "method": "register_action_post_hook", "args": ["codegen", "execute_codegen", "cg-action-post"]},
                    {"surface": "command", "method": "execute_codegen", "args": ["result = 1"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "execution"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cg-action-pre", "cg-action-post"],
        },
        {
            "name": "command_category_hooks_link_frame",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["command", "cmd-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["command", "cmd-category-post"]},
                    {"surface": "command", "method": "link_frame", "args": ["@manifest.frames.finance.frame_name"]},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cmd-category-pre", "cmd-category-post"],
        },
        {
            "name": "command_action_hooks_link_frame",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_action_pre_hook", "args": ["command", "link_frame", "cmd-action-pre"]},
                    {"surface": "bench", "method": "register_action_post_hook", "args": ["command", "link_frame", "cmd-action-post"]},
                    {"surface": "command", "method": "link_frame", "args": ["@manifest.frames.finance.frame_name"]},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cmd-action-pre", "cmd-action-post"],
        },
        {
            "name": "viewer_category_hooks_list_linked_frames",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["viewer", "viewer-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["viewer", "viewer-category-post"]},
                    {"surface": "viewer", "method": "list_linked_frame_names", "save_as": "frames"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["viewer-category-pre", "viewer-category-post"],
        },
        {
            "name": "viewer_action_hooks_list_linked_frames",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_action_pre_hook", "args": ["viewer", "list_linked_frame_names", "viewer-action-pre"]},
                    {"surface": "bench", "method": "register_action_post_hook", "args": ["viewer", "list_linked_frame_names", "viewer-action-post"]},
                    {"surface": "viewer", "method": "list_linked_frame_names", "save_as": "frames"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["viewer-action-pre", "viewer-action-post"],
        },
        {
            "name": "combined_command_and_codegen_hook_sequence",
            "profile_name": "hybrid",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["command", "cmd-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["command", "cmd-category-post"]},
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["codegen", "cg-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["codegen", "cg-category-post"]},
                    {"surface": "command", "method": "link_frame", "args": ["@manifest.frames.finance.frame_name"]},
                    {"surface": "command", "method": "execute_codegen", "args": ["result = viewer.list_linked_frame_names()"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "execution"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": ["cmd-category-pre", "cmd-category-post", "cg-category-pre", "cg-category-post"],
        },
        {
            "name": "hook_clear_resets_recorder",
            "profile_name": "safe",
            "script": {
                "turns": [
                    {"surface": "bench", "method": "register_category_pre_hook", "args": ["codegen", "cg-category-pre"]},
                    {"surface": "bench", "method": "register_category_post_hook", "args": ["codegen", "cg-category-post"]},
                    {"surface": "command", "method": "validate_codegen", "args": ["result = 1"], "kwargs": {"frame_name": "@manifest.frames.ops.frame_name"}, "save_as": "validation"},
                    {"surface": "bench", "method": "clear_hook_events"},
                    {"surface": "bench", "method": "list_hook_events", "save_as": "events"},
                ]
            },
            "kind": "hook_events",
            "expected_events": [],
        },
    ]


def build_turn_script_scenarios() -> List[Dict[str, object]]:
    scenarios = (
        _build_validation_scenarios()
        + _build_execution_scenarios()
        + _build_workspace_frame_scenarios()
        + _build_hook_scenarios()
    )
    if len(scenarios) != 40:
        raise RuntimeError(
            "Codegen Rift turn-script matrix should contain 40 scenarios, got {0}.".format(
                len(scenarios)
            )
        )
    return scenarios


def _assert_turn_script_result(
        bench: CodegenRiftJsonBench,
        scenario: Dict[str, object],
        saved_results: Dict[str, Any],
) -> None:
    kind = scenario["kind"]
    if kind == "validation":
        result = saved_results["validation"]
        assert result["accepted"] is bool(scenario["accepted"])
        if result["accepted"]:
            return
        assert scenario["message_fragment"] in result["validation_issues"][0]
        return
    if kind == "execution":
        result = saved_results["execution"]
        assert result["accepted"] is bool(scenario["accepted"])
        if result["accepted"]:
            if scenario["expected_result"] is None:
                assert "result" not in result
            else:
                assert result["result"] == scenario["expected_result"]
        else:
            if "runtime_error_fragment" in scenario:
                assert scenario["runtime_error_fragment"] in result["runtime_error"]
        return
    if kind == "workspace_object_method":
        assert saved_results["created"]["result"] == scenario["created_result"]
        assert saved_results["executed"] == scenario["executed_result"]
        assert scenario["binding_name"] in saved_results["bindings"]["objects"]
        return
    if kind == "workspace_linked_objects":
        assert saved_results["created"]["result"] == scenario["created_result"]
        assert saved_results["executed"] == scenario["executed_result"]
        return
    if kind == "workspace_attribute_binding":
        assert saved_results["created"]["result"] == scenario["created_result"]
        assert saved_results["payload"]["value"] == scenario["payload_value"]
        return
    if kind == "workspace_method_binding":
        assert saved_results["called"] == scenario["called_result"]
        return
    if kind == "workspace_inheritance":
        assert saved_results["created"]["result"] == scenario["created_result"]
        assert saved_results["executed"] == scenario["executed_result"]
        return
    if kind == "finance_root_binding":
        assert saved_results["created"]["result"] == scenario["expected_frame_name"]
        assert saved_results["frame_name"] == scenario["expected_frame_name"]
        return
    if kind == "linked_frame_transition":
        assert saved_results["before"] == ["ops"]
        assert saved_results["after"] == ["finance", "ops"]
        return
    if kind == "finance_execution":
        assert saved_results["execution"]["accepted"] is True
        assert saved_results["execution"]["result"] == scenario["expected_result"]
        return
    if kind == "binding_inventory":
        assert "alpha" in saved_results["bindings"]["objects"]
        assert "beta" in saved_results["bindings"]["attributes"]
        return
    if kind == "clear_target":
        assert "holder" in saved_results["bindings"]["objects"]
        return
    if kind == "hook_events":
        assert saved_results["events"] == scenario["expected_events"]
        return
    raise AssertionError(kind)


@pytest.mark.parametrize(
    "scenario",
    build_turn_script_scenarios(),
    ids=lambda scenario: scenario["name"],
)
def test_codegen_rift_json_turn_script_matrix(
        scenario: Dict[str, object],
) -> None:
    """
    Verify 40 turn-based codegen integration scenarios through the JSON harness.

    Args:
        scenario:
            Parametrized turn-script scenario.

    Returns:
        None.
    """
    bench = CodegenRiftJsonBench()
    try:
        bench.set_codegen_profile(
            scenario["profile_name"],
            precision_profile_name=scenario.get("precision_profile_name"),
            frame_name="ops",
        )
        bench.set_codegen_profile(
            scenario["profile_name"],
            precision_profile_name=scenario.get("precision_profile_name"),
            frame_name="finance",
        )
        saved_results = bench.dispatch_turn_script(scenario["script"])
        _assert_turn_script_result(bench, scenario, saved_results)
    finally:
        bench.cleanup()
