# Bluetooth for Vehicles

This document provides detailed examples for using Bluetooth for vehicles.

## Initialize TeslaBluetooth

The `TeslaBluetooth` class provides methods to interact with Tesla vehicles using Bluetooth. Here's a basic example to initialize the `TeslaBluetooth` class and discover nearby Tesla vehicles:

```python
import asyncio
from bleak import BleakScanner
from tesla_fleet_api import TeslaBluetooth

async def main():
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        if TeslaBluetooth().valid_name(device.name):
            print(f"Found Tesla vehicle: {device.name}")

asyncio.run(main())
```

## Create VehicleBluetooth Instance

You can create a `VehicleBluetooth` instance using the `TeslaBluetooth` class. Here's a basic example to create a `VehicleBluetooth` instance and set the private key from a file:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    vehicle.find_vehicle()
    print(f"Created VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

## Pair Vehicle

You can pair a `VehicleBluetooth` instance using the `pair` method. Here's a basic example to pair a `VehicleBluetooth` instance:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.pair()
    print(f"Paired with VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

## Wake Up Vehicle

You can wake up a `VehicleBluetooth` instance using the `wake_up` method. Here's a basic example to wake up a `VehicleBluetooth` instance:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.wake_up()
    print(f"Woke up VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

`wake_up()` returns when the vehicle-security computer acknowledges the wake
request. The infotainment computer can take longer to become ready, so
INFO-domain reads immediately after waking, such as `charge_state()` or
`vehicle_data()`, should retry `BluetoothTimeout` with backoff.

## Open/Close Individual Doors (Bluetooth Only)

The individual door closure commands are Bluetooth-only and are not available via Fleet API signed commands.
`open_*_door()` unlatches the selected door. `close_*_door()` only means the
vehicle accepted the close request; on vehicles without reliable powered door
close support, the door may remain physically ajar until someone pushes it
shut. Do not rely on an automated open-then-close cycle without checking
`closures_state()` or getting physical confirmation.

Available commands:

- `open_front_driver_door()`
- `close_front_driver_door()`
- `open_front_passenger_door()`
- `close_front_passenger_door()`
- `open_rear_driver_door()`
- `close_rear_driver_door()`
- `open_rear_passenger_door()`
- `close_rear_passenger_door()`

Example:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.connect()
    await vehicle.open_front_driver_door()
    await vehicle.disconnect()

asyncio.run(main())
```

## Get Vehicle Data

You can get data from a `VehicleBluetooth` instance using the individual state
reader methods. Each reader sends one BLE vehicle-data request and returns the
typed protobuf state from the signed-command reply.

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    charge_state = await vehicle.charge_state()
    print(f"Battery level for VIN {vehicle.vin}: {charge_state.battery_level}")

asyncio.run(main())
```

Available BLE state readers:

- `vehicle_state()`
- `charge_state()`
- `climate_state()`
- `drive_state()`
- `location_state()`
- `closures_state()`
- `charge_schedule_state()`
- `preconditioning_schedule_state()`
- `tire_pressure_state()`
- `media_state()`
- `media_detail_state()`
- `software_update_state()`
- `parental_controls_state()`

For explicit composite requests, use `vehicle_data(endpoints)` with
`BluetoothVehicleData` values:

```python
from tesla_fleet_api import BluetoothVehicleData

data = await vehicle.vehicle_data([BluetoothVehicleData.CHARGE_STATE])
```

Unlike `VehicleFleet.vehicle_data()`, the BLE `vehicle_data()` method requires
an explicit `endpoints` list and returns a `VehicleData` protobuf message, not a
REST JSON `dict`. Prefer the individual state readers, or a single explicit
endpoint, because requesting multiple endpoints together can exceed the
vehicle's signed-command response-size cap and raise
`TeslaFleetMessageFaultResponseSizeExceedsMTU`.
