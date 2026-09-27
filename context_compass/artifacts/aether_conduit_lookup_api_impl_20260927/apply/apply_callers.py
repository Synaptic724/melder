"""Step 3 of the aether_conduit_lookup_api lane: migrate the four src callers.

TransferOfOwnership and StaticCommandSystem move to the root names (owners are roots); CommandSystem and
StaticFrameViewer delegate their live-conduit lookup to Aether.get_conduit_by_id and keep their error surface.

Usage: python apply_callers.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

ROOT = sys.argv[1]
TRANSFER = os.path.join(ROOT, "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py")
STATIC_COMMANDS = os.path.join(ROOT, "src/melder/nexus/rift/command_system/static_command_system.py")
COMMANDS = os.path.join(ROOT, "src/melder/nexus/rift/command_system/command_system.py")
STATIC_VIEWER = os.path.join(ROOT, "src/melder/nexus/rift/frame_viewer/static_frame_viewer.py")

TRANSFER_OLD = '''        for conduit_id in self._aether.list_conduit_ids(self._frame_name):
            if not conduit_id:
                continue
            try:
                conduit = self._aether.get_conduit_by_id(
                    conduit_id,
                    self._frame_name,
                )
'''
TRANSFER_NEW = '''        # Roots only, by design: a lesser scope owns nothing but the lifecycle of what it creates, so the
        # lineage sweep never needs the lesser lineage (owner ruling, 2026-09-27).
        for conduit_id in self._aether.list_root_conduit_ids(self._frame_name):
            if not conduit_id:
                continue
            try:
                conduit = self._aether.get_root_conduit_by_id(
                    conduit_id,
                    self._frame_name,
                )
'''

STATIC_MELD_OLD = '''            owner_conduit = self._aether._get_conduit_by_id(
                owner_conduit_id,
                frame_name,
            )
            try:
                return owner_conduit.meld_existing_spell(
'''
STATIC_MELD_NEW = '''            # Spell owners are roots.
            owner_conduit = self._aether.get_root_conduit_by_id(
                owner_conduit_id,
                frame_name,
            )
            try:
                return owner_conduit.meld_existing_spell(
'''
STATIC_STATUS_OLD = '''            owner_conduit = self._aether._get_conduit_by_id(
                owner_conduit_id,
                frame_name,
            )
            is_live = owner_conduit.has_live_creation(spell=spell_record.spell_id)
'''
STATIC_STATUS_NEW = '''            # Spell owners are roots.
            owner_conduit = self._aether.get_root_conduit_by_id(
                owner_conduit_id,
                frame_name,
            )
            is_live = owner_conduit.has_live_creation(spell=spell_record.spell_id)
'''

COMMANDS_OLD = '''        Contract:
            - Enforces raw-runtime access, frame command enablement, and
              conduit-level ACL checks before touching Aether runtime state.
            - Falls back through lesser-conduit lineage traversal when the root
              conduit lookup misses.
            - Requires the caller to hold `self._lock`.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Live conduit object or matching lesser conduit object.

        Raises:
            ValueError:
                If runtime-object access is denied, the frame/conduit ACL gate
                fails, or the conduit cannot be found in the frame.
        """
        self._assert_raw_runtime_object_access_allowed("get_conduit_by_id")
        self._assert_frame_command_enabled(frame_name)
        self._assert_conduit_command_enabled(
            conduit_id,
            frame_name=frame_name,
        )
        try:
            return self._aether.get_conduit_by_id(
                conduit_id,
                frame_name,
            )
        except ValueError:
            frame = self._get_required_runtime_frame(frame_name)
            for root_conduit in frame._conduits.values():
                conduit_ward = root_conduit._conduit_ward
                if conduit_ward is None:
                    continue
                lesser_conduit = conduit_ward._get_lesser_conduit(conduit_id)
                if lesser_conduit is not None:
                    return lesser_conduit
            raise ValueError(
                "Conduit id '{0}' was not found in frame '{1}'.".format(
                    conduit_id,
                    frame_name,
                )
            )
'''
COMMANDS_NEW = '''        Contract:
            - Enforces raw-runtime access, frame command enablement, and
              conduit-level ACL checks before touching Aether runtime state.
            - Resolves through `Aether.get_conduit_by_id`, which covers the
              frame's live roots and their attached lesser lineage, named or
              anonymous, at any depth.
            - Keeps this surface's errors: a missing frame raises the frame
              error from `_get_required_runtime_frame`, and an id that is not
              live in the frame raises "Conduit id '<id>' was not found in
              frame '<frame>'." chained from Aether's error.
            - Requires the caller to hold `self._lock`.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Live conduit object or matching lesser conduit object.

        Raises:
            ValueError:
                If runtime-object access is denied, the frame/conduit ACL gate
                fails, or the conduit cannot be found in the frame.
        """
        self._assert_raw_runtime_object_access_allowed("get_conduit_by_id")
        self._assert_frame_command_enabled(frame_name)
        self._assert_conduit_command_enabled(
            conduit_id,
            frame_name=frame_name,
        )
        try:
            return self._aether.get_conduit_by_id(
                conduit_id,
                frame_name,
            )
        except ValueError as error:
            # Re-raise in this surface's wording: the frame error first, else the id error.
            self._get_required_runtime_frame(frame_name)
            raise ValueError(
                "Conduit id '{0}' was not found in frame '{1}'.".format(
                    conduit_id,
                    frame_name,
                )
            ) from error
'''

VIEWER_OLD = '''        """
        Resolve one owner conduit, including lesser-conduit fallback.

        Args:
            frame_name:
                Hosted frame name.
            conduit_id:
                Owner conduit id to resolve.

        Returns:
            Optional[Any]: Matching conduit, or None when missing.
        """
        try:
            return self._aether.get_conduit_by_id(conduit_id, frame_name)
        except ValueError:
            if frame_name != "default":
                frame = self._aether._aetheric_frames.get(frame_name)
            else:
                self._aether._ensure_default_frame()
                frame = self._aether._default_frame
            if frame is None:
                return None
            for root_conduit in frame._conduits.values():
                conduit_ward = root_conduit._conduit_ward
                if conduit_ward is None:
                    continue
                lesser_conduit = conduit_ward._get_lesser_conduit(conduit_id)
                if lesser_conduit is not None:
                    return lesser_conduit
        return None
'''
VIEWER_NEW = '''        """
        Resolve one owner conduit, root or attached lesser, or None.

        Contract:
            - Resolves through `Aether.get_conduit_by_id`, which covers the
              frame's live roots and their attached lesser lineage, named or
              anonymous, at any depth.
            - Returns None instead of raising when the frame does not exist or
              no live conduit in it has this id.

        Args:
            frame_name:
                Hosted frame name.
            conduit_id:
                Owner conduit id to resolve.

        Returns:
            Optional[Any]: Matching conduit, or None when missing.
        """
        try:
            return self._aether.get_conduit_by_id(conduit_id, frame_name)
        except ValueError:
            return None
'''

print("transfer:", replace_block(TRANSFER, TRANSFER_OLD, TRANSFER_NEW))
print("static meld:", replace_block(STATIC_COMMANDS, STATIC_MELD_OLD, STATIC_MELD_NEW))
print("static status:", replace_block(STATIC_COMMANDS, STATIC_STATUS_OLD, STATIC_STATUS_NEW))
print("commands:", replace_block(COMMANDS, COMMANDS_OLD, COMMANDS_NEW))
print("static viewer:", replace_block(STATIC_VIEWER, VIEWER_OLD, VIEWER_NEW))
