# Teslemetry

Teslemetry is a service that provides additional telemetry data for Tesla vehicles. This document provides detailed examples of how to use the Teslemetry class in the Tesla Fleet API library.

## Initialization

To use the Teslemetry class, you need to initialize it with an aiohttp ClientSession and an access token.

```python
import asyncio
import aiohttp
from tesla_fleet_api import Teslemetry

async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

asyncio.run(main())
```

## Ping

The `ping` method sends a ping request to the Teslemetry server.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.ping()
        print(response)

asyncio.run(main())
```

## Test API Authentication

The `test` method tests the API authentication.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.test()
        print(response)

asyncio.run(main())
```

## Get User Data

The `userdata` method retrieves user data.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.userdata()
        print(response)

asyncio.run(main())
```

## Get Metadata

The `metadata` method retrieves user metadata, including scopes.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.metadata()
        print(response)

asyncio.run(main())
```

## Get Scopes

The `scopes` method retrieves user scopes.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.scopes()
        print(response)

asyncio.run(main())
```

## Server-Side Polling

The `server_side_polling` method gets or sets the server-side polling mode for a vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        # Get the current server-side polling mode
        response = await teslemetry.server_side_polling(vin)
        print(response)

        # Enable server-side polling
        response = await teslemetry.server_side_polling(vin, value=True)
        print(response)

        # Disable server-side polling
        response = await teslemetry.server_side_polling(vin, value=False)
        print(response)

asyncio.run(main())
```

## Force Vehicle Data Refresh

The `vehicle_data_refresh` method forces a refresh of the vehicle data.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await teslemetry.vehicle_data_refresh(vin)
        print(response)

asyncio.run(main())
```

## Get Streaming Fields

The `fields` method retrieves streaming field parameters and metadata.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.fields()
        print(response)

asyncio.run(main())
```

## Get Vehicle Configuration

The `vehicle_config` method retrieves the saved vehicle configuration for a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await teslemetry.vehicle_config(vin)
        print(response)

asyncio.run(main())
```

## Get Streaming Configuration

The `streaming_config` method retrieves the streaming configuration for a specific vehicle, including certificate, hostname, port, and configurable telemetry fields.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await teslemetry.streaming_config(vin)
        print(response)

asyncio.run(main())
```

## Stop Streaming

The `stop_streaming` method stops streaming data from a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await teslemetry.stop_streaming(vin)
        print(response)

asyncio.run(main())
```

## Modify Streaming Configuration

The `modify_streaming_config` method modifies the streaming configuration for a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        # Configure specific fields to stream
        fields = {
            "BatteryLevel": {
                "interval_seconds": 60,
                "minimum_delta": 0.1
            },
            "VehicleSpeed": {
                "interval_seconds": 30,
                "minimum_delta": 0.5
            }
        }

        response = await teslemetry.modify_streaming_config(vin, fields)
        print(response)

asyncio.run(main())
```

## Create Streaming Configuration

The `create_streaming_config` method creates or updates the streaming configuration for a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        # Configure fields to stream
        fields = {
            "BatteryLevel": {
                "interval_seconds": 60
            },
            "Location": {
                "interval_seconds": 120
            }
        }

        response = await teslemetry.create_streaming_config(vin, fields)
        print(response)

asyncio.run(main())
```

## Vehicle Custom Commands

### Clear PIN to Drive

The `clear_pin_to_drive` method deactivates PIN to Drive on the vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        # Clear PIN to Drive with your 4-digit PIN
        response = await vehicle.clear_pin_to_drive("1234")
        print(response)

asyncio.run(main())
```

### Remove All Impermanent Keys

The `remove_key` method removes all impermanent keys from the vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.remove_key()
        print(response)

asyncio.run(main())
```

### Ping Vehicle

The `ping` method performs a no-op on the vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.ping()
        print(response)

asyncio.run(main())
```

### Data Refresh

The `data_refresh` method forces a refresh of the vehicle data.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.data_refresh()
        print(response)

asyncio.run(main())
```

### Closure Control

The `closure` method opens, closes, moves, or stops vehicle closures (doors, trunks, charge port, tonneau).

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )
        from tesla_fleet_api.const import ClosureState

        vehicle = teslemetry.vehicles.create("<vin>")

        # Open the front trunk
        response = await vehicle.closure(front_trunk=ClosureState.OPEN)
        print(response)

        # Close all doors
        response = await vehicle.closure(
            front_driver_door=ClosureState.CLOSE,
            front_passenger_door=ClosureState.CLOSE,
            rear_driver_door=ClosureState.CLOSE,
            rear_passenger_door=ClosureState.CLOSE,
        )
        print(response)

asyncio.run(main())
```

### Seat Heater

The `seat_heater` method sets multiple seat heaters at once.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )
        from tesla_fleet_api.const import SeatHeaterLevel

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.seat_heater(
            front_left=SeatHeaterLevel.HIGH,
            front_right=SeatHeaterLevel.HIGH,
        )
        print(response)

asyncio.run(main())
```

### Charge on Solar

The `charge_on_solar` method enables or disables charging on solar and sets charge limits.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.charge_on_solar(
            enabled=True,
            lower_charge_limit=20,
            upper_charge_limit=80,
        )
        print(response)

asyncio.run(main())
```

### Dashcam Save

The `dashcam_save` method saves the last 10 minutes of dashcam footage.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.dashcam_save()
        print(response)

asyncio.run(main())
```

### Play Video

The `play_video` method plays a supported video URL in the vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.play_video(url="https://www.youtube.com/watch?v=example")
        print(response)

asyncio.run(main())
```

### Light Show

The `start_light_show` and `stop_light_show` methods control vehicle light shows.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        vehicle = teslemetry.vehicles.create("<vin>")

        response = await vehicle.start_light_show(show_index=0)
        print(response)

        response = await vehicle.stop_light_show()
        print(response)

asyncio.run(main())
```

## Migrate to OAuth

The `migrate_to_oauth` method migrates from an access token to OAuth.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        teslemetry = Teslemetry(
            session=session,
            access_token="<access_token>",
        )

        response = await teslemetry.migrate_to_oauth(client_id="homeassistant")
        print(response)

asyncio.run(main())
```
