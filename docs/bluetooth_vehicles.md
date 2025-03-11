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
    tesla_bluetooth.get_private_key("path/to/private_key.pem")
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
    private_key = tesla_bluetooth.get_private_key("path/to/private_key.pem")
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
    private_key = tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.wake_up()
    print(f"Woke up VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

## Get Vehicle Data

You can get data from a `VehicleBluetooth` instance using the `vehicle_data` method. Here's a basic example to get data from a `VehicleBluetooth` instance:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth, BluetoothVehicleData

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    data = await vehicle.vehicle_data([BluetoothVehicleData.CHARGE_STATE, BluetoothVehicleData.CLIMATE_STATE])
    print(f"Vehicle data for VIN: {vehicle.vin}")
    print(data)

asyncio.run(main())
```
