from melder.aether.nexus.rift.rift_space.rift_event_configuration import (
    RiftEventConfiguration,
)


def test_rift_event_configuration_preserves_callback_order_and_cleanup_is_idempotent() -> None:
    calls = []

    def _action_enricher(action) -> None:
        calls.append(("action_enricher", action))

    def _memory_enricher(memory) -> None:
        calls.append(("memory_enricher", memory))

    def _action_observer(action) -> None:
        calls.append(("action_observer", action))

    def _memory_observer(memory) -> None:
        calls.append(("memory_observer", memory))

    configuration = RiftEventConfiguration(
        action_enrichers=[_action_enricher],
        memory_enrichers=[_memory_enricher],
        action_observers=[_action_observer],
        memory_observers=[_memory_observer],
    )

    assert configuration._action_enrichers == [_action_enricher]
    assert configuration._memory_enrichers == [_memory_enricher]
    assert configuration._action_observers == [_action_observer]
    assert configuration._memory_observers == [_memory_observer]

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True
    assert configuration._action_enrichers is None
    assert configuration._memory_enrichers is None
    assert configuration._action_observers is None
    assert configuration._memory_observers is None

