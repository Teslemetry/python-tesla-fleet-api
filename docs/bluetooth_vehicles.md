# Detailed Examples for Using Bluetooth for Vehicles

This document provides detailed examples for using the `TeslaBluetooth` class to interact with Tesla vehicles using Bluetooth.

## Example 1: Discovering Tesla Vehicles

The following example demonstrates how to discover Tesla vehicles using Bluetooth:

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

## Example 2: Querying Display Name

The following example demonstrates how to query the display name of a Tesla vehicle using Bluetooth:

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
            name = await TeslaBluetooth().query_display_name(device)
            print(f"Display name: {name}")

asyncio.run(main())
```

## Example 3: Connecting to a Tesla Vehicle

The following example demonstrates how to connect to a Tesla vehicle using Bluetooth:

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
            async with TeslaBluetooth() as bluetooth:
                await bluetooth.connect(device)
                print("Connected to Tesla vehicle")

asyncio.run(main())
```

## Example 4: Querying Vehicle Data

The following example demonstrates how to query vehicle data from a Tesla vehicle using Bluetooth:

```python
import asyncio
from bleak import BleakScanner
from tesla_fleet_api import TeslaBluetooth, BluetoothVehicleData

async def main():
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        if TeslaBluetooth().valid_name(device.name):
            print(f"Found Tesla vehicle: {device.name}")
            async with TeslaBluetooth() as bluetooth:
                await bluetooth.connect(device)
                data = await bluetooth.vehicle_data([
                    BluetoothVehicleData.CHARGE_STATE,
                    BluetoothVehicleData.CLIMATE_STATE,
                    BluetoothVehicleData.DRIVE_STATE,
                ])
                print(f"Vehicle data: {data}")

asyncio.run(main())
```
