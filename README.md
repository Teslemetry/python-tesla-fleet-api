# tesla_fleet_api
Python library for Tesla Fleet API and Teslemetry

Currently does not support the End to End encrypted Telemetry or Command API.

Based on [Tesla Developer documentation](https://developer.tesla.com/docs/fleet-api).

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