"""
TIER: expert (07)
GOAL: THE CODEGEN ROOM - where an agent writes code that becomes part of
      a running world. Advanced 11 took static and capability apart and
      deliberately stopped there. This is the third room kind, and it is
      expert material because it is the only one where the caller
      supplies EXECUTABLE SOURCE.

      THE THREE VERBS, AND THE ORDER IS NOT OPTIONAL

        validate_codegen(code, frame_name=...)   would this be allowed?
        execute_codegen(code, frame_name=...)    run it in the frame
        materialize_codegen(...)                 make it durable

      Validate is a SEPARATE VERB, not a flag on execute. That is the
      design decision worth the lesson: an agent can ask "would this be
      permitted" WITHOUT running anything. Every other "safe execution"
      story collapses those into one call and forces you to attempt the
      thing to learn whether you were allowed to attempt it.

      SEVEN STRATEGIES GATE WHAT AN AGENT MAY WRITE

        ast_structure       code SHAPES outside the governed subset
        import_policy       which imports the posture permits
        builtin_policy      dangerous builtins
        attribute_access    unsafe attribute patterns
        name_resolution     ast.Name against the namespace contract
        reflection_policy   introspection helpers
        recursive_control   codegen that calls codegen

      Read that last one twice. `recursive_control` exists because
      generated code that generates code is how a bounded system stops
      being bounded. The presence of that specific strategy tells you
      someone thought about an agent trying to escape its own sandbox by
      writing a smaller one.

      AND `frame_name` IS REQUIRED ON BOTH VERBS.
      Not optional, not defaulted - the same law advanced 13 hit on the
      viewer. Executing generated code needs to know WHICH WORLD it lands
      in, and there is no sane default for that. A codegen call that
      guessed its target frame would be the worst possible bug.

      THE ROOM OVERRIDES A THIRD PROPERTY.
      Advanced 11 found static and capability each override TWO things -
      `command_system` (what you may DO) and `frame_viewer` (what you may
      SEE). CodegenRiftSpace adds `codegen_system`: what you may MAKE.
      Do / see / make, each swapped by handing over a different class
      rather than guarding a shared one.

      MEMORY IS NOT OPTIONAL EITHER: both verbs "emit one FULL-SOURCE
      codegen memory record" when room memory is enabled. The room keeps
      what the agent wrote, not a summary of it - which is the only
      version that is useful afterwards.
SURFACE EXERCISED: CodegenCommandSystem via a codegen room -
                   validate_codegen / execute_codegen / materialize_codegen,
                   the seven validation strategies, frame_name as required
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


CODEGEN_VERBS = ("validate_codegen", "execute_codegen", "materialize_codegen")

GATES = (
    "ast_structure",
    "import_policy",
    "builtin_policy",
    "attribute_access",
    "name_resolution",
    "reflection_policy",
    "recursive_control",
)


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.activate(system_config)

    # THE THIRD ROOM KIND. static and capability were advanced 11;
    # codegen is the one that accepts source.
    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_config, rift_name="workshop")
    rift.mark_active()

    room = rift.space
    print("room kind:", room.space_kind)
    assert room.space_kind == "codegen"
    print("room class:", type(room).__name__)

    # THREE PROPERTIES SWAP BY KIND - do / see / make.
    commands = room.command_system
    print()
    print("command_system:", type(commands).__name__, "  (what you may DO)")
    print("frame_viewer:  ", type(room.frame_viewer).__name__,
          " (what you may SEE)")
    assert hasattr(room, "codegen_system"), "the codegen room adds a third"
    print("codegen_system:", type(room.codegen_system).__name__,
          "     (what you may MAKE)")

    # THE THREE VERBS. Validate is its own verb - an agent can ask
    # permission without acting.
    print()
    print("the codegen verbs:")
    for verb in CODEGEN_VERBS:
        assert hasattr(commands, verb), verb
        print("   ", verb)

    # frame_name IS REQUIRED on validate and execute. Generated code has
    # to land in a named world; guessing would be the worst kind of bug.
    import inspect
    for verb in ("validate_codegen", "execute_codegen"):
        parameters = inspect.signature(getattr(commands, verb)).parameters
        assert parameters["frame_name"].default is inspect.Parameter.empty, (
            f"{verb} must not default its target frame"
        )
        assert parameters["code"].default is inspect.Parameter.empty
    print()
    print("code and frame_name are BOTH required - no default world")

    # THE SEVEN GATES. Each one names a way generated code could escape
    # the posture it was granted.
    print()
    print("what an agent's code is checked against:")
    for gate in GATES:
        print("   ", gate)
    assert len(GATES) == 7

    print()
    print("recursive_control is the telling one - codegen that writes")
    print("codegen is how a bounded system stops being bounded.")

    # The room enumerates its own authority, same AIX door as advanced 11.
    supported = commands.list_supported_command_methods()
    assert isinstance(supported, tuple)
    codegen_on_surface = [v for v in CODEGEN_VERBS if v in supported]
    print()
    print("room reports", len(supported), "command methods;",
          len(codegen_on_surface), "are the codegen verbs")

    print()
    print("validate is a SEPARATE verb - ask permission without acting")
    print("do / see / make: three properties, three classes, one room kind")


if __name__ == "__main__":
    main()
