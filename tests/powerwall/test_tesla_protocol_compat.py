"""Canary for the ``tesla-protocol`` dependency range in ``pyproject.toml``.

Imports every ``tesla_protocol.energy_device`` symbol this package relies on
and asserts the specific field/enum names it reads or writes still exist,
so a future ``tesla-protocol`` release that renames or removes one of them
fails here instead of as a runtime ``AttributeError`` against a gateway.
"""

from __future__ import annotations

from tesla_protocol.energy_device import (
    authorization_api_pb2,
    authorization_types_pb2,
    common_api_pb2,
    filestore_api_pb2,
    graphql_api_pb2,
    signed_message_pb2,
    teg_api_pb2,
    transport_pb2,
)


def _field_names(descriptor: object) -> set[str]:
    return {f.name for f in descriptor.fields}  # type: ignore[attr-defined]


def test_signed_message_pb2_symbols() -> None:
    assert signed_message_pb2.TAG_SIGNATURE_TYPE == 0
    assert signed_message_pb2.TAG_DOMAIN == 1
    assert signed_message_pb2.TAG_PERSONALIZATION == 2
    assert signed_message_pb2.TAG_EXPIRES_AT == 4
    assert signed_message_pb2.TAG_END == 255
    assert hasattr(signed_message_pb2, "SIGNATURE_TYPE_RSA")
    assert hasattr(signed_message_pb2, "DOMAIN_ENERGY_DEVICE")
    assert hasattr(signed_message_pb2, "MESSAGEFAULT_ERROR_NONE")
    assert hasattr(signed_message_pb2, "MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID")
    assert signed_message_pb2.MessageFault_E.Name(
        signed_message_pb2.MESSAGEFAULT_ERROR_NONE
    ) == "MESSAGEFAULT_ERROR_NONE"

    routable_fields = _field_names(signed_message_pb2.RoutableMessage.DESCRIPTOR)
    assert {
        "to_destination",
        "from_destination",
        "protobuf_message_as_bytes",
        "signature_data",
        "signed_message_status",
        "request_uuid",
        "uuid",
        "flags",
    } <= routable_fields


def test_transport_pb2_symbols() -> None:
    assert hasattr(transport_pb2, "DELIVERY_CHANNEL_HERMES_COMMAND")
    envelope_fields = _field_names(transport_pb2.MessageEnvelope.DESCRIPTOR)
    assert {"delivery_channel", "teg", "authorization"} <= envelope_fields
    assert transport_pb2.DELIVERY_CHANNEL_LOCAL_HTTPS == 1
    assert transport_pb2.LOCAL_PARTICIPANT_INSTALLER == 1


def test_graphql_api_pb2_symbols() -> None:
    assert graphql_api_pb2.GRAPH_QL_QUERY_FORMAT_SIGNED_SHA256_ECDSA_ASN1 == 2
    assert {"version", "query"} <= _field_names(graphql_api_pb2.SignedGraphQLQuery.DESCRIPTOR)
    assert {"format", "query", "signature", "variables_json"} <= _field_names(
        graphql_api_pb2.GraphQLAPIQueryRequest.DESCRIPTOR
    )
    assert "data" in _field_names(graphql_api_pb2.GraphQLAPIQueryResponse.DESCRIPTOR)
    envelope = transport_pb2.MessageEnvelope.DESCRIPTOR.fields_by_name
    assert envelope["graphql"].number == 16
    assert envelope["common"].number == 4


def test_common_api_pb2_system_info_layout() -> None:
    """``get_firmware_details`` needs the layout the gateway sends; the pre-4.0
    definition (``Din`` message at 2, enum at 5) fails to parse a real reply."""
    fields = common_api_pb2.CommonAPIGetSystemInfoResponse.DESCRIPTOR.fields_by_name
    expected = {
        "device_id": 1,
        "din": 2,
        "firmware_version": 3,
        "system_update": 5,
        "device_type": 6,
    }
    assert expected.items() <= {name: f.number for name, f in fields.items()}.items()
    assert fields["din"].message_type is None
    assert common_api_pb2.CommonMessages.DESCRIPTOR.fields_by_name[
        "get_system_info_request"
    ].number == 2


def test_filestore_api_pb2_symbols() -> None:
    assert hasattr(filestore_api_pb2, "FILE_STORE_API_DOMAIN_CONFIG_JSON")


def test_authorization_types_pb2_enums() -> None:
    assert hasattr(authorization_types_pb2, "AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP")
    for enum_name in (
        "AuthorizedState",
        "AuthorizedClientType",
        "AuthorizedKeyType",
        "AuthorizationRole",
        "AuthorizedVerificationType",
    ):
        assert hasattr(authorization_types_pb2, enum_name)


def test_authorization_api_pb2_messages_request() -> None:
    msgs = authorization_api_pb2.AuthorizationMessages()
    request_response_fields = {
        "list_authorized_clients_request",
        "list_authorized_clients_response",
        "remove_authorized_client_request",
        "remove_authorized_client_response",
    }
    assert request_response_fields <= _field_names(msgs.DESCRIPTOR)

    record_fields = _field_names(
        msgs.list_authorized_clients_response.clients.add().DESCRIPTOR
    )
    assert {
        "public_key",
        "state",
        "type",
        "description",
        "key_type",
        "roles",
        "verification",
        "added_time",
        "identifier",
        "authorized_by_public_key",
    } <= record_fields


def test_teg_api_pb2_backup_event_scheduling_fields() -> None:
    """``PowerwallClient.get_backup_events`` depends on this exact (mis)spelling.

    See ``AGENTS.md`` — ``teg_api_pb2.BackupEvent`` field 3 is published as
    ``sheduling_info`` (sic); ``ManualBackupEvent`` field 1 is the correctly
    spelled ``scheduling_info``. If this test starts failing on
    ``sheduling_info``, check whether upstream fixed the typo before widening
    the ``tesla-protocol`` pin further.
    """
    msgs = teg_api_pb2.TEGMessages()
    assert {
        "get_backup_events_request",
        "get_backup_events_response",
        "schedule_manual_backup_event_request",
        "schedule_manual_backup_event_response",
        "cancel_manual_backup_event_request",
        "cancel_manual_backup_event_response",
    } <= _field_names(msgs.DESCRIPTOR)

    backup_events_response = msgs.get_backup_events_response
    assert {"manual_backup_event", "backup_events"} <= _field_names(
        backup_events_response.DESCRIPTOR
    )

    backup_event_fields = _field_names(teg_api_pb2.BackupEvent.DESCRIPTOR)
    assert {"id", "name", "sheduling_info"} <= backup_event_fields

    manual_backup_event_fields = _field_names(teg_api_pb2.ManualBackupEvent.DESCRIPTOR)
    assert {"scheduling_info"} <= manual_backup_event_fields

    scheduling_info_fields = _field_names(
        msgs.schedule_manual_backup_event_request.scheduling_info.DESCRIPTOR
    )
    assert {"start_time", "duration_seconds", "priority"} <= scheduling_info_fields


def _numbers(descriptor: object) -> dict[str, int]:
    return {f.name: f.number for f in descriptor.fields}  # type: ignore[attr-defined]


def test_teg_api_pb2_dispatch_battery_power_fields() -> None:
    """``dispatch_battery_power`` / ``resume_battery_operation`` wire layout."""
    teg = _numbers(teg_api_pb2.TEGMessages.DESCRIPTOR)
    assert teg["dispatch_battery_power_request"] == 37
    assert teg["dispatch_battery_power_response"] == 38

    request = teg_api_pb2.TEGAPIDispatchBatteryPowerRequest.DESCRIPTOR
    assert _numbers(request) == {"resume_device_mode": 1, "real_power": 2}
    assert (
        request.fields_by_name["resume_device_mode"].message_type
        is teg_api_pb2.TEGAPIDispatchBatteryPowerRequest_ResumeDeviceOperatingMode.DESCRIPTOR
    )

    real_power = teg_api_pb2.TEGAPIDispatchBatteryPowerRequest_RealPowerCommand.DESCRIPTOR
    assert _numbers(real_power) == {"power_watts": 1, "duration_seconds": 2}
    fd = real_power.fields_by_name
    assert fd["power_watts"].type == fd["power_watts"].TYPE_DOUBLE
    assert fd["duration_seconds"].type == fd["duration_seconds"].TYPE_UINT32
    assert _numbers(teg_api_pb2.TEGAPIDispatchBatteryPowerResponse.DESCRIPTOR) == {}


def test_teg_api_pb2_battery_calibration_delay_fields() -> None:
    """``delay_battery_calibration`` / ``get_battery_calibration_delay_status``."""
    teg = _numbers(teg_api_pb2.TEGMessages.DESCRIPTOR)
    assert teg["delay_battery_calibration_request"] == 75
    assert teg["delay_battery_calibration_response"] == 76
    assert teg["get_delay_battery_calibration_status_request"] == 77
    assert teg["get_delay_battery_calibration_status_response"] == 78

    assert _numbers(teg_api_pb2.TEGAPIDelayBatteryCalibrationRequest.DESCRIPTOR) == {
        "delay_hours": 1
    }
    assert _numbers(
        teg_api_pb2.TEGAPIGetDelayBatteryCalibrationStatusResponse.DESCRIPTOR
    ) == {
        "calibration_delays_left": 1,
        "calibration_delay_remaining_seconds": 2,
        "max_calibration_delays": 3,
    }
