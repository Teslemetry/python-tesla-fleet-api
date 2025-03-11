# Fleet API for Energy Sites

This document provides detailed examples for using the Fleet API for energy sites.

## List Energy Sites

The `TeslaFleetApi` class provides methods to interact with the Fleet API for energy sites. Here's a basic example to list all energy sites:

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
            data = await api.energySites.list()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Get Energy Site Data

You can get detailed data for a specific energy site using its ID:

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
            energy_site_data = await api.energySites.get("<energy_site_id>")
            print(energy_site_data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Backup Reserve

You can adjust the backup reserve for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            backup_reserve_response = await energy_site.backup(backup_reserve_percent=20)
            print(backup_reserve_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Backup History

You can get the backup (off-grid) event history of a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            backup_history_response = await energy_site.backup_history(period="day")
            print(backup_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Charge History

You can get the charging history of a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            charge_history_response = await energy_site.charge_history(start_date="2022-01-01", end_date="2022-01-31")
            print(charge_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Energy History

You can get the energy measurements of a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            energy_history_response = await energy_site.energy_history(period="day")
            print(energy_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Grid Import/Export

You can allow or disallow charging from the grid and exporting energy to the grid for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            grid_import_export_response = await energy_site.grid_import_export(disallow_charge_from_grid_with_solar_installed=True)
            print(grid_import_export_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Live Status

You can get the live status of a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            live_status_response = await energy_site.live_status()
            print(live_status_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Off-Grid Vehicle Charging Reserve

You can adjust the off-grid vehicle charging backup reserve for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            off_grid_vehicle_charging_reserve_response = await energy_site.off_grid_vehicle_charging_reserve(off_grid_vehicle_charging_reserve_percent=10)
            print(off_grid_vehicle_charging_reserve_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Operation Mode

You can set the operation mode for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            operation_mode_response = await energy_site.operation(default_real_mode="self_consumption")
            print(operation_mode_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Site Info

You can get information about a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            site_info_response = await energy_site.site_info()
            print(site_info_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Storm Mode

You can update the storm watch participation for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            storm_mode_response = await energy_site.storm_mode(enabled=True)
            print(storm_mode_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Time of Use Settings

You can update the time of use settings for a specific energy site using its ID:

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
            energy_site = await api.energySites.get("<energy_site_id>")
            time_of_use_settings_response = await energy_site.time_of_use_settings(settings={"tou_settings": {"tariff_content_v2": {}}})
            print(time_of_use_settings_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```
