"""
TIER: expert (12)
GOAL: THE CODEGEN LOOP, ACTUALLY RUN. Expert 07 introduced the room and
      named its three verbs. This drives them: an agent asks permission,
      writes code into a named world, and reads back what it did.

      THE LOOP

        validate_codegen(code, frame_name=...)     may I?
        execute_codegen(code, frame_name=...)      do it
        materialize_codegen(...)                   make it durable

      A REFUSAL IS A RETURN VALUE, NOT AN EXCEPTION. `validate_codegen`
      hands back a `CodegenValidationResult`. Rejected code does not
      raise - and on the execute path a rejected validation returns a
      VALIDATION-FAILED `CodegenExecutionResult` without ever reaching
      compile or exec. An agent reads a verdict; it does not catch one.
      (Exceptions are reserved for malformed REQUESTS: empty code or an
      empty frame name raise `ValueError`. Bad input raises, bad code
      reports.)

      VALIDATE IS A SEPARATE VERB, AND THAT IS THE WHOLE DESIGN. An
      agent can ask "would this be permitted" WITHOUT running anything.
      And `execute_codegen` VALIDATES FIRST anyway - the invariant is
      "validation runs before execution on the execute path", so the
      separate verb buys you the answer early, never a way around it.
      Every other safe-execution story collapses those into one call and
      forces you to attempt the thing to learn whether you were allowed
      to attempt it - which means the only way to discover a boundary is
      to cross it.

      WHAT `validate` ACTUALLY ANSWERS
      Not "is this good code". It answers "does this code stay inside the
      posture this room was granted", against seven strategies:
      ast_structure, import_policy, builtin_policy, attribute_access,
      name_resolution, reflection_policy, recursive_control.

      Read `recursive_control` twice. It exists because generated code
      that generates code is how a bounded system stops being bounded.
      Someone thought about an agent escaping its sandbox by writing a
      smaller one inside it.

      THE ROOM REMEMBERS THE SOURCE, AND IT PUSHES
      Memory is not a describe-door you pull from the command system - it
      is `room.memory_system`, a `RiftMemorySystem`, and you SUBSCRIBE:

        room.memory_system.register_memory_callback(fn)   -> subscription id

      `memory_enabled` is literally "does anyone have a callback
      registered", so emission costs nothing until something is
      listening. A paraphrase would be useless afterwards anyway - the
      question you ask later is always "what EXACTLY did it write".

      AND THE RECORD IS ONE PER SUCCESSFUL TOP-LEVEL CALL. Two details
      make that precise, and both matter:
        - SUCCESSFUL. A refused command does not emit. Memory is a log of
          what happened, not of what was attempted.
        - TOP-LEVEL. The command system keeps a nested call-depth counter
          precisely to SUPPRESS duplicate emission when one public command
          calls another internally. You get the call you made, not the
          call tree underneath it.

      frame_name IS REQUIRED ON BOTH. Generated code has to land in a
      named world and there is no sane default for that - a codegen call
      that guessed its target frame would be the worst possible bug.
SURFACE EXERCISED: CodegenCommandSystem.validate_codegen /
                   execute_codegen / research_preview, the
                   CodegenValidationResult / CodegenExecutionResult
                   verdicts, and RiftSpace.memory_system callbacks.
                   materialize_codegen is DESCRIBED here, not called - the
                   third rung is a separate decision and expert 26 takes
                   it; running is not keeping.
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness. The SURFACE
        line above was corrected 2026-08-05; executable code unchanged
        since that run, so the green still stands.
"""
import melder as md


SAFE = "result = 2 + 2\n"

# Reaching for a module the posture never granted. This is what
# import_policy is for.
UNGRANTED = "import socket\nresult = socket\n"


def main() -> None:
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    # Expert 11's gate A: the shipped allow-list is ("default",), so a
    # world this Nexus has never been told about is refused before its
    # posture is even read. Naming it here is the observer's half of the
    # consent.
    system_configuration.with_allowed_target_frame_names(["loop-world"])
    nexus.activate(system_configuration)

    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="loop")
    rift.mark_active()
    room = rift.space
    commands = room.command_system

    # A codegen room needs a target world, and the frame must have opted in
    # (expert 11). No posture, no attachment, nothing to write into.
    book = md.Spellbook(aetheric_frame="loop-world")
    book.bind(spell=object, existence="many", binding_name="loop-world")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    book.conjure(name="loop-root")
    rift.create_frame_link("loop-world")
    frame_name = "loop-world"
    print("codegen room up:", type(room).__name__, "-> targets", frame_name)

    # 1. ASK FIRST. Validation is a real answer, returned without running
    #    anything - which is the only reason an agent can explore a
    #    boundary safely.
    verdict = commands.validate_codegen(SAFE, frame_name=frame_name)
    print()
    print("validate(safe)   ->", verdict)

    # 2. A REFUSAL COMES BACK AS A VALUE. No try/except - rejected code
    #    is a verdict object, and reading one is how an agent learns a
    #    boundary without crossing it.
    denied = commands.validate_codegen(UNGRANTED, frame_name=frame_name)
    print("validate(ungranted) ->", type(denied).__name__, "-", denied)

    # ...and executing rejected code returns a VALIDATION-FAILED result
    # rather than raising, because validation runs first on the execute
    # path too. Nothing was compiled and nothing ran.
    refused = commands.execute_codegen(UNGRANTED, frame_name=frame_name)
    print("execute(ungranted) ->", type(refused).__name__)
    print("  validation ran BEFORE execution - no compile, no exec")

    # THE EXCEPTIONS ARE FOR MALFORMED REQUESTS, not for rejected code.
    # Bad input raises; bad code reports.
    for bad_code, bad_frame in (("", frame_name), ("result = 1\n", "")):
        try:
            commands.validate_codegen(bad_code, frame_name=bad_frame)
            raise AssertionError("expected ValueError on an empty argument")
        except ValueError:
            pass
    print("empty code / empty frame_name raise ValueError - malformed")
    print("  REQUEST is a different failure from disallowed CODE")

    # 3. NOW RUN IT. Same code, same frame, and this is the only call
    #    that changes the world.
    outcome = commands.execute_codegen(SAFE, frame_name=frame_name)
    print()
    print("execute(safe)    ->", type(outcome).__name__)

    # 4. WHAT THE ROOM KEPT. Memory is a ROOM system and it PUSHES -
    #    subscribe before you act, or there is nothing to have kept.
    #    `memory_enabled` is exactly "is anyone listening", so a room with
    #    no subscriber pays nothing for the feature.
    seen = []
    assert room.memory_system.memory_enabled is False
    subscription = room.memory_system.register_memory_callback(seen.append)
    assert room.memory_system.memory_enabled is True
    print()
    print("subscribed to room memory ->", type(subscription).__name__)

    commands.execute_codegen("result = 5\n", frame_name=frame_name)
    print("records captured after one execute:", len(seen))
    print("  ONE record - top-level only. Internal command-to-command")
    print("  calls are suppressed by a call-depth counter, so you get")
    print("  the call you made, not the tree underneath it")
    print("  full source, not a summary - `what exactly did it write` is")
    print("  the only question anyone asks afterwards")

    room.memory_system.unregister_memory_callback(subscription)
    assert room.memory_system.memory_enabled is False
    print("unsubscribed - emission goes quiet again")

    # 5. THE SECOND QUESTION - and it needs a LIVE research root.
    #    `research_preview` is part of the research family, which reaches
    #    the Aether-hosted MutationResearch through a NON-CONSTRUCTING
    #    peek: absent or inactive research refuses rather than quietly
    #    booting one behind your back.
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    print()
    print("mutation research activated - research commands need it live")

    #    `validate` asks "am I PERMITTED"; `research_preview` asks "what
    #    would this DO" - the read-only candidate mock. Give it a
    #    frame_name and it FOLDS THE VALIDATE VERDICT IN, so one call
    #    answers both questions. Nothing executes, binds, or records.
    preview = commands.research_preview("result = 3\n", frame_name=frame_name)
    print("research_preview ->", type(preview).__name__)
    print("  would-be source, structural diff, blast radius - and the")
    print("  validate verdict too, because frame_name was given")
    print("  nothing executed, nothing bound, nothing recorded")

    # 6. MATERIALIZE is the third rung and a SEPARATE decision, with its
    #    own argument: executing code and giving it a MODULE NAME are
    #    different acts. Running is not keeping.
    print()
    print("materialize_codegen(code, module_name=..., frame_name=...)")
    print("  the module_name is the tell - durability needs an address")

    # 7. frame_name IS REQUIRED. Not defaulted, not inferred.
    import inspect
    for verb in ("validate_codegen", "execute_codegen"):
        parameters = inspect.signature(getattr(commands, verb)).parameters
        assert parameters["frame_name"].default is inspect.Parameter.empty, (
            f"{verb} must not default its target frame"
        )
    print("both verbs require frame_name - generated code lands somewhere")
    print("  named, or it does not land")

    print()
    print("ask, then act, then read back what you did")
    print("a boundary you can probe without crossing is the whole point")


if __name__ == "__main__":
    main()
