"""Scratch probe: does materialize_codegen accept core and dependency module names? Process-local only."""
import importlib
import sys

from tests._codegen_system_support import create_codegen_rift, create_enabled_nexus, reset_runtime_singletons


def room(profile_name):
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    change = nexus.get_frame_acl_builder("ops").begin_codegen_change(reason="probe")
    change.use_profile(profile_name)
    change.commit_change()
    rift.create_frame_link("ops")
    return conduit, rift.space.command_system


import csv as real_csv
import melder.aether.spellbook.bind.bind as real_bind_module

for profile_name in ("safe", "hybrid"):
    reset_runtime_singletons()
    conduit, command_system = room(profile_name)
    try:
        core_name = "melder.aether.spellbook.bind.bind"
        outcome = command_system.materialize_codegen("Bind = None\nresult = 1", module_name=core_name, frame_name="ops")
        live = sys.modules[core_name]
        print("[%s] core module replaced:" % profile_name, outcome["materialized"], "| sys.modules is original:",
              live is real_bind_module, "| type:", type(live).__name__,
              "| import_module returns it:", importlib.import_module(core_name) is live,
              "| parent attribute is it:", sys.modules["melder.aether.spellbook.bind"].bind is live)
        new_name = "melder.injected_probe"
        outcome = command_system.materialize_codegen("VALUE = 2", module_name=new_name, frame_name="ops")
        import melder
        print("[%s] new module under melder:" % profile_name, outcome["materialized"],
              "| melder.injected_probe.VALUE:", melder.injected_probe.VALUE)
        outcome = command_system.materialize_codegen("VALUE = 3", module_name="csv", frame_name="ops")
        print("[%s] stdlib csv replaced:" % profile_name, outcome["materialized"], "| sys.modules is original:",
              sys.modules["csv"] is real_csv)
        outcome = command_system.materialize_codegen("VALUE = 4", module_name="pytest", frame_name="ops")
        print("[%s] installed name pytest shadowed:" % profile_name, outcome["materialized"],
              "| import pytest gives:", type(importlib.import_module("pytest")).__name__)
    finally:
        # Put the real modules back so the next profile starts from the same world.
        sys.modules["melder.aether.spellbook.bind.bind"] = real_bind_module
        setattr(sys.modules["melder.aether.spellbook.bind"], "bind", real_bind_module)
        sys.modules["csv"] = real_csv
        sys.modules.pop("pytest", None)
        sys.modules.pop("melder.injected_probe", None)
        conduit.cleanup()
reset_runtime_singletons()
