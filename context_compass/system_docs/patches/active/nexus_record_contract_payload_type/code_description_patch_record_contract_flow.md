# Code Description Patch: Record Contract Flow

1. Descriptor manager publishes frame/conduit/spell records.
2. Each record is stamped with:
   - `nexus_label`
   - `nexus_version`
3. Spell payload keeps its own `payload_type`.
4. ACL validation checks descriptor records against the required Nexus contract.
5. Viewer profile binding checks the same Nexus contract before execution.
