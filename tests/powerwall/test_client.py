"""Unit tests for PowerwallClient's authorized-client and backup-event commands.

Exercises the protobuf parsing (enum-name stripping, base64 encoding,
optional-field presence) and write paths against hand-built
``AuthorizationMessages`` / ``TEGMessages`` messages — no real hardware,
LAN, or signing.
"""

from __future__ import annotations

from typing import Any

import pytest
from tesla_protocol.energy_device import (
    authorization_types_pb2,
    teg_api_pb2,
    transport_pb2,
)

from tesla_fleet_api.tesla.powerwall import (
    PowerwallClient,
    PowerwallCommandError,
    PowerwallNotSupportedError,
    PowerwallProtocolError,
)


class _FakeTransport:
    def __init__(self, response: transport_pb2.MessageEnvelope) -> None:
        self._response = response
        self.sent: list[bytes] = []

    async def post_v1r(self, envelope_bytes: bytes, din: str) -> bytes:
        self.sent.append(envelope_bytes)
        result: bytes = self._response.SerializeToString()
        return result


def _client_for(response: transport_pb2.MessageEnvelope) -> PowerwallClient:
    """A bare client (no real transport/session) that returns ``response``."""
    pw = PowerwallClient.__new__(PowerwallClient)

    async def fake_connect() -> str:
        return "1234567-00-A--CJ2000000000"

    pw.connect = fake_connect  # type: ignore[method-assign]
    pw._transport = _FakeTransport(response)  # type: ignore[attr-defined]
    return pw


def _envelope_with_clients() -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    resp = envelope.authorization.list_authorized_clients_response
    entry = resp.clients.add()
    entry.type = authorization_types_pb2.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
    entry.description = "Test Client"
    entry.key_type = authorization_types_pb2.AUTHORIZED_KEY_TYPE_RSA
    entry.public_key = b"\x01\x02\x03"
    entry.roles.append(authorization_types_pb2.AUTHORIZATION_ROLE_CUSTOMER)
    entry.state = authorization_types_pb2.AUTHORIZED_STATE_VERIFIED
    entry.verification = authorization_types_pb2.AUTHORIZED_VERIFICATION_TYPE_SIGNED
    entry.added_time.seconds = 1_700_000_000
    entry.identifier = "abc-123"
    resp.enable_line_switch_off = True
    return envelope


async def test_list_authorized_clients_parses_response() -> None:
    pw = _client_for(_envelope_with_clients())
    result = await pw.list_authorized_clients()
    assert result == {
        "clients": [
            {
                "public_key": "AQID",
                "state": "VERIFIED",
                "type": "CUSTOMER_MOBILE_APP",
                "description": "Test Client",
                "key_type": "RSA",
                "roles": ["CUSTOMER"],
                "verification": "SIGNED",
                "added_time": 1_700_000_000,
                "identifier": "abc-123",
                "authorized_by_public_key": None,
            }
        ],
        "enable_line_switch_off": True,
    }


async def test_list_authorized_clients_sends_request_over_v1r() -> None:
    pw = _client_for(_envelope_with_clients())
    transport = pw._transport  # type: ignore[attr-defined]
    await pw.list_authorized_clients()
    assert len(transport.sent) == 1
    sent_envelope = transport_pb2.MessageEnvelope()
    sent_envelope.ParseFromString(transport.sent[0])
    assert sent_envelope.HasField("authorization")
    assert sent_envelope.authorization.HasField("list_authorized_clients_request")


async def test_list_authorized_clients_omits_optional_fields_when_absent() -> None:
    envelope = transport_pb2.MessageEnvelope()
    resp = envelope.authorization.list_authorized_clients_response
    entry = resp.clients.add()
    entry.type = authorization_types_pb2.AUTHORIZED_CLIENT_TYPE_VEHICLE
    entry.key_type = authorization_types_pb2.AUTHORIZED_KEY_TYPE_ECC
    entry.public_key = b""
    entry.state = authorization_types_pb2.AUTHORIZED_STATE_PENDING_VERIFICATION
    entry.verification = authorization_types_pb2.AUTHORIZED_VERIFICATION_TYPE_PRESENCE_PROOF
    # No roles, added_time, identifier, or authorized_by_public_key set.

    pw = _client_for(envelope)
    result = await pw.list_authorized_clients()
    client = result["clients"][0]
    assert client["roles"] == []
    assert client["added_time"] is None
    assert client["identifier"] is None
    assert client["authorized_by_public_key"] is None


async def test_list_authorized_clients_unknown_state_does_not_raise() -> None:
    """A gateway firmware newer than the `tesla-protocol` pin can report a
    state number the enum doesn't know; it must come through as the raw int,
    never raise `ValueError`."""
    envelope = transport_pb2.MessageEnvelope()
    resp = envelope.authorization.list_authorized_clients_response
    entry = resp.clients.add()
    entry.public_key = b"\x01\x02\x03"
    entry.state = 99  # not a valid AuthorizedState member

    pw = _client_for(envelope)
    result = await pw.list_authorized_clients()
    assert result["clients"][0]["state"] == 99


async def test_list_authorized_clients_empty_list() -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.authorization.list_authorized_clients_response.SetInParent()

    pw = _client_for(envelope)
    result = await pw.list_authorized_clients()
    assert result == {"clients": [], "enable_line_switch_off": False}


# ── remove_authorized_client ────────────────────────────────────────────────


def _remove_ack() -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.authorization.remove_authorized_client_response.SetInParent()
    return envelope


async def test_remove_authorized_client_sends_raw_der_key() -> None:
    pw = _client_for(_remove_ack())
    transport = pw._transport  # type: ignore[attr-defined]

    await pw.remove_authorized_client(b"\x01\x02\x03")

    assert len(transport.sent) == 1
    sent = transport_pb2.MessageEnvelope()
    sent.ParseFromString(transport.sent[0])
    assert sent.authorization.HasField("remove_authorized_client_request")
    assert sent.authorization.remove_authorized_client_request.public_key == b"\x01\x02\x03"


async def test_remove_authorized_client_accepts_base64_from_listing() -> None:
    """A key can be round-tripped straight out of list_authorized_clients."""
    pw = _client_for(_remove_ack())
    transport = pw._transport  # type: ignore[attr-defined]

    # "AQID" is exactly what the listing reports for b"\x01\x02\x03".
    await pw.remove_authorized_client("AQID")

    sent = transport_pb2.MessageEnvelope()
    sent.ParseFromString(transport.sent[0])
    assert sent.authorization.remove_authorized_client_request.public_key == b"\x01\x02\x03"


async def test_remove_authorized_client_returns_none_on_empty_ack() -> None:
    """Firmware may omit the (fieldless) response oneof entirely."""
    pw = _client_for(transport_pb2.MessageEnvelope())
    assert await pw.remove_authorized_client(b"\x01\x02\x03") is None


@pytest.mark.parametrize("empty", [b"", ""])
async def test_remove_authorized_client_rejects_empty_key(empty: bytes | str) -> None:
    """An empty key would otherwise be a request to remove nothing."""
    pw = _client_for(_remove_ack())
    transport = pw._transport  # type: ignore[attr-defined]

    with pytest.raises(ValueError, match="must not be empty"):
        await pw.remove_authorized_client(empty)

    assert transport.sent == []


# ── get_backup_events ────────────────────────────────────────────────────────


async def test_get_backup_events_parses_scheduled_and_manual_events() -> None:
    """teg_api_pb2.BackupEvent field 3 is published as ``sheduling_info``

    (missing the first "c") in tesla-protocol 1.3.1 — this pins the client's
    matching attribute access against that upstream misspelling.
    """
    envelope = transport_pb2.MessageEnvelope()
    events_resp = envelope.teg.get_backup_events_response

    events_resp.manual_backup_event.scheduling_info.start_time.seconds = 1_700_000_000
    events_resp.manual_backup_event.scheduling_info.duration_seconds = 3600
    events_resp.manual_backup_event.scheduling_info.priority = (1 << 64) - 1

    evt = events_resp.backup_events.add()
    evt.id = "evt-1"
    evt.name = "Storm Watch"
    evt.sheduling_info.start_time.seconds = 1_700_100_000
    evt.sheduling_info.duration_seconds = 7200
    evt.sheduling_info.priority = 42

    pw = _client_for(envelope)
    result = await pw.get_backup_events()

    assert result["backup_events"] == [
        {
            "id": "evt-1",
            "name": "Storm Watch",
            "start_time": 1_700_100_000,
            "duration_seconds": 7200,
            "priority": 42,
        }
    ]
    manual = result["manual_backup"]
    assert manual is not None
    assert manual["start_time"] == 1_700_000_000
    assert manual["duration_seconds"] == 3600
    assert manual["priority"] == (1 << 64) - 1


async def test_get_backup_events_sends_request_over_v1r() -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.get_backup_events_response.SetInParent()

    pw = _client_for(envelope)
    transport = pw._transport  # type: ignore[attr-defined]
    await pw.get_backup_events()

    assert len(transport.sent) == 1
    sent = transport_pb2.MessageEnvelope()
    sent.ParseFromString(transport.sent[0])
    assert sent.HasField("teg")
    assert sent.teg.HasField("get_backup_events_request")


# ── dispatch_battery_power / resume_battery_operation ────────────────────────


def _dispatch_ack() -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.dispatch_battery_power_response.SetInParent()
    return envelope


def _sent_teg(pw: PowerwallClient) -> transport_pb2.MessageEnvelope:
    transport = pw._transport  # type: ignore[attr-defined]
    assert len(transport.sent) == 1
    sent = transport_pb2.MessageEnvelope()
    sent.ParseFromString(transport.sent[0])
    assert sent.HasField("teg")
    return sent


@pytest.mark.parametrize("watts", [-500.0, 0, 3300, 1250.5])
async def test_dispatch_battery_power_sends_real_power(watts: float) -> None:
    pw = _client_for(_dispatch_ack())
    await pw.dispatch_battery_power(watts, 30)

    sent = _sent_teg(pw)
    assert sent.teg.WhichOneof("message") == "dispatch_battery_power_request"
    assert (
        sent.teg.DESCRIPTOR.fields_by_name["dispatch_battery_power_request"].number
        == 37
    )
    request = sent.teg.dispatch_battery_power_request
    # The schema has no oneof here, so check that only one variant is set.
    assert request.HasField("real_power")
    assert not request.HasField("resume_device_mode")
    assert request.real_power.power_watts == watts
    assert request.real_power.duration_seconds == 30
    assert sent.recipient.din == "1234567-00-A--CJ2000000000"


async def test_resume_battery_operation_sends_resume_device_mode() -> None:
    pw = _client_for(_dispatch_ack())
    await pw.resume_battery_operation()

    request = _sent_teg(pw).teg.dispatch_battery_power_request
    assert request.HasField("resume_device_mode")
    assert not request.HasField("real_power")


@pytest.mark.parametrize(
    ("watts", "duration"),
    [
        (float("nan"), 30),
        (float("inf"), 30),
        (float("-inf"), 30),
        (10**1000, 30),
        (True, 30),
        ("500", 30),
        (500, 0),
        (500, -1),
        (500, 86401),
        (500, 1.5),
        (500, True),
    ],
)
async def test_dispatch_battery_power_rejects_bad_input(
    watts: object, duration: object
) -> None:
    pw = _client_for(_dispatch_ack())
    with pytest.raises(ValueError):
        await pw.dispatch_battery_power(watts, duration)  # type: ignore[arg-type]
    assert pw._transport.sent == []  # type: ignore[attr-defined]


@pytest.mark.parametrize("duration", [1, 86400])
async def test_dispatch_battery_power_accepts_duration_bounds(duration: int) -> None:
    pw = _client_for(_dispatch_ack())
    await pw.dispatch_battery_power(-500, duration)
    request = _sent_teg(pw).teg.dispatch_battery_power_request
    assert request.real_power.duration_seconds == duration


@pytest.mark.parametrize(
    "call",
    [
        lambda pw: pw.dispatch_battery_power(-500, 30),
        lambda pw: pw.resume_battery_operation(),
    ],
)
async def test_dispatch_missing_ack_raises(call: Any) -> None:
    wrong = transport_pb2.MessageEnvelope()
    wrong.teg.cancel_manual_backup_event_response.SetInParent()
    pw = _client_for(wrong)
    with pytest.raises(PowerwallProtocolError):
        await call(pw)


# ── battery calibration delay ────────────────────────────────────────────────


async def test_delay_battery_calibration_sends_delay_hours() -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.delay_battery_calibration_response.SetInParent()
    pw = _client_for(envelope)
    await pw.delay_battery_calibration(24)

    sent = _sent_teg(pw)
    assert sent.teg.WhichOneof("message") == "delay_battery_calibration_request"
    assert sent.teg.delay_battery_calibration_request.delay_hours == 24


@pytest.mark.parametrize("hours", [0, -1, 1.5, True, "24", 1 << 32])
async def test_delay_battery_calibration_rejects_bad_input(hours: object) -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.delay_battery_calibration_response.SetInParent()
    pw = _client_for(envelope)
    with pytest.raises(ValueError):
        await pw.delay_battery_calibration(hours)  # type: ignore[arg-type]
    assert pw._transport.sent == []  # type: ignore[attr-defined]


async def test_delay_battery_calibration_missing_ack_raises() -> None:
    pw = _client_for(_dispatch_ack())
    with pytest.raises(PowerwallProtocolError):
        await pw.delay_battery_calibration(24)


async def test_get_battery_calibration_delay_status_parses_response() -> None:
    envelope = transport_pb2.MessageEnvelope()
    status = envelope.teg.get_delay_battery_calibration_status_response
    status.calibration_delays_left = 2
    status.calibration_delay_remaining_seconds = 3600
    status.max_calibration_delays = 3
    pw = _client_for(envelope)

    result = await pw.get_battery_calibration_delay_status()

    assert result == {
        "calibration_delays_left": 2,
        "calibration_delay_remaining_seconds": 3600,
        "max_calibration_delays": 3,
    }
    sent = _sent_teg(pw)
    assert (
        sent.teg.WhichOneof("message")
        == "get_delay_battery_calibration_status_request"
    )


async def test_get_battery_calibration_delay_status_missing_response_raises() -> None:
    pw = _client_for(_dispatch_ack())
    with pytest.raises(PowerwallProtocolError):
        await pw.get_battery_calibration_delay_status()


# ── gateway error status ─────────────────────────────────────────────────────

# Verbatim reply from a Powerwall 3 on firmware 26.26.4 to
# get_delay_battery_calibration_status_request: common.error_response with
# status code 12 (UNIMPLEMENTED), "not implemented".
_UNIMPLEMENTED_REPLY = bytes.fromhex(
    "22170a150a13080c120f6e6f7420696d706c656d656e746564"
)


def _error_reply(code: int, message: str) -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.common.error_response.status.code = code
    envelope.common.error_response.status.message = message
    return envelope


async def test_unimplemented_reply_raises_not_supported() -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.ParseFromString(_UNIMPLEMENTED_REPLY)
    pw = _client_for(envelope)

    with pytest.raises(PowerwallNotSupportedError) as excinfo:
        await pw.get_battery_calibration_delay_status()

    err = excinfo.value
    assert isinstance(err, PowerwallProtocolError)
    assert err.command == "get_delay_battery_calibration_status_request"
    assert err.code == 12
    assert err.status_message == "not implemented"
    assert "not implemented" in str(err)


async def test_other_error_status_raises_command_error() -> None:
    pw = _client_for(_error_reply(7, "permission denied"))

    with pytest.raises(PowerwallCommandError) as excinfo:
        await pw.dispatch_battery_power(-500, 30)

    assert not isinstance(excinfo.value, PowerwallNotSupportedError)
    assert excinfo.value.code == 7
    assert excinfo.value.status_message == "permission denied"


async def test_error_status_tolerated_when_missing_response_allowed() -> None:
    pw = _client_for(_error_reply(5, "no active event"))
    await pw.cancel_max_backup()



# ── set_island_mode result ───────────────────────────────────────────────────


def _island_reply(result: int) -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.set_island_mode_response.result = result
    return envelope


async def test_set_island_mode_accepted() -> None:
    pw = _client_for(
        _island_reply(teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_ACCEPTED)
    )
    await pw.go_off_grid()
    assert len(pw._transport.sent) == 1  # type: ignore[attr-defined]


async def test_set_island_mode_rejected_raises_command_error() -> None:
    pw = _client_for(
        _island_reply(
            teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_EXCESSIVE_SOLAR
        )
    )
    with pytest.raises(PowerwallCommandError) as excinfo:
        await pw.go_off_grid()

    assert excinfo.value.command == "set_island_mode_request"
    assert (
        excinfo.value.code
        == teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_EXCESSIVE_SOLAR
    )
    assert (
        excinfo.value.status_message
        == "TEG_SET_ISLAND_MODE_RESULT_REJECTED_EXCESSIVE_SOLAR"
    )


async def test_set_island_mode_without_response_is_tolerated() -> None:
    await _client_for(transport_pb2.MessageEnvelope()).reconnect_grid()


# ── controllable device programs / OCPP ──────────────────────────────────────


def _programs_envelope() -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.get_controllable_device_programs_response.SetInParent()
    return envelope


async def test_get_controllable_device_programs_empty() -> None:
    pw = _client_for(_programs_envelope())

    assert await pw.get_controllable_device_programs() == {
        "active_programs": [],
        "inactive_programs": [],
    }


async def test_get_controllable_device_programs_one_program() -> None:
    envelope = _programs_envelope()
    resp = envelope.teg.get_controllable_device_programs_response
    program = resp.active_programs.add()
    program.key.device_id = "breaker-1"
    program.key.priority = 5000
    program.settings.contactor_state = 1
    program.schedule.start.seconds = 1_700_000_000
    program.schedule.end.seconds = 1_700_003_600
    unknown = resp.inactive_programs.add()
    unknown.key.device_id = "breaker-2"
    unknown.key.priority = 777
    unknown.settings.contactor_state = 9
    pw = _client_for(envelope)

    result = await pw.get_controllable_device_programs(["breaker-1"])

    assert result["active_programs"] == [
        {
            "key": {"device_id": "breaker-1", "priority": "CUSTOMER_DEFAULT"},
            "settings": {"contactor_state": "OPEN"},
            "schedule": {
                "start": 1_700_000_000,
                "end": 1_700_003_600,
                "expiry": None,
            },
        }
    ]
    assert result["inactive_programs"][0]["key"]["priority"] == 777
    assert result["inactive_programs"][0]["settings"]["contactor_state"] == 9
    sent = transport_pb2.MessageEnvelope.FromString(
        pw._transport.sent[0]  # type: ignore[attr-defined]
    )
    request = sent.teg.get_controllable_device_programs_request
    assert list(request.device_ids) == ["breaker-1"]


async def test_configure_ocpp_success() -> None:
    envelope = transport_pb2.MessageEnvelope()
    envelope.teg.configure_ocpp_response.SetInParent()
    pw = _client_for(envelope)

    await pw.configure_ocpp("wss://csms.example.com/ocpp")

    sent = transport_pb2.MessageEnvelope.FromString(
        pw._transport.sent[0]  # type: ignore[attr-defined]
    )
    assert sent.teg.configure_ocpp_request.csms_base_url == (
        "wss://csms.example.com/ocpp"
    )


async def test_configure_ocpp_unimplemented_raises_not_supported() -> None:
    pw = _client_for(_error_reply(12, "not implemented"))

    with pytest.raises(PowerwallNotSupportedError) as excinfo:
        await pw.configure_ocpp("wss://csms.example.com/ocpp")

    assert excinfo.value.command == "configure_ocpp_request"
    assert excinfo.value.code == 12


async def test_configure_ocpp_rejects_empty_url() -> None:
    pw = _client_for(_error_reply(12, "not implemented"))
    with pytest.raises(ValueError):
        await pw.configure_ocpp("")
