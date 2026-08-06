"""
TIER: expert (07)
GOAL: THE CODEGEN ROOM - where an agent writes code that becomes part of
      a running world, and the gate it has to get through first. This is
      the only room kind where the caller supplies EXECUTABLE SOURCE, so
      it is the only one that has to answer "may I" before "did it work".

      THE DEFAULT POSTURE IS DENY, AND THE DENYLIST IS THE THREAT MODEL
      WRITTEN DOWN. A codegen room with no widening projection ships with
      imports OFF entirely and thirteen builtins refused by name:

        __import__  breakpoint  compile  dir     eval    exec   getattr
        globals     input       locals   setattr delattr vars

      Read that list as a document rather than a setting. Every entry is a
      door OUT of the namespace contract: `eval`/`exec`/`compile` execute
      text the gate never saw, `__import__` bypasses the import rules,
      `getattr`/`setattr`/`vars`/`dir` reach attributes by computed name,
      and `globals`/`locals` hand back the environment itself. Somebody
      enumerated the ways out and wrote them down where you can read them.

      A REFUSAL IS A VALUE, AND IT NAMES THE OFFENDER.
      `validate_codegen` returns a payload, not an exception and not a
      bare boolean:
        {"accepted": bool, "frame_name": str, "reason": str,
         "validation_issues": (str, ...)}
      Rejected source comes back as `accepted: False` with a message that
      names the specific thing - "Builtin 'eval' is not allowed in this
      codegen mode" - because a bare False would force you to re-run
      validation with different instrumentation just to learn why.

      THE CHAIN IS ORDERED AND IT SHORT-CIRCUITS. Syntax is checked first
      (a parse failure never reaches a gate), then seven strategies run in
      a fixed sequence and the FIRST refusal returns immediately:

        ast_structure -> import_policy -> builtin_policy ->
        name_resolution -> attribute_access -> reflection_policy ->
        recursive_control

      So `validation_issues` is normally ONE issue: the first gate that
      objected, not an audit of everything wrong. Fix it and re-ask - the
      next answer may well name a different gate. And the order is
      observable, which is why it is worth knowing rather than guessing:
      `eval('1 + 1')` is refused by builtin_policy, which sits BEFORE
      name_resolution, so you get the builtin message rather than an
      unresolved-name one.

      READ `recursive_control` TWICE. It is last in the chain and it
      exists because generated code that generates code is how a bounded
      system stops being bounded. Someone thought about an agent escaping
      its sandbox by writing a smaller one inside it.

      VALIDATION RUNS BEFORE THE ENVIRONMENT EXISTS, AND THAT ORDERING IS
      THE POINT. The gates read the AST, not a live namespace. The
      execution environment has not been built when they run - and
      building it to find out whether building it was allowed "would be
      exactly the escape the gate exists to prevent". That is why
      `validate_codegen` is a separate verb rather than a flag on execute:
      you can learn a boundary without approaching it.

      AND MELDER DOES NOT CLAIM THIS IS A PROOF. In its own words, the
      checks reject OBVIOUS violations, because "static analysis of Python
      cannot be exhaustive, so the validation chain is defence in depth
      alongside the namespace denylists and the ACL posture, not a proof
      of safety on its own". Three layers, named, with the honest limit
      stated. A system that claimed a guarantee here would be lying, and
      the willingness to write that down is worth more than the claim.

      THE ROOM OVERRIDES A THIRD PROPERTY. Advanced 11 found static and
      capability each swap TWO - `command_system` (what you may DO) and
      `frame_viewer` (what you may SEE). CodegenRiftSpace adds
      `codegen_system`: what you may MAKE. Do / see / make, each by
      handing over a different class rather than guarding a shared one.
SURFACE EXERCISED: validate_codegen driven against accepted source, a
                   denied import and a denied builtin; the validation
                   payload shape; RiftSpace.space_kind / command_system /
                   frame_viewer / codegen_system;
                   list_supported_command_methods
VERIFY: rewritten 2026-08-05 to DRIVE the validator instead of listing
        gate names; not yet re-run.
"""
import melder as md


FRAME = "gate-world"

SAFE = "result = 2 + 2\n"
IMPORTING = "import socket\nresult = socket\n"
EVALUATING = "result = eval('1 + 1')\n"

# The shipped deny list for a room with no widening projection. Named
# here so the lesson can CHECK the refusals against it rather than assert
# a number it typed.
DENIED_BUILTINS = (
    "__import__", "breakpoint", "compile", "dir", "eval", "exec",
    "getattr", "globals", "input", "locals", "setattr", "delattr", "vars",
)


def main() -> None:
    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    # An empty conjured frame is a real frame - `conjure` realizes it and
    # publishes it to the Nexus, and spells are cargo rather than a
    # precondition (expert 33).
    book.conjure(name="gate-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="workshop")
    rift.mark_active()
    rift.create_frame_link(FRAME)

    room = rift.space
    commands = room.command_system

    # DO / SEE / MAKE - three properties, three classes, one room kind.
    assert room.space_kind == "codegen"
    print("room kind:", room.space_kind, "->", type(room).__name__)
    print("  command_system:", type(commands).__name__, "(what you may DO)")
    print("  frame_viewer  :", type(room.frame_viewer).__name__,
          "(what you may SEE)")
    assert hasattr(room, "codegen_system"), "the codegen room adds a third"
    print("  codegen_system:", type(room.codegen_system).__name__,
          "(what you may MAKE)")

    # ACCEPTED SOURCE. The payload is a verdict, not a boolean.
    print()
    print("ASKING PERMISSION, WITHOUT RUNNING ANYTHING:")
    accepted = commands.validate_codegen(SAFE, frame_name=FRAME)
    assert isinstance(accepted, dict), accepted
    assert accepted["accepted"] is True, accepted
    assert accepted["frame_name"] == FRAME
    print("  validate(result = 2 + 2)  -> accepted:", accepted["accepted"],
          "| reason:", accepted.get("reason"))

    # A DENIED IMPORT. The shipped posture has imports OFF entirely, so
    # the refusal is about the STATEMENT, not about `socket` specifically.
    denied_import = commands.validate_codegen(IMPORTING, frame_name=FRAME)
    assert denied_import["accepted"] is False, denied_import
    import_issues = denied_import.get("validation_issues", ())
    assert import_issues, denied_import
    print()
    print("  validate(import socket)   -> accepted:",
          denied_import["accepted"])
    print("    reason :", denied_import.get("reason"))
    print("    issue  :", import_issues[0])
    print("    imports are OFF in the shipped posture, so the refusal is")
    print("    about the STATEMENT - a widening ACL projection is what")
    print("    turns them on and supplies an allow-list to be named by")

    # A DENIED BUILTIN. This one DOES name the offender, because the
    # denylist is per-name.
    denied_builtin = commands.validate_codegen(EVALUATING, frame_name=FRAME)
    assert denied_builtin["accepted"] is False, denied_builtin
    builtin_issues = denied_builtin.get("validation_issues", ())
    assert builtin_issues, denied_builtin
    assert "eval" in builtin_issues[0], builtin_issues
    print()
    print("  validate(eval('1 + 1'))   -> accepted:",
          denied_builtin["accepted"])
    print("    issue  :", builtin_issues[0])
    print("    it NAMES the builtin. A bare False would make you re-run")
    print("    validation with different instrumentation to learn why")

    # ONE ISSUE, NOT AN AUDIT. The chain returns on the FIRST refusal, so
    # a rejected payload carries the first gate's objection and stops.
    assert len(builtin_issues) == 1, builtin_issues
    print("    and exactly ONE issue came back - the chain short-circuits,")
    print("    so this is the first gate that objected, not a list of")
    print("    everything wrong. Fix it and ask again; the next answer")
    print("    may name a different gate.")

    # NOTHING RAN. Three verdicts, zero execution - which is the whole
    # reason validate is its own verb.
    print()
    print("three verdicts so far and NOTHING has executed. The gates read")
    print("the AST; the namespace does not exist yet. Building it to find")
    print("out whether building it was permitted would be exactly the")
    print("escape the gate exists to prevent.")

    # THE DENYLIST AS A DOCUMENT.
    print()
    print("the shipped builtin denylist -", len(DENIED_BUILTINS), "names:")
    print("   ", " ".join(DENIED_BUILTINS[:7]))
    print("   ", " ".join(DENIED_BUILTINS[7:]))
    print("  every one is a door OUT of the namespace contract:")
    print("    eval / exec / compile  run text the gate never saw")
    print("    __import__             bypasses the import rules")
    print("    getattr / setattr /")
    print("    vars / dir             reach attributes by computed name")
    print("    globals / locals       hand back the environment itself")

    # MALFORMED REQUEST IS A DIFFERENT FAILURE FROM DISALLOWED CODE.
    for bad_code, bad_frame in (("", FRAME), (SAFE, "")):
        try:
            commands.validate_codegen(bad_code, frame_name=bad_frame)
            raise AssertionError("expected ValueError on an empty argument")
        except ValueError:
            pass
    print()
    print("empty code or empty frame_name RAISE ValueError - a malformed")
    print("REQUEST is a different failure from disallowed CODE, and they")
    print("are not spelled the same way")

    # The room enumerates its own authority (the AIX door from advanced 11).
    supported = commands.list_supported_command_methods()
    assert isinstance(supported, tuple)
    assert "validate_codegen" in supported
    print()
    print("the room reports", len(supported), "command methods it will answer")

    print()
    print("validate is a SEPARATE verb - learn a boundary without")
    print("approaching it. And melder does not call this a proof: the")
    print("checks reject OBVIOUS violations, and the honest claim is")
    print("defence in depth across gates, namespace denylists and the ACL")
    print("posture. A system promising a guarantee here would be lying.")


if __name__ == "__main__":
    main()
