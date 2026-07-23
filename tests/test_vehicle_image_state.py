"""``vehicle_image_state`` (INFO read, defined on the shared ``Commands`` class)
over the mocked BLE transport.

Unlike every other ``GetVehicleData`` sub-state, image bytes are paged: an
``ID`` request reports the total size, then ``DATA`` requests advance by
``chunk_size`` until the full range is retrieved. Defined on ``Commands``
(not ``VehicleBluetooth``) so it is available on both signed transports -
BLE and the Fleet API signed-command relay (``VehicleSigned``).
"""

from tesla_protocol.command.car_server_pb2 import Action, VehicleImageRequest
from tesla_protocol.command.vehicle_pb2 import (
    VehicleData,
    VehicleImage,
    VehicleImageData,
    VehicleImageState,
)

from tesla_fleet_api.const import VehicleImageType
from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_vehicle_data_reply,
)


def _image_state_reply(
    total_size: int, data: bytes = b"", start_offset: int = 0
) -> VehicleData:
    return VehicleData(
        vehicle_image_state=VehicleImageState(
            vehicle_images=[
                VehicleImage(
                    total_image_size=total_size,
                    asset_data=VehicleImageData(
                        data=data, start_offset=start_offset
                    ),
                )
            ]
        )
    )


class VehicleImageStateTests(MockedBleTransportTestCase):
    async def test_pages_chunks_and_reassembles_full_image(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [
            infotainment_vehicle_data_reply(_image_state_reply(total_size=10)),
            infotainment_vehicle_data_reply(
                _image_state_reply(total_size=10, data=b"abcdef")
            ),
            infotainment_vehicle_data_reply(
                _image_state_reply(total_size=10, data=b"ghij", start_offset=6)
            ),
        ]

        result = await vehicle.vehicle_image_state(
            VehicleImageType.AUTOPILOT_VISUALIZATION_WRAP, chunk_size=6
        )

        self.assertEqual(result, b"abcdefghij")
        self.assertEqual(send.await_count, 3)

        id_msg = send.await_args_list[0].args[0]
        id_action = Action.FromString(decrypt_sent_command(vehicle, id_msg))
        id_request = (
            id_action.vehicleAction.getVehicleData.getVehicleImageState.imageRequests[0]
        )
        self.assertEqual(id_request.dataType, VehicleImageRequest.Type.ID)
        self.assertEqual(
            id_request.imageType, VehicleImageType.AUTOPILOT_VISUALIZATION_WRAP
        )

        chunk1_msg = send.await_args_list[1].args[0]
        chunk1_action = Action.FromString(decrypt_sent_command(vehicle, chunk1_msg))
        chunk1_request = chunk1_action.vehicleAction.getVehicleData.getVehicleImageState.imageRequests[
            0
        ]
        self.assertEqual(chunk1_request.dataType, VehicleImageRequest.Type.DATA)
        self.assertEqual(chunk1_request.chunkRequest.chunk_offset, 0)
        self.assertEqual(chunk1_request.chunkRequest.chunk_size, 6)

        chunk2_msg = send.await_args_list[2].args[0]
        chunk2_action = Action.FromString(decrypt_sent_command(vehicle, chunk2_msg))
        chunk2_request = chunk2_action.vehicleAction.getVehicleData.getVehicleImageState.imageRequests[
            0
        ]
        self.assertEqual(chunk2_request.chunkRequest.chunk_offset, 6)
        self.assertEqual(chunk2_request.chunkRequest.chunk_size, 4)

    async def test_zero_size_image_makes_no_data_requests(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            _image_state_reply(total_size=0)
        )

        result = await vehicle.vehicle_image_state(VehicleImageType.LICENSE_PLATE)

        self.assertEqual(result, b"")
        send.assert_awaited_once()

    async def test_rejects_invalid_chunk_size_before_requesting_metadata(
        self,
    ) -> None:
        vehicle, send = self.make_vehicle()

        for chunk_size in (0, -1, 1.5, True):
            with self.subTest(chunk_size=chunk_size):
                with self.assertRaisesRegex(
                    ValueError, "chunk_size must be a positive integer"
                ):
                    await vehicle.vehicle_image_state(
                        VehicleImageType.LICENSE_PLATE,
                        chunk_size=chunk_size,  # pyright: ignore[reportArgumentType]
                    )

        send.assert_not_awaited()

    async def test_rejects_empty_chunk_before_total_size(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [
            infotainment_vehicle_data_reply(_image_state_reply(total_size=4)),
            infotainment_vehicle_data_reply(_image_state_reply(total_size=4)),
        ]

        with self.assertRaisesRegex(
            ValueError, "Vehicle image ended after 0 of 4 bytes"
        ):
            await vehicle.vehicle_image_state(VehicleImageType.LICENSE_PLATE)

    async def test_rejects_chunk_with_unexpected_offset(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [
            infotainment_vehicle_data_reply(_image_state_reply(total_size=4)),
            infotainment_vehicle_data_reply(
                _image_state_reply(
                    total_size=4, data=b"abcd", start_offset=1
                )
            ),
        ]

        with self.assertRaisesRegex(
            ValueError, "Unexpected vehicle image chunk offset 1; expected 0"
        ):
            await vehicle.vehicle_image_state(VehicleImageType.LICENSE_PLATE)

    async def test_rejects_data_beyond_declared_size(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [
            infotainment_vehicle_data_reply(_image_state_reply(total_size=3)),
            infotainment_vehicle_data_reply(
                _image_state_reply(total_size=3, data=b"abcd")
            ),
        ]

        with self.assertRaisesRegex(
            ValueError, "Vehicle image exceeded declared size of 3 bytes"
        ):
            await vehicle.vehicle_image_state(VehicleImageType.LICENSE_PLATE)

    def test_available_on_the_fleet_api_signed_transport_too(self) -> None:
        """Defined on ``Commands`` (not ``VehicleBluetooth``), so it is
        inherited by ``VehicleSigned`` (Fleet API signed-command relay) as
        well as by BLE - the same signed-command wrapper, two transports."""
        self.assertTrue(issubclass(VehicleSigned, Commands))
        self.assertTrue(hasattr(VehicleSigned, "vehicle_image_state"))
