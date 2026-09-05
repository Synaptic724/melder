# Enable Nexus and open a Rift

Prerequisite: [world posture](posture.md). Nexus hosts the public room surface.
The two saved setup lessons give a complete activation path and separate the
process-wide Nexus configuration from the configuration consumed by one Rift.

## Configuration is not liveness

The Nexus factory returns a fresh, defaulted configuration. `nexus.activate(config)`
installs and finalizes it. The lesson checks `is_configured` and `is_activated`
separately, including after deactivation.

For a Rift, create a new configuration, choose its space type and name, then pass
it to `create_rift(...)`. That configuration is consumed: a second Rift needs a
second configuration object. Registration and active state are distinct; the
opening lesson explicitly marks the Rift active and inactive.

## Choose the room for the job

Start with a [static room](read-only-rooms.md) for inspection. A newly opened Rift
has no assigned frames. Opening a room and attaching it to an eligible target are
separate operations. The [inspection walkthrough](inspection-walkthrough.md)
connects the setup to a real target.

The Rift owns its room. Give the application ownership of the Rift's lifetime and
clean it up when the inspection session ends.
