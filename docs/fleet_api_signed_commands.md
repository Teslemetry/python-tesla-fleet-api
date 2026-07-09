# Fleet API with Signed Vehicle Commands

This document provides detailed examples for using the Fleet API with signed vehicle commands.

## Handshake

The `VehicleSigned` class provides methods to interact with the Fleet API using signed vehicle commands. Here's a basic example to perform a handshake:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            print("Handshake successful")
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Wake Up Vehicle

You can wake up a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            wake_up_response = await vehicle.wake_up()
            print(wake_up_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Lock/Unlock Vehicle

You can lock or unlock a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            lock_response = await vehicle.door_lock()
            print(lock_response)
            unlock_response = await vehicle.door_unlock()
            print(unlock_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Start/Stop Charging

You can start or stop charging a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            start_charging_response = await vehicle.charge_start()
            print(start_charging_response)
            stop_charging_response = await vehicle.charge_stop()
            print(stop_charging_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Set Charge Limit

You can set the charge limit for a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            set_charge_limit_response = await vehicle.set_charge_limit(80)
            print(set_charge_limit_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Other Charging Commands

Signed commands also include `charge_standard()`, `charge_max_range()`,
`set_charging_amps(charging_amps)`, schedule configuration, and charge-port
door commands. These methods share the same signatures as the Fleet API vehicle
commands, but are sent through the signed-command protocol.

`set_scheduled_charging()` and `set_scheduled_departure()` both update the
vehicle's shared `scheduled_charging_mode`. Disabling one mode while the other
is active can turn scheduled charging/departure off entirely, so callers that
toggle either setting should read the current `charge_state()` first and
restore the prior mode and fields when preserving the other schedule matters.

For signed commands, `set_scheduled_departure()` sends `enable`,
`departure_time`, weekday/all-week recurrence choices, and
`end_off_peak_time`. Its `preconditioning_enabled` and
`off_peak_charging_enabled` arguments are accepted for API compatibility but do
not map to fields in the vehicle's signed-command protobuf.

`charge_standard()` is not treated as a no-op by all vehicles: if the current
charge limit already equals `charge_limit_soc_std`, the vehicle may reject the
command with `already_standard`.

## Flash Lights

You can flash the lights of a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            flash_lights_response = await vehicle.flash_lights()
            print(flash_lights_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Honk Horn

You can honk the horn of a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            honk_horn_response = await vehicle.honk_horn()
            print(honk_horn_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Remote Start

You can remotely start a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            remote_start_response = await vehicle.remote_start_drive()
            print(remote_start_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Climate Commands

`VehicleSigned` supports signed climate command methods including
`auto_conditioning_start()`, `auto_conditioning_stop()`, `set_temps()`,
`set_climate_keeper_mode()`, `set_cabin_overheat_protection()`,
`set_cop_temp()`, `set_bioweapon_mode()`, `set_preconditioning_max()`,
`set_recirculation()`, the remote seat heater/cooler methods, and the
remote steering-wheel heat methods.

Remote seat and steering-wheel comfort commands can be rejected by the vehicle
with `cabin comfort remote settings not enabled` when
`climate_state().remote_heater_control_enabled` is false. That field is a
read-only vehicle setting; the library has no command to enable it.

## Low Power / Keep Accessory Power Modes

These are signed-only commands with no Fleet API REST equivalent. `set_low_power_mode` reduces standby power consumption while the vehicle is parked, and `set_keep_accessory_power_mode` keeps 12V accessory power available while parked. Both take a single `bool` to turn the mode on or off:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            low_power_response = await vehicle.set_low_power_mode(True)
            print(low_power_response)
            accessory_power_response = await vehicle.set_keep_accessory_power_mode(True)
            print(accessory_power_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```
