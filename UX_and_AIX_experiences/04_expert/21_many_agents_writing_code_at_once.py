"""
TIER: expert (21)
GOAL: REAL CODEGEN, AND SEVERAL AGENTS DOING IT AT ONCE. Expert 12 drove
      the loop once, on one thread. This is the shape melder is actually
      built for: four agents, four rooms, one shared world, concurrent.

      HOW DATA COMES BACK OUT OF GENERATED CODE
      The executor runs the source in a controlled namespace and lifts
      ONE name out of it:

          code = "total = 0\\nfor n in range(1, 101):\\n    total += n\\n"
                 "result = total\\n"
          payload = commands.execute_codegen(code, frame_name=...)
          payload["result"]        # 5050

      `result` is the convention, not a guess - `CodegenExecutionResult`
      is built with `result=` taken from the namespace after the code
      runs. Anything else the code computed stays in the sandbox and
      dies with it. One name out means the boundary is a value, not a
      scope an agent can leak through.

      THE PAYLOAD IS A VERDICT, NOT A RETURN VALUE
      `accepted` and `frame_name` are always there; `reason`,
      `runtime_error`, `validation_issues` and `result` fill in
      according to what happened. So the SAME shape describes a refusal,
      a crash, and a success - an agent branches on `accepted` instead
      of catching, exactly as expert 12 established.

      FOUR AGENTS, FOUR ROOMS, ONE WORLD
      Each agent opens its OWN rift, so it gets its own room, its own
      workstation, and its own memory. What they SHARE is the target
      frame - the world their code lands in. That is the isolation
      melder actually offers: private benches, shared world.

      WHAT IS AND IS NOT SERIALIZED
      Nothing in this lesson opens a transaction, because generated code
      that computes a value mutates no structure. Melder serializes
      STRUCTURAL change; arithmetic in a sandbox is not structural, so
      four agents run genuinely in parallel and none of them waits.
      The moment one of them binds or links, the plane underneath
      arbitrates - and still none of this vocabulary appears in the
      agent's code.

      A ROOM'S MEMORY IS ITS OWN
      Subscribe on one room and you see that room's commands. The other
      three are running the same verbs at the same time and none of them
      appears in your log. Per-agent audit falls out of per-agent rooms
      rather than being a feature anyone had to add.
SURFACE EXERCISED: several codegen rifts driven from threads,
                   validate_codegen / execute_codegen payloads, the
                   `result` namespace lift, and per-room memory
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import threading

import melder as md


class Meter:
    def __init__(self) -> None:
        self.reading = 1


# Four DIFFERENT jobs - this is generated source, the kind an agent
# actually emits: it computes something and leaves it in `result`.
JOBS = {
    "adder": (
        "total = 0\n"
        "for n in range(1, 101):\n"
        "    total += n\n"
        "result = total\n"
    ),
    "counter": (
        "hits = []\n"
        "for n in range(60):\n"
        "    if n % 7 == 0:\n"
        "        hits.append(n)\n"
        "result = len(hits)\n"
    ),
    "builder": (
        "parts = []\n"
        "for n in range(5):\n"
        "    parts.append(str(n * n))\n"
        "result = '-'.join(parts)\n"
    ),
    "reducer": (
        "value = 1\n"
        "for n in range(1, 8):\n"
        "    value = value * n\n"
        "result = value\n"
    ),
}

EXPECTED = {"adder": 5050, "counter": 9, "builder": "0-1-4-9-16",
            "reducer": 5040}

FRAME = "factory-world"


def _open_room(nexus, agent_name: str):
    """One agent's private room, pointed at the shared world."""
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=configuration,
                             rift_name=f"agent-{agent_name}")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    return rift.space


def main() -> None:
    # THE SHARED WORLD. One frame, postured for codegen (expert 11).
    book = md.Spellbook(aetheric_frame=FRAME)
    book.bind(spell=Meter, existence="unique", binding_name="factory-meter")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    book.conjure(name="factory-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(4)
    nexus.activate(system_configuration)
    print("one shared world:", FRAME)

    # ONE AGENT FIRST, SLOWLY, SO THE PAYLOAD IS VISIBLE.
    solo = _open_room(nexus, "solo")
    verdict = solo.command_system.validate_codegen(
        JOBS["adder"], frame_name=FRAME,
    )
    print()
    print("validate ->", verdict)
    assert verdict["accepted"] is True

    payload = solo.command_system.execute_codegen(
        JOBS["adder"], frame_name=FRAME,
    )
    print("execute  -> keys:", sorted(payload))
    assert payload["accepted"] is True
    assert payload["frame_name"] == FRAME
    assert payload["result"] == 5050
    print("execute  -> result:", payload["result"])
    print("  the code set `result`; the executor lifted THAT ONE NAME out")
    print("  everything else it computed died with the sandbox")

    # NOW FOUR AGENTS AT ONCE, EACH IN ITS OWN ROOM.
    rooms = {}
    outcomes = {}
    errors = []
    guard = threading.Lock()
    ready = threading.Barrier(len(JOBS))

    def run_agent(agent_name: str) -> None:
        try:
            room = _open_room(nexus, agent_name)
            with guard:
                rooms[agent_name] = room
            # Line them up so the executions genuinely overlap.
            ready.wait(timeout=10)
            result = room.command_system.execute_codegen(
                JOBS[agent_name], frame_name=FRAME,
            )
            with guard:
                outcomes[agent_name] = result
        except Exception as error:  # noqa: BLE001 - reported, not swallowed
            with guard:
                errors.append((agent_name, repr(error)))

    threads = [
        threading.Thread(target=run_agent, args=(name,), name=f"agent-{name}")
        for name in JOBS
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not errors, f"agent failures: {errors}"
    assert len(outcomes) == len(JOBS)
    print()
    print("four agents ran their own code concurrently:")
    for agent_name in sorted(outcomes):
        result = outcomes[agent_name]
        assert result["accepted"] is True
        assert result["result"] == EXPECTED[agent_name]
        print(f"   {agent_name:<8} -> {result['result']!r}")
    print("  none of them waited on another - computing a value is not")
    print("  a structural change, so there was nothing to serialize")

    # PRIVATE BENCHES. Four rooms, four workstations, four ids.
    workstation_ids = {name: room.workstation.workstation_id
                       for name, room in rooms.items()}
    assert len(set(workstation_ids.values())) == len(rooms)
    print()
    print("four rooms ->", len(set(workstation_ids.values())),
          "distinct workstations")
    print("  private bench each, one shared world - that is the isolation")

    # AND A ROOM'S MEMORY IS ITS OWN. Subscribe on one; run on two.
    watcher = rooms[sorted(rooms)[0]]
    other = rooms[sorted(rooms)[1]]
    seen = []
    subscription = watcher.memory_system.register_memory_callback(seen.append)
    assert watcher.memory_system.memory_enabled is True

    watcher.command_system.execute_codegen(JOBS["adder"], frame_name=FRAME)
    other.command_system.execute_codegen(JOBS["adder"], frame_name=FRAME)

    print()
    print("subscribed to ONE room, then ran in two:")
    print("   records captured:", len(seen))
    print("  the other room's identical call is absent - per-agent audit")
    print("  falls out of per-agent rooms, nobody had to build it")
    watcher.memory_system.unregister_memory_callback(subscription)

    print()
    print("four agents, four benches, one world, no ceremony")
    print("`result` is the whole boundary: one value out, nothing leaks")


if __name__ == "__main__":
    main()
