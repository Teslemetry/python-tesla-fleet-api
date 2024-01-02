# tesla_fleet_api
Python library for Tesla Fleet API and Teslemetry.

Currently does not support the end to end encrypted telemetry or command API.

Based on [Tesla Developer documentation](https://developer.tesla.com/docs/fleet-api).


## TeslaFleetApi
This is the base class, however can also be used directly if you have a valid user access_token.

```
import asyncio
import aiohttp

from tesla_fleet_api import TeslaFleetApi, TeslaFleetError


async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
            raise_for_status=True,
        )

        try:
            data = await api.vehicle.list()
            print(data)
        except TeslaFleetError.Base as e:
            print(e.message, e.error)

asyncio.run(main())
```

## TeslaFleetOAuth
This extends TeslaFleetApi to support OAuth, and requires a client_id, and either a refresh_token or initial authentication code.

## Teslemetry
This extends TeslaFleetApi to send requests through Teslemetry, which manages all aspects of Tesla OAuth. This class only requires an access_token from the Teslemetry console.

```
import asyncio
import aiohttp

from tesla_fleet_api import Teslemetry, TeslaFleetError


async def main():
    async with aiohttp.ClientSession() as session:
        api = Teslemetry(
            access_token="<access_token>",
            session=session,
            raise_for_status=True,
        )

        try:
            data = await api.vehicle.list()
            print(data)
        except TeslaFleetError.Base as e:
            print(e.message, e.error)

asyncio.run(main())
```