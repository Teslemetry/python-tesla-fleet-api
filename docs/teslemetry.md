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
