# Tessie

Tessie is a service that provides additional telemetry data for Tesla vehicles. This document provides detailed examples of how to use the Tessie class in the Tesla Fleet API library.

## Initialization

To use the Tessie class, you need to initialize it with an aiohttp ClientSession and an access token.

```python
import asyncio
import aiohttp
from tesla_fleet_api import Tessie

async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

asyncio.run(main())
```

## Get Vehicles

The `vehicles` method retrieves the list of vehicles associated with the account.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        response = await tessie.vehicles()
        print(response)

asyncio.run(main())
```

## Get Vehicle State

The `state` method retrieves the state of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.state(vin)
        print(response)

asyncio.run(main())
```

## Get Battery Data

The `battery` method retrieves the battery data of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.battery(vin)
        print(response)

asyncio.run(main())
```

## Get Battery Health Data

The `battery_health` method retrieves the battery health data of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.battery_health(vin)
        print(response)

asyncio.run(main())
```

## Get All Battery Health Data

The `all_battery_health` method retrieves the battery health data of all vehicles associated with the account.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        response = await tessie.all_battery_health()
        print(response)

asyncio.run(main())
```
