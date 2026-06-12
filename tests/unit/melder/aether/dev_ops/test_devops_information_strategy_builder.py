from typing import Dict

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_strategy_builder import (
    DevopsInformationStrategyBuilder,
)


class _EchoInformationStrategy(DevopsInformationStrategy):
    """
    Minimal strategy double for registry-builder tests.

    Contract:
        - Echoes the supplied metadata.
        - Includes the registry frame name in the result.
    """

    @staticmethod
    def execute(
            *,
            devops_information_registry: DevopsInformationRegistry,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Execute the echo strategy.

        Returns:
            Dict[str, object]:
                Detached payload containing the frame name and original metadata.
        """
        return {
            "frame_name": devops_information_registry.aetheric_frame_name,
            "metadata": dict(metadata),
        }


def test_devops_information_strategy_builder_requires_registry() -> None:
    """
    Verify builder construction rejects a missing registry.
    """
    with pytest.raises(ValueError, match="must not be None"):
        DevopsInformationStrategyBuilder(None)


def test_devops_information_registry_exposes_information_strategy_builder() -> None:
    """
    Verify the registry owns and exposes one information-strategy builder.
    """
    registry = DevopsInformationRegistry("frame-1")

    builder = registry.information_strategy_builder

    assert isinstance(builder, DevopsInformationStrategyBuilder)


def test_devops_information_strategy_builder_registers_and_resolves_strategy() -> None:
    """
    Verify strategy registration and resolution are name-normalized.
    """
    registry = DevopsInformationRegistry("frame-1")
    builder = registry.information_strategy_builder

    builder.register_strategy(" Echo ", _EchoInformationStrategy)

    assert builder.resolve("echo") is _EchoInformationStrategy
    # The default catalog is pre-registered; the new name joins it.
    assert "echo" in builder.list_registered_strategy_names()


def test_devops_information_strategy_builder_rejects_unknown_strategy() -> None:
    """
    Verify unknown strategy resolution raises a clear error.
    """
    registry = DevopsInformationRegistry("frame-1")

    with pytest.raises(NotImplementedError, match="not implemented"):
        registry.information_strategy_builder.resolve("missing")


def test_devops_information_strategy_builder_executes_registered_strategy() -> None:
    """
    Verify builder execution passes registry and metadata to the strategy.
    """
    registry = DevopsInformationRegistry("frame-1")
    builder = registry.information_strategy_builder
    builder.register_strategy("echo", _EchoInformationStrategy)

    result = builder.execute(
        strategy_name="echo",
        metadata={"lane": "alpha"},
    )

    assert result == {
        "frame_name": "frame-1",
        "metadata": {"lane": "alpha"},
    }
