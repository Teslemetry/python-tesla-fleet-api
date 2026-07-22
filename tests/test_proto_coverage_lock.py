"""Coverage-lock test: every ``VehicleAction``/``GetVehicleData`` proto field
must have a library wrapper, or be one of a short, explicitly-reasoned
allowlist of fields that need their own design before they can be wrapped.

Without this test, a future ``tesla-protocol`` version bump that adds a new
oneof/message field would silently drift the library out of full command
coverage with no signal - this test fails loudly instead, forcing a deliberate
decision (wrap it, or add it to an allowlist with a reason) for anything new.

This test asserts full coverage of ``commands.py``, so it only passes once
every command-wrapper PR in the full-surface rollout has landed; if merged
before the others, rebase this branch onto the updated main once they have.
"""

import inspect
import unittest

from tesla_protocol.command import car_server_pb2 as cs

from tesla_fleet_api.tesla.vehicle import bluetooth as bluetooth_module
from tesla_fleet_api.tesla.vehicle import commands as commands_module

COMMANDS_SOURCE = inspect.getsource(commands_module)
BLUETOOTH_SOURCE = inspect.getsource(bluetooth_module)

# Covered via an equivalent alternate proto path (VCSEC), not the CarServer
# field of the same name/intent - not literally missing from the library.
ALTERNATE_PATH_VEHICLE_ACTION_FIELDS = frozenset(
    {
        "getVehicleData",  # the wrapper's own input message, not a command
        "remoteStartDrive",  # built from VCSEC RKEAction_E.RKE_ACTION_REMOTE_DRIVE
        "chargePortDoorClose",  # built from VCSEC ClosureMoveRequest
        "chargePortDoorOpen",  # built from VCSEC ClosureMoveRequest
    }
)

# A persistent push-style subscription sub-protocol: the vehicle sends
# unsolicited updates after a subscription is established, unlike every other
# VehicleAction's one-shot send/reply. Needs its own broadcast-dispatcher
# design (mirroring the VCSEC broadcast listeners), not a one-shot wrapper.
STREAMING_SUBSCRIPTION_VEHICLE_ACTION_FIELDS = frozenset(
    {
        "createStreamSession",
        "streamMessage",
        "vehicleDataSubscription",
        "vehicleDataAck",
        "vitalsSubscription",
        "vitalsAck",
        "cancelVehicleDataSubscription",
    }
)

KNOWN_UNWRAPPED_VEHICLE_ACTION_FIELDS = (
    ALTERNATE_PATH_VEHICLE_ACTION_FIELDS | STREAMING_SUBSCRIPTION_VEHICLE_ACTION_FIELDS
)

# Explicitly chunked binary image-data transfer (paged offset/size requests),
# unlike every other GetVehicleData sub-state's single no-arg read. Needs its
# own chunking/reassembly design, not a one-shot reader.
KNOWN_UNWRAPPED_GET_VEHICLE_DATA_FIELDS = frozenset({"getVehicleImageState"})


def _vehicle_action_fields():
    return cs.VehicleAction.DESCRIPTOR.oneofs_by_name["vehicle_action_msg"].fields


def _get_vehicle_data_fields():
    return cs.GetVehicleData.DESCRIPTOR.fields


class VehicleActionCoverageLockTests(unittest.TestCase):
    def test_every_field_is_wrapped_or_allowlisted(self) -> None:
        unwrapped = []
        for field in _vehicle_action_fields():
            if field.name in KNOWN_UNWRAPPED_VEHICLE_ACTION_FIELDS:
                continue
            if field.name in ALTERNATE_PATH_VEHICLE_ACTION_FIELDS:
                continue
            type_name = field.message_type.name if field.message_type else None
            if field.name in COMMANDS_SOURCE:
                continue
            if type_name and type_name in COMMANDS_SOURCE:
                continue
            unwrapped.append(field.name)
        self.assertEqual(
            unwrapped,
            [],
            f"VehicleAction fields with no commands.py wrapper and no "
            f"allowlist entry: {unwrapped}",
        )

    def test_allowlisted_fields_still_exist_in_the_proto(self) -> None:
        """Catches a stale allowlist entry after a tesla-protocol field rename/removal."""
        all_names = {field.name for field in _vehicle_action_fields()}
        stale = KNOWN_UNWRAPPED_VEHICLE_ACTION_FIELDS - all_names
        self.assertEqual(
            stale, set(), f"Allowlisted fields no longer in proto: {stale}"
        )


class GetVehicleDataCoverageLockTests(unittest.TestCase):
    def test_every_field_is_wrapped_or_allowlisted(self) -> None:
        unwrapped = []
        for field in _get_vehicle_data_fields():
            if field.name in KNOWN_UNWRAPPED_GET_VEHICLE_DATA_FIELDS:
                continue
            type_name = field.message_type.name if field.message_type else None
            if field.name in BLUETOOTH_SOURCE:
                continue
            if type_name and type_name in BLUETOOTH_SOURCE:
                continue
            unwrapped.append(field.name)
        self.assertEqual(
            unwrapped,
            [],
            f"GetVehicleData fields with no bluetooth.py reader and no "
            f"allowlist entry: {unwrapped}",
        )

    def test_allowlisted_fields_still_exist_in_the_proto(self) -> None:
        all_names = {field.name for field in _get_vehicle_data_fields()}
        stale = KNOWN_UNWRAPPED_GET_VEHICLE_DATA_FIELDS - all_names
        self.assertEqual(
            stale, set(), f"Allowlisted fields no longer in proto: {stale}"
        )
