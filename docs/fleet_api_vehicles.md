# Fleet API for Vehicles

This document provides detailed examples for using the Fleet API for vehicles.

## List Vehicles

The `TeslaFleetApi` class provides methods to interact with the Fleet API for vehicles. Here's a basic example to list all vehicles:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            data = await api.vehicles.list()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Get Vehicle Data

You can get detailed data for a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle_data = await api.vehicles.get("<vin>")
            print(vehicle_data)
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
            lock_response = await vehicle.lock()
            print(lock_response)
            unlock_response = await vehicle.unlock()
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
            start_charging_response = await vehicle.start_charging()
            print(start_charging_response)
            stop_charging_response = await vehicle.stop_charging()
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
            set_charge_limit_response = await vehicle.set_charge_limit(80)
            print(set_charge_limit_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Flash Lights

You can flash the lights of a specific vehicle using its VIN:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
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
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = await api.vehicles.get("<vin>")
            remote_start_response = await vehicle.remote_start()
            print(remote_start_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```
