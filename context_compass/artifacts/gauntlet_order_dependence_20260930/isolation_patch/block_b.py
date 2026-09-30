def _gauntlet_libraries() -> tuple[str, ...]:
    """
    Return the libraries the shared gauntlet compares, in their printed order.

    Contract:
        - The order the standalone runner has always used: dependency-injector,
          dishka, melder. Every name is accepted by `_build_ops`.
        - Pure: returns the same constant names on every call.

    Returns:
        tuple[str, ...]: The three library names.
    """
    return ("dependency-injector", "dishka", "melder")


def _gauntlet_rounds() -> int:
    """
    Read how many times the pytest wrapper measures every library.

    Contract:
        - `REAL_WORLD_GAUNTLET_ROUNDS` unset or blank means one round; any other
          value must be a positive integer.
        - Each round runs every library once, each in its own process.

    Returns:
        int: The number of rounds, at least 1.

    Raises:
        AssertionError: When the variable is set to zero or a negative number.
        ValueError: When the variable is not an integer.
    """
    rounds = _env_int("REAL_WORLD_GAUNTLET_ROUNDS", 1)
    if rounds <= 0:
        raise AssertionError("REAL_WORLD_GAUNTLET_ROUNDS must be > 0")
    return rounds


def _isolated_order(round_ix: int) -> tuple[str, ...]:
    """
    Return the library order for one round of the one-process-per-library wrapper.

    Contract:
        - Round 0 is the printed order of `_gauntlet_libraries()`; each later round
          rotates it by one, so over three rounds every library runs once in every
          slot.
        - Every library runs in a fresh process whatever its slot, so the rotation
          does not remove the order effect (the separate processes do); it spreads
          machine drift over a session (heat, background load) across the libraries.

    Args:
        round_ix: Zero-based round index.

    Returns:
        tuple[str, ...]: The three library names in this round's order.

    Raises:
        AssertionError: When `round_ix` is negative.
    """
    if round_ix < 0:
        raise AssertionError("round_ix must be >= 0")
    libraries = _gauntlet_libraries()
    shift = round_ix % len(libraries)
    return libraries[shift:] + libraries[:shift]


