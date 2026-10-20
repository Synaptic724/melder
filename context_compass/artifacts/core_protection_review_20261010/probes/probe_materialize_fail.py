"""Scratch probe: a failed materialize over an existing module name - is the original restored?"""
import sys

from tests._codegen_system_support import create_codegen_rift, create_enabled_nexus, reset_runtime_singletons

import csv as real_csv
import json as real_json

reset_runtime_singletons()
nexus = create_enabled_nexus()
rift = create_codegen_rift(nexus)
conduit = rift.create_nexus_frame(frame_name="ops")
change = nexus.get_frame_acl_builder("ops").begin_codegen_change(reason="probe")
change.use_profile("hybrid")
change.commit_change()
rift.create_frame_link("ops")
command_system = rift.space.command_system
try:
    try:
        command_system.materialize_codegen("value = 1 // 0\n", module_name="csv", frame_name="ops")
    except ZeroDivisionError as error:
        print("materialize raised:", type(error).__name__)
    print("csv still in sys.modules:", "csv" in sys.modules,
          "| original restored:", sys.modules.get("csv") is real_csv)
    outcome = command_system.materialize_codegen("VALUE = 1\n", module_name="json", frame_name="ops")
    replacement = sys.modules["json"]
    replacement.cleanup()
    print("after cleanup of a successful replacement: json in sys.modules:", "json" in sys.modules,
          "| original restored:", sys.modules.get("json") is real_json)
finally:
    sys.modules["csv"] = real_csv
    sys.modules["json"] = real_json
    conduit.cleanup()
    reset_runtime_singletons()
